from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
import time

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# -------------------------
# SIMPLE USAGE LIMIT (IP-BASED)
# -------------------------
USAGE_LIMIT = 3
usage_store = {}

def check_usage(ip):
    now = time.time()

    if ip not in usage_store:
        usage_store[ip] = {"count": 0, "reset": now + 86400}

    if now > usage_store[ip]["reset"]:
        usage_store[ip] = {"count": 0, "reset": now + 86400}

    if usage_store[ip]["count"] >= USAGE_LIMIT:
        return False

    usage_store[ip]["count"] += 1
    return True

# -------------------------
# TEMP FEEDBACK STORAGE (MVP)
# -------------------------
feedback_store = []
founder_feedback_store = []

# -------------------------
# HEALTH CHECK
# -------------------------
@app.route("/")
def home():
    return "VC AI Backend Running!"

# -------------------------
# VC ANALYSIS
# -------------------------
def generate_vc_analysis(startup_text, founder_info):
    url = "https://api.groq.com/openai/v1/chat/completions"

    payload = {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "You are a cautious, professional venture capital analyst."
            },
            {
                "role": "user",
                "content": f"""
Respond ONLY with valid JSON.

Return EXACT structure:

{{
  "company_overview": "",
  "problem": "",
  "solution": "",
  "market": "",
  "business_model": "",
  "founder_team_signals": "",
  "strengths": "",
  "risks": "",
  "red_flags": "",
  "verdict": "Invest / Pass / Needs More Data",
  "analysis_disclaimer": "This is an inferred analysis, not verification."
}}

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

    response = requests.post(url, json=payload, headers=headers, timeout=20)

    raw = response.json()["choices"][0]["message"]["content"]

    try:
        return json.loads(raw)
    except:
        return {"error": "Invalid AI output", "raw": raw}

# -------------------------
# ANALYZE ENDPOINT
# -------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    ip = request.remote_addr

    if not check_usage(ip):
        return jsonify({
            "error": "Usage limit reached",
            "message": "Daily limit reached. Join waitlist for extended access."
        }), 429

    data = request.get_json()
    startup_text = data.get("startup_text", "").strip()

    if not startup_text:
        return jsonify({"error": "Startup description required"}), 400

    founder_info = f"""
Founder: {data.get("founder_name", "Not provided")}
LinkedIn: {data.get("linkedin", "Not provided")}
GitHub: {data.get("github", "Not provided")}
"""

    result = generate_vc_analysis(startup_text, founder_info)
    return jsonify(result)

# -------------------------
# VC FEEDBACK (POST-ANALYSIS)
# -------------------------
@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()
    feedback_store.append({
        "timestamp": time.time(),
        "rating": data.get("rating"),
        "comment": data.get("comment")
    })
    return jsonify({"status": "Feedback received"})

# -------------------------
# FOUNDER IMPROVEMENT FEEDBACK
# -------------------------
@app.route("/founder-feedback", methods=["POST"])
def founder_feedback():
    data = request.get_json()
    founder_feedback_store.append({
        "timestamp": time.time(),
        "decision": data.get("decision"),
        "reason": data.get("reason"),
        "improvements": data.get("improvements")
    })
    return jsonify({"status": "Founder feedback sent"})

# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
