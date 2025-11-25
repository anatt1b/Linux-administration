#!/bin/bash

# Siirry projektihakemistoon
cd /home/ubuntu/cron_energy || exit 1

VENV_DIR="venv"

# Luo virtuaaliympäristö tarvittaessa
if [ ! -d "$VENV_DIR" ]; then
    echo "Luodaan virtuaaliympäristö..."
    python3 -m venv "$VENV_DIR"
fi

# Aktivoi virtuaaliympäristö
source "$VENV_DIR/bin/activate"

# Asenna riippuvuudet
if [ -f "requirements.txt" ]; then
    echo "Asennetaan riippuvuudet..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "requirements.txt ei löytynyt!"
fi

# Suorita fetch_energy.py
if [ -f "fetch_energy.py" ]; then
    echo "Suoritetaan fetch_energy.py..."
    python fetch_energy.py
else
    echo "fetch_energy.py ei löytynyt!"
fi

echo "Valmis!"