#!/bin/bash
# =========================================
# Script to run Python in isaac-env environment
# safely without interference from ROS2 Python 3.10 packages
# =========================================

# Save old PYTHONPATH
OLD_PYTHONPATH="$PYTHONPATH"

# Unset PYTHONPATH to avoid conflicts with ROS2 Python 3.10
unset PYTHONPATH
echo "[INFO] PYTHONPATH temporarily unset"

# Activate conda environment
source ~/anaconda3/etc/profile.d/conda.sh
conda activate isaac-env

# Run Python with any arguments passed to the script
# If no arguments, opens interactive Python
##############################3
#if [ "$#" -eq 0 ]; then
#    python
#else
    # "$@" passes all arguments exactly as they were given
#    python "$@"
#fi

# Run whatever command is passed
if [ "$#" -eq 0 ]; then
    python
else
    "$@"
fi

# Restore old PYTHONPATH after exiting Python
export PYTHONPATH="$OLD_PYTHONPATH"
echo "[INFO] PYTHONPATH restored"
