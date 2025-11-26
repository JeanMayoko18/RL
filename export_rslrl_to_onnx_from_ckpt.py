#!/usr/bin/env python3
"""
Export an RSL-RL checkpoint (.pt) to ONNX.

Usage:
    python export_rslrl_to_onnx_from_ckpt.py \
        --checkpoint /path/to/model_9500.pt \
        --output     /path/to/model_9500.onnx \
        --task whole_body_tracking/G1PunchTask \
        --num_envs 1

Notes:
- This script does NOT require Isaac Sim to be running.
- It creates a dummy IsaacLab environment only for observation/action shapes.
- It loads the PPO runner and exports the trained policy to ONNX.
"""

import argparse
import os
import torch
import gymnasium as gym

# IsaacLab
from isaaclab_tasks.utils.hydra import hydra_task_config
from isaaclab.envs import DirectRLEnvCfg, ManagerBasedRLEnvCfg, DirectMARLEnvCfg
from isaaclab.envs import multi_agent_to_single_agent
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlVecEnvWrapper

# RSL-RL
from rsl_rl.runners import OnPolicyRunner

# Export utilities (these come from whole_body_tracking repo)
try:
    from whole_body_tracking.utils.exporter import (
        export_motion_policy_as_onnx,
        attach_onnx_metadata,
    )
except Exception as e:
    print("❌ ERROR: Missing exporter utilities from whole_body_tracking.")
    print("Make sure your Python environment contains:")
    print("   whole_body_tracking/utils/exporter.py")
    raise e


# ---------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------

parser = argparse.ArgumentParser(description="Export RSL-RL policy checkpoint to ONNX")

parser.add_argument("--checkpoint", type=str, required=True,
                    help="Path to the .pt checkpoint downloaded from WandB")

parser.add_argument("--output", type=str, required=True,
                    help="Path to save the exported .onnx model")

parser.add_argument("--task", type=str, default="whole_body_tracking/G1PunchTask",
                    help="IsaacLab task name")

parser.add_argument("--num_envs", type=int, default=1,
                    help="Number of envs for dummy environment")

parser.add_argument("--device", type=str, default="cpu",
                    help="Device to use for inference and export")

args = parser.parse_args()

checkpoint_path = os.path.abspath(args.checkpoint)
output_path = os.path.abspath(args.output)

if not os.path.isfile(checkpoint_path):
    raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

print("==============================================")
print("     RSL-RL → ONNX Exporter")
print("==============================================")
print(f"Checkpoint: {checkpoint_path}")
print(f"Output ONNX: {output_path}")
print(f"Task: {args.task}")
print("==============================================")


# -------------------------------------------------------------------------
# Load Hydra Config for Task / RSL-RL
# -------------------------------------------------------------------------

@hydra_task_config(args.task, "rsl_rl_cfg_entry_point")
def load_config(env_cfg: DirectRLEnvCfg | ManagerBasedRLEnvCfg | DirectMARLEnvCfg,
                agent_cfg: RslRlOnPolicyRunnerCfg):
    """Return loaded configs."""
    return env_cfg, agent_cfg


env_cfg, agent_cfg = load_config()

# Fix environment count
env_cfg.scene.num_envs = args.num_envs

# -------------------------------------------------------------------------
# Create environment (NO Isaac Sim required)
# -------------------------------------------------------------------------

print("→ Creating dummy IsaacLab environment...")
env = gym.make(
    args.task,
    cfg=env_cfg,
    headless=True,
    render_mode=None,
)
if isinstance(env.unwrapped, DirectMARLEnvCfg):
    env = multi_agent_to_single_agent(env)

env = RslRlVecEnvWrapper(env)
device = torch.device(args.device)

# -------------------------------------------------------------------------
# Load PPO policy from checkpoint
# -------------------------------------------------------------------------

print("→ Loading PPO policy from checkpoint...")
ppo_runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=device)

try:
    ppo_runner.load(checkpoint_path)
except Exception as e:
    print("❌ ERROR: Failed to load PyTorch checkpoint.")
    raise e

policy = ppo_runner.get_inference_policy(device=device)

# Extract normalizer (obs_rms)
normalizer = getattr(ppo_runner.alg, "obs_rms", None)
if normalizer is None and hasattr(ppo_runner.alg, "actor_critic"):
    normalizer = getattr(ppo_runner.alg.actor_critic, "obs_rms", None)

# -------------------------------------------------------------------------
# Export to ONNX
# -------------------------------------------------------------------------

export_dir = os.path.dirname(output_path)
os.makedirs(export_dir, exist_ok=True)

print(f"→ Exporting ONNX policy to: {output_path}")

export_motion_policy_as_onnx(
    env.unwrapped,
    ppo_runner.alg.policy,
    normalizer=normalizer,
    path=export_dir,
    filename=os.path.basename(output_path),
)

# Attach metadata
attach_onnx_metadata(env.unwrapped, checkpoint_path, export_dir)

print("==============================================")
print("   ✅ Export completed successfully!")
print(f"   ONNX saved at: {output_path}")
print("==============================================")
