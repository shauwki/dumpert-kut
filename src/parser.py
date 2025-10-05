# src/parser.py
import os
import json
import logging
from rich.progress import track
from rich.console import Console

console = Console(force_terminal=True)
CACHE_FILE = 'word_database.json'

def _search_segments(json_files, search_terms):
    """PRIORITEIT 1: Zoekt naar de exacte zin in het 'text' veld van segmenten."""
    master_list = []
    console.print("-> [cyan]Zoekmethode: Hele segmenten (snel)[/cyan]")
    for json_path in track(json_files, description="[green]Scannen..."):
        logging.info(f"Scannen (segment-modus): {os.path.basename(json_path)}")
        video_path = json_path.replace('.json', '.mp4')
        if not os.path.exists(video_path): continue

        with open(json_path, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except json.JSONDecodeError: continue
        
        for segment in data.get('segments', []):
            segment_text = segment.get('text', '').strip()
            for term in search_terms:
                if term.lower() in segment_text.lower():
                    master_list.append({
                        'video_path': video_path,
                        'start_timestamp': segment['start'],
                        'end_timestamp': segment['end'],
                        'found_phrase': term,
                        'context': segment_text
                    })
    return master_list

def _search_words(json_files, search_terms):
    """PRIORITEIT 2 (Fallback): Zoekt woord-voor-woord."""
    master_list = []
    console.print("-> [yellow]Fallback zoekmethode: Woord-voor-woord (langzamer)[/yellow]")
    for json_path in track(json_files, description="[green]Scannen..."):
        logging.info(f"Scannen (woord-modus): {os.path.basename(json_path)}")
        video_path = json_path.replace('.json', '.mp4')
        if not os.path.exists(video_path): continue

        with open(json_path, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except json.JSONDecodeError: continue
        
        all_words = [word for segment in data.get('segments', []) for word in segment.get('words', [])]
        if not all_words: continue

        for term in search_terms:
            phrase_words = term.lower().split()
            for i in range(len(all_words) - len(phrase_words) + 1):
                json_phrase_words = [w.get('word', '').strip(".,!?").lower() for w in all_words[i:i+len(phrase_words)]]
                if json_phrase_words == phrase_words:
                    start_word = all_words[i]
                    end_word = all_words[i + len(phrase_words) - 1]
                    if 'start' in start_word and 'end' in end_word:
                        master_list.append({
                            'video_path': video_path,
                            'start_timestamp': start_word['start'],
                            'end_timestamp': end_word['end'],
                            'found_phrase': term
                        })
    return master_list

def find_phrases(root_dir, search_terms):
    """
    Vindt zinnen door eerst op hele segmenten te zoeken en dan als fallback woord-voor-woord.
    """
    logging.info(f"Zoeken naar: {', '.join(f'\"{t}\"' for t in search_terms)}")
    json_files = [os.path.join(subdir, file) 
                  for subdir, _, files in os.walk(root_dir) 
                  for file in files if file.endswith('.json')]
    
    results = _search_segments(json_files, search_terms)
    
    if not results:
        console.print("[yellow]Niks gevonden in segmenten, fallback naar woord-voor-woord zoeken...[/yellow]")
        logging.warning("Niks gevonden in segmenten, fallback naar woord-voor-woord zoeken.")
        results = _search_words(json_files, search_terms)
    return results

def build_word_database(root_dir):
    """
    Scant .json bestanden en bouwt een database van elk uniek woord.
    Gebruikt een cache-bestand om herhaaldelijk scannen te versnellen.
    """
    json_files = [os.path.join(subdir, file) 
                  for subdir, _, files in os.walk(root_dir) 
                  for file in files if file.endswith('.json')]
    
    cache_is_valid = False
    if os.path.exists(CACHE_FILE):
        cache_mtime = os.path.getmtime(CACHE_FILE)
        latest_transcript_mtime = 0
        if json_files:
            latest_transcript_mtime = max(os.path.getmtime(f) for f in json_files)

        if cache_mtime > latest_transcript_mtime:
            console.print("-> [green]Actuele woorden-database cache gevonden. Laden...[/green]")
            logging.info("Actuele cache gevonden, laden vanuit word_database.json.")
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                word_db = json.load(f)
            console.print(f"--> [bold green]✓ Database geladen met {len(word_db)} unieke woorden.[/bold green]")
            return word_db

    console.print("-> [yellow]Geen (actuele) cache gevonden. Woorden-database wordt volledig opnieuw gebouwd...[/yellow]")
    
    word_db = {}
    for json_path in track(json_files, description="[green]Woorden indexeren..."):
        video_path = json_path.replace('.json', '.mp4')
        if not os.path.exists(video_path): continue

        with open(json_path, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except json.JSONDecodeError: continue
        
        all_words_in_file = [word for segment in data.get('segments', []) for word in segment.get('words', [])]
        
        for word_info in all_words_in_file:
            if 'word' in word_info and 'start' in word_info and 'end' in word_info:
                word = word_info['word'].strip(".,!?").lower()
                if not word: continue
                
                if word not in word_db:
                    word_db[word] = []
                
                word_db[word].append({
                    'video_path': video_path,
                    'start_timestamp': word_info['start'],
                    'end_timestamp': word_info['end'],
                    'found_phrase': word
                })

    console.print(f"--> [bold green]✓ Database gebouwd met {len(word_db)} unieke woorden.[/bold green]")
    console.print(f"-> Opslaan naar cache-bestand: {CACHE_FILE}...")
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(word_db, f)
    logging.info(f"Woorden-database opgeslagen in cache: {CACHE_FILE}")

    return word_db

def find_precise_clips(root_dir, search_terms):
    """
    Zoekt naar termen in segmenten en retourneert de PRECIEZE start/end tijden
    van de gevonden woorden binnen dat segment.
    """
    master_list = []
    console.print("-> [cyan]Zoekmethode: Chirurgisch (precisie)[/cyan]")
    
    json_files = [os.path.join(subdir, file) 
                  for subdir, _, files in os.walk(root_dir) 
                  for file in files if file.endswith('.json')]

    for json_path in track(json_files, description="[green]Scannen..."):
        logging.info(f"Scannen (precisie-modus): {os.path.basename(json_path)}")
        video_path = json_path.replace('.json', '.mp4')
        if not os.path.exists(video_path): continue

        with open(json_path, 'r', encoding='utf-8') as f:
            try: data = json.load(f)
            except json.JSONDecodeError: continue

        for segment in data.get('segments', []):
            segment_text = segment.get('text', '').strip().lower()
            segment_words = segment.get('words', [])
            if not segment_words: continue

            for term in search_terms:

                if term.lower() in segment_text:
                    term_words = term.lower().split()
                    for i in range(len(segment_words) - len(term_words) + 1):
                        phrase_to_check = [w.get('word', '').strip(".,!?").lower() for w in segment_words[i:i+len(term_words)]]
                        if phrase_to_check == term_words:
                            start_word_obj = segment_words[i]
                            end_word_obj = segment_words[i + len(term_words) - 1]
                            if 'start' in start_word_obj and 'end' in end_word_obj:
                                master_list.append({
                                    'video_path': video_path,
                                    'start_timestamp': start_word_obj['start'],
                                    'end_timestamp': end_word_obj['end'],
                                    'found_phrase': term
                                })
                            break
    return master_list