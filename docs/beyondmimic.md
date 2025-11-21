---
title: BeyondMimic Full Documentation
layout: page
---

# BeyondMimic — Whole-body Imitation Learning for Unitree G1

---

# 1. Overview

**BeyondMimic** is a whole-body imitation learning framework that uses:

- **MuJoCo** humanoid physics  
- **IsaacLab** for rendering, sensors, and control  
- **Human motion retargeting**  
- **Tracking-based imitation learning**  

> BeyondMimic is independent from **LeggedGym**.  
> It can be used **alone** or as a **front-end** before RL fine-tuning.

---

# 2. Goals

This documentation explains how to:

- Use **MuJoCo** humanoid models of the Unitree G1  
- Perform **whole-body tracking (WBT)** from human motion  
- Train imitation policies using BeyondMimic  
- Log experiments using **Weights & Biases (W&B)**  
- Transfer policies to **IsaacLab** or **IsaacGym** for SIM2SIM or RL  

---

# 3. Components

## 3.1 Whole-body Tracking

- Human motion extraction (OpenPose / MoCap / WBT)  
- Skeleton normalization  
- Human-to-G1 joint retargeting  
- Normalized joint/velocity/contact representation  

---

## 3.2 Imitation Learning Losses

- Pose matching loss  
- Velocity matching loss  
- Contact consistency  
- Smoothness / regularization penalties  

---

## 3.3 MuJoCo Training Details

- 2000 Hz physics  
- Soft contacts  
- Tracking controller  
- Optional domain randomization  

---

## 3.4 IsaacLab Integration

- GPU rendering and observation packing  
- PD / torque controllers  
- Policy execution inside IsaacLab  
- Optional bridge to IsaacGym or ROS  

---

# 4. Training & Deployment Phases

## 4.1 Training Phase — `whole_body_tracking/`

- Motion dataset preparation  
- MuJoCo G1 model configuration  
- Imitation learning training  
- W&B logging  

## 4.2 Deployment Phase — `motion_tracking_controller/`

- Load trained policy  
- Evaluate in IsaacLab  
- Optional real-robot execution  

---

# 5. Outputs

- `checkpoint.pt` — trained policy weights  
- `policy.json` — metadata & config  
- (Optional) W&B logs — curves, videos, metrics  

---

# 6. Detailed Notebook

➡️ [**BeyondMimic/BeyondMimic.ipynb**](../BeyondMimic/BeyondMimic.ipynb)

---

# 7. External References

- IsaacLab installation  
  https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html  

- Unitree MuJoCo models  
  https://github.com/unitreerobotics/unitree_mujoco  

- Whole Body Tracking (The Construct)  
  https://bitbucket.org/theconstructcore/whole_body_tracking/src/master/  

- Weights & Biases  
  https://wandb.ai/site/  

---

# 8. Training Architecture

```mermaid
flowchart LR
    A[Human Motion Capture<br/>(MoCap / WBT)] --> B[Retargeting<br/>Whole-body Tracking]
    B --> C[MuJoCo Humanoid G1 Model]
    C --> D[Imitation Learning<br/>BeyondMimic]
    D --> E[Policy Checkpoints]
    E --> F[Deployment Controller<br/>IsaacLab / Real Robot]
