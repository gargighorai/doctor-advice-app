#!/bin/bash

echo "Syncing with GitHub..."

# Pull latest changes first
git pull origin main

# Add all files
git add .

# Ask for commit message
echo "Enter commit message:"
read msg

# Commit
git commit -m "$msg"

# Push changes
git push origin main

echo "✅ Sync completed."
