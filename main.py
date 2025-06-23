from flask import Flask, render_template, request
from flask_session import Session
import backend


app = Flask(__name__)
app.secret_key = 'a8f$2k@1!z9x7v3q6b0p4w5e2r8t1y6u'

# Configure server-side sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    return backend.handle_upload(request)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    return backend.handle_chat(request)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
