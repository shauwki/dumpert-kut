# src/transcriber.py
import subprocess
import os
import sys

def _run_transcription_on_file(video_file, prompt):
    """
    Voert het transcriptieproces (ffmpeg + whisperx) uit op een enkel videobestand.
    Een underscore (_) aan het begin van een functienaam suggereert dat het een
    interne 'hulpfunctie' is voor deze module.
    """
    dirname = os.path.dirname(video_file)
    filename_no_ext = os.path.splitext(os.path.basename(video_file))[0]
    wav_file = os.path.join(dirname, f"{filename_no_ext}.wav")

    print(f"-> Start verwerking van: {os.path.basename(video_file)}")
    
    # Stap 1: Audio extraheren met ffmpeg
    print("[1/2] Audio extraheren...")
    ffmpeg_command = [
        'ffmpeg', '-i', video_file, '-vn', '-ar', '16000', '-ac', '1',
        '-c:a', 'pcm_s16le', wav_file, '-y', '-hide_banner', '-loglevel', 'error'
    ]
    subprocess.run(ffmpeg_command, check=True)

    # Stap 2: Transcriberen met WhisperX
    print("[2/2] Transcriberen met WhisperX...")
    whisperx_command = [
        'whisperx', wav_file, '--model', 'medium', '--language', 'nl',
        '--output_format', 'json', '--align_model', 'jonatasgrosman/wav2vec2-large-xlsr-53-dutch',
        '--output_dir', dirname, '--threads', '4'
    ]
    if prompt:
        print(f"-> Hint wordt gebruikt: '{prompt}'")
        whisperx_command.extend(['--initial_prompt', prompt])

    subprocess.run(whisperx_command, check=True)

    # Stap 3: Opruimen
    os.remove(wav_file)
    print(f"-> Verwerking van {os.path.basename(video_file)} is klaar.")

def transcribe_path(target_path, prompt):
    """
    Transcribeert een enkel videobestand of alle nieuwe video's in een map.
    """
    if os.path.isfile(target_path) and target_path.endswith('.mp4'):
        print("--- TRANSCRIPTIE GESTART (ENKEL BESTAND) ---")
        _run_transcription_on_file(target_path, prompt)
        print("--- TRANSCRIPTIE KLAAR ---")

    elif os.path.isdir(target_path):
        print("--- BATCH TRANSCRIPTIE GESTART ---")
        files_to_process = []
        files_to_skip = []
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith('.mp4'):
                    video_file = os.path.join(root, file)
                    json_file = os.path.splitext(video_file)[0] + '.json'
                    if os.path.exists(json_file):
                        files_to_skip.append(os.path.basename(video_file))
                    else:
                        files_to_process.append(video_file)

        if files_to_skip:
            print(f"-> Overgeslagen (al getranscribeerd): {len(files_to_skip)} bestand(en)")
        
        if not files_to_process:
            print("-> Niks nieuws te doen.")
        else:
            print(f"-> Starten met {len(files_to_process)} nieuwe video('s):")
            for video_file in files_to_process:
                print("--------------------")
                try:
                    _run_transcription_on_file(video_file, prompt)
                except subprocess.CalledProcessError as e:
                    print(f"Fout bij verwerken van {os.path.basename(video_file)}: {e}", file=sys.stderr)
                    # We gaan door met de volgende video, ook als er een mislukt
                    continue
        print("--- BATCH TRANSCRIPTIE KLAAR ---")
    else:
        print(f"Fout: '{target_path}' is geen geldig .mp4-bestand of map.", file=sys.stderr)