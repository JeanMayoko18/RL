---
title: Home
layout: page
---

# RL Framework for Unitree Humanoid G1

Welcome to the documentation for the **RL Framework for Unitree Humanoid G1**.
This website describes two complementary humanoid control pipelines:

## 🔹 LeggedGym (IsaacGym RL)
GPU-accelerated reinforcement learning for locomotion.  
Parallel simulation, domain randomization, export to ONNX/TorchScript.

➡️ See: [LeggedGym Documentation](leggedgym.md)

---

## 🔹 BeyondMimic (IsaacLab Imitation Learning)
Whole-body human motion retargeting and tracking using MuJoCo physics.  
Designed for high-quality whole-body control.

➡️ See: [BeyondMimic Documentation](beyondmimic.md)

---

## 🔄 SIM2SIM + SIM2REAL Pipeline
Covers:
- IsaacGym → MuJoCo → IsaacLab transfer
- Real deployment on Unitree G1
- PD tuning, filtering, safety layers

➡️ See: [SIM2REAL Workflow](sim2real.md)

---

## ⚙️ Installation
Complete installation instructions for IsaacGym, IsaacLab, MuJoCo, and dependencies.

➡️ See: [Installation Guide](installation.md)