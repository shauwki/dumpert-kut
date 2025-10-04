# src/transcriber.py
import subprocess
import os
import sys
import shutil
import logging 
from rich.console import Console
from subprocess import Popen, PIPE
from rich.live import Live

console = Console(force_terminal=True)

def _run_transcription_on_file(video_file, prompt, mode):
    """
    Voert het transcriptieproces uit op een enkel videobestand volgens de gekozen modus.
    """
    dirname = os.path.dirname(video_file)
    filename_no_ext = os.path.splitext(os.path.basename(video_file))[0]
    
    temp_wav_file = os.path.join(dirname, f"{filename_no_ext}.wav")
    target_audio_for_whisperx = temp_wav_file
    cleanup_paths = [temp_wav_file]

    console.print(f"-> Start verwerking van: [yellow]{os.path.basename(video_file)}[/yellow]")    
    console.print(f"[1/{'3' if mode == 'demucs' else '2'}] Audio extraheren met ffmpeg...")
    ffmpeg_command = [
        'ffmpeg', '-i', video_file, '-vn', '-ar', '16000', '-ac', '1',
        '-c:a', 'pcm_s16le', temp_wav_file, '-y', '-hide_banner', '-loglevel', 'error'
    ]
    subprocess.run(ffmpeg_command, check=True)

    if mode == 'demucs':
        console.print("-> Hernoemen van demucs-output naar correct formaat...")
        source_json_path = os.path.join(dirname, "vocals.json")
        target_json_path = os.path.join(dirname, f"{filename_no_ext}.json")
        if os.path.exists(source_json_path):
            os.rename(source_json_path, target_json_path)
            logging.info(f"Hernoemd: {source_json_path} -> {target_json_path}")
        else:
            console.print(f"[yellow]Waarschuwing: geen {source_json_path} dus ekkes transcriberen.[/yellow]")
            logging.warning(f"{source_json_path} niet gevonden om te hernoemen na demucs-transcriptie.")

    step_num = "3/3" if mode == 'demucs' else "2/2"
    console.print(f"[{step_num}] Transcriberen met WhisperX...Dit duurt wat langer maar valt mee 😉")
    whisperx_command = [
        'whisperx', target_audio_for_whisperx, '--model', 'medium', '--language', 'nl',
        '--output_format', 'json', '--align_model', 'jonatasgrosman/wav2vec2-large-xlsr-53-dutch',
        '--output_dir', dirname, '--threads', '4'
    ]
    if prompt:
        console.print(f"      |--> Hints: '{prompt}'")
        whisperx_command.extend(['--initial_prompt', prompt])

    process = Popen(whisperx_command, stdout=PIPE, stderr=PIPE, text=True, encoding='utf-8', bufsize=1)
    with Live(console=console, auto_refresh=True, vertical_overflow="crop") as live:
        live.update("[cyan]WhisperX gestart, er kan nog output komen, maar laat dit gerust even runnen[/cyan]")
        for line in iter(process.stdout.readline, ""):
            if line.strip():
                live.update(f"[green]{line.strip().replace("Transcript: ","")}[/green]")
    process.wait()
    if process.returncode != 0:
        stderr_output = process.stderr.read()
        console.print("[bold red]Fout tijdens uitvoeren van WhisperX.[/bold red]")
        console.print(f"[red]{stderr_output}[/red]")
        return 
    console.print("-> Opruimen van tijdelijke bestanden...")
    for path in cleanup_paths:
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except OSError as e:
            console.print(f"[red]Fout bij opruimen van {path}: {e}[/red]")
    console.print(f"-> [green]Verwerking van {os.path.basename(video_file)} is klaar.[/green]")

def transcribe_path(target_path, prompt, mode):
    """
    Transcribeert een enkel videobestand of alle nieuwe video's in een map.
    """
    if os.path.isfile(target_path) and target_path.endswith('.mp4'):
        console.print("--- Transcriptie gestart (enkel bestand) ---")
        try:
            _run_transcription_on_file(target_path, prompt, mode)
        except Exception as e:
            console.print(f"[bold red]Er is een onverwachte fout opgetreden: {e}[/bold red]")
        console.print("--- Transcriptie klaar ---")
    elif os.path.isdir(target_path):
        console.print("--- Batch transcriptie gestart ---")
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
            console.print(f"-> [yellow]{len(files_to_skip)}[/yellow] bestand(en) overgeslagen (al getranscribeerd).")
            for skipped_file in files_to_skip:
                logging.info(f"Overgeslagen: {skipped_file}")
        if not files_to_process:
            console.print("-> [green]Geen nieuwe video's gevonden om te transcriberen.[/green]")
        else:
            console.print(f"-> [bold green]{len(files_to_process)}[/bold green] nieuwe video('s) gevonden. Starten...")
            for i, video_file in enumerate(files_to_process, 1):
                console.print(f"\n--- Video {i}/{len(files_to_process)} ---")
                try:
                    _run_transcription_on_file(video_file, prompt, mode)
                except Exception as e:
                    console.print(f"[bold red]Fout bij verwerken van {os.path.basename(video_file)}: {e}[/bold red]")
                    logging.error(f"Fout bij verwerken van {os.path.basename(video_file)}: {e}")
                    console.print("[yellow]Doorgaan met de volgende video...[/yellow]")
                    continue
        console.print("\n--- Batch transcriptie klaar ---")
    else:
        console.print(f"[red]Fout: '{target_path}' is geen geldig .mp4-bestand of map.[/red]", file=sys.stderr)
