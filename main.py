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
# VC MEMO + FOUNDER SIGNALS
# -------------------------
def generate_vc_analysis(startup_text, founder_info):
    if not GROQ_API_KEY:
        return "GROQ_API_KEY is missing in environment variables."

    url = "https://api.groq.com/openai/v1/chat/completions"

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": "You are a top-tier venture capital investment analyst."
            },
            {
                "role": "user",
                "content": f"""
You are writing an internal VC investment memo.

Startup Description:
{startup_text}

Founder / Team Signals (provided, may be incomplete):
{founder_info}

Instructions:
- Infer founder/team qualifications ONLY from provided signals
- Do NOT claim verification
- Clearly state uncertainty when data is missing
- Think like a cautious VC

Produce these sections:

1. Company Overview
2. Problem
3. Solution
4. Market & Opportunity
5. Business Model
6. Founder & Team Signals
7. Strengths
8. Risks
9. Red Flags
10. Overall Verdict (Invest / Pass / Needs More Data)
"""
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
    except Exception as e:
        return f"Request error: {str(e)}"

    if response.status_code != 200:
        return f"Groq API error {response.status_code}: {response.text}"

    return response.json()["choices"][0]["message"]["content"]

# -------------------------
# API ENDPOINT
# -------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    if not data or "startup_text" not in data:
        return jsonify({"error": "No startup description provided"}), 400

    startup_text = data["startup_text"].strip()

    if not startup_text:
        return jsonify({"error": "Empty startup description"}), 400

    founder_info = f"""
Founder Name: {data.get("founder_name", "Not provided")}
LinkedIn: {data.get("linkedin", "Not provided")}
GitHub: {data.get("github", "Not provided")}
Twitter/X: {data.get("twitter", "Not provided")}
Team Background: {data.get("team_background", "Not provided")}
"""

    memo = generate_vc_analysis(startup_text, founder_info)

    return jsonify({
        "memo": memo
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
