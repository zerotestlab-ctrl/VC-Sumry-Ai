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
        return {"error": "GROQ_API_KEY missing"}

    url = "https://api.groq.com/openai/v1/chat/completions"

    payload = {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "You are a cautious, professional VC analyst."
            },
            {
                "role": "user",
                "content": f"""
Return ONLY valid JSON. No markdown. No explanations.

JSON format:
{{
  "company_overview": "...",
  "problem": "...",
  "solution": "...",
  "market": "...",
  "business_model": "...",
  "founder_team_signals": "...",
  "strengths": "...",
  "risks": "...",
  "red_flags": "...",
  "verdict": "Invest / Pass / Needs More Data"
}}

Rules:
- Be concise
- No speculation
- State uncertainty clearly

Startup description:
{startup_text}

Founder / Team signals:
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
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=15
        )
    except requests.exceptions.Timeout:
        return {"error": "Analysis timed out. Try a shorter description."}
    except Exception as e:
        return {"error": str(e)}

    if response.status_code != 200:
        return {
            "error": "Groq API failure",
            "details": response.text
        }

    raw = response.json()["choices"][0]["message"]["content"]

    try:
        return json.loads(raw)
    except:
        return {
            "error": "Invalid AI response",
            "raw_output": raw
        }

# -------------------------
# API ENDPOINT
# -------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    if not data or "startup_text" not in data:
        return jsonify({"error": "Startup description required"}), 400

    startup_text = data["startup_text"].strip()
    if not startup_text:
        return jsonify({"error": "Empty description"}), 400

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
