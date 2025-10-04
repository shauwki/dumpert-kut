# src/downloader.py
import subprocess
import os

# Het pad naar de yt-dlp executable. 
# We kunnen dit later flexibeler maken, maar voor nu is dit prima.
YT_DLP_EXEC_PATH = os.path.join(os.getcwd(), 'vendor/yt-dlp/yt-dlp_linux') # Pas aan als je macOS gebruikt

def download_video(url, output_dir):
    """
    Download een video of playlist met de opgegeven yt-dlp executable.

    Args:
        url (str): De URL van de video of playlist.
        output_dir (str): De map waar de video's moeten worden opgeslagen.
    """
    if not os.path.exists(YT_DLP_EXEC_PATH):
        print(f"Fout: yt-dlp niet gevonden op: {YT_DLP_EXEC_PATH}")
        return False

    # Zorg ervoor dat de output directory bestaat
    os.makedirs(output_dir, exist_ok=True)

    # Dit is de Python-vertaling van je yt-dlp commando
    command = [
        YT_DLP_EXEC_PATH,
        '-f', 'bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]',
        '--cookies-from-browser', 'firefox',
        '--restrict-filenames',
        '-o', os.path.join(output_dir, '%(title)s/%(title)s.%(ext)s'),
        url
    ]

    print("--- DOWNLOAD GESTART ---")
    try:
        subprocess.run(command, check=True)
        print("--- DOWNLOAD KLAAR ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Fout tijdens het downloaden: {e}")
        return False
    except FileNotFoundError:
        print(f"Fout: Kan commando niet uitvoeren. Is yt-dlp correct geplaatst en uitvoerbaar?")
        return False