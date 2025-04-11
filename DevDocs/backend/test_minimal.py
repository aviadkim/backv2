import os
from flask import Flask

# Disable .env file loading which is causing the UnicodeDecodeError
os.environ["FLASK_SKIP_DOTENV"] = "1"

app = Flask(__name__)

@app.route('/')
def home():
    return "Minimal Flask App is working!"

@app.route('/test')
def test():
    return "Test endpoint is working!"

if __name__ == '__main__':
    print("Starting minimal Flask app on port 24125...")
    print("Try accessing http://localhost:24125/")
    app.run(host='0.0.0.0', port=24125, debug=True)
