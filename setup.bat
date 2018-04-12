"venv\Scripts\python" "manage.py" makemigrations
"venv\Scripts\python" "manage.py" migrate
"venv\Scripts\python" "manage.py" migrate --run-syncdb

"venv\Scripts\python.exe" "manage.py" createsuperuser --username admin --email example@email.com