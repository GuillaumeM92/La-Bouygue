# PurBeurreWeb
Repository for Project 8 from Openclassrooms cursus in Software Development

Website address : https://purbeurreweb.herokuapp.com/

## Project Description
This project is a web application built with **Django** to help users find healthier products to their favorite food.
The application is deployed on **Heroku**.

## Features
* Register
* Login
* Search a product
* Browse substitutes
* Add them to your favorites
* View your favorite products
* Access your Profile page
* Logout

## APIs
The following API was used in this project :
* [Open Food Facts](https://developers.google.com/maps/get-started/)

## Getting Started

1. Clone the repository:
```
git clone https://github.com/JN-Lab/OC-Pr8-OpenFoodFacts-App.git
```

When you are in your directory (root):

2. Set-up your virtual environment
```
python3 -m venv env
```

3. Activate your virtual environment:
```
source env/bin/activate
```

5. Install all necessary frameworks and libraries
```
pip install -r requirements.txt
```

6. Set-up your database in **settings.py** file

7. Go in purbeurre platform directory to have access to manage.py file to launch the initialisation of the database with the basic data:
```
./manage.py inject_db
```

8. Run the django local server:
```
./manage.py runserver
```

9. You go on your favorite browser and copy paste this url:
```
http://127.0.0.1:8000/
```

## Running the tests
To run all the tests:
```
coverage run --source='.' --omit='venv/*' ./manage.py test apps.purbeurreweb.tests apps.favorites.tests apps.users.tests
```
To view the report:
```
coverage report
```

## Deploying on Heroku
Download and install Heroku CLI
```
https://devcenter.heroku.com/articles/heroku-cli#download-and-install
```
or
```
sudo snap install --classic heroku
```

Create your Heroku app
```
heroku login
heroku apps:create --region eu yourappname
```
Create the pgsql DB to go along:
```
heroku addons:create heroku-postgresql:hobby-dev
```

Configure the environment variables
```
heroku config:set SECRET_KEY=yoursecretkey
heroku config:set EMAIL_USER=youruseremail
heroku config:set EMAIL_PASSWORD=youruserpassword
heroku config:set ENV=production
```

In your venv
```
pip install django-heroku
pip install gunicorn
```

In Django settings.py add:
```
import django_heroku
[...]
DEBUG = False if os.getenv("ENV", "development") == "production" else True
ALLOWED_HOSTS = [".herokuapp.com", "localhost", "127.0.0.1"]
[...]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
[...]
django_heroku.settings(locals())
```

Create a Procfile (make it point to your .wsgi file)
```
web: gunicorn config.wsgi --log-file -
```

Create requirements.txt
```
pip freeze > requirements.txt
```

Push to the Heroku remote
```
git add .
git commit -m "message"
git push heroku master
```

Setup the DB on Heroku
```
heroku run bash
python manage.py migrate
python manage.py createsuperuser
python manage.py inject_db 3
python manage.py collectstatic
```
NB: inject_db "3" is the number of pages to return, you can change this value if you want (1 page = 1000 products)

...

Done! =)

## Deploying on a VPS
Download and install Heroku CLI
```
https://devcenter.heroku.com/articles/heroku-cli#download-and-install
```
or
```
sudo snap install --classic heroku
```

Create your Heroku app
```
heroku login
heroku apps:create --region eu yourappname
```
Create the pgsql DB to go along:
```
heroku addons:create heroku-postgresql:hobby-dev
```

Configure the environment variables
```
heroku config:set SECRET_KEY=yoursecretkey
heroku config:set EMAIL_USER=youruseremail
heroku config:set EMAIL_PASSWORD=youruserpassword
heroku config:set ENV=production
```

In your venv
```
pip install django-heroku
pip install gunicorn
```

In Django settings.py add:
```
import django_heroku
[...]
DEBUG = False if os.getenv("ENV", "development") == "production" else True
ALLOWED_HOSTS = [".herokuapp.com", "localhost", "127.0.0.1"]
[...]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
[...]
django_heroku.settings(locals())
```

Create a Procfile (make it point to your .wsgi file)
```
web: gunicorn config.wsgi --log-file -
```

Create requirements.txt
```
pip freeze > requirements.txt
```

Push to the Heroku remote
```
git add .
git commit -m "message"
git push heroku master
```

Setup the DB on Heroku
```
heroku run bash
python manage.py migrate
python manage.py createsuperuser
python manage.py inject_db 3
python manage.py collectstatic
```
NB: inject_db "3" is the number of pages to return, you can change this value if you want (1 page = 1000 products)

...

Done! =)

## Built With
* Django
* psycopg2
* requests

## Deployed With
* Heroku
