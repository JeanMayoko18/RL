#!/bin/bash
# Script to download LAFAN1 retargeted motions for G1 robot

BASE_URL="https://huggingface.co/datasets/lvhaidong/LAFAN1_Retargeting_Dataset/resolve/main/g1"
OUTPUT_DIR="./motions"

mkdir -p "$OUTPUT_DIR"

# Available motion categories and some examples:
# Dance: dance1_subject1.csv, dance1_subject2.csv, dance2_subject1.csv
# Walk: walk1_subject1.csv, walk1_subject2.csv
# Run: run1_subject1.csv, run1_subject2.csv
# Fight/Sports: fight1_subject2.csv, fightAndSports1_subject1.csv
# Fall and Get Up: fallAndGetUp1_subject1.csv, fallAndGetUp2_subject2.csv
# Jumps: jumps1_subject1.csv, jumps1_subject2.csv
# Obstacles: obstacles1_subject1.csv, obstacles1_subject2.csv
# Sprintjump: sprintJump1_subject1.csv, sprintJump1_subject2.csv

# Function to download a motion
download_motion() {
    local motion_name=$1
    echo "Downloading: $motion_name"
    wget -q --show-progress -O "$OUTPUT_DIR/$motion_name" "$BASE_URL/$motion_name"
    if [ $? -eq 0 ]; then
        echo "✓ Successfully downloaded: $motion_name"
    else
        echo "✗ Failed to download: $motion_name"
    fi
}

# Download popular motions (uncomment the ones you want)
download_motion "dance1_subject1.csv"
download_motion "walk1_subject1.csv"
download_motion "run1_subject1.csv"
# download_motion "fight1_subject2.csv"
# download_motion "jumps1_subject1.csv"
# download_motion "fallAndGetUp1_subject1.csv"

echo ""
echo "Downloaded motions:"
ls -lh "$OUTPUT_DIR"/*.csv

echo ""
echo "To download other motions, see the full list at:"
echo "https://huggingface.co/datasets/lvhaidong/LAFAN1_Retargeting_Dataset/tree/main/g1"
