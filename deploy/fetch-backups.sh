#!/bin/sh
# Copy the server's database dumps and uploaded media to this Mac, so a lost
# server does not take its backups with it. Run weekly by launchd, see
# deploy/mac/fr.labouygue.fetch-backups.plist. Nothing is ever deleted here:
# the server prunes old dumps, this copy keeps them.
set -eu

exec >> "$HOME/Library/Logs/la-bouygue-fetch-backups.log" 2>&1

DEST="$HOME/Documents/Sauvegardes/La Bouygue"
mkdir -p "$DEST/base de données" "$DEST/media"

rsync -a -e "ssh -o BatchMode=yes" \
    ionos:/var/backups/la_bouygue/ "$DEST/base de données/"
rsync -a -e "ssh -o BatchMode=yes" \
    ionos:/home/ubuntu/My-Websites/La-Bouygue/media/ "$DEST/media/"

echo "$(date '+%F %T') OK, dernier dump : $(ls "$DEST/base de données" | tail -1)"
