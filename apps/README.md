# RoundyPi app library

Ce dossier sert de mémoire pour les prototypes développés sur le RoundyPi.

Le fichier actif envoyé sur la carte reste `code.py` à la racine du projet.

## Apps explorées

### Horloge analogique

Premier prototype stable avec aiguilles heure/minute/seconde et synchronisation depuis le PC via `sync_clock.ps1`.

### Animation galaxie

Prototype visuel autonome : anneaux lumineux, particules en orbite, cœur pulsant. Bon test d’affichage GC9A01.

### Citations inspirantes

Petit oracle de bureau : citation centrée, changement horaire, fond animé. Notes importantes : éviter `str.rjust()` et `input()` bloquant sur cette build CircuitPython.

### Diagnostic stabilité

Monitoring longue durée : uptime, FPS, boucles, mémoire libre/minimum, température CPU si disponible, heartbeat visuel.

### Pomodoro

Timer focus piloté par USB : focus 25 min, pause 5 min, pause longue 15 min après 4 sessions. Commandes via `pomodoro_control.ps1` : `start`, `pause`, `reset`, `skip`, `focus`, `break`, `long`.

### Status display + companion app

RoundyPi utilisé comme afficheur piloté par PC avec états `FREE`, `BUSY`, `DND`, `AWAY`. Companion app Windows : `status_companion.ps1`.

### Status display + tamagotchi coach

Compagnon visuel qui encourage le pointage quotidien, le focus et les quick wins. Actions : `CHECKIN`, `FOCUS`, `WIN`, `REST`.

### Creature eyes

Deux yeux expressifs avec regard gauche/droite, clignements, clin d’œil et micro-mouvements. La version active légère est `creature_eyes.py`; la version précédente plus organique est sauvegardée dans `creature_eyes_realistic_saved.py`.

### Game of Life

Automate cellulaire de Conway adapté à l’écran rond : grille 48x48, masque circulaire, détection d’extinction/stabilité/boucles courtes, reseed automatique quand le monde se stabilise.

## Scripts utilitaires

- `install_app.ps1` : installe une app vers le disque `CIRCUITPY`.
- `sync_clock.ps1` : synchronise l’heure depuis le PC.
- `pomodoro_control.ps1` : pilote le Pomodoro par USB série.
- `status_companion.ps1` : companion app graphique pour le status display.
- `flash_when_rp2_appears.ps1` : surveille `RPI-RP2` et reflashe CircuitPython.
- `watch_roundypi_usb.ps1` : surveille les changements USB/PnP.
- `upload_via_serial.ps1` : tentative d’upload via REPL série.

## Notes matérielles

- Carte : RoundyPi, RP2040.
- Bootloader : disque `RPI-RP2`.
- CircuitPython : disque `CIRCUITPY`.
- Port série observé : `COM11`.
- Écran : GC9A01 rond 240x240.
- Pins écran : SCK `GP10`, MOSI `GP11`, CS `GP9`, DC `GP8`, RST `GP12`, BL `GP13`.

## Installer une app

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\fgobe\Documents\RoundyPi\install_app.ps1 C:\Users\fgobe\Documents\RoundyPi\apps\pomodoro.py
```

Le script copie l’app vers `D:\code.py` et copie aussi `_roundypi.py` vers `D:\_roundypi.py` quand l’app utilise le helper partagé.

Note : `status_tamagotchi.py` est standalone, car c’est la version active sauvegardée telle quelle.
