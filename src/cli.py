# src/cli.py
import click, os
import logging 
from rich.console import Console 
from parser import find_phrases
from downloader import download_video
from transcriber import transcribe_path
from compiler import create_supercut
import time 
from rich.live import Live

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
def zeg():
    """Bouwt een zin woord-voor-woord uit de videobibliotheek."""
    click.echo("Zeg-commando wordt uitgevoerd...")

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