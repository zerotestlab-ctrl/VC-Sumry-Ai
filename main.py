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

# -------------------------
# INVESTMENT MEMO GENERATOR
# -------------------------
def generate_investment_memo(text):
    url = "https://api.groq.com/openai/v1/chat/completions"

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {
                "role": "system",
                "content": "You are a top-tier venture capital investment analyst."
            },
            {
                "role": "user",
                "content": f"""
You are writing an internal VC investment memo.

Based ONLY on the startup description below, generate a clear, structured investment memo with the following sections:

1. Company Overview
2. Problem
3. Solution
4. Target Market & Size (estimate if needed)
5. Business Model
6. Traction / Signals (infer if early)
7. Strengths
8. Risks
9. Red Flags
10. Overall Verdict (Invest / Pass / Needs More Data)

Startup description:
{text}
"""
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        return "Failed to generate memo. Please try again."

    return response.json()["choices"][0]["message"]["content"]

# -------------------------
# API ENDPOINT
# -------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    if not data or "text" not in data:
        return jsonify({"error": "No input provided"}), 400

    text = data["text"].strip()

    if not text:
        return jsonify({"error": "Empty description"}), 400

    memo = generate_investment_memo(text)

    return jsonify({
        "summary": memo
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
