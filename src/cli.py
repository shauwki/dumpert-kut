# src/cli.py
import os
import time 
import click
import logging 
import random
from rich.live import Live
from rich.console import Console 
from compiler import create_supercut
from downloader import download_video
from transcriber import transcribe_path
from parser import find_phrases, build_word_database, find_precise_clips

console = Console(force_terminal=True)

def parse_limit_range(limit_str: str | None) -> tuple[int | None, int | None]:
    """
    Parset een limiet-string (bijv. "10;20", "40", ";50", "30;") naar start- en eind-indices.
    Gebruikt 1-gebaseerde indexering voor gebruiksvriendelijkheid.
    """
    if not limit_str:
        return None, None

    separator = ';' if ';' in limit_str else '-' if '-' in limit_str else None

    start, end = None, None
    try:
        if not separator:
            end = int(limit_str)
        else:
            parts = limit_str.split(separator, 1)
            start_str, end_str = parts[0], parts[1]
            
            if start_str:
                start = int(start_str)
            if end_str:
                end = int(end_str)

        start_index = (start - 1) if start is not None else None
        end_index = end

        return start_index, end_index
    except (ValueError, IndexError):
        console.print(f"[bold red]Fout: Ongeldig limiet-formaat '{limit_str}'. Gebruik 'N', 'start;eind' of ';eind'[/bold red]")
        return None, None
    
def setup_logging():
    """Configureert logging om naar een bestand te schrijven."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename='log.txt',
        filemode='w'
    )
    
@click.group()
def cli():
    """
    dumpert is een tool voor het downloaden, transcriberen en compileren van videoclips.
    """
    setup_logging()
    pass

@cli.command()
@click.argument('sentence')
@click.option('--directory', '-d', default='videos', help='De map die doorzocht moet worden.')
@click.option('--create', '-k', is_flag=True, help='Maak de compilatievideo.')
@click.option('--pre', default=0.0, help='Seconden extra voor de start van de clip.')
@click.option('--post', default=0.0, help='Seconden extra na het einde van de clip.')
@click.option('--name', '-n', default=None, help='Geef een aangepaste bestandsnaam (zonder .mp4).')
@click.option('--limit', '-l', type=str, default=None, help='Beperk zinnen. Formaat: "10" (eerste 10), "5;8" (5 t/m 8), etc.')
def zeg(sentence, directory, create, pre, post, name, limit):
    """Bouwt een zin woord-voor-woord uit de videobibliotheek."""
    
    word_db = build_word_database(directory)
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
            available_clips[word] = word_db[word]
            if count < min_count:
                min_count = count
                limiting_word = word
        else:
            console.print(f"- Woord '[red]{word}[/red]' -> NIET GEVONDEN in de database.")
            console.print("\n[bold red]Kan de zin niet bouwen omdat een of meerdere woorden missen.[/bold red]")
            return
            
    console.print("--------------------")
    console.print(f"De zwakste schakel is '[yellow]{limiting_word}[/yellow]'.")
    console.print(f"Er kunnen maximaal [bold green]{min_count}[/bold green] unieke zinnen worden gemaakt.")
    
    with Live(console=console, screen=False, auto_refresh=False, vertical_overflow="crop") as live:
        for word in words_to_find:
            count = len(available_clips.get(word, []))
            preview_text = f"> Woord '[green]{word}[/green]' -> [cyan]{count}[/cyan] keer gevonden."
            live.update(preview_text, refresh=True)
            time.sleep(0.1)

    if create:
        if min_count == 0:
            console.print("[red]Kan geen video maken omdat niet alle woorden gevonden zijn.[/red]")
            return
            
        start_index, end_index = parse_limit_range(limit)
        loop_start = start_index if start_index is not None and start_index >= 0 else 0
        loop_end = end_index if end_index is not None and end_index <= min_count else min_count
        
        if loop_start >= loop_end:
            console.print(f"[red]Ongeldige range voor limiet. Maximaal aantal zinnen is {min_count}.[/red]")
            return

        num_sentences_to_build = loop_end - loop_start
        console.print(f"\nStarten met het bouwen van [bold green]{num_sentences_to_build}[/bold green] zin(nen) (range {loop_start + 1} tot {loop_end})...")
        
        for word in available_clips:
            random.shuffle(available_clips[word])
            
        master_clip_plan = []
        for i in range(loop_start, loop_end):
            for word in words_to_find:
                if i < len(available_clips[word]):
                    clip_to_add = available_clips[word][i]
                    master_clip_plan.append(clip_to_add)
        
        if name:
            output_name = f"{name}.mp4"
        else:
            output_name = f"zeg-compilatie.mp4" 
        
        create_supercut(
            master_clip_plan, 
            output_filename=output_name, 
            pre=pre, 
            post=post
        )
    else:
        console.print("\n-> Gebruik de [bold cyan]-k[/bold cyan] vlag om de video te genereren.")


@cli.command()
@click.option('--directory', '-d', default='videos', help='De map die doorzocht moet worden.')
@click.option('--create', '-k', is_flag=True, help='Maak de compilatievideo.')
@click.option('--pre', default=0.0, help='Seconden extra voor de start van de clip.')
@click.option('--post', default=0.0, help='Seconden extra na het einde van de clip.')
@click.option('--name', '-n', default=None, help='Geef een aangepaste bestandsnaam (zonder .mp4).')
@click.option('--limit', '-l', type=str, default=None, help='Beperk clips. Formaat: "40" (eerste 40), "10;20" (10 t/m 20), ";20" (t/m 20), "10;" (vanaf 10).')
@click.argument('search_terms', nargs=-1)
def zoek(directory, create, pre, post, name, limit, search_terms): 
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
        for res in results[:10]:
            preview_text = (f"> [cyan]Gevonden[/cyan] '[yellow]{res['found_phrase']}[/yellow]' in "
                            f"[green]{os.path.basename(res['video_path'])}[/green] "
                            f"op [magenta]{res['start_timestamp']:.2f}s[/magenta]")
            live.update(preview_text, refresh=True)
            time.sleep(0.02) 
    console.print(f"--> [bold green]✓ {len(results)}[/bold green] resultaten gevonden!")
    if create:
        clips_to_compile = results
        start_index, end_index = parse_limit_range(limit)
        if start_index is not None or end_index is not None:
            slice_str = f"{start_index or ''}:{end_index or ''}"
            console.print(f"-> Limiet toegepast: selectie '[bold cyan]{slice_str}[/bold cyan]' wordt gecompileerd.")
            clips_to_compile = clips_to_compile[start_index:end_index]
            
        if name:
            output_name = f"{name}.mp4"
        else:
            output_name = f"zoek-compilatie.mp4"
        create_supercut(clips_to_compile, output_filename=output_name, pre=pre, post=post)

@cli.command()
@click.option('--pre', default=0.0, help='Seconden extra voor de start van de clip.')
@click.option('--post', default=0.0, help='Seconden extra na het einde van de clip.')
@click.option('--randomize', '-r', is_flag=True, help='Schud de gevonden clips in willekeurige volgorde.')
@click.option('--create', '-k', is_flag=True, help='Maak de compilatievideo.')
@click.option('--name', '-n', default=None, help='Geef een aangepaste bestandsnaam (zonder .mp4).')
@click.option('--limit', '-l', type=str, default=None, help='Beperk clips. Formaat: "40" (eerste 40), "10;20" (10 t/m 20), ";20" (t/m 20), "10;" (vanaf 10).')
@click.argument('search_terms', nargs=-1)
def kut(pre, post, randomize, create, name, limit, search_terms): 
    """Zoekt en compileert direct een video van exacte woorden/zinnen."""
    if not search_terms:
        console.print("[red]Fout: Geen zoektermen opgegeven.[/red]")
        return

    results = find_precise_clips('videos', list(search_terms))

    if not results:
        console.print("[yellow]Geen resultaten gevonden.[/yellow]")
        return
    
    console.print(f"--> [bold green]✓ {len(results)}[/bold green] precieze clips gevonden!")
    
    if create:
        clips_to_compile = results
        if randomize:
            console.print("-> Clips worden in willekeurige volgorde geplaatst...")
            random.shuffle(results)
            logging.info("Clip-volgorde is willekeurig gemaakt.")

        start_index, end_index = parse_limit_range(limit)
        if start_index is not None or end_index is not None:
            slice_str = f"{start_index or ''}:{end_index or ''}"
            console.print(f"-> Limiet toegepast: selectie '[bold cyan]{slice_str}[/bold cyan]' wordt gecompileerd.")
            clips_to_compile = clips_to_compile[start_index:end_index]
            
        if name:
            output_name = f"{name}.mp4"
        else:
            output_name = f"kut-compilatie.mp4"
        create_supercut(clips_to_compile, output_filename=output_name, pre=pre, post=post)
    else:
        console.print("\n-> Gebruik de [bold cyan]-k[/bold cyan] vlag om de video te genereren.")

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