from flask import Flask, render_template, request
import backend

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    return backend.handle_upload(request)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
