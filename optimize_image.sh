#!/bin/bash

# A simple tool to compress images and convert them to WebP

if [ -z "$1" ]; then
    echo "Usage: ./optimize_image.sh <path-to-image> [quality 1-100]"
    echo "Example: ./optimize_image.sh myphoto.jpg 80"
    exit 1
fi

INPUT_FILE="$1"
QUALITY="${2:-80}" # Default quality is 80 if not provided

if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File '$INPUT_FILE' not found!"
    exit 1
fi

# Get the filename without the extension
BASENAME=$(basename "$INPUT_FILE")
FILENAME="${BASENAME%.*}"
DIRNAME=$(dirname "$INPUT_FILE")

OUTPUT_FILE="${DIRNAME}/${FILENAME}.webp"

echo "Compressing and converting '$INPUT_FILE' to WebP (Quality: $QUALITY)..."

# Run cwebp to convert the image
cwebp -q $QUALITY "$INPUT_FILE" -o "$OUTPUT_FILE" -quiet

if [ $? -eq 0 ]; then
    echo "✅ Success! Saved as: $OUTPUT_FILE"
    
    # Compare file sizes (Linux)
    ORIG_SIZE=$(stat -c%s "$INPUT_FILE")
    NEW_SIZE=$(stat -c%s "$OUTPUT_FILE")
    
    # Convert bytes to MB using awk for floating point math
    ORIG_MB=$(awk "BEGIN {printf \"%.2f\", $ORIG_SIZE/1048576}")
    NEW_MB=$(awk "BEGIN {printf \"%.2f\", $NEW_SIZE/1048576}")
    
    echo "Size comparison:"
    echo "Original: $ORIG_MB MB"
    echo "New file: $NEW_MB MB"
else
    echo "❌ Error during conversion. Make sure it is a valid image (JPG/PNG)."
fi
