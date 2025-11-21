---
title: Full Installation Guide
layout: page
---

# Installation Overview

This page provides a very **short summary** of the installation steps.  
Full details are provided in the Jupyter notebooks and project-specific docs.

---

## System Requirements
- Ubuntu 20.04 or 22.04
- NVIDIA GPU (RTX 20xx – 50xx)
- Driver 525+
- CUDA 11.7+
- Python 3.8–3.10

## 1. Common Requirements

- Ubuntu 20.04 / 22.04
- NVIDIA GPU with recent driver (e.g. 525+)
- Conda (Anaconda / Miniconda)
- Python 3.8–3.10
- Git

---

## Installation Breakdown

### 1. For LeggedGym
1. Install NVIDIA driver  
2. Install CUDA  
3. Install Conda  
4. Install PyTorch CUDA  
5. Install IsaacGym  
6. Clone LeggedGym repo  
7. Run environment tests  

### 2. LeggedGym / IsaacGym

1. Install NVIDIA drivers and CUDA.
2. Install Conda and create an environment for RL.
3. Download and install **IsaacGym** from NVIDIA.
4. Validate IsaacGym examples.
5. Follow the instructions in:
   - `LeggedGym/LeggGym.ipynb`
   - Any `LeggedGym/docs/` files.

---
### 2. For BeyondMimic
1. Install Isaac Sim  
2. Install IsaacLab  
3. Install MuJoCo  
4. Install Unitree MuJoCo models  
5. Install whole-body tracking tools  
6. Configure WandB  

### 3. BeyondMimic / IsaacLab + MuJoCo

1. Install **Isaac Sim** and **IsaacLab**  
   👉 <https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/index.html>

2. Install **MuJoCo** and Unitree models  
   👉 <https://github.com/unitreerobotics/unitree_mujoco>

3. Install **Whole Body Tracking** tools  
   👉 <https://bitbucket.org/theconstructcore/whole_body_tracking/src/master/>

4. Set up **Weights & Biases**  
   👉 <https://wandb.ai/site/>

5. Follow:
   - `BeyondMimic/BeyondMimic.ipynb`
   - any additional docs in `BeyondMimic/docs/`.

---
## Verification
- `python3 -c "import mujoco"`  
- IsaacLab loading G1  

This page is intentionally minimal.  
Use it as a pointer to the more detailed notebooks and documentation.