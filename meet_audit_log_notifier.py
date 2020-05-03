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


if __name__ == '__main__':
    app.run(debug=True)
