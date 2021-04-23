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

*Immer in der aktivierten Conda-Umgebung*

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