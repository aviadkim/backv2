from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/health")
def health_check():
    return jsonify({"status": "healthy", "version": "0.1.0"})

@app.route("/api/documents")
def get_documents():
    # Placeholder for document retrieval
    return jsonify({"documents": []})

@app.route("/api/agents")
def list_agents():
    # Placeholder for agent listing
    return jsonify({"agents": []})

if __name__ == "__main__":
    app.run(debug=True)
