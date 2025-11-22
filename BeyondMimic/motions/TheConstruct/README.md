# Motion Data Sources

This folder contains reference motion CSV files for training BeyondMimic tracking policies.

## Available Data Sources

### 1. LAFAN1 Dataset (Retargeted for G1) ✅ **EASIEST TO USE**
**Source:** https://huggingface.co/datasets/lvhaidong/LAFAN1_Retargeting_Dataset

Already retargeted to Unitree G1 format - ready to use!

**Categories available:**
- Dance motions (dance1, dance2)
- Walking (walk1, walk1turn90, walk1turn180)
- Running (run1)
- Fighting/Sports (fight1, fightAndSports1)
- Fall and Get Up (fallAndGetUp1, fallAndGetUp2, fallAndGetUp3)
- Jumps (jumps1)
- Obstacles (obstacles1)
- Sprint Jumps (sprintJump1)

**Download with:**
```bash
# Use the provided script
./download_motions.sh

# Or manually download specific motions:
wget -P motions "https://huggingface.co/datasets/lvhaidong/LAFAN1_Retargeting_Dataset/resolve/main/g1/dance1_subject1.csv"
```

### 2. KungfuBot Sidekicks
**Source:** https://kungfu-bot.github.io/

Contains sidekick motions. **Requires retargeting** to Unitree G1 format before use.

### 3. ASAP - Cristiano Ronaldo Celebration
**Source:** https://github.com/LeCAR-Lab/ASAP

Contains CR7 celebration motion. **Requires retargeting** to Unitree G1 format before use.

### 4. HuB - Balance Motions
**Source:** https://hub-robot.github.io/

Contains balance motions. **Requires retargeting** to Unitree G1 format before use.

## Current Downloaded Motions

Run `ls -lh *.csv` in this directory to see downloaded files.

## Next Steps on GPU Machine

Once you have CSV files, process them with Isaac Lab:

```bash
# Convert CSV to NPZ (with maximum coordinates via FK)
python scripts/csv_to_npz.py \
  --input_file motions/dance1_subject1.csv \
  --input_fps 30 \
  --output_name dance1_subject1 \
  --headless

# Test the motion playback
python scripts/replay_npz.py \
  --registry_name={your-org}-org/wandb-registry-motions/dance1_subject1

# Train on the motion
python scripts/rsl_rl/train.py \
  --task=Tracking-Flat-G1-v0 \
  --registry_name {your-org}-org/wandb-registry-motions/dance1_subject1 \
  --headless \
  --logger wandb \
  --log_project_name beyondmimic \
  --run_name dance1_test
```

## Notes

- CSV files are in Unitree's retargeting format: base pose (7 values) + joint positions
- NPZ files add maximum coordinates (body positions, orientations, velocities) computed via FK
- WandB registry is used to store and version control processed motions
- Remember to set `WANDB_ENTITY` to your organization name (not username)
