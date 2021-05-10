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

## Dev-Environment starten
Nachdem die vorhergehenden Schritte ausgeführt wurden, kann auch der lokale Flask Server gestartet werden:

``` CMD/ZSH
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

- Für die Docker Engine Installation kann folgender Anleitung gefolgt werden:
  https://docs.docker.com/engine/install/ubuntu/
- Installation Docker Compose: https://docs.docker.com/compose/install/

### Step 1 - Clone Git Repository

```ZSH / CMD
mkdir /opt/apps
cd /opt/apps
git clone https://github.com/JanickHuerzeler/wodss-02-gr-backend.git
```

### Step 2 - Create Virtual Conda Environment

Because the virtual machine has insufficient memory, we first have to create a temporary 2GB swapfile

```ZSH / CMD
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
Shorthander:
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
```

Now we can create the conda env using environment.yml

```ZSH / CMD
conda env create -f /opt/apps/wodss-02-gr-backend/resources/environment.yml

source activate WODSS-Backend
```

### Step 3 - Setup Nginx

First we have to open ports 80+443 on SWITCHEngine: https://bit.ly/3fN5UD0

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

### Step 4 - Setup backend as a system service

```ZSH / CMD
sudo tee /etc/systemd/system/wodss-02-gr-backend.service << EOF
[Unit]
Description=uWSGI instance to serve wodss-02-gr-backend

[Service]
ExecStart=/bin/bash -c 'cd /opt/apps/wodss-02-gr-backend && uwsgi -H /opt/anaconda/envs/WODSS-Backend resources/uwsgi.ini'

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable wodss-02-gr-backend
```

### Step 5 - Setup SSL

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

### Create deploy script

First we have to open ports 20-21 + 4242-4243 on SWITCHEngine: https://bit.ly/3fN5UD0

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
