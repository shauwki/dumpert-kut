# Dumpert Kutter

## Context
Dit project, liefkozend "Dumpert Kutter" gedoopt, begon als een persoonlijk zijproject om specifiek de "ratings" uit DumpertReeten-video's te kunnen extraheren en analyseren. Wat begon als een hulpmiddel voor een niche-gebruik, is inmiddels uitgegroeid tot een veelzijdige open-source tool voor iedereen.<br/>
De `Dumpert Kutter`(cutter, snapje? oke, just saying:)..> maakt het gemakkelijk om video's te downloaden, te transcriberen, en vervolgens op basis van gesproken woorden of zinnen compilaties te maken. Hoewel de initiële focus lag op Nederlandstalige content, is de tool modulair opgebouwd en aanpasbaar voor andere talen en toepassingen. De kern van de geavanceerde functionaliteit ligt in de **`kut`**-functie, die hieronder uitgebreid wordt toegelicht.

## Installatie

Om Dumpert Kutter te installeren na het clonen van de repository, volg je deze stappen:<br/>
1.  **Clone de repository:**
    ```bash
    git clone https://github.com/shauwki/dumpert-kut.git
    cd dumpert-kut
    ```
2.  **Maak het setup script uitvoerbaar:**<br/>
    Dit geeft het script de benodigde permissies om de installatie uit te voeren.
    ```bash
    chmod +x setup.sh
    ```
3.  **Voer het setup script uit:**<br/>
    Dit script controleert op systeemafhankelijkheden (zoals `python3`, `ffmpeg`, `git`), maakt een Python virtuele omgeving (`venv`) aan, installeert alle benodigde Python-pakketten uit `requirements.txt` (inclusief `whisperX` en `demucs`), en maakt de executables uitvoerbaar.
    ```bash
    ./setup.sh
    ```
    Na succesvolle installatie ben je klaar om de tool te gebruiken.

## Configuratie
De Dumpert Kutter-tool werkt met video's die in de `videos/` map in de root van het project worden geplaatst.<br/>
* **Videobestanden:** De `setup.sh` haalt geen videobestanden voor je op. Je dient je `.mp4`-videobestanden handmatig in de `videos/` map te plaatsen (of in submappen daarbinnen). Houd er rekening mee dat de DumpertReeten-playlist zelf meer dan 100GB aan video's bevat.
* **WhisperX Taal:** Het WhisperX-model is standaard afgestemd op Nederlands (`--language nl`), maar kan handmatig worden aangepast in `src/transcriber.py` als je met andere talen wilt werken.

## Usage

De `dumpert` CLI biedt verschillende commando's voor diverse taken:<br/>
Alle commando's worden uitgevoerd via `./dumpert [commando] [opties] [argumenten]`.

### `download`
Download video's of playlists van YouTube (of andere ondersteunde bronnen) naar de `videos/` map.

**Voorbeeld:** (dit is de dumpert-reeten playlist)
```bash
./dumpert download "[https://www.youtube.com/playlist?list=PLMe_6SSHyqcYh032ZieiNHW8bwusy7FPJ](https://www.youtube.com/playlist?list=PLMe_6SSHyqcYh032ZieiNHW8bwusy7FPJ)"
```

_(De complete DumpertReeten-playlist van 100GB+ kun je hier vinden.)_

### `transcribe`

Transcribeert videobestanden naar JSON-transcripties met WhisperX. Ondersteunt verschillende modi voor kwaliteit versus snelheid.

**Opties:**

- `--prompt <tekst>`: Een hint voor de transcribeer-engine om de nauwkeurigheid te verbeteren (bijv. veelvoorkomende termen).
    
- `--mode <modus>`: Kies de transcriptie-modus.
    
    - `standard` (standaard): Gebruikt de ingebouwde VAD (Voice Activity Detection) van WhisperX. Snel en vaak voldoende.
        
    - `demucs`: Gebruikt `demucs` om eerst zang/spraak van muziek te scheiden, en transcribeert daarna alleen de zang. Dit is de langzaamste maar meest accurate methode voor video's met achtergrondmuziek.
        

**Voorbeelden:**

- **Transcribeer een hele map (standaard modus):**
    
    Bash
    
    ```
    ./dimper transcribe videos/
    ```
    
- **Transcribeer een specifieke video met een prompt:**
    
    Bash
    
    ```
    ./dimper transcribe videos/een_aflevering/mijn_video.mp4 --prompt "DumpertReeten, reeten, raten"
    ```
    
- **Transcribeer met Demucs voor hoge kwaliteit:**
    
    Bash
    
    ```
    ./dimper transcribe videos/ --mode demucs
    ```
    

### `zoek`

Vindt en compileert hele segmenten waarin een zoekterm voorkomt.

**Opties:**

- `--directory -d <pad>`: De map om te doorzoeken (standaard: `videos/`).
    
- `--pre <seconden>`: Voeg extra seconden toe vóór de start van de clip.
    
- `--post <seconden>`: Voeg extra seconden toe ná het einde van de clip.
    
- `--create -k`: Genereer de compilatievideo (anders alleen een analyse).
    

**Voorbeelden:**

- **Zoek naar een term en analyseer de resultaten:**
    
    Bash
    
    ```
    ./dimper zoek "tien reten"
    ```
    
- **Creëer een compilatievideo van gevonden zinnen:**
    
    Bash
    
    ```
    ./dimper zoek "vijf reten" -k
    ```
    
- **Zoek en genereer met extra marge:**
    
    Bash
    
    ```
    ./dimper zoek "ik geef het negen reten" -k --pre 0.5 --post 0.2
    ```
    

### `zeg`

Bouwt een video-compilatie van een complete zin, woord-voor-woord, door losse woorden uit de videobibliotheek samen te voegen. Het maximale aantal zinnen dat kan worden opgebouwd, wordt bepaald door het minst gevonden woord (de "zwakste schakel").

**Opties:**

- `--pre <seconden>`: Voeg extra seconden toe vóór de start van elk woordfragment.
    
- `--post <seconden>`: Voeg extra seconden toe ná het einde van elk woordfragment.
    
- `--create -k`: Genereer de compilatievideo (anders alleen een analyse).
    

**Voorbeelden:**

- **Analyseer hoe vaak elk woord in de zin voorkomt:**
    
    Bash
    
    ```
    ./dimper zeg "hallo jongen en welkom"
    ```
    
- **Creëer een compilatie van de complete zin, opgebouwd uit losse woorden:**
    
    Bash
    
    ```
    ./dimper zeg "hallo jongen en welkom" -k
    ```
    
- **Genereer de zin met aangepaste fragmentlengtes:**
    
    Bash
    
    ```
    ./dimper zeg "een twee drie vier" -k --pre 0.1 --post 0.1
    ```
    

### `kut`

Dit is de meest precieze functie. Het zoekt naar exacte woorden of zinnen en knipt die chirurgisch uit de video's, met respect voor de exacte start- en eindtijden van die specifieke woorden.

**Opties:**

- `--pre <seconden>`: Voeg extra seconden toe vóór de start van de clip.
    
- `--post <seconden>`: Voeg extra seconden toe ná het einde van de de clip.
    
- `--randomize -r`: Schud de gevonden clips in willekeurige volgorde voordat de video wordt gemaakt.
    
- `--create -k`: Genereer de compilatievideo (anders alleen een analyse).
    

**Voorbeelden:**

- **Zoek en analyseer precieze woordfragmenten:**
    
    Bash
    
    ```
    ./dimper kut "vijf reten"
    ```
    
- **Genereer een compilatie van meerdere, exact geknipte termen, gerandomiseerd:**
    
    Bash
    
    ```
    ./dimper kut "vijf reten" "twee reten" "drie raten" -k -r
    ```
    
- **Creëer een video van een langere precieze zin:**
    
    Bash
    
    ```
    ./dimper kut "ik geef het negen reten" -k
    ```
    

## Contact

Voor vragen, suggesties of opmerkingen kun je een e-mail sturen naar alshauwki@gmail.com.

## Mijn Setup

- **CPU:** AMD Ryzen 7 1800X
    
- **RAM:** 16.0 GB 3.60 GHz
    
- **GPU:** NVIDIA GeForce GTX 1660 Ti (6 GB)
    
- **OS:** 64-bit operating system, x64-based processor (Ubuntu 24.04 LTS)
    

**Let op:** Deze tool kan veel resources verbruiken, met name de transcriptie- en demucs-stappen. Zorg voor een krachtig systeem (bij voorkeur met een goede GPU) voor de beste prestaties. De tool is ontwikkeld op Linux, maar zou op de meeste UNIX-achtige systemen (zoals macOS) moeten werken.
