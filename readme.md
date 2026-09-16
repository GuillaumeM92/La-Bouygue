# La-Bouygue
Repository for a family website project named after the vacation house : La Bouygue.

Website address : https://labouygue.fr

## Project Description
Website for our family's vacation house.

The site handles reservations, as well as discussions, and other functionnalities listed below.

The calendar was built with FullCalendar : https://fullcalendar.io/

## Features
* Register
* Login or Reset your Password
* Make a reservation, modify it or delete it
* View other people's reservations on the calendar
* Create new discussions, read other people's discussions, post comments..
* Attach a picture to any form
* View any user Profile and change your profile picture
* Create and view new activities to do during the holidays
* Read the latest important informations about the house
* Create and view what work there is to do inside and outside the house
* See the budget for each year, watch contributions progress
* Activate New Users (Admin only)
* Update Budget and Funding (Admin only)
* Logout

## Built With
* Python
* Django
* JavaScript
* Nginx
* PostgreSQL
* Bootstrap
* Gunicorn
* Supervisor
* GitHub

### Js modules :
* FullCalendar
* Cookies
* Bootbox
* Django Client Side Image Cropping

## Special thanks
To my Openclassrooms mentor Mikael Briolet for helping me build this project!

## Local development
Django 3.1 needs Python 3.9 or older.
```
python3 -m venv venv
venv/bin/pip install -r requirements/requirements-dev.txt
```
Create a `.env` with `ENV=dev` (SQLite, DEBUG), a `SECRET_KEY`, and Google's reCAPTCHA test keys in `RECAPTCHA_PUBLIC` / `RECAPTCHA_PRIVATE`.
`migrations/` folders are not versioned: run `makemigrations` then `migrate` on a fresh clone, then `venv/bin/python manage.py runserver`.

## Deployment (VPS: Nginx, Gunicorn under Supervisor, PostgreSQL)
Static files are served by Nginx from `staticfiles/`, and Django caches templates in production, so a `git pull` alone is not enough.
```
# 1. Back up the database first
pg_dump -h localhost -U <DB_USER> <DB_NAME> > db_backups/labouygue-$(date +%F).sql

# 2. Update the code (the working tree must be clean)
git status
git pull

# 3. Publish the static files (CSS, fonts, scripts)
venv/bin/python manage.py collectstatic --noinput

# 4. Only if models changed: check, then apply
venv/bin/python manage.py migrate --plan

# 5. Reload Gunicorn (find the program name with `sudo supervisorctl status`)
sudo supervisorctl restart <program>
```
To roll back: `git checkout <previous commit>`, then steps 3 and 5 again.
