"env\Scripts\python" "manage.py" makemigrations core
"env\Scripts\python" "manage.py" makemigrations api
"env\Scripts\python" "manage.py" makemigrations web

"env\Scripts\python" manage.py migrate --fake-initial

"env\Scripts\python" "manage.py" makemigrations
"env\Scripts\python" "manage.py" migrate
"env\Scripts\python" "manage.py" migrate --run-syncdb
pause