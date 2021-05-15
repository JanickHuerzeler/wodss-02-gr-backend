# WODSS Gruppe 02 Backend

Backend für den Workshop in der Vertiefung "Distributed Software Systems" (WODSS).

---

## Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- Python 3.8 (z.B. direkt aus Miniconda)
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

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

Docker Daemon muss installiert sein und laufen.

```zsh / CMD
docker-compose up -d
```

---

## Dev-Environment starten

Nachdem die vorhergehenden Schritte ausgeführt wurden, kann auch der lokale Flask Server gestartet werden:

```CMD/ZSH
python server.py
```

Dieser ist unter [http://localhost:5001](http://localhost:5001) erreichbar und zeigt direkt das Swagger UI an.

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

danach:

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

## Cache Warm-Up

Das Caching von Inzidenzzahlen kann mit `python cache_warmup.py` aufgewärmt werden. Wird dieses Script ausgeführt, werden alle Kantone, für welche ein Server konfiguriert ist aus dem `config.json` gelesen. Bei diesen Kantonen werden alle BFS-Nr. angefragt und schliesslich für diese BFS-Nr die Requests gesendet. Mit dem Senden der Requests wird der Cache augewärmt.

---

## Live Environment

Server wird gemäss Kantonsservice-[README.md](https://github.com/JanickHuerzeler/wodss-02-gr-canton-service#readme) bereits zur Verfügung gestellt.

---

Folgende Übersicht zeigt die wichtigsten URL und Pfade auf dem Live-Server

#### **URLs** `api.corona-navigator.ch`

#### **Deploy latest branch** `~/deploy_backend.sh`

#### **Git Repo Path** `/opt/apps/wodss-02-gr-backend/`

#### **Restart Backend-Service** `sudo systemctl restart wodss-02-gr-backend.service`

#### **Conda Env Update** `conda env update --file /opt/apps/wodss-02-gr-backend/resources/environment.yml`

---

### Docker Setup

- Für die Docker Engine Installation kann folgender Anleitung gefolgt werden:
  https://docs.docker.com/engine/install/ubuntu/
- Installation Docker Compose: https://docs.docker.com/compose/install/

### Step 1 - Clone Git Repository

```ZSH / CMD
mkdir /opt/apps
cd /opt/apps
git clone https://github.com/JanickHuerzeler/wodss-02-gr-backend.git
```

### Step 2 - Virtual Conda Environment erstellen

Weil die bereitgestellte VM zu wenig Arbeitsspeicher hat, wird zuerst ein 2GB Swap-File erstellt

```ZSH / CMD
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
Shorthander:
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
```

Nun kann die conda env mit Hilfe des environment.yml erstellt werden

```ZSH / CMD
conda env create -f /opt/apps/wodss-02-gr-backend/resources/environment.yml

source activate WODSS-Backend
```

### Step 3 - Setup cronjob (requests-cache warm-up)

```ZSH / CMD
crontab -e
50 */3 * * * cd /opt/apps/wodss-02-gr-backend && /opt/anaconda/envs/WODSS-Backend/bin/python3.8 cache_warmup.py
```

### Step 4 - Setup Nginx

Die Ports 80 und 443 müssen auf der VM offen sein. SWITCHEngine: https://bit.ly/3fN5UD0
Danach einen vhost in nginx mit folgender Konfiguration erstellen:

```ZSH / CMD
export DOMAIN=corona-navigator.ch

sudo tee /etc/nginx/sites-available/api.$DOMAIN <<EOF
server {
  listen 80;
  listen [::]:80;
  server_name localhost api.$DOMAIN;

  location / {
    proxy_pass http://localhost:5001;
  }
}
EOF

sudo ln -s /etc/nginx/sites-available/api.$DOMAIN /etc/nginx/sites-enabled/api.$DOMAIN
sudo systemctl enable nginx
```

### Step 5 - Setup backend als system service

```ZSH / CMD
sudo tee /etc/systemd/system/wodss-02-gr-backend.service << EOF
[Unit]
Description=uWSGI instance to serve wodss-02-gr-backend

[Service]
ExecStart=/bin/bash -c 'cd /opt/apps/wodss-02-gr-backend && uwsgi --processes 4 --threads 2 -H /opt/anaconda/envs/WODSS-Backend resources/uwsgi.ini'

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable wodss-02-gr-backend
```

### Step 6 - Setup SSL

```ZSH / CMD
# Ensure that the version of snapd is up to date
sudo snap install core; sudo snap refresh core

# Install Certbot
sudo snap install --classic certbot

# Prepare the Certbot command
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Confirm plugin containment level
sudo snap set certbot trust-plugin-with-root=ok

# Create Certificate
sudo certbot run -a manual -i nginx -d api.corona-navigator.ch
```

### Deploy Script erstellen

Mit Hilfe dieses Scripts können neue Versionen im Git Repo geholt und auf dem Server ausgerollt werden.

Die Ports 20-21 und 4242-4243 müssen auf der VM offen sein. SWITCHEngine: https://bit.ly/3fN5UD0

```ZSH / CMD
sudo tee /home/ubuntu/deploy_backend.sh <<EOF
echo -e '\nTry to create swapfile...'
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile

echo -e '\nGit fetch & merge...'
cd /opt/apps/wodss-02-gr-backend/
git fetch
git reset --hard HEAD > /dev/null
git merge '@{u}'

echo -e '\nUpdate conda environment...'
conda env update --file /opt/apps/wodss-02-gr-backend/resources/environment.yml

echo -e '\nRestarting backend service...'
sudo systemctl restart wodss-02-gr-backend.service

GREEN='\033[0;32m'
NC='\033[0m' # No Color
printf "\n${GREEN}Deployment successfull${NC}\n\n"
EOF
```
