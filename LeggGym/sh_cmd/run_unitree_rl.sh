#!/bin/bash
# =========================================
# Script to run Python in unitree-rl environment
# safely without interference from ROS2 Python 3.10 packages
# =========================================

# Save old PYTHONPATH
OLD_PYTHONPATH="$PYTHONPATH"

# Unset PYTHONPATH to avoid conflicts with ROS2 Python 3.10
unset PYTHONPATH

# Activate conda environment
source ~/anaconda3/etc/profile.d/conda.sh
#conda activate unitree-rl
conda activate leggGym-rl

# Run Python with any arguments passed to the script
# If no arguments, opens interactive Python
if [ "$#" -eq 0 ]; then
    python
else
    python "$@"
fi

# Restore old PYTHONPATH after exiting Python
export PYTHONPATH="$OLD_PYTHONPATH"
