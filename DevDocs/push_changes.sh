#!/bin/bash

# Script to push all changes to GitHub

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "Git is not installed. Please install Git and try again."
    exit 1
fi

# Check if the current directory is a git repository
if [ ! -d ".git" ]; then
    echo "This directory is not a git repository. Please run this script from the root of the repository."
    exit 1
fi

# Add all changes
echo "Adding all changes..."
git add .

# Commit the changes
echo "Committing changes..."
git commit -m "Add OpenRouter integration with Optimus Alpha model"

# Push the changes
echo "Pushing changes to GitHub..."
git push origin main

echo "Changes pushed to GitHub successfully!"
