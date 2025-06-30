import os
from dotenv import load_dotenv

load_dotenv()

from src.server_instance import server
# from src.extensions import scheduler

app = server  # This is what Gunicorn will look for

# Optionally start scheduler if not running
# if not scheduler.running:
#     scheduler.start()
