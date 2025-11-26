#!/usr/bin/env python3
"""
Add a minute of standing motion (repeating the last pose) to a motion CSV file
"""
import numpy as np
import csv

# Read the CSV file
csv_file = '/home/rodrigo/git-repo/beyondmimic/whole_body_tracking/motions/horse_stance_punch.csv'
data = np.genfromtxt(csv_file, delimiter=',')

print(f'Original data shape: {data.shape}')
print(f'Original frames: {data.shape[0]}')

# Get the last pose
last_pose = data[-1, :]

# Assuming 30 fps, 1 minute = 60 seconds * 30 fps = 1800 frames
fps = 30
duration_seconds = 60
frames_to_add = fps * duration_seconds

print(f'Adding {frames_to_add} frames ({duration_seconds} seconds at {fps} fps)')

# Repeat the last pose
standing_motion = np.tile(last_pose, (frames_to_add, 1))

# Concatenate
extended_data = np.vstack([data, standing_motion])

print(f'Extended data shape: {extended_data.shape}')
print(f'Total frames: {extended_data.shape[0]}')

# Save to new file
output_file = csv_file.replace('.csv', '_with_standing.csv')
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    for row in extended_data:
        formatted_row = [f'{val:.6f}' for val in row]
        writer.writerow(formatted_row)

print(f'\n✅ Saved to: {output_file}')
