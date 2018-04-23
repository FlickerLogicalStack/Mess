# Mess
Django Web Messenger

###### (Sorry for my English)
## Installation
### Windows

* Download repo
* Run `install.bat`, it contains a few instalations throught `env\Scripts\pip.exe` (Yea I know about setuptools. I will fix it)
* Install [Redis](https://redis.io)
* Base config in `Mess\settings.py` using default redis port - `6379`
* Run `setup.bat`. It make migrations, apply it then `setup.bat` run `manage.py createsuperuser` and you must input username/email/password
* Default DB - default sqlite3
* Enter `SECRET_KEY` in `Mess\settings.py`
* #### Now you can run it!

### Linux
* Will be as soon as possible)

## Configurations
You can switch db on postgre (it works more faster):  
* document this lines
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
```

* undocument this lines

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mess_db',
        'USER' : 'postgres',
        'PASSWORD' : '',
        'HOST' : '127.0.0.1',
        'PORT' : '5432',
    }
}
```

* Create db `mess_db` by superuser (I heard that it is bad practice, will be fixed later)
* Then it must work
