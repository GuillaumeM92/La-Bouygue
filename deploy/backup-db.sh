#!/bin/sh
# Dump the La Bouygue database. Run by root's crontab every night:
#   30 3 * * * /home/ubuntu/My-Websites/La-Bouygue/deploy/backup-db.sh
# Keeps 30 days of dumps, plus the dump of the 1st of each month for a year.
# Restore: pg_restore --clean --if-exists -d la_bouygue <file>   (as postgres)
set -eu

DB=la_bouygue
DIR=/var/backups/la_bouygue
FILE="$DIR/$DB-$(date +%Y-%m-%d).dump"

mkdir -p "$DIR"
chmod 700 "$DIR"

runuser -u postgres -- pg_dump --format=custom "$DB" > "$FILE.tmp"
# A dump that pg_restore cannot read is not a backup
pg_restore --list "$FILE.tmp" > /dev/null
mv "$FILE.tmp" "$FILE"
chmod 600 "$FILE"

find "$DIR" -name "$DB-*.dump" ! -name "$DB-*-01.dump" -mtime +30 -delete
find "$DIR" -name "$DB-*-01.dump" -mtime +400 -delete

echo "$(date '+%F %T') $FILE $(du -h "$FILE" | cut -f1)"
