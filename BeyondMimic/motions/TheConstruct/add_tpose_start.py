#!/usr/bin/env python3
"""
Add a T-pose starting position to hooks_punch motion with smooth transition
This ensures the robot starts from a safe, stable position

WHY THIS SCRIPT EXISTS:
- The converted PBHC motions often start in dynamic poses (e.g., fighting stance)
- Starting the G1 robot directly in these poses can be unstable or unsafe
- The robot needs time to initialize and stabilize before performing complex motions
- T-pose is a standard, balanced position that's safe for robot initialization

WHAT IT DOES:
1. Prepends a T-pose (arms extended horizontally) to the beginning of a motion
2. Holds the T-pose for a configurable duration (default: 1 second)
3. Creates a smooth transition from T-pose to the first frame of the actual motion
4. Preserves the original motion data after the transition

HOW IT WORKS:
- Creates a 36-column frame matching the beyondmimic CSV format
- Generates T-pose joint angles with arms extended laterally (~84 degrees)
- Uses interpolation with cosine easing for smooth transitions
- Maintains proper quaternion normalization for rotation data
"""

import numpy as np
import csv

def create_tpose_frame():
    """
    Create a standard T-pose frame for G1 robot
    
    The T-pose is chosen because:
    - It's a balanced, stable position for the robot
    - Arms are clear of the body, preventing collision
    - It's easy to transition from T-pose to any other pose
    - It gives clear visual confirmation that the robot is ready
    
    Returns:
        numpy array with 36 values representing one frame in beyondmimic format
    """
    frame = np.zeros(36)  # Initialize all joint values to zero
    
    # Root position - standing upright at reasonable height
    frame[0] = 0.0     # X position (forward/back in world space)
    frame[1] = 0.0     # Y position (left/right in world space)
    frame[2] = 0.8     # Z position (height - 0.8m is safe standing height for G1)
    
    # Root orientation - neutral (facing forward)
    # Using identity quaternion (0,0,0,1) for no rotation
    frame[3] = 0.0     # qx (quaternion x component)
    frame[4] = 0.0     # qy (quaternion y component)
    frame[5] = 0.0     # qz (quaternion z component)
    frame[6] = 1.0     # qw (quaternion w component - identity means no rotation)
    
    # Joint positions (29 DOF total in frame, but only 23 used by beyondmimic)
    # Indices 7-36 contain joint angle values in radians
    
    # Lower body joints (indices 7-18) - all zeros for standing straight
    # This includes: left leg (6 DOF) and right leg (6 DOF)
    for i in range(7, 19):
        frame[i] = 0.0  # Straight legs for stable standing
    
    # Waist joints (indices 19-21)
    # Note: Only waist_pitch is actually used in beyondmimic (23 DOF version)
    frame[19] = 0.0  # waist_yaw (excluded in 23 DOF mapping)
    frame[20] = 0.0  # waist_roll (excluded in 23 DOF mapping)
    frame[21] = 0.0  # waist_pitch (this one IS used in beyondmimic)
    
    # Left arm - T-pose position (arm extended to the side)
    frame[22] = 0.0   # left_shoulder_pitch (forward/back swing)
    frame[23] = 1.47  # left_shoulder_roll (out to side ~84 degrees for T-pose)
    frame[24] = 0.0   # left_shoulder_yaw (internal/external rotation)
    frame[25] = 0.0   # left_elbow (straight arm)
    frame[26] = 0.0   # left_wrist_roll (included in 23 DOF)
    frame[27] = 0.0   # left_wrist_pitch (excluded in 23 DOF mapping)
    frame[28] = 0.0   # left_wrist_yaw (excluded in 23 DOF mapping)
    
    # Right arm - T-pose position (mirror of left arm)
    frame[29] = 0.0    # right_shoulder_pitch (forward/back swing)
    frame[30] = -1.47  # right_shoulder_roll (negative for right side, ~-84 degrees)
    frame[31] = 0.0    # right_shoulder_yaw (internal/external rotation)
    frame[32] = 0.0    # right_elbow (straight arm)
    frame[33] = 0.0    # right_wrist_roll (included in 23 DOF)
    frame[34] = 0.0    # right_wrist_pitch (excluded in 23 DOF mapping)
    frame[35] = 0.0    # right_wrist_yaw (excluded in 23 DOF mapping)
    
    return frame

def interpolate_frames(frame1, frame2, alpha):
    """
    Interpolate between two frames for smooth transitions
    
    This is crucial for preventing jerky movements that could:
    - Damage the robot's motors
    - Cause the robot to lose balance
    - Create unrealistic motion
    
    Args:
        frame1: Starting frame (36 values)
        frame2: Ending frame (36 values)
        alpha: Interpolation factor (0.0 = frame1, 1.0 = frame2)
    
    Returns:
        Interpolated frame with proper quaternion normalization
    """
    # Linear interpolation for position and joints
    result = (1 - alpha) * frame1 + alpha * frame2
    
    # Special handling for quaternion (indices 3-6)
    # Quaternions need special interpolation to maintain valid rotations
    q1 = frame1[3:7]
    q2 = frame2[3:7]
    
    # Using linear interpolation for quaternions (LERP)
    # Note: For large rotations, SLERP would be more accurate, but LERP
    # is sufficient for our T-pose to fighting stance transition
    quat_interp = (1 - alpha) * q1 + alpha * q2
    
    # CRITICAL: Normalize quaternion to maintain unit length
    # Without this, the rotation would be invalid and cause errors
    quat_norm = quat_interp / np.linalg.norm(quat_interp)
    result[3:7] = quat_norm
    
    return result

def add_tpose_to_motion(input_csv, output_csv, tpose_duration=30, transition_duration=30):
    """
    Add T-pose start to motion with smooth transition
    
    This function modifies motion data to include:
    1. Initial T-pose hold (for robot stabilization)
    2. Smooth transition period (prevents jerky motion)
    3. Original motion sequence (unchanged)
    
    Args:
        input_csv: Path to input motion CSV (beyondmimic format)
        output_csv: Path to output CSV with T-pose added
        tpose_duration: Number of frames to hold T-pose 
                       (30 = 1 second at 30fps, gives robot time to stabilize)
        transition_duration: Number of frames for smooth transition 
                            (30 = 1 second, prevents sudden movements)
    
    The timing parameters are crucial:
    - Too short tpose_duration: Robot might not stabilize
    - Too short transition_duration: Motion will be jerky
    - Too long: Wastes time before the actual motion
    """
    
    print(f"Loading {input_csv}...")
    # Load existing motion
    motion_data = []
    with open(input_csv, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            motion_data.append([float(x) for x in row])
    
    motion_data = np.array(motion_data)
    original_frames = len(motion_data)
    
    # Create T-pose frame
    tpose = create_tpose_frame()
    
    # Get the first frame of the original motion
    first_motion_frame = motion_data[0]
    
    # Adjust T-pose position to match the starting position better
    # This prevents the robot from having to move laterally during transition
    # Keep X and Y from the original motion's starting position
    tpose[0] = first_motion_frame[0]  # X position - match original
    tpose[1] = first_motion_frame[1]  # Y position - match original
    # Keep Z at safe standing height (0.8m) regardless of original
    
    print(f"Creating new motion sequence:")
    print(f"  - T-pose hold: {tpose_duration} frames")
    print(f"  - Transition: {transition_duration} frames")
    print(f"  - Original motion: {original_frames} frames")
    
    # Build new motion sequence
    new_motion = []
    
    # 1. Hold T-pose
    for i in range(tpose_duration):
        new_motion.append(tpose.copy())
    
    # 2. Smooth transition from T-pose to first motion frame
    for i in range(transition_duration):
        alpha = i / transition_duration  # Linear progress from 0 to 1
        
        # Apply ease-in-out curve for smoother, more natural transition
        # This creates an S-curve: slow start, faster middle, slow end
        # Formula: 0.5 - 0.5 * cos(alpha * pi) maps [0,1] to [0,1] with easing
        alpha = 0.5 - 0.5 * np.cos(alpha * np.pi)
        
        interpolated = interpolate_frames(tpose, first_motion_frame, alpha)
        new_motion.append(interpolated)
    
    # 3. Original motion (rest of the frames)
    for frame in motion_data:
        new_motion.append(frame)
    
    # Convert to array
    new_motion = np.array(new_motion)
    
    print(f"Total frames: {len(new_motion)}")
    print(f"Duration: {len(new_motion)/30:.2f} seconds at 30fps")
    
    # Save to CSV
    print(f"Saving to {output_csv}...")
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        for row in new_motion:
            formatted_row = [f"{val:.6f}" for val in row]
            writer.writerow(formatted_row)
    
    print("Done!")
    
    # Print summary
    print("\nMotion structure:")
    print(f"  Frames 0-{tpose_duration-1}: T-pose (safe starting position)")
    print(f"  Frames {tpose_duration}-{tpose_duration+transition_duration-1}: Smooth transition")
    print(f"  Frames {tpose_duration+transition_duration}-{len(new_motion)-1}: Original hooks_punch motion")
    
    return new_motion

if __name__ == "__main__":
    # Example usage: Adding T-pose to hooks_punch motion
    # This motion starts in a fighting stance which could be unstable
    input_file = "beyondmimic/whole_body_tracking/motions/hooks_punch_fixed.csv"
    output_file = "beyondmimic/whole_body_tracking/motions/hooks_punch_with_tpose.csv"
    
    # Add T-pose with 1 second hold and 1 second transition
    # At 30 FPS: 30 frames = 1 second
    add_tpose_to_motion(input_file, output_file, tpose_duration=30, transition_duration=30)
    
    print("\n✅ Created motion with safe T-pose start!")
    print(f"Output: {output_file}")
    print("\nThis motion:")
    print("1. Starts with a stable T-pose (arms out)")
    print("2. Holds for 1 second (robot can stabilize)")
    print("3. Smoothly transitions to fighting stance over 1 second")
    print("4. Performs the hooks_punch motion")
    print("\nTo visualize:")
    print("cd /home/rodrigo/git-repo/LAFAN1_Retargeting_Dataset")
    print("python rerun_visualize.py --file_name hooks_punch_with_tpose --robot_type g1")