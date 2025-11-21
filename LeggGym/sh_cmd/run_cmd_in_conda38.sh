#!/bin/bash
# =========================================
# Script to install or run a Python component
# inside the isaac-env or unitree-rl or leggGym-rl environment,
# avoiding conflicts between ROS2 and Python 3.10.
# PYTHONPATH will be restored only when you exit the shell.
# When you type exit or press Ctrl+D, the shell closes and your original PYTHONPATH is restored.
#make the script executable: chmod +x run_cmd_in_conda38.sh 
# =========================================

# Save the current PYTHONPATH
OLD_PYTHONPATH="$PYTHONPATH"

# Temporarily disable PYTHONPATH
unset PYTHONPATH
echo "[INFO] PYTHONPATH temporarily disabled"

# Activate the conda environment
source ~/anaconda3/etc/profile.d/conda.sh
#conda activate isaac-env
#conda activate unitree-rl
conda activate leggGym-rl

# Export LD_LIBRARY_PATH for libpython3.8.so
export LD_LIBRARY_PATH=~/anaconda3/envs/leggGym-rl/lib:$LD_LIBRARY_PATH

# Run the command passed as an argument (optional)
if [ $# -gt 0 ]; then
    echo "[INFO] Running command: $@"
    "$@"
else
    echo "[INFO] No command provided, opening interactive shell..."
fi

# Open an interactive shell with environment name in prompt
echo "[INFO] You are now inside the environment '$(basename $CONDA_DEFAULT_ENV)'."
echo "[INFO] Type 'exit' to leave and restore PYTHONPATH."

# Create a temporary RC file for a clean shell prompt
bash --rcfile <(echo "PS1='($(basename $CONDA_DEFAULT_ENV)) \w\$ '")

# When the user exits this shell, restore PYTHONPATH
export PYTHONPATH="$OLD_PYTHONPATH"
echo "[INFO] PYTHONPATH restored after exiting the shell."
