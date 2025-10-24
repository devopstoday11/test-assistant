#!/bin/bash
# Script to rename the project directory from cheat-tool to test-assistant

echo "=========================================="
echo "Directory Rename Script"
echo "=========================================="
echo ""

CURRENT_DIR="cheat-tool"
NEW_DIR="test-assistant"
PARENT_DIR="/Users/username/Downloads"

# Check if we're in the right location
CURRENT_PATH=$(pwd)
if [[ "$CURRENT_PATH" == *"$CURRENT_DIR"* ]]; then
    echo "⚠️  You are currently inside the $CURRENT_DIR directory."
    echo "📂 You need to be in the parent directory to rename."
    echo ""
    echo "Run these commands:"
    echo "   cd .."
    echo "   bash $CURRENT_DIR/rename_directory.sh"
    echo ""
    exit 1
fi

# Change to parent directory
cd "$PARENT_DIR" || {
    echo "❌ Failed to navigate to $PARENT_DIR"
    exit 1
}

# Check if source directory exists
if [ ! -d "$CURRENT_DIR" ]; then
    echo "❌ Directory $CURRENT_DIR not found in $PARENT_DIR"
    echo "📂 Current directory: $(pwd)"
    echo "📁 Contents:"
    ls -1
    exit 1
fi

# Check if target directory already exists
if [ -d "$NEW_DIR" ]; then
    echo "⚠️  Directory $NEW_DIR already exists!"
    echo "❌ Cannot rename. Please resolve the conflict first."
    exit 1
fi

# Perform the rename
echo "📦 Renaming directory..."
echo "   From: $CURRENT_DIR"
echo "   To:   $NEW_DIR"
echo ""

mv "$CURRENT_DIR" "$NEW_DIR"

if [ $? -eq 0 ]; then
    echo "✅ Directory renamed successfully!"
    echo ""
    echo "📂 New location: $PARENT_DIR/$NEW_DIR"
    echo ""
    echo "🧪 Verify the rename:"
    echo "   cd $NEW_DIR"
    echo "   python3 test_test_assistant.py"
    echo ""
    echo "🎉 Rename complete!"
else
    echo "❌ Failed to rename directory"
    exit 1
fi
