#!/bin/sh
# Put the latest master online. Run as root on the server:
#   /home/ubuntu/My-Websites/La-Bouygue/deploy/deploy.sh
# To roll back: git checkout <previous commit>, then run this script with
# SKIP_PULL=1.
set -eu

SITE=/home/ubuntu/My-Websites/La-Bouygue
PROGRAM=la_bouygue-gunicorn
cd "$SITE"

echo "1/5 Database backup"
"$SITE/deploy/backup-db.sh"

echo "2/5 Code"
if [ -z "${SKIP_PULL:-}" ]; then
    git pull --ff-only
fi
git log --oneline -1

echo "3/5 Migrations"
# migrations/ is not versioned: never generate them here, only check.
if ! env/bin/python manage.py migrate --plan | grep -q "No planned migration operations"; then
    echo "Migrations are pending: review them, apply them by hand, then rerun with SKIP_PULL=1." >&2
    exit 1
fi

echo "4/5 Static files"
# Collected into a fresh folder, then swapped in, so the live site never
# serves a half-copied folder.
rm -rf staticfiles-new
STATIC_ROOT="$SITE/staticfiles-new" env/bin/python manage.py collectstatic --noinput -v 0
rm -rf staticfiles-old
mv staticfiles staticfiles-old
mv staticfiles-new staticfiles

echo "5/5 Restart"
supervisorctl restart "$PROGRAM"
sleep 3
curl -fsS -o /dev/null -H "Host: labouygue.fr" http://127.0.0.1:8000/login/
echo "Site up."
