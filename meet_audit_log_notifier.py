import argparse

from flask import Flask, request

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
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--register', type=str, help='Register callback URL.')
    args = parser.parse_args()
    if args.register:
        __register(args.register)
    else:
        app.run(debug=True)
