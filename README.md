# Dumpert Kutter

## Context
Dit project, liefkozend "Dumpert Kutter" (cutter, snapte?), begon als een persoonlijk zijproject om specifiek de "reeten" uit DumpertReeten-video's te kunnen extraheren en analyseren. Wat begon als een hulpmiddel voor een niche-gebruik, is inmiddels uitgegroeid tot een veelzijdige open-source tool speciaal voor jou.<br/>
De `Dumpert Kutter` maakt het gemakkelijk om video's te downloaden, te transcriberen, en vervolgens op basis van gesproken woorden of zinnen video compilaties te maken. De kern van de geavanceerde functionaliteit ligt in de **`kut`**-functie, die hieronder uitgebreid wordt toegelicht.

## Installatie

Om Dumpert Kutter te installeren na het clonen van de repository, volg je deze stappen:<br/>
1.  **Clone cut:**
    ```bash
    git clone https://github.com/shauwki/dumpert-kut.git
    cd dumpert-kut
    ```

2.  **Run de setup met geduld:**<br/>
    Dit script controleert op systeemafhankelijkheden (zoals `python3`, `ffmpeg`, `git`), maakt een Python virtuele omgeving (`venv`) aan, installeert alle benodigde Python-pakketten uit `requirements.txt` (inclusief `whisperX` en `demucs`), en maakt de executables uitvoerbaar.
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```
    Na succesvolle installatie ben je klaar om de tool te gebruiken.

## Configuratie
De Dumpert Kutter-tool werkt met video's die in de `videos/` map in de root van het project worden geplaatst.<br/>
* **Videobestanden:** De `setup.sh` haalt geen videobestanden voor je op. Je dient je `.mp4`-videobestanden handmatig in de `videos/` map te plaatsen (of in submappen daarbinnen). Of de in-house downloader gebruiken.
* **WhisperX Taal:** Het WhisperX-model is standaard afgestemd op Nederlands (`--language nl`), maar kan handmatig worden aangepast in `src/transcriber.py` als je met andere talen wilt werken.

## Usage
De `dumpert` CLI biedt verschillende commando's voor diverse taken:<br/>
Alle commando's worden uitgevoerd via `./dumpert [commando] [opties] [argumenten]`.

### `download`
Download video's of playlists van YouTube (of andere ondersteunde bronnen) naar de `videos/` map.
**Voorbeeld:**
```bash
./dumpert download "https://www.youtube.com/playlist?list=PLMe_6SSHyqcYh032ZieiNHW8bwusy7FPJ"
```
_(Ik heb hier de link naar alle dumpert-reeten videos van Dumpert gebruikt :)_

### `transcribe`
Transcribeert videobestanden naar JSON-transcripties met WhisperX. Ondersteunt verschillende modi voor kwaliteit versus snelheid.
**Opties:**
- `--prompt <tekst>`: Een hint voor de transcribeer-engine om de nauwkeurigheid te verbeteren (bijv. veelvoorkomende termen als reten, reeten).
- `--mode <modus>`: Kies de transcriptie-modus.
    - `standard` (standaard): Gebruikt de ingebouwde VAD (Voice Activity Detection) van WhisperX. Snel en vaak voldoende.
    - `demucs`: Gebruikt `demucs` om eerst zang/spraak van muziek te scheiden, en transcribeert daarna alleen de zang. Dit is de langzaamste maar meest accurate methode voor video's met achtergrondmuziek.  

_Alles wat ik tot nu toe heb getranscribeerd upload ik bij iedere push mee dan hoef jij het niet te doen. Ik heb er aardig veel, dus jij hoeft alleen de videos te downloaden met deze exacte cmd: `./dumpert download [link van dumpertreeten videos]`_
- **Transcribeer een hele map (standaard modus):**
    ``` bash
    ./dumpert transcribe videos/
    ```
- **Transcribeer een specifieke video met een prompt:**
    ``` bash
    ./dumpert transcribe videos/een_aflevering/mijn_video.mp4 --prompt "DumpertReeten, dumpert, reeten, raten"
    ```
    _(--prompt zijn dus woorden waar de transcriber meer op let, ofzoiets (initial prompt))_
- **Transcribeer met Demucs voor hoge kwaliteit:**
    ``` bash
    ./dumpert transcribe videos/ --mode demucs
    ```
_(Ik run transcribe met --mode demucs meestal op de achtergrond in een tweede terminal terwijl ik de tool gebruik. Over-time heb je meer en meer data, des te meer videos je download. Mijn GPU is niet zo krachtig, maar downloaden van 100GB videos duurde kort vergeleken met alles transcriben. Dat duurde dagen bij mij, dus succes!)_

### `kut`
Dit is de meest precieze functie. Het zoekt naar exacte woorden of zinnen en knipt die chirurgisch uit de video's, met respect voor de exacte start- en eindtijden van die specifieke woorden.
**Opties:**
- `--pre <seconden>`: Voeg extra seconden toe vóór de start van de clip.
- `--post <seconden>`: Voeg extra seconden toe ná het einde van de de clip.
- `--randomize -r`: Schud de gevonden clips in willekeurige volgorde voordat de video wordt gemaakt.
- `--create -k`: Genereer de compilatievideo (anders alleen een analyse).
**Voorbeelden:**
- **Zoek en analyseer precieze woordfragmenten:**
    ``` bash
    ./dumpert kut "vijf reten"
    ```
- **Genereer een compilatie van meerdere, exact geknipte termen, gerandomiseerd:**
    ``` bash
    ./dumpert kut "vijf reten" "twee reten" "drie raten" -k -r
    ```
- **Creëer een video van een langere precieze zin:**
    ``` bash
    ./dumpert kut "ik geef het negen reten" -k
    ```

### `zoek`
Vindt en compileert hele segmenten waarin een zoekterm voorkomt. Dit werkt in principe hetzelfde als kut, maar knipt niet zoals kut. Hierbij zul je een soortgelijke resultaat krijgen, maar bij sommige clips krijg je nog een comment voor of na je zoekterm. Ook leuke resultaten. _Let op: geen randomizer, komt misschien ooit n keer._
**Opties:**
- `--directory -d <pad>`: De map om te doorzoeken (standaard: `videos/`).
- `--pre <seconden>`: Voeg extra seconden toe vóór de start van de clip.
- `--post <seconden>`: Voeg extra seconden toe ná het einde van de clip.
- `--create -k`: Genereer de compilatievideo (anders alleen een analyse).
**Voorbeelden:**
- **Zoek naar een term en analyseer de resultaten:**
    ``` bash
    ./dumpert zoek "tien reten"
    ```
- **Creëer een compilatievideo van gevonden zinnen:**
    ``` bash
    ./dumpert zoek "vijf reten" -k
    ```
- **Zoek en genereer met extra marge:**
    ``` bash
    ./dumpert zoek "ik geef het negen reten" -k --pre 0.5 --post 0.2
    ```

### `zeg`
Bouwt een video-compilatie van een complete gegeven zin, woord-voor-woord, door losse woorden uit de videobibliotheek samen te voegen. Het maximale aantal zinnen dat kan worden opgebouwd, wordt bepaald door het minst gevonden aantal woorden uit de gegeven zin (de "zwakste schakel"). _Deze functie moet ik nog verbeteren. Duurt altijd lang als je veel resultaten hebt. Dus probeer niche woorden te gebruiken voor sneller? resultaat._
**Opties:**
- `--pre <seconden>`: Voeg extra seconden toe vóór de start van elk woordfragment.
- `--post <seconden>`: Voeg extra seconden toe ná het einde van elk woordfragment.
- `--create -k`: Genereer de compilatievideo (anders alleen een analyse). 
**Voorbeelden:**
- **Analyseer hoe vaak elk woord in de zin voorkomt:**
    ``` bash
    ./dumpert zeg "hallo jongen en welkom"
    ```
- **Creëer een compilatie van de complete zin, opgebouwd uit losse woorden:**
    ``` bash
    ./dumpert zeg "hallo meisje en welkom" -k
    ```
- **Genereer de zin met aangepaste fragmentlengtes:**
    ``` bash
    ./dumpert zeg "een twee drie vier hoedje van papier" -k --pre 0.1 --post 0.1
    ```

## Contact
Voor vragen, suggesties of opmerkingen kun je een e-mail sturen naar [alshauwki@gmail.com](mailto:alshauwki@gmail.com?subject=Dumpert%20Kutter&body=Jo%20maat,%20).
## Mijn Setup
- **CPU:** AMD Ryzen 7 1800X
- **RAM:** 16.0 GB 3.60 GHz
- **GPU:** NVIDIA GeForce GTX 1660 Ti (6 GB)<-- die 6GB was m'n limiet op deze GPU. Echter, snel genoeg voor mij)
- **OS:** x64-based processor (Ubuntu 24.04 LTS)
    
**Let op:** Deze tool kan veel resources verbruiken, met name de transcriptie- en demucs-stappen. Zorg voor een krachtig systeem (bij voorkeur met een goede GPU) voor de beste prestaties. De tool is ontwikkeld op Linux, maar zou op de meeste UNIX-achtige systemen (zoals macOS met M-chip) moeten werken. Maar mijn M1 MBpro was traag. As of now, moet ik nog testen hoe ffmpeg het doet met compileren. Transcriberen kon ik in mijn geval over laten aan mijn broertjes oude game-pc. Ik moet nog 230/438-ish afleveringen transcriberen. 


# Voorbeeld resultaten

[![Halloo](https://img.youtube.com/vi/ZWEb3xTyTRA/0.jpg)](https://www.youtube.com/watch?v=ZWEb3xTyTRA)
```bash
./dumpert kut "hallo allemaal" "welkom allemaal" "hallo" -kr
```
-----
[![Dumpert Reeten voorbeeld output](https://img.youtube.com/vi/7BvqmrFZrHE/0.jpg)](https://www.youtube.com/watch?v=7BvqmrFZrHE)
```bash
./dumpert kut "dumpertreten" -k -r
```
-----
[![nul reten voor mijn voorbeelden:p](https://img.youtube.com/vi/cYIxwT0rwqk/0.jpg)](https://www.youtube.com/watch?v=cYIxwT0rwqk)
```bash
./dumpert zeg "nul reten"
```
-----
[![lange compilatie van 5 reeten](https://img.youtube.com/vi/Z3BwtRlV1JI/0.jpg)](https://www.youtube.com/watch?v=Z3BwtRlV1JI)
```bash
./dumpert kut "vijf reten" "vijf rate" "vijf raten" "vijf reeten" -kr
```
-----
[![mixed reetings](https://img.youtube.com/vi/N4gVH1Bbh6M/0.jpg)](https://www.youtube.com/watch?v=N4gVH1Bbh6M)
```bash
./dumpert kut "nul reten" "een reet" "twee reten" "drie reten" "vier reten" "vijf reten" "nul reeten" "vier reeten" "vijf reeten" -kr --limit "25;100"
```
-----
[![homooooo, dit was een culturele keuze x ly](https://img.youtube.com/vi/PeWKg4v9n4k/0.jpg)](https://www.youtube.com/watch?v=PeWKg4v9n4k)
```bash
./dumpert kut "homo" -k -r
```
-----
[![thema bleef ff hangen, sorrry](https://img.youtube.com/vi/FD1iC_Hmnc8/0.jpg)](https://www.youtube.com/watch?v=FD1iC_Hmnc8)
```bash
./dumpert kut flikker -kr
```