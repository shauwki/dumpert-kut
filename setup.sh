#!/bin/env bash
# Dit script zet de volledige dumpert-omgeving op na een git clone.

# Stop on first error
set -e

# Ga naar de map van het script, zodat het vanaf elke locatie kan worden uitgevoerd
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

echo "--- dumpert Setup Script ---"

# --- Stap 1: OS Detectie en Compatibiliteit ---
echo "[1/5] Besturingssysteem detecteren..."
OS_TYPE=$(uname -s)

case "$OS_TYPE" in
    Linux*)
        echo "      ... Linux gedetecteerd. Systeem is compatibel."
        ;;
    Darwin*)
        echo "      ... macOS (Darwin) gedetecteerd. Systeem is compatibel."
        ;;
    *)
        echo "FOUT: Niet-ondersteund besturingssysteem gedetecteerd: $OS_TYPE"
        echo "Dit script is alleen getest op Linux en macOS."
        exit 1
        ;;
esac

# --- Stap 2: Systeemafhankelijkheden controleren ---
echo "[2/5] Controleren op benodigde software (git, python3, ffmpeg)..."

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

# --- Stap 3: Python virtuele omgeving aanmaken ---
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[3/5] Virtuele omgeving aanmaken in '$VENV_DIR'..."
    python3 -m venv $VENV_DIR
else
    echo "[3/5] Virtuele omgeving '$VENV_DIR' bestaat al, stap overgeslagen."
fi

# --- Stap 4: Python packages installeren ---
echo "[4/5] Python-dependencies installeren vanuit requirements.txt..."
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt
deactivate
echo "      ... installatie van dependencies voltooid."

# --- Stap 5: Scripts uitvoerbaar maken ---
echo "[5/5] Scripts uitvoerbaar maken..."
chmod +x dumpert

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
echo "./dumpert --help"
echo ""