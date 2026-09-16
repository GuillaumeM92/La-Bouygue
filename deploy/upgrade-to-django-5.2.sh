#!/bin/sh
# One-off: move the live site from Django 3.1 (env/) to Django 5.2 (.venv/).
# Run as root on the server, once origin/master holds the upgrade, straight
# from git so the old checkout stays live while the new environment builds:
#   cd /home/ubuntu/My-Websites/La-Bouygue && git fetch && git show origin/master:deploy/upgrade-to-django-5.2.sh > /root/upgrade-django-5.2.sh && sh /root/upgrade-django-5.2.sh
#
# Only the django_migrations table changes in the database (a copy is kept in
# django_migrations_before_5_2), plus two foreign keys the schema was missing.
# The old env/ is left in place. To roll back:
#   sed -i 's#/La-Bouygue/.venv/bin/gunicorn#/La-Bouygue/env/bin/gunicorn#' /etc/supervisor/conf.d/la_bouygue-gunicorn.conf
#   git checkout 688f2f2 && supervisorctl reread && supervisorctl update la_bouygue-gunicorn
set -eu

SITE=/home/ubuntu/My-Websites/La-Bouygue
CONF=/etc/supervisor/conf.d/la_bouygue-gunicorn.conf
PROGRAM=la_bouygue-gunicorn
DB=la_bouygue
cd "$SITE"
psql_db() { runuser -u postgres -- psql -v ON_ERROR_STOP=1 -X -q -d "$DB" "$@"; }

echo "1/6 Database backup"
"$SITE/deploy/backup-db.sh"

echo "2/6 New Python environment (the site keeps running on env/)"
REQ=$(mktemp)
git show origin/master:requirements/requirements-prod.txt > "$REQ"
[ -x .venv/bin/python ] || python3.12 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r "$REQ"
rm -f "$REQ"
.venv/bin/python -m django --version

echo "3/6 New code, served from the new environment"
git pull --ff-only
git log --oneline -1
.venv/bin/python manage.py check
sed -i 's#/La-Bouygue/env/bin/gunicorn#/La-Bouygue/.venv/bin/gunicorn#' "$CONF"
grep -q "/La-Bouygue/.venv/bin/gunicorn" "$CONF"
supervisorctl reread
supervisorctl update "$PROGRAM"

echo "4/6 Migration history"
psql_db -c "CREATE TABLE IF NOT EXISTS django_migrations_before_5_2 AS SELECT * FROM django_migrations"
.venv/bin/python manage.py shell < deploy/reset-migration-history.py
.venv/bin/python manage.py makemigrations --check --dry-run

echo "5/6 Missing foreign keys"
ORPHANS=$(psql_db -At -c "
    SELECT (SELECT count(*) FROM users_myuser_groups g
            WHERE NOT EXISTS (SELECT 1 FROM users_myuser u WHERE u.id = g.myuser_id))
         + (SELECT count(*) FROM users_myuser_user_permissions p
            WHERE NOT EXISTS (SELECT 1 FROM users_myuser u WHERE u.id = p.myuser_id))")
if [ "$ORPHANS" != "0" ]; then
    echo "$ORPHANS group/permission rows point to deleted accounts: keys not added." >&2
else
    psql_db <<'SQL'
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'users_myuser_groups_myuser_id_fk_users_myuser_id') THEN
        ALTER TABLE users_myuser_groups ADD CONSTRAINT users_myuser_groups_myuser_id_fk_users_myuser_id
            FOREIGN KEY (myuser_id) REFERENCES users_myuser(id) DEFERRABLE INITIALLY DEFERRED;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'users_myuser_user_permissions_myuser_id_fk_users_myuser_id') THEN
        ALTER TABLE users_myuser_user_permissions ADD CONSTRAINT users_myuser_user_permissions_myuser_id_fk_users_myuser_id
            FOREIGN KEY (myuser_id) REFERENCES users_myuser(id) DEFERRABLE INITIALLY DEFERRED;
    END IF;
END $$;
SQL
    echo "Keys in place."
fi

echo "6/6 Static files, restart and checks (deploy.sh)"
SKIP_PULL=1 "$SITE/deploy/deploy.sh"
pgrep -af "La-Bouygue/.venv/bin/gunicorn" > /dev/null
curl -fsS -o /dev/null https://labouygue.fr/login/
echo "Django 5.2 is live."
