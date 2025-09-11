#!/bin/bash

# Create a virtual environment named 'prospection_env'
python3 -m venv prospection_env

# Activate the virtual environment
source prospection_env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install required Python packages
pip install streamlit pandas openpyxl

echo "✅ Environnement virtuel 'prospection_env' configuré avec succès et bibliothèques installées."
