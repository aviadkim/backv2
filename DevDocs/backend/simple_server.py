from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/api/health')
def health():
    return '{"status": "healthy"}'

if __name__ == '__main__':
    print("Starting minimal Flask server on http://localhost:24125")
    app.run(host='0.0.0.0', port=24125)
