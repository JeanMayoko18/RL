#!/bin/bash
# =========================================
# Script to install a Python component
# inside the isaac-env or unitree-rl environment
# without conflicts between ROS2 and Python 3.10
# =========================================

# Save the current PYTHONPATH
OLD_PYTHONPATH="$PYTHONPATH"

# Temporarily disable PYTHONPATH
unset PYTHONPATH
echo "[INFO] PYTHONPATH temporarily disabled"

# Automatically restore PYTHONPATH when the script exits
trap 'export PYTHONPATH="$OLD_PYTHONPATH"; echo "[INFO] PYTHONPATH restored on exit"' EXIT

# Activate the conda environment
source ~/anaconda3/etc/profile.d/conda.sh
#conda activate isaac-env
#conda activate unitree-rl
#conda activate leggGym-rl
conda activate isaacLab

# Export LD_LIBRARY_PATH for libpython3.8.so
#export LD_LIBRARY_PATH=~/anaconda3/envs/unitree-rl/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=~/anaconda3/envs/isaacLab/lib:$LD_LIBRARY_PATH

# Run the command passed as an argument
# Example usage: ./temp_pythonpath.sh pip install -e ~/isaacgym/python
echo "[INFO] Installing or verifying the component..."
"$@"
#pip install -e ~/isaacgym/python

# Optional: stay in an interactive shell
# bash
