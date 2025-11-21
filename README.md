# RL Framework for Unitree Humanoid G1

This repository provides a complete workflow for training and deploying control policies for the **Unitree Humanoid G1** using two independent (but complementary) learning pipelines:

- **LeggedGym** → Reinforcement Learning (RL) using NVIDIA **IsaacGym**
- **BeyondMimic** → Whole-body imitation learning using **IsaacLab**

You can choose to train with:
- **LeggedGym only** (RL locomotion)
- **BeyondMimic only** (whole-body tracking)
- **Both pipelines** for a more complete humanoid control system

---

## 🚀 1. LeggedGym (IsaacGym Reinforcement Learning)

LeggedGym provides:
- GPU-accelerated reinforcement learning
- Massive parallel simulation (thousands of environments)
- Domain randomization for robustness
- Export of learned policies to **ONNX** or **TorchScript**
- Fast prototyping for locomotion controllers

---

## 🤖 2. BeyondMimic (IsaacLab Whole-Body Imitation Learning)

BeyondMimic enables:
- Whole-body human-to-humanoid motion retargeting
- Reference motion tracking and imitation learning
- High-fidelity physics using **MuJoCo**
- Connection with IsaacLab controllers and policy runners

---

## 🔄 3. SIM2SIM with MuJoCo + SIM2REAL Pipeline

This repository documents:
- SIM2SIM transfer between IsaacGym → MuJoCo → IsaacLab
- Real deployment on Unitree G1 using the SDK or ROS 2
- Motor PD tuning, sensor filtering, safety layers
- Fallback control strategies for real robot experiments

---

## 📘 Documentation

A complete documentation website is included in the `docs/` folder and can be published as **GitHub Pages**.

---



## 📁 Repository Structure

RL/
├── LeggedGym/                      # Training environments for legged robots (IsaacGym)
├── BeyondMimic/                    # Whole-body tracking & imitation learning (IsaacLab)
├── docs/                           # GitHub Pages documentation website
│   ├── index.md                    # Website homepage (Overview + navigation)
│   ├── leggedgym.md               # Full LeggedGym documentation
│   ├── beyondmimic.md             # Full BeyondMimic documentation
│   ├── sim2real.md                # SIM2SIM + SIM2REAL pipeline
│   ├── installation.md            # Installation + environment setup (IsaacGym/IsaacLab)
│   └── _config.yml                # GitHub Pages configuration (theme + navbar)
└── README.md                      # Main repository README (project overview)



