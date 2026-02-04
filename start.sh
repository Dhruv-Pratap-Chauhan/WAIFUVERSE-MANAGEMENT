#!/bin/bash

# Kill all running instances of the bot to prevent conflicts
echo "Killing any existing bot processes..."
pkill -f "python3 -m MukeshRobot" || echo "No existing bot processes found."

# Wait a moment for processes to exit
sleep 2

# Activate virtual environment
source venv/bin/activate

# Start the bot
echo "Starting MukeshRobot..."
python3 -m MukeshRobot
