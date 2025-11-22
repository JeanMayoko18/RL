
#!/bin/bash
# =========================================
# Universal script to run Python or Conda commands
# inside the isaac-env / unitree-rl / leggGym-rl environment
# Avoid conflicts between ROS2 and Python 3.10+
# Restores PYTHONPATH on shell exit
# =========================================

# Save current PYTHONPATH
OLD_PYTHONPATH="$PYTHONPATH"
unset PYTHONPATH
echo "[INFO] PYTHONPATH temporarily disabled"

# Restore PYTHONPATH on exit
trap 'export PYTHONPATH="$OLD_PYTHONPATH"; echo "[INFO] PYTHONPATH restored on exit"' EXIT

# ------------------------------
# Detect package manager
# Priority: Conda > Micromamba
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
#conda activate isaac-env
#conda activate unitree-rl
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
# Configure LD_LIBRARY_PATH
# ------------------------------
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib/python3.8/site-packages/isaacgym/_bindings/linux-x86_64:$LD_LIBRARY_PATH"
echo "[INFO] LD_LIBRARY_PATH configured for $CONDA_PREFIX"

# ------------------------------
# Check the first argument to decide execution
# ------------------------------
if [ $# -eq 0 ]; then
    echo "[INFO] No command provided, opening interactive shell..."
    bash --rcfile <(echo "PS1='($ENV_NAME) \w\$ '")
    exit 0
fi

CMD="$1"
shift  # remove first argument

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
