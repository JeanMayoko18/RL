#!/bin/bash
# =========================================
# Universal script to run/install a Python component
# inside isaac-env / unitree-rl / leggGym-rl environments,
# avoiding conflicts between ROS2 and Python 3.10+.
# PYTHONPATH is restored on shell exit.
# =========================================

# Save current PYTHONPATH
OLD_PYTHONPATH="$PYTHONPATH"
unset PYTHONPATH
echo "[INFO] PYTHONPATH temporarily disabled"

# Restore PYTHONPATH on exit
trap 'export PYTHONPATH="$OLD_PYTHONPATH"; echo "[INFO] PYTHONPATH restored on exit"' EXIT

# ------------------------------
# Detect package manager (priority: conda > micromamba)
# ------------------------------
CONDA_BASE=""
MAMBA_BASE=""

if command -v conda >/dev/null 2>&1; then
    CONDA_BASE=$(conda info --base)
    echo "[INFO] Using Conda at $CONDA_BASE"
elif command -v micromamba >/dev/null 2>&1; then
    MAMBA_BASE=$(micromamba info --base)
    echo "[INFO] Using Micromamba at $MAMBA_BASE"
else
    echo "[ERROR] Neither Conda nor Micromamba found. Please install one first."
    exit 1
fi

# ------------------------------
# Activate environment
# ------------------------------
ENV_NAME="leggGym-rl"
if [ -n "$CONDA_BASE" ]; then
    source "$CONDA_BASE/etc/profile.d/conda.sh"
    echo "[INFO] Activating conda environment: $ENV_NAME"
    conda activate "$ENV_NAME" || { echo "[ERROR] Failed to activate $ENV_NAME"; exit 1; }
elif [ -n "$MAMBA_BASE" ]; then
    source "$MAMBA_BASE/etc/profile.d/micromamba.sh"
    echo "[INFO] Activating micromamba environment: $ENV_NAME"
    micromamba activate "$ENV_NAME" || { echo "[ERROR] Failed to activate $ENV_NAME"; exit 1; }
fi

# ------------------------------
# Configure LD_LIBRARY_PATH for libpython3.8.so and IsaacGym
# ------------------------------
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib/python3.8/site-packages/isaacgym/_bindings/linux-x86_64:$LD_LIBRARY_PATH"
echo "[INFO] LD_LIBRARY_PATH configured for $CONDA_PREFIX"

# ------------------------------
# Execute command passed as argument
# ------------------------------
if [ $# -gt 0 ]; then
    CMD="$1"
    shift
    case "$CMD" in
        python)
            echo "[INFO] Running Python command: $CMD $*"
            python "$@"
            ;;
        conda)
            echo "[INFO] Running Conda command: $CMD $*"
            conda "$@"
            ;;
        micromamba)
            echo "[INFO] Running Micromamba command: $CMD $*"
            micromamba "$@"
            ;;
        *)
            echo "[INFO] Running generic command: $CMD $*"
            "$CMD" "$@"
            ;;
    esac
else
    echo "[INFO] No command provided, opening interactive shell..."
    echo "[INFO] You are now inside the environment '$ENV_NAME'. Type 'exit' to leave and restore PYTHONPATH."
    bash --rcfile <(echo "PS1='($ENV_NAME) \w\$ '")
fi
