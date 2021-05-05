# WODSS Gruppe 02 Backend

Backend für den Workshop in der Vertiefung "Distributed Software Systems" (WODSS).

---

## Prerequisites

- Miniconda
- Python 3.8

Es wird empfohlen, mit einem Conda Environment zu arbeiten.
Folgender Befehl erstellt ein neues Conda Environment mit dem Namen `WODSS-Backend`:

```zsh / CMD
conda env create -f resources/environment.yml
```

Das soeben erstellte Conda Environment muss dabei noch aktiviert werden:

```zsh /CMD
conda activate WODSS-Backend
```

---

## Installieren von neuen Libraries

_Immer in der aktivierten Conda-Umgebung_

Wird eine Library neu installiert (`conda install XYZ`), muss diese im `resources/environment.yml` nachgeführt werden.
Dies kann manuell geschehen, am einfachsten durch Kopieren der Ausgabe von folgendem Befehl:

```zsh / CMD
 conda env export --from-history
```

Sobald das `resources/environment.yml` gepushed wurde, können die Projektmitarbeitenden ihr Environment durch folgenden Befehl auf den aktuellsten Stand bringen, resp. die neue Library auch installieren:

```zsh / CMD
conda env update --file resources/environment.yml
```

`--prune` würde zusätzlich noch nicht mehr verwendete Libraries gleich entfernen.

---

## Redis

Für das Caching von Inzidenzzahlen wird Redis verwendet. Der Redis-Server steht im `docker-compose.yml` als Docker Image bereit.

### Prerequisites

Docker Deamon muss installiert sein und laufen.

```zsh / CMD
docker-compose up -d
```

---

## Unit Tests

Als Test Framework wird `pytest` verwendet.
Die Unit Tests können mit folgendem Befehl im Hauptverzeichnis ausgeführt werden:

```zsh / CMD
pytest
```

Visual Studio Code bietet einen integrierten Test-Explorer an, der auch pytest unterstützt. Dazu muss die Test Discovery gemäss [Anleitung](https://code.visualstudio.com/docs/python/testing#_test-discovery) eingerichtet werden. Als Test Framework wird logischerweise `pytest` ausgewählt und als Test Directory `tests`.

### Coverage

```zsh / CMD
coverage run -m pytest
```

oder

```zsh / CMD
coverage report -m
```

oder

```zsh / CMD
coverage html
```

und dann:

Windows

```zsh / CMD
cd htmlcov
start index.html
```

MacOS X

```zsh / CMD
cd htmlcov
open index.html
```

---

## Live Environment

Server wird gemäss Kantonsservice-[README.md](https://github.com/JanickHuerzeler/wodss-02-gr-canton-service#readme) bereits zur Verfügung gestellt.

### Docker Setup
Für die Docker Engine Installation kann folgender Anleitung gefolgt werden:
https://docs.docker.com/engine/install/ubuntu/

TODO: Docker Compose, Daemon Konfiguration (Autostart): https://docs.docker.com/config/daemon/
--