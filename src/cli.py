# src/cli.py
import click, os
import logging 
from rich.console import Console 
from parser import find_phrases, build_word_database
from downloader import download_video
from transcriber import transcribe_path
from compiler import create_supercut
from rich.live import Live
import random
import time 

def setup_logging():
    """Configureert logging om naar een bestand te schrijven."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='log.txt',
        filemode='w'
    )
    
console = Console(force_terminal=True)
@click.group()
def cli():
    """
    Dimper is een tool voor het downloaden, transcriberen en compileren van videoclips.
    """
    setup_logging()
    pass

@cli.command()
@click.argument('sentence')
@click.option('--create', '-k', is_flag=True, help='Maak de compilatievideo.')
@click.option('--pre', default=0.0, help='Seconden extra voor de start van de clip.')
@click.option('--post', default=0.0, help='Seconden extra na het einde van de clip.')
def zeg(sentence, create, pre, post):
    """Bouwt een zin woord-voor-woord uit de videobibliotheek."""
    
    word_db = build_word_database('videos')
    words_to_find = sentence.lower().split()
    if not words_to_find:
        console.print("[red]Fout: Geen zin opgegeven.[/red]")
        return

    console.print(f"\n--- Analyse voor de zin: '[cyan]{sentence}[/cyan]' ---")
    
    available_clips = {}
    min_count = float('inf')
    limiting_word = ""

    for word in words_to_find:
        if word in word_db:
            count = len(word_db[word])
            console.print(f"- Woord '[green]{word}[/green]' -> {count} keer gevonden.")
            available_clips[word] = word_db[word]
            if count < min_count:
                min_count = count
                limiting_word = word
        else:
            console.print(f"- Woord '[red]{word}[/red]' -> NIET GEVONDEN in de database.")
            console.print("\n[bold red]Kan de zin niet bouwen omdat een of meerdere woorden missen.[/bold red]")
            return
    console.print("--------------------")
    # console.print(f"De zwakste schakel is '[yellow]{limiting_word}[/yellow]'.")
    console.print(f"Er kunnen maximaal [bold green]{min_count}[/bold green] unieke zinnen worden gemaakt.")

    if create:
        if min_count == 0:
            console.print("[red]Kan geen video maken omdat niet alle woorden gevonden zijn.[/red]")
            return        
        console.print(f"\nStarten met het bouwen van {min_count} zin(nen)...")
        for word in available_clips:
            random.shuffle(available_clips[word])
        master_clip_plan = []
        for i in range(min_count):
            for word in words_to_find:
                clip_to_add = available_clips[word][i]
                master_clip_plan.append(clip_to_add)
        create_supercut(
            master_clip_plan, 
            output_filename="dumpert-komp.mp4", 
            pre=pre, 
            post=post
        )

@cli.command()
@click.option('--directory', '-d', default='videos', help='De map die doorzocht moet worden.')
@click.option('--create', '-k', is_flag=True, help='Maak de compilatievideo.') 
@click.option('--pre', default=0.0, help='Seconden extra voor de start van de clip.')
@click.option('--post', default=0.0, help='Seconden extra na het einde van de clip.')
@click.argument('search_terms', nargs=-1)
def zoek(directory, create, pre, post, search_terms):
    """Vindt en compileert hele segmenten waarin een zoekterm voorkomt."""
    if not search_terms:
        click.echo("Fout: Geef ten minste één zoekterm op.", err=True)
        return
    if not os.path.isdir(directory):
        click.echo(f"Fout: De map '{directory}' is niet gevonden.", err=True)
        return

    click.echo(f"Zoek-commando wordt uitgevoerd in '{directory}'...")
    results = find_phrases(directory, list(search_terms))
    
    if not results:
        console.print("[yellow]-> Geen resultaten gevonden.[/yellow]")
        return

    for res in results:
        logging.info(f"  - Gevonden '{res['found_phrase']}' in {os.path.basename(res['video_path'])} op {res['start_timestamp']:.2f}s")
    logging.info(f"{len(results)} resultaten gevonden!")
    
    with Live(console=console, screen=False, auto_refresh=False, vertical_overflow="crop") as live:
        for res in results:
            preview_text = (f"> [cyan]Gevonden[/cyan] '[yellow]{res['found_phrase']}[/yellow]' in "
                            f"[green]{os.path.basename(res['video_path'])}[/green] "
                            f"op [magenta]{res['start_timestamp']:.2f}s[/magenta]")
            live.update(preview_text, refresh=True)
            time.sleep(0.02) 
    console.print(f"--> [bold green]✓ {len(results)}[/bold green] resultaten gevonden!")
    if create:
        create_supercut(results, pre=pre, post=post)

@cli.command()
def kut():
    """Een snelkoppeling die direct een compilatievideo maakt."""
    click.echo("Kut-commando wordt uitgevoerd...")

@cli.command()
@click.argument('url')
@click.option('--output-dir', default='videos', help='Map om video\'s in op te slaan.')
def download(url, output_dir):
    """Download een video of playlist met yt-dlp."""
    download_video(url, output_dir)

@cli.command()
@click.argument('path')
@click.option('--prompt', default="reet, reten, reeten, rate, raten", help='Hint voor de transcribeer-engine.')
@click.option(
    '--mode',
    default='standard',
    type=click.Choice(['standard', 'demucs'], case_sensitive=False),
    help="Transcriptie modus: 'standard' (snel, met VAD), 'demucs' (langzaamst, hoogste kwaliteit)."
)
def transcribe(path, prompt, mode):
    """Transcribeert een video of map met WhisperX."""
    console.print(f"--> Transcriptie gestart in [cyan]{mode}[/cyan] modus...")
    transcribe_path(path, prompt, mode)

if __name__ == '__main__':
    cli()