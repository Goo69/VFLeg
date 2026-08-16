#!/bin/bash

# Tue TOUT ce qui contient "main.py" dans sa ligne de commande (SIGTERM)
pkill -f "main.py"

# Petite pause
sleep 1

# Force l'arrêt radical (SIGKILL) au cas où des processus bloqués refusent de mourir
pkill -9 -f "main.py"

# Double sécurité : s'assure qu'il ne reste vraiment plus rien de ce projet
sleep 1

# Lancement propre
cd /home/ticoop/VFLeg/source/python
python3 main.py
