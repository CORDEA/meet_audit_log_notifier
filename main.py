import argparse
import os
import pickle
from uuid import uuid4

import requests
from flask import Flask, request, render_template
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import settings

TOKEN_PICKLE = 'token.pickle'
ID = str(uuid4())
SCOPES = ['https://www.googleapis.com/auth/admin.reports.audit.readonly']

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/events', methods=['POST'])
def events():
    headers = request.headers
    if headers['X-Goog-Resource-State'] == 'sync':
        return {'status': 'ok'}

    json = request.json
    print(json)
    print(headers)
    response = requests.post(settings.SLACK_WEBHOOK_URL, data={
        'text': json
    })
    response.raise_for_status()
    return {'status': 'ok'}


def __notify(args):
    app.run(debug=True)


def __register(args):
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
    response = service.activities().watch(
        userKey='all',
        applicationName='meet',
        body={
            'address': settings.CALLBACK_URL,
            'type': 'web_hook',
            'id': ID
        }
    ).execute()
    print(response.resourceUri)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_register = subparsers.add_parser('register')
    parser_register.set_defaults(func=__register)
    parser_notify = subparsers.add_parser('notify')
    parser_notify.set_defaults(func=__notify)
    args = parser.parse_args()
    args.func(args)
