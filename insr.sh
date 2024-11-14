#!/bin/bash

# Check if pip is installed
echo "Checking if pip is installed..."
if ! command -v pip &> /dev/null
then
    echo "pip could not be found. Please install pip first."
    exit 1
fi

# Ask the user if they want to update the OS
read -p "Do you want to update the OS? (y/n): " update_choice
if [[ "$update_choice" == "y" || "$update_choice" == "Y" ]]; then
    echo "Updating OS..."
    sudo apt full-upgrade -y
else
    echo "Skipping OS update."
fi

# Optionally create a virtual environment (recommended)
echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    echo "requirements.txt not found. Please ensure it exists in the current directory."
    exit 1
fi

# Install libraries from requirements.txt
echo "Installing libraries from requirements.txt..."
pip install -r requirements.txt

# Deactivate the virtual environment
deactivate

echo "Libraries installed successfully!"

# Run the program
echo "Running the program..."
sleep 1
echo "1"
sleep 1
echo "2"
sleep 1
echo "3"
python password_house.py
