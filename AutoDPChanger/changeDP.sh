#!/bin/bash

# Directory containing wallpapers
WALLPAPER_DIR="/home/praveen/Pictures/Wallpapers"

# Get a list of image files (you can adjust extensions if needed)
IMAGES=($(find "$WALLPAPER_DIR" -type f \( -iname '*.jpg' -o -iname '*.png' -o -iname '*.jpeg' \)))

# Check if any images were found
if [ ${#IMAGES[@]} -eq 0 ]; then
    echo "No images found in $WALLPAPER_DIR"
    exit 1
fi

# Pick a random image
RANDOM_IMAGE="${IMAGES[RANDOM % ${#IMAGES[@]}]}"

# Set the wallpaper using gsettings
gsettings set org.gnome.desktop.background picture-uri "file://$RANDOM_IMAGE"

# Optional: Set scaling (e.g., zoom, centered, stretched)
gsettings set org.gnome.desktop.background picture-options "zoom"

echo "Wallpaper changed to: $RANDOM_IMAGE"

