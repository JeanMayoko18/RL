import argparse
import time
import numpy as np
import pinocchio as pin
import rerun as rr
import trimesh
import pickle
import joblib
import os

class RerunURDF():
    def __init__(self, robot_type):
        self.name = robot_type
        match robot_type:
            case 'g1':
                self.robot = pin.RobotWrapper.BuildFromURDF('robot_description/g1/g1_29dof_rev_1_0.urdf', './robot_description/g1', pin.JointModelFreeFlyer())
                self.Tpose = np.array([0,0,0.785,0,0,0,1,
                                       -0.15,0,0,0.3,-0.15,0,
                                       -0.15,0,0,0.3,-0.15,0,
                                       0,0,0,
                                       0, 1.57,0,1.57,0,0,0,
                                       0,-1.57,0,1.57,0,0,0]).astype(np.float32)
            case 'h1_2':
                self.robot = pin.RobotWrapper.BuildFromURDF('robot_description/h1_2/h1_2_wo_hand.urdf', 'robot_description/h1_2', pin.JointModelFreeFlyer())
                assert self.robot.model.nq == 7 + 12+1+14
                self.Tpose = np.array([0,0,1.02,0,0,0,1,
                                       0,-0.15,0,0.3,-0.15,0,
                                       0,-0.15,0,0.3,-0.15,0,
                                       0,
                                       0, 1.57,0,1.57,0,0,0,
                                       0,-1.57,0,1.57,0,0,0]).astype(np.float32)
            case 'h1':
                self.robot = pin.RobotWrapper.BuildFromURDF('robot_description/h1/h1.urdf', 'robot_description/h1', pin.JointModelFreeFlyer())
                assert self.robot.model.nq == 7 + 10+1+8
                self.Tpose = np.array([0,0,1.03,0,0,0,1,
                                       0,0,-0.15,0.3,-0.15,
                                       0,0,-0.15,0.3,-0.15,
                                       0,
                                       0, 1.57,0,1.57,
                                       0,-1.57,0,1.57]).astype(np.float32)
            case _:
                print(robot_type)
                raise ValueError('Invalid robot type')
        
        # print all joints names
        # for i in range(self.robot.model.njoints):
        #     print(self.robot.model.names[i])
        
        self.link2mesh = self.get_link2mesh()
        self.load_visual_mesh()
        self.update()
    
    def get_link2mesh(self):
        link2mesh = {}
        for visual in self.robot.visual_model.geometryObjects:
            mesh = trimesh.load_mesh(visual.meshPath)
            name = visual.name[:-2]
            mesh.visual = trimesh.visual.ColorVisuals()
            mesh.visual.vertex_colors = visual.meshColor
            link2mesh[name] = mesh
        return link2mesh
   
    def load_visual_mesh(self):       
        self.robot.framesForwardKinematics(pin.neutral(self.robot.model))
        for visual in self.robot.visual_model.geometryObjects:
            frame_name = visual.name[:-2]
            mesh = self.link2mesh[frame_name]
            
            frame_id = self.robot.model.getFrameId(frame_name)
            parent_joint_id = self.robot.model.frames[frame_id].parent
            parent_joint_name = self.robot.model.names[parent_joint_id]
            frame_tf = self.robot.data.oMf[frame_id]
            joint_tf = self.robot.data.oMi[parent_joint_id]
            rr.log(f'urdf_{self.name}/{parent_joint_name}',
                   rr.Transform3D(translation=joint_tf.translation,
                                  mat3x3=joint_tf.rotation,
                                  axis_length=0.01))
            
            relative_tf = joint_tf.inverse() * frame_tf
            mesh.apply_transform(relative_tf.homogeneous)
            rr.log(f'urdf_{self.name}/{parent_joint_name}/{frame_name}',
                   rr.Mesh3D(
                       vertex_positions=mesh.vertices,
                       triangle_indices=mesh.faces,
                       vertex_normals=mesh.vertex_normals,
                       vertex_colors=mesh.visual.vertex_colors,
                       albedo_texture=None,
                       vertex_texcoords=None,
                   ),
                   static=True)
    
    def update(self, configuration = None):
        self.robot.framesForwardKinematics(self.Tpose if configuration is None else configuration)
        for visual in self.robot.visual_model.geometryObjects:
            frame_name = visual.name[:-2]
            frame_id = self.robot.model.getFrameId(frame_name)
            parent_joint_id = self.robot.model.frames[frame_id].parent
            parent_joint_name = self.robot.model.names[parent_joint_id]
            joint_tf = self.robot.data.oMi[parent_joint_id]
            rr.log(f'urdf_{self.name}/{parent_joint_name}',
                   rr.Transform3D(translation=joint_tf.translation,
                                  mat3x3=joint_tf.rotation,
                                  axis_length=0.01))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_name', type=str, help="File name", default='dance1_subject2')
    parser.add_argument('--robot_type', type=str, help="Robot type", default='g1')
    args = parser.parse_args()

    rr.init(
        'Reviz', 
        spawn=True
    )
    rr.log('', rr.ViewCoordinates.RIGHT_HAND_Z_UP, static=True)

    file_name = args.file_name
    robot_type = args.robot_type
    
    # Check if file_name is a full path or just a name
    if os.path.isfile(file_name):
        # Full path provided
        file_path = os.path.expanduser(file_name)
        print(f"Loading file: {file_path}")
        if file_path.endswith('.pkl'):
            try:
                data = joblib.load(file_path)
            except Exception as e:
                print(f"Joblib failed ({e}), trying standard pickle")
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
            
            # Check if it's PBHC format (nested dict with motion data)
            if isinstance(data, dict) and len(data) > 0:
                motion_key = list(data.keys())[0]
                if isinstance(data[motion_key], dict) and 'dof' in data[motion_key]:
                    print(f"Detected PBHC format: {motion_key}")
                    motion_data = data[motion_key]
                    
                    # Extract components
                    dof = motion_data['dof']  # (T, 23)
                    root_rot = motion_data['root_rot']  # (T, 4) - quaternion
                    root_trans = motion_data.get('root_trans', motion_data.get('root_trans_offset'))
                    
                    num_frames = root_trans.shape[0]
                    print(f"Frames: {num_frames}, DOF: {dof.shape[1]}, Root trans: {root_trans.shape}")
                    
                    # Combine into format expected by visualizer: [x, y, z, qx, qy, qz, qw, joint1, ..., joint29]
                    data = np.zeros((num_frames, 7 + 29))
                    
                    # Root translation and rotation
                    data[:, 0:3] = root_trans
                    data[:, 3:7] = root_rot
                    
                    # Map 23 DOF to 29 DOF (same as conversion script)
                    # Lower body (0-11)
                    data[:, 7:19] = dof[:, 0:12]
                    # Waist - only waist_yaw from PBHC
                    data[:, 19] = dof[:, 12]  # waist_yaw
                    data[:, 20] = 0.0  # waist_roll (missing in PBHC)
                    data[:, 21] = 0.0  # waist_pitch (missing in PBHC)
                    # Left arm (15-18 in PBHC -> 22-25 in output)
                    data[:, 22:26] = dof[:, 15:19]
                    # Left wrist (missing in PBHC)
                    data[:, 26:29] = 0.0
                    # Right arm (19-22 in PBHC -> 29-32 in output)
                    data[:, 29:33] = dof[:, 19:23]
                    # Right wrist (missing in PBHC)
                    data[:, 33:36] = 0.0
                    
                    print(f"Converted PBHC data to visualization format: {data.shape}")
                else:
                    data = np.array(data)
            elif not isinstance(data, np.ndarray):
                data = np.array(data)
        elif file_path.endswith('.csv'):
            data = np.genfromtxt(file_path, delimiter=',')
        else:
            raise ValueError(f"Unsupported file format. Use .csv or .pkl")
    else:
        # Just a name, look in robot_type directory
        csv_file = robot_type + '/' + file_name + '.csv'
        pkl_file = robot_type + '/' + file_name + '.pkl'
        
        if os.path.exists(pkl_file):
            print(f"Loading pickle file: {pkl_file}")
            try:
                data = joblib.load(pkl_file)
            except Exception as e:
                print(f"Joblib failed ({e}), trying standard pickle")
                with open(pkl_file, 'rb') as f:
                    data = pickle.load(f)
            # Ensure data is numpy array
            if not isinstance(data, np.ndarray):
                data = np.array(data)
        elif os.path.exists(csv_file):
            print(f"Loading CSV file: {csv_file}")
            data = np.genfromtxt(csv_file, delimiter=',')
        else:
            raise FileNotFoundError(f"Could not find {csv_file} or {pkl_file}")

    rerun_urdf = RerunURDF(robot_type)
    for frame_nr in range(data.shape[0]):
        rr.set_time_sequence('frame_nr', frame_nr)
        configuration = data[frame_nr, :]
        rerun_urdf.update(configuration)
        time.sleep(0.03)
