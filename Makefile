run:
	. venv/bin/activate && \
	gunicorn --worker-class eventlet -w 2 -b 172.21.224.217:5000 wsgi:app --access-logfile - --log-level debug
