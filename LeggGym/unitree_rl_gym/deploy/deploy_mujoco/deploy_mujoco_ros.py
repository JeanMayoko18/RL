#!/usr/bin/env python

import time
import os
import argparse

import mujoco
import mujoco.viewer
import numpy as np
import yaml

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray

from legged_gym import LEGGED_GYM_ROOT_DIR

# --------- MUJOCO / EGL BACKEND (comme dans ton script original) ----------
os.environ["MUJOCO_GL"] = "egl"
os.environ["EGL_DEVICE_ID"] = "0"
os.environ["DRI_PRIME"] = "1"


def get_gravity_orientation(quaternion):
    qw = quaternion[0]
    qx = quaternion[1]
    qy = quaternion[2]
    qz = quaternion[3]

    gravity_orientation = np.zeros(3)
    gravity_orientation[0] = 2 * (-qz * qx + qw * qy)
    gravity_orientation[1] = -2 * (qz * qy + qw * qx)
    gravity_orientation[2] = 1 - 2 * (qw * qw + qz * qz)
    return gravity_orientation


def pd_control(target_q, q, kp, target_dq, dq, kd):
    """Calculates torques from position commands"""
    return (target_q - q) * kp + (target_dq - dq) * kd


class MujocoRosBridge(Node):
    """
    Lance la simulation MuJoCo G1 (comme deploy_mujoco.py) mais :
      - ne charge PLUS de policy Torch
      - lit les actions RL depuis /mujoco/joint_torque_cmd (Float64MultiArray)
      - applique PD pour générer les torques
      - publie JointState sur /mujoco/joint_states
    """

    def __init__(self, config_file: str):
        super().__init__("mujoco_ros_bridge")

        # --------- Charger la config YAML (exactement comme ton script) ----------
        with open(f"{LEGGED_GYM_ROOT_DIR}/deploy/deploy_mujoco/configs/{config_file}", "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            # on ignore policy_path ici: la policy vient de ROS / ONNX
            xml_path = config["xml_path"].replace("{LEGGED_GYM_ROOT_DIR}", LEGGED_GYM_ROOT_DIR)

            self.simulation_duration = config["simulation_duration"]
            self.simulation_dt = config["simulation_dt"]
            self.control_decimation = config["control_decimation"]

            self.kps = np.array(config["kps"], dtype=np.float32)
            self.kds = np.array(config["kds"], dtype=np.float32)
            self.default_angles = np.array(config["default_angles"], dtype=np.float32)

            self.ang_vel_scale = config["ang_vel_scale"]
            self.dof_pos_scale = config["dof_pos_scale"]
            self.dof_vel_scale = config["dof_vel_scale"]
            self.action_scale = config["action_scale"]
            self.cmd_scale = np.array(config["cmd_scale"], dtype=np.float32)

            self.num_actions = config["num_actions"]
            self.num_obs = config["num_obs"]
            self.cmd = np.array(config["cmd_init"], dtype=np.float32)

        # --------- Variables de contexte (comme ton script original) ----------
        self.action = np.zeros(self.num_actions, dtype=np.float32)
        self.target_dof_pos = self.default_angles.copy()
        self.obs = np.zeros(self.num_obs, dtype=np.float32)
        self.counter = 0

        # --------- Charger le modèle MuJoCo ----------
        self.m = mujoco.MjModel.from_xml_path(xml_path)
        self.d = mujoco.MjData(self.m)
        self.m.opt.timestep = self.simulation_dt

        # --------- ROS I/O ----------
        # /mujoco/joint_torque_cmd transporte ICI l'action RL normalisée
        self.last_action = np.zeros(self.num_actions, dtype=np.float32)

        self.sub_action = self.create_subscription(
            Float64MultiArray,
            "/mujoco/joint_torque_cmd",
            self.action_callback,
            10,
        )

        self.pub_js = self.create_publisher(JointState, "/mujoco/joint_states", 10)

        # Nom des joints (optionnel, juste pour JointState)
        self.joint_names = [f"joint_{i}" for i in range(self.num_actions)]

        self.get_logger().info(
            f"✅ MujocoRosBridge initialized with config '{config_file}'\n"
            f"  xml_path={xml_path}\n"
            f"  num_actions={self.num_actions}, num_obs={self.num_obs}\n"
            f"  simulation_dt={self.simulation_dt}, control_decimation={self.control_decimation}"
        )

    # -------------------- ROS callbacks ------------------------

    def action_callback(self, msg: Float64MultiArray):
        data = np.array(msg.data, dtype=np.float32)
        if data.shape[0] != self.num_actions:
            self.get_logger().warn(
                f"Received action size {data.shape[0]} != num_actions {self.num_actions}. "
                "Clamping/padding."
            )
            if data.shape[0] > self.num_actions:
                data = data[: self.num_actions]
            else:
                tmp = np.zeros(self.num_actions, dtype=np.float32)
                tmp[: data.shape[0]] = data
                data = tmp
        self.last_action = data

    # -------------------- Boucle de simulation ------------------------

    def run(self):
        """
        Boucle de simulation principale, avec viewer MuJoCo et bridge ROS.
        """
        with mujoco.viewer.launch_passive(self.m, self.d) as viewer:
            start = time.time()
            while viewer.is_running() and time.time() - start < self.simulation_duration:
                step_start = time.time()

                # PD control vers target_dof_pos
                # d.qpos[7:] = positions articulaires
                # d.qvel[6:] = vitesses articulaires
                tau = pd_control(
                    self.target_dof_pos,
                    self.d.qpos[7:],
                    self.kps,
                    np.zeros_like(self.kds),
                    self.d.qvel[6:],
                    self.kds,
                )
                self.d.ctrl[:] = tau

                mujoco.mj_step(self.m, self.d)

                self.counter += 1

                # -- Contrôle toutes les "control_decimation" steps --
                if self.counter % self.control_decimation == 0:
                    # On pourrait garder le code de construction d'obs pour debug,
                    # mais la policy ne tourne plus ici -> c'est ROS qui fournit action.
                    # On met simplement target_dof_pos à partir de last_action (RL externe).
                    self.action = self.last_action.copy()
                    self.target_dof_pos = self.action * self.action_scale + self.default_angles

                # Publier JointState pour ROS
                self.publish_joint_state()

                # Laisser ROS traiter les callbacks
                rclpy.spin_once(self, timeout_sec=0.0)

                # Sync viewer
                viewer.sync()

                # Time-keeping (comme ton script)
                time_until_next_step = self.m.opt.timestep - (time.time() - step_start)
                if time_until_next_step > 0:
                    time.sleep(time_until_next_step)

            self.get_logger().info("⏹ Simulation finished (duration reached or viewer closed).")

    def publish_joint_state(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names

        # positions/vitesses articulaires comme dans ton script (qpos[7:], qvel[6:])
        qj = self.d.qpos[7 : 7 + self.num_actions]
        dqj = self.d.qvel[6 : 6 + self.num_actions]

        msg.position = qj.tolist()
        msg.velocity = dqj.tolist()
        self.pub_js.publish(msg)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file", type=str, help="config file name in the config folder (e.g. g1.yaml)")
    args = parser.parse_args()
    config_file = args.config_file

    rclpy.init()
    node = MujocoRosBridge(config_file)

    try:
        node.run()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
