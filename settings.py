import os

from dotenv import load_dotenv

load_dotenv()

CALLBACK_URL = os.getenv('CALLBACK_URL')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')
