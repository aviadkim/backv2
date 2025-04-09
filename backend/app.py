from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/render', methods=['POST'])
def render_markdown():
    data = request.json
    markdown_text = data.get('text', '')
    
    # This is a simple mock renderer
    # In a real application, this would convert markdown to HTML
    html = f"<div>{markdown_text}</div>"
    
    return jsonify({"html": html})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=24126, debug=True)
