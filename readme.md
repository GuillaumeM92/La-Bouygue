# La Bouygue

The family website of La Bouygue, a house in the Pyrenees: https://labouygue.fr

Members share a calendar of stays, practical information about the house,
hiking ideas, discussions, the list of repairs to do, an address book and the
budget of the house. New accounts must be validated by an administrator.

## Features
* Register, log in, reset a forgotten password
* Calendar of stays: month grid, and a list of upcoming stays (the default on
  phones); add, edit or delete your own stays
* Discussions, practical information, activities and repairs, with comments
  and photos (cropped in the browser before upload)
* Address book and member profiles
* Budget of the house, with its history chart
* Administration: account activation, budget and funding updates, Django admin

## Stack
* Python 3, Django 3.1, PostgreSQL in production (SQLite locally)
* Gunicorn under Supervisor, behind Nginx, on an Ubuntu VPS
* Front end: Bootstrap 4 and the "Bergerie" design (`apps/bouygue/static/bouygue/css/bergerie.css`),
  FullCalendar, Chart.js, django-client-side-image-cropping
* Everything is served by the site itself: fonts, icons and JavaScript
  libraries live under `static/` (see `apps/bouygue/static/vendor/README.md`),
  and no page calls a third-party service

## Layout
```
apps/
  bouygue/      home, landing and error pages, base template, shared blocks,
                static files (design, fonts, vendored libraries, maintenance page)
  users/        accounts, login, registration, profiles, bot protection (antispam.py)
  agenda/       calendar of stays
  blog/         discussions
  info/         practical information, address book, account activation
  activities/   hikes and outings
  work/         repairs
  budget/       budget and funding
config/         settings, URLs, static storage
deploy/         deployment and backup scripts, reference copies of the server configuration
media/          default images (uploads are not versioned)
```

## Local development
Django 3.1 officially supports Python 3.6 to 3.9 (the server runs it on 3.12).
```
python3 -m venv venv
venv/bin/pip install -r requirements/requirements-dev.txt
```
Create `config/.env` (or `.env` at the root):
```
ENV=dev
SECRET_KEY=any-long-random-string
```
`ENV=dev` switches to SQLite and `DEBUG`. Migration files are not versioned
(`migrations/` is in `.gitignore`), so on a fresh clone run
`venv/bin/python manage.py makemigrations` then `migrate`, create an account
with `createsuperuser`, and start `venv/bin/python manage.py runserver`.

## Configuration (production)
`config/.env` on the server holds:

| Variable | Use |
|---|---|
| `ENV` | `prod` (anything but `dev` means production: PostgreSQL, no DEBUG, secure cookies) |
| `SECRET_KEY` | Django secret key |
| `HOST` | allowed host, `.labouygue.fr` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL database on localhost |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Gmail account used to send e-mails |

## Server
| What | Where |
|---|---|
| Code | `/home/ubuntu/My-Websites/La-Bouygue` (owned by root; run git as root) |
| Python environment | `env/` in that folder |
| Gunicorn | Supervisor program `la_bouygue-gunicorn`, port 8000, user `ubuntu` |
| Nginx | `/etc/nginx/sites-enabled/la_bouygue` (copy in `deploy/server/`) |
| Database backups | `/var/backups/la_bouygue`, nightly (see below) |

Nginx serves `/static/` and `/media/` itself, compresses text files, lets
browsers cache content-hashed static files for a year, and shows
`static/bouygue/maintenance.html` while Gunicorn restarts.

## Deployment
Push to `master`, then on the server, as root:
```
/home/ubuntu/My-Websites/La-Bouygue/deploy/deploy.sh
```
The script backs up the database, pulls, checks that no migration is
pending, collects the static files into a fresh folder and swaps it in,
restarts Gunicorn and checks that the site answers.

A plain `git pull` is not enough: Nginx serves the collected static files,
and Django caches its templates until Gunicorn restarts.

Migrations: the files in `migrations/` on the server are the only record of
what was applied to the production database. Never run `makemigrations`
there without comparing with the actual schema first.

To roll back: `git checkout <previous commit>`, then
`SKIP_PULL=1 deploy/deploy.sh`.

## Database backups
`deploy/backup-db.sh` runs every night from root's crontab
(`deploy/server/crontab-root.txt`). It keeps 30 days of dumps plus the dump of
the first of each month for a year, in `/var/backups/la_bouygue`, and logs to
`/var/log/la_bouygue-backup.log`.

Restore a dump (it replaces the current data):
```
runuser -u postgres -- pg_restore --clean --if-exists -d la_bouygue /var/backups/la_bouygue/la_bouygue-YYYY-MM-DD.dump
```
These backups live on the same disk as the database: copy one elsewhere from
time to time, for example `scp ionos:/var/backups/la_bouygue/<file> .`

## Special thanks
To my OpenClassrooms mentor Mikael Briolet for helping me build this project!
