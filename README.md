# DUMPERT KUT videos
dit genereert dumpert videos op basis van meegegeven termen of zinnen.
ik maak nog wel een guide, druk.

## INSTALLATIE
Voor nu kun je de setup.sh runnen. Dit zet de hele omgeving voor je op. (misschien eerst chmod +x setup.sh runnen)

Vervolgens kun je alle videos downloaden. Dat kost je 100GB+-.
Dit doe je met: ./dimper downloade <url video of een hele playlist url> (alle dumpert videos(100GB): https://www.youtube.com/watch?v=ykpYKOnzgG4&list=PLMe_6SSHyqcYh032ZieiNHW8bwusy7FPJ) (not promoted, verveelde me en begon aan dit sideprojects, maar wilde het alsnog delen)
Alles word in videos/ gezet. Daar staan nu mijn videobestanden in (zonder .mp4 bestanden die de 100GB zijn, moet je ff zelf downloaden)

## TRANSCRIBEREN
Als je alle video bestanden hebt moeten we transcriberen. Dat doen we met WhisperX (van openai, met een touch)
./dimper transcribe videos/ <hier geef je de videos folder mee en transcriberen begint>
Het zoekt alle mappen die nog niet getranscribeerd zijn.

## USAGE
Nu kun je dus superkuts maken (cuts, pun inserted yada yada).
./dimper zoek "tien reten" <nu zoekt het programma naar alle segmenten in alle videos waar "tien reten" wordt gezegd>

als je nu:
./dimper zoek "tien reten" -k runt dan krijg je een compilatie clip van je gezochte termen. 
je kunt ook [--pre 0.1 --post 0.12] meegeven als je stukjes voor en na de clip wil meenemen.

Ja dit werkt op alle videos, dus niet alleen dumpert videos. Ik zou zeggen be creative. 
WhisperX model is wel afgestemd op nederlands, maar kun je zelf allemaal aanpassen (succes!)

geen zin meer om te typen, hier zul je het even mee moeten doen. stuur me mailtje als je vragen hebt:
alshauwki@gmail.com

# MIJN SETUP
CPU:  AMD Ryzen 7 1800X Eight-Core Processor
RAMP: 16.0 GB 3.60 GHz
GPU:  NVIDIA GeForce GTX 1660 Ti (6 GB)
64-bit operating system, x64-based processor
Ik heb Ubuntu 24.04 LTS op mijn systeem, maar dit zou ook moeten werken op meeste UNIX system, zoals een macbook. Mind you: dit slurpt je resources, dus zorg voor een goede M1 of hoger of goede GPU met ubuntu ofzo.
