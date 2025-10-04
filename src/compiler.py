# src/compiler.py
import subprocess
import os
import shutil
import logging
from rich.console import Console
from rich.progress import Progress

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

console = Console(force_terminal=True)
def create_supercut(clips, output_filename="dumpert-kut.mp4", pre=0.0, post=0.0):
    """
    Maakt een supercut-video van een lijst met clips.
    """
    if not clips:
        console.print("[yellow]Geen clips om te compileren.[/yellow]")
        return

    project_root = os.getcwd()
    temp_dir = os.path.join(project_root, "temp_clips")
    os.makedirs(temp_dir, exist_ok=True)

    ts_files = []
    total_clips = len(clips)

    console.print(f"\n[FASE 1/2] Clips genereren ({total_clips} in totaal)...")
    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Verwerken...", total=total_clips)

        for i, clip in enumerate(clips, 1):
            video_path = clip['video_path']
            found_phrase = clip['found_phrase']
        
            progress.update(task, description=f"[cyan]Clip {i}/{total_clips}: '{found_phrase}'[/cyan]")
            logging.info(f"Clip {i}/{total_clips}: '{found_phrase}' in {os.path.basename(video_path)}")

            ts_filepath = os.path.join(temp_dir, f"clip_{i:04d}.ts")
            ts_files.append(ts_filepath)
            
            start_seconds = float(clip['start_timestamp'])
            end_seconds = float(clip['end_timestamp'])
            clip_start = max(0, start_seconds - pre)
            clip_end = end_seconds + post
            clip_duration = clip_end - clip_start

            video_title = os.path.basename(os.path.dirname(video_path)).replace("_", " ")
            text_counter = f"{clip['found_phrase']} ({i}/{total_clips})"

            ffmpeg_command = [
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-ss', str(clip_start), '-t', str(clip_duration), '-i', video_path,
                '-vf', (
                    f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1,format=yuv420p,"
                    f"drawtext=fontfile='{FONT_PATH}':text='{video_title}':x=(w-text_w)/2:y=h-text_h-20:fontsize=32:fontcolor=white:box=1:boxcolor=black@0.5,"
                    f"drawtext=fontfile='{FONT_PATH}':text='{text_counter}':x=w-text_w-20:y=20:fontsize=32:fontcolor=white:box=1:boxcolor=black@0.5"
                ),
                '-c:v', 'libx264', '-preset', 'ultrafast', '-c:a', 'aac', ts_filepath
            ]
            subprocess.run(ffmpeg_command, check=True)
            progress.advance(task)

    print("\n[FASE 2/2] Finale supercut renderen...")
    concat_list_path = os.path.join(temp_dir, "concat_list.txt")
    with open(concat_list_path, 'w') as f:
        for ts_file in sorted(ts_files):
            f.write(f"file '{os.path.basename(ts_file)}'\n")
    
    output_dir = os.path.join(project_root, "kuts")
    os.makedirs(output_dir, exist_ok=True)
    final_output_path = os.path.join(output_dir, output_filename)
    concat_command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-f', 'concat', 
        '-safe', '0', '-i', concat_list_path, '-c', 'copy', final_output_path
    ]
    subprocess.run(concat_command, check=True)

    shutil.rmtree(temp_dir)
    print(f"-> Supercut opgeslagen als: {output_filename}")
    logging.info(f"-> Supercut opgeslagen als: {output_filename}")