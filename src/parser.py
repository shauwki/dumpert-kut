# src/parser.py
import os
import json
import sys
import re
import logging
from rich.console import Console

console = Console()
def find_phrases(root_dir, search_terms):
    """
    Zoekt naar volledige zinnen of losse woorden in .json-bestanden.
    """
    master_list = []
    logging.info(f"Zoeken naar: {', '.join(f'\"{t}\"' for t in search_terms)}")

    json_files = [os.path.join(subdir, file) 
                  for subdir, _, files in os.walk(root_dir) 
                  for file in files if file.endswith('.json')]

    from rich.progress import track
    for json_path in track(json_files, description="[green]Scannen..."):
        logging.info(f"Scannen: {os.path.basename(json_path)}")
        
        video_path = json_path.replace('.json', '.mp4')
        if not os.path.exists(video_path):
            continue

        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                continue
        
        all_words = [word for segment in data.get('segments', []) for word in segment.get('words', [])]
        if not all_words:
            continue

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