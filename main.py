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
    response = requests.post(settings.SLACK_WEBHOOK_URL, json={
        'text': __get_formatted_message(request.json)
    })
    response.raise_for_status()
    return {'status': 'ok'}


def __get_formatted_message(json):
    result = 'New event arrived at ' + json['id']['time'] + '!\n\n'
    for event in json['events']:
        result += '*' + event['name'] + '*\n'
        for param in event['parameters']:
            if param['name'] == 'organizer_email':
                result += 'Organizer: ' + param['value'] + '\n'
            elif param['name'] == 'meeting_code':
                result += 'Meeting Code: ' + param['value'] + '\n'
    return result


def __notify(args):
    app.run(debug=True)


def __get_google_service():
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
    return build('admin', 'reports_v1', credentials=creds)


def __register(args):
    response = __get_google_service().activities().watch(
        userKey='all',
        applicationName='meet',
        body={
            'address': settings.CALLBACK_URL,
            'type': 'web_hook',
            'id': ID
        }
    ).execute()
    print('ID: ' + response['id'] + '\nResource ID: ' + response['resourceId'])


def __unregister(args):
    channels = __get_google_service().channels()
    # Admin SDK returns wrong URL.
    # https://github.com/googleapis/google-api-python-client/issues/403
    # noinspection PyProtectedMember
    channels._baseUrl = channels._baseUrl.replace('/admin/reports/v1', '')
    channels.stop(
        body={
            'id': args.id,
            'resourceId': args.resource_id
        }
    ).execute()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_register = subparsers.add_parser('register')
    parser_register.set_defaults(func=__register)

    parser_unregister = subparsers.add_parser('unregister')
    parser_unregister.add_argument('--id', type=str, help='ID')
    parser_unregister.add_argument('--resource-id', type=str, help='Resource ID')
    parser_unregister.set_defaults(func=__unregister)

    parser_notify = subparsers.add_parser('notify')
    parser_notify.set_defaults(func=__notify)

    args = parser.parse_args()
    args.func(args)
