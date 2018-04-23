python -m venv env
"env\Scripts\pip" install pypiwin32
"env\Scripts\python" "env\Scripts\pywin32_postinstall.py" -install
"env\Scripts\easy_install" djangorestframework
"env\Scripts\easy_install" markdown
"env\Scripts\easy_install" django-filter
"env\Scripts\easy_install" msgpack
"env\Scripts\easy_install" channels
"env\Scripts\easy_install" channels_redis
"env\Scripts\easy_install" redis
"env\Scripts\easy_install" fleep

"env\Scripts\pip" install -r requirements.txt