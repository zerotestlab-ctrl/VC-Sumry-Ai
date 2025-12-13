from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

@app.route("/")
def home():
    return "VC AI Backend Running!"

def ai_summary(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a professional VC analyst."},
            {"role": "user", "content": f"""
Analyze this startup and produce a short investment-style summary:

{text}

Include:
- What the company does
- Market & problem
- Strengths
- Risks
- High-level verdict
            """}
        ]
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()["choices"][0]["message"]["content"]

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No input provided"}), 400

    summary = ai_summary(text)

    return jsonify({
        "summary": summary
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
