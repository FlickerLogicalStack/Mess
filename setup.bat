"env\Scripts\python" "manage.py" makemigrations
"env\Scripts\python" "manage.py" migrate
"env\Scripts\python" "manage.py" migrate --run-syncdb

"env\Scripts\python.exe" "manage.py" createsuperuser --username admin --email example@email.com