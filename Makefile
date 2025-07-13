run:
	gunicorn --worker-class eventlet -w 2 -b 0.0.0.0:5000 wsgi:app --access-logfile - --log-level debug

online:
	ngrok http --domain=hideously-patient-dolphin.ngrok-free.app 5000
