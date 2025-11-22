# PKL to CSV Conversion: PBHC to BeyondMimic

This document explains the conversion process from PBHC (Physics-Based Humanoid Control) PKL motion files to the CSV format required by the BeyondMimic whole body tracking system for the Unitree G1 robot.

## Overview

The conversion script `convert_pbhc_pkl_to_beyondmimic_csv.py` transforms motion data from PBHC's PKL format into the specific CSV format expected by BeyondMimic's whole body tracking system.

## Source Data: PBHC PKL Format

PBHC motion files are stored in PKL (pickle) format at `~/git-repo/PBHC/example/motion_data/`. Each PKL file contains:

- **root_trans**: Root translation (3D position)
- **root_rot**: Root rotation as quaternion (qx, qy, qz, qw)
- **dof**: Joint angles for all degrees of freedom
- **fps**: Frame rate (typically 30 FPS)

Example files:
- `Horse-stance_punch.pkl`
- `Cross_punch.pkl`
- `Step_back_punch.pkl`

## Target Format: BeyondMimic CSV

The CSV format for BeyondMimic has a very specific structure with **30 columns per frame**:

### Column Structure (30 total columns)
1. **Columns 0-2**: Root translation (x, y, z)
2. **Columns 3-6**: Root rotation quaternion (qx, qy, qz, qw)
3. **Columns 7-29**: Joint angles (23 DOF)

### Joint Mapping (23 DOF)

The 23 degrees of freedom represent the G1 robot's joint configuration:

#### Lower Body (12 DOF - Columns 7-18)
- **Left Leg (6 DOF)**: Hip Roll, Hip Yaw, Hip Pitch, Knee, Ankle Pitch, Ankle Roll
- **Right Leg (6 DOF)**: Hip Roll, Hip Yaw, Hip Pitch, Knee, Ankle Pitch, Ankle Roll

#### Upper Body (11 DOF - Columns 19-29)
- **Torso (1 DOF)**: Waist pitch
- **Left Arm (5 DOF)**: Shoulder Pitch, Shoulder Roll, Shoulder Yaw, Elbow, Wrist Roll
- **Right Arm (5 DOF)**: Shoulder Pitch, Shoulder Roll, Shoulder Yaw, Elbow, Wrist Roll

**Note**: The G1 robot has 29 total DOF in PBHC, but BeyondMimic uses only 23 DOF, excluding:
- Waist yaw and roll (indices 12-13)
- Head pitch and yaw (indices 14-15)
- Left and right wrist pitch/yaw (indices 24-25, 28-29)

## Conversion Process

### 1. Load PKL Data
```python
import joblib
data = joblib.load(pkl_path)
motion_key = list(data.keys())[0]
motion_data = data[motion_key]
```

### 2. Extract Components
```python
dof = motion_data['dof']
root_rot = motion_data['root_rot']
root_trans = motion_data.get('root_trans', motion_data['root_trans_offset'])
```

### 3. Map Joints to 23 DOF
The conversion maps from PBHC's 29 DOF to BeyondMimic's 23 DOF:

```python
# Lower body (indices 0-11) - direct mapping
for i in range(12):
    joint_values_23.append(frame_dof[i])

# Upper body - selective mapping
joint_values_23.append(frame_dof[12])  # Waist pitch only
# Skip waist yaw (13), waist roll (14)
# Skip head pitch (15), head yaw (16)

# Arms - partial mapping
for arm_start in [17, 23]:  # Left arm, Right arm
    for j in range(5):  # Only first 5 DOF per arm
        joint_values_23.append(frame_dof[arm_start + j])
```

### 4. Write CSV
Each row in the CSV represents one frame with exactly 30 values:
- 3 root translation values
- 4 root rotation values (quaternion)
- 23 joint angle values

## Usage Example

```bash
# Convert a single file
python convert_pbhc_pkl_to_beyondmimic_csv.py \
    ~/git-repo/PBHC/example/motion_data/Horse-stance_punch.pkl \
    ~/git-repo/beyondmimic/whole_body_tracking/motions/horse_stance_punch.csv

# The converted CSV can then be used with BeyondMimic
cd ~/git-repo/beyondmimic/whole_body_tracking
python motion_player.py --motion motions/horse_stance_punch.csv
```

## Converted Motion Files

The following PBHC motions have been converted for use in BeyondMimic:
- `horse_stance_punch.csv` - Martial arts horse stance with punch
- `cross_punch.csv` - Cross punching motion
- `step_back_punch.csv` - Step back with punch combination

These files are stored in `~/git-repo/beyondmimic/whole_body_tracking/motions/`.

## Important Notes

1. **Quaternion Format**: PBHC already uses the (qx, qy, qz, qw) format that BeyondMimic expects, so no reordering is needed.

2. **Frame Rate**: PBHC motions are typically at 30 FPS, which matches the expected playback rate in BeyondMimic.

3. **Joint Limits**: The converted values should be validated against the G1 robot's joint limits to ensure safe operation.

4. **Missing DOF**: The 6 excluded degrees of freedom (waist yaw/roll, head pitch/yaw, wrist pitch/yaw) are set to zero or neutral positions in the physical robot during playback.

## Script Location

The conversion script is located at:
```
~/git-repo/beyondmimic/convert_pbhc_pkl_to_beyondmimic_csv.py
```

This script handles the complete conversion pipeline from PBHC PKL files to BeyondMimic-compatible CSV files.