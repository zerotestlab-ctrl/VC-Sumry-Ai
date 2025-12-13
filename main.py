from flask import Flask, request, jsonify
import PyPDF2
import requests
import os

app = Flask(__name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# ------------------------
# PDF TEXT EXTRACTION
# ------------------------
def extract_pdf_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


# ------------------------
# AI SUMMARY USING GROQ
# ------------------------
def ai_summary(pdf_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an expert VC analyst."},
            {"role": "user", "content": f"Summarize this pitch deck:\n\n{pdf_text}"}
        ]
    }

    response = requests.post(url, json=payload, headers={
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    })

    return response.json()["choices"][0]["message"]["content"]


# ------------------------
# SIMPLE FOUNDER VERIFICATION
# ------------------------
def simple_founder_lookup(name):
    # Not detailed scraping — only a simple quick lookup.
    query = f"{name} LinkedIn startup founder"
    search_url = f"https://ddg-api.herokuapp.com/search?q={query}"

    try:
        r = requests.get(search_url).json()
        return r[:3]  # Return top 3 results
    except:
        return [{"error": "lookup failed"}]


# ------------------------
# INVESTMENT MEMO GENERATION
# ------------------------
def generate_memo(summary, founder_data):
    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a professional VC investment analyst."},
            {"role": "user", "content": f"""
Generate a structured investment memo based on:

Summary: {summary}
Founder Info: {founder_data}

Include:
- Company overview
- Problem
- Solution
- Market
- Traction
- Risks
- Red Flags
- Verdict (Invest / Pass)
            """}
        ]
    }

    response = requests.post(url, json=payload, headers={
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    })

    return response.json()["choices"][0]["message"]["content"]


# ------------------------
# API ENDPOINTS
# ------------------------

@app.route("/analyze", methods=["POST"])
def analyze():
    pdf = request.files["file"]
    founder = request.form.get("founder")

    # 1. Extract PDF text
    pdf_text = extract_pdf_text(pdf)

    # 2. Generate summary
    summary = ai_summary(pdf_text)

    # 3. Founder Lookup
    founder_data = simple_founder_lookup(founder)

    # 4. Memo
    memo = generate_memo(summary, founder_data)

    return jsonify({
        "summary": summary,
        "founder_data": founder_data,
        "memo": memo
    })


@app.route("/")
def home():
    return "VC AI Backend Running!"


app.run(host="0.0.0.0", port=8080)