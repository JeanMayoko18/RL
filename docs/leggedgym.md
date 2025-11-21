---
title: LeggedGym (IsaacGym RL)
layout: page
---

# LeggedGym — IsaacGym RL for Unitree Humanoid G1

---

# 1. Overview

**LeggedGym** is an IsaacGym-based reinforcement learning (RL) framework enabling massively parallel GPU simulation for training locomotion and stabilization policies on the **Unitree Humanoid G1**.

- Backend: **NVIDIA IsaacGym**
- Focus: standing, balance, robust locomotion
- Output: deployable ONNX / TorchScript policies
- Usage: standalone or combined with **BeyondMimic (IsaacLab)**

---

# 2. Goals

This documentation provides a complete pipeline to:

- Prepare the **NVIDIA GPU environment** for IsaacGym  
- Configure and train **PPO-based locomotion policies**  
- Use terrain generation and domain randomization  
- Monitor training with TensorBoard  
- Export policies to **ONNX / TorchScript**  
- Prepare deployment for **SIM2REAL** via Unitree SDK + ROS  

---

# 4. Features

- GPU-accelerated physics simulation  
- Parallel PPO-based RL training  
- Domain randomization (mass, friction, noise, latency)  
- Terrain generation (flat, slopes, uneven terrain)  
- Fast policy export (ONNX / TorchScript)

---

# 5. Training Workflow

## 5.1 Install IsaacGym

```bash
conda create -n isaacgym_legged python=3.8
conda activate isaacgym_legged
```
Install IsaacGym from the NVIDIA SDK package and verify the sample environments.

## 5.2 Configure LeggedGym for Unitree G1

Edit the environment and configuration files:

```bash
legged_gym/envs/
legged_gym/cfg/
```
Configure:

- robot asset
- observation and action spaces
- control mode
- terrain
- domain randomization
- reward terms

### 5.3 Train RL Policies
```bash
python unitree_rl_gym/legged_gym/scripts/train.py --task=g1

```
```markdown
Optional arguments:
 * --headless
 * --max_iterations
 * --num_envs

```
### 5.4 Monitor Training
```bash
tensorboard --logdir=logs/
```

```markdown
Use TensorBoard to track:
 * rewards
 * value loss
 * policy loss
 * success rate

```

## 6. Detailed Notebook

For detailed, step-by-step commands and screenshots, follow the notebook:

➡️ [**LeggedGym/LeggGym.ipynb**](../LeggedGym/LeggGym.ipynb)

## 7. External References

Isaac Gym SDK
👉 https://developer.nvidia.com/isaac-gym
Unitree ROS to Real
👉 https://github.com/unitreerobotics/unitree_ros_to_real
Unitree ROS
👉 https://github.com/unitreerobotics/unitree_ros
(Optional) The Construct learning platform
👉 https://www.theconstructsim.com/

