python -m venv venv
"venv\Scripts\pip" pypiwin32
"venv\Scripts\python" "venv\Scripts\pywin32_postinstall.py" -install
"venv\Scripts\easy_install" msgpack
"venv\Scripts\easy_install" channels
"venv\Scripts\easy_install" channels_redis
"venv\Scripts\easy_install" redis
"venv\Scripts\easy_install" fleep

"venv\Scripts\pip" install -r requirements.txt