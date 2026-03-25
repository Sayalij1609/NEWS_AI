from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
BACKEND_URL = "http://localhost:8000/analyze"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    topic = data.get("topic", "").strip()
    num = int(data.get("num_articles", 5))
    if not topic:
        return jsonify({"error": "Topic is required"}), 400
    try:
        resp = requests.post(
            BACKEND_URL,
            json={"topic": topic, "num_articles": num},
            timeout=180
        )
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)