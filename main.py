# main.py - Entry point for the DocuBridge Flask app
from flask import Flask, render_template, request
from flask_session import Session
import backend

# Initialize Flask app
app = Flask(__name__)
# Secret key for Flask session management
app.secret_key = 'a8f$2k@1!z9x7v3q6b0p4w5e2r8t1y6u'

# Configure server-side sessions to avoid cookie size limits
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Home page route: renders the upload form
@app.route('/')
def index():
    return render_template('index.html')

# Upload route: handles file upload and initial question
@app.route('/upload', methods=['POST'])
def upload():
    return backend.handle_upload(request)

# Chat route: handles chat UI and follow-up questions
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    return backend.handle_chat(request)

# Runs the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
