install:
	pip3 install virtualenv && virtualenv venv -p python3 && ./venv/bin/pip install -r requirements.txt

setup:
	./venv/bin/python manage.py migrate && \
	./venv/bin/python manage.py migrate --run-syncdb && \
	./venv/bin/python manage.py createsuperuser --username admin --email example@email.com

run:
	./venv/bin/python manage.py runserver