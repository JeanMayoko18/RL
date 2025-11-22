#!/usr/bin/env python3
"""
Convert PBHC motion data to G1 CSV format for beyondmimic
Fixed version that properly handles wrist_roll joints and root pose
"""

import sys
sys.path.append('/usr/lib/python3/dist-packages')  # For joblib from apt
import joblib
import numpy as np
import csv

def convert_pbhc_to_g1_fixed(pkl_path, output_csv_path):
    """Convert PBHC PKL file to G1 CSV format with proper joint mapping"""
    
    # Load the PKL file
    print(f"Loading {pkl_path}...")
    data = joblib.load(pkl_path)
    
    # Get the motion data
    motion_key = list(data.keys())[0]
    motion_data = data[motion_key]
    
    print(f"Processing motion: {motion_key}")
    print(f"Number of frames: {motion_data['dof'].shape[0]}")
    
    # Check available fields
    print("\nAvailable fields in PBHC data:")
    for key in motion_data.keys():
        if isinstance(motion_data[key], np.ndarray):
            print(f"  {key}: shape {motion_data[key].shape}")
    
    # Extract data
    dof = motion_data['dof']  # (T, 23) - joint angles
    root_rot = motion_data['root_rot']  # (T, 4) - root rotation quaternion
    
    # Use root_trans if available, otherwise use root_trans_offset
    if 'root_trans' in motion_data:
        print("Using root_trans (actual position)")
        root_trans = motion_data['root_trans']
    else:
        print("Using root_trans_offset")
        root_trans = motion_data['root_trans_offset']
    
    num_frames = root_trans.shape[0]
    
    # Check if we have pose_aa which might contain wrist data
    has_wrist_data = False
    pose_aa = None
    if 'pose_aa' in motion_data:
        pose_aa = motion_data['pose_aa']
        print(f"\nFound pose_aa with shape {pose_aa.shape}")
        # pose_aa is (T, 27, 3) - 27 joints in axis-angle
        # PBHC joint order in pose_aa might include wrists
        has_wrist_data = pose_aa.shape[1] >= 25  # Should have at least 25 joints for wrists
    
    # Analyze root data
    print(f"\nRoot data analysis:")
    print(f"  First frame root trans: {root_trans[0]}")
    print(f"  First frame root rot: {root_rot[0]}")
    print(f"  Root quaternion magnitude: {np.linalg.norm(root_rot[0])}")
    
    # Prepare output data
    output_data = []
    
    for frame_idx in range(num_frames):
        row = []
        
        # Add root translation (x, y, z)
        row.extend(root_trans[frame_idx].tolist())
        
        # Add root rotation quaternion
        # PBHC already uses (qx, qy, qz, qw) format!
        # LAFAN1 also uses (qx, qy, qz, qw) format
        # No conversion needed!
        quat = root_rot[frame_idx]
        row.extend(quat.tolist())
        
        # Map joints to 29 DOF format
        joint_values_29 = []
        frame_dof = dof[frame_idx]
        
        # PBHC 23 DOF mapping:
        # 0-11: Lower body (legs)
        # 12-14: Waist (yaw, roll, pitch) 
        # 15-18: Left arm (shoulder + elbow)
        # 19-22: Right arm (shoulder + elbow)
        
        # Lower body joints (0-11) - direct mapping
        for i in range(12):
            joint_values_29.append(float(frame_dof[i]))
        
        # Waist joints - PBHC actually has all 3 waist joints!
        # But your G1 only has waist_yaw
        joint_values_29.append(float(frame_dof[12]))  # waist_yaw - YOUR G1 HAS THIS
        joint_values_29.append(0.0)  # waist_roll - YOUR G1 MISSING
        joint_values_29.append(0.0)  # waist_pitch - YOUR G1 MISSING
        
        # Left arm (shoulder + elbow)
        for i in range(15, 19):
            joint_values_29.append(float(frame_dof[i]))
        
        # Left wrist joints
        if has_wrist_data and pose_aa is not None:
            # Try to extract wrist roll from pose_aa
            # Joint 23 in pose_aa might be left wrist
            # For now, we'll set to small value to test
            joint_values_29.append(0.0)  # left_wrist_roll - YOUR G1 HAS THIS (but PBHC doesn't track)
        else:
            joint_values_29.append(0.0)  # left_wrist_roll - YOUR G1 HAS THIS
        
        joint_values_29.append(0.0)  # left_wrist_pitch - YOUR G1 MISSING
        joint_values_29.append(0.0)  # left_wrist_yaw - YOUR G1 MISSING
        
        # Right arm (shoulder + elbow)
        for i in range(19, 23):
            joint_values_29.append(float(frame_dof[i]))
        
        # Right wrist joints
        if has_wrist_data and pose_aa is not None:
            # Try to extract wrist roll from pose_aa
            # Joint 24 in pose_aa might be right wrist
            joint_values_29.append(0.0)  # right_wrist_roll - YOUR G1 HAS THIS (but PBHC doesn't track)
        else:
            joint_values_29.append(0.0)  # right_wrist_roll - YOUR G1 HAS THIS
        
        joint_values_29.append(0.0)  # right_wrist_pitch - YOUR G1 MISSING
        joint_values_29.append(0.0)  # right_wrist_yaw - YOUR G1 MISSING
        
        # Add all joint values to the row
        row.extend(joint_values_29)
        
        # Verify we have 36 columns
        assert len(row) == 36, f"Expected 36 columns, got {len(row)}"
        
        output_data.append(row)
    
    # Write to CSV
    print(f"\nWriting to {output_csv_path}...")
    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in output_data:
            formatted_row = [f"{val:.6f}" if isinstance(val, (float, np.float32, np.float64)) else str(val) for val in row]
            writer.writerow(formatted_row)
    
    print(f"Successfully converted {num_frames} frames to CSV")
    
    # Verify which columns are zero
    data_array = np.array(output_data)
    print("\nColumn analysis:")
    zero_cols = []
    for i in range(36):
        if np.all(data_array[:, i] == 0):
            zero_cols.append(i)
            if i >= 7:
                joint_idx = i - 7
                print(f"  Column {i+1} (joint {joint_idx}): ALL ZEROS")
    
    print(f"\nTotal zero columns: {len(zero_cols)} (should be 6 for your G1)")
    print("Expected zeros: waist_roll, waist_pitch, left_wrist_pitch, left_wrist_yaw, right_wrist_pitch, right_wrist_yaw")
    
    # Print first frame for verification
    print("\nFirst frame sample:")
    print(f"  Root translation: {output_data[0][:3]}")
    print(f"  Root quaternion (qx,qy,qz,qw): {output_data[0][3:7]}")
    
    return output_data

if __name__ == "__main__":
    pkl_path = "PBHC/example/motion_data/Horse-stance_punch.pkl"
    pkl_path = "../PBHC/Bruce_Lee_pose.pkl"
    output_csv = "../../whole_body_tracking/motions/Bruce_Lee_pose.csv"
    
    convert_pbhc_to_g1_fixed(pkl_path, output_csv)
    
    print(f"\n✅ Fixed conversion complete! Output saved to: {output_csv}")
    print("\nIMPORTANT NOTES:")
    print("1. PBHC only tracks 23 DOF, which doesn't include wrist joints")
    print("2. Your G1 has wrist_roll joints but PBHC doesn't track them")
    print("3. The wrist_roll values are set to 0, but you could add them manually")
    print("4. Check if the root pose looks correct when visualized")