import argparse
import os
import pickle
from uuid import uuid4

from flask import Flask, request
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

TOKEN_PICKLE = 'token.pickle'
ID = uuid4()
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']

app = Flask(__name__)


@app.route('/')
def index():
    return 'Meet audio log notifier'


@app.route('/events', methods=['POST'])
def events():
    json = request.json
    headers = request.headers
    print(json)
    print(headers)


def __register(url):
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)
    service = build('admin', 'reports_v1', credentials=creds)
    response = service.watch(
        userKey='all',
        applicationName='meet',
        body={
            'address': url,
            'type': 'web_hook',
            'id': ID
        }
    )
    print(response.resouceUri)
    print(response.address)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--register', type=str, help='Register callback URL.')
    args = parser.parse_args()
    if args.register:
        __register(args.register)
    else:
        app.run(debug=True)
