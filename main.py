from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json

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
        return {"error": "GROQ_API_KEY is missing in environment variables."}

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
You must respond ONLY in valid JSON.
Do NOT include markdown.
Do NOT include commentary outside JSON.

Return this exact JSON structure:

{{
  "company_overview": "",
  "problem": "",
  "solution": "",
  "market_opportunity": "",
  "business_model": "",
  "founder_team_signals": "",
  "strengths": "",
  "risks": "",
  "red_flags": "",
  "verdict": ""
}}

Rules:
- Write clearly and professionally
- Infer cautiously
- State uncertainty where appropriate
- Think like a real VC

Startup Description:
{startup_text}

Founder / Team Signals:
{founder_info}
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
        return {"error": f"Request error: {str(e)}"}

    if response.status_code != 200:
        return {
            "error": f"Groq API error {response.status_code}",
            "details": response.text
        }

    raw_output = response.json()["choices"][0]["message"]["content"]

    try:
        return json.loads(raw_output)
    except:
        return {
            "error": "AI returned invalid JSON",
            "raw_output": raw_output
        }

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

    result = generate_vc_analysis(startup_text, founder_info)

    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
