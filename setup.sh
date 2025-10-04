#!/bin/env bash
# Dit script zet de volledige Dimper-omgeving op na een git clone.

# Stop on first error
set -e

# Ga naar de map van het script, zodat het vanaf elke locatie kan worden uitgevoerd
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

echo "--- Dimper Setup Script ---"

# --- Stap 1: Systeemafhankelijkheden controleren ---
echo "[1/4] Controleren op benodigde software (git, python3, ffmpeg)..."

# Helper functie voor het controleren van commando's
check_command() {
    if ! command -v $1 &> /dev/null
    then
        echo "FOUT: Het commando '$1' is niet gevonden. Installeer het en probeer het opnieuw."
        exit 1
    fi
}

check_command "git"
check_command "python3"
check_command "ffmpeg"
echo "      ... alle software is aanwezig."

# --- Stap 2: Python virtuele omgeving aanmaken ---
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[2/4] Virtuele omgeving aanmaken in '$VENV_DIR'..."
    python3 -m venv $VENV_DIR
else
    echo "[2/4] Virtuele omgeving '$VENV_DIR' bestaat al, stap overgeslagen."
fi

# --- Stap 3: Python packages installeren ---
echo "[3/4] Python-dependencies installeren vanuit requirements.txt..."
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt
deactivate
echo "      ... installatie van dependencies voltooid."

# --- Stap 4: Scripts uitvoerbaar maken ---
echo "[4/4] Scripts uitvoerbaar maken..."
chmod +x dimper
# Maak ook de yt-dlp binaries uitvoerbaar
chmod +x vendor/yt-dlp/yt-dlp_linux
chmod +x vendor/yt-dlp/yt-dlp_macos
echo "      ... permissies ingesteld."

echo ""
echo "--- ✅ Setup voltooid! ---"
echo ""
echo "Om de omgeving te activeren, gebruik:"
echo "source venv/bin/activate"
echo ""
echo "Om de applicatie te starten, gebruik:"
echo "./dimper --help"
echo ""