import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"


def analyze_article(title: str, content: str) -> dict:
    """
    Analyze article using Ollama LLM.
    Handles both news + Wikipedia intelligently.
    """

    # 🔍 Detect Wikipedia / informational content
    is_wikipedia = "wikipedia" in title.lower() or "overview" in title.lower()

    # 🎯 Dynamic instruction
    if is_wikipedia:
        extra_instruction = "Explain the concept clearly like teaching a beginner student."
    else:
        extra_instruction = "Focus on latest updates, events, and key developments."

    prompt = f"""
You are an intelligent AI news analyst.

Analyze the given article and return a structured JSON.

Article Title: {title}
Article Content: {content[:3000]}

Instructions:
- {extra_instruction}
- Keep answers simple, clear, and meaningful
- Do not include unnecessary text

Return ONLY this JSON format:

{{
  "summary": "Clear 3 sentence summary",
  "explanation": "Simple explanation in easy language",
  "category": "Technology",
  "sentiment": "Neutral",
  "key_points": ["point one", "point two", "point three"]
}}
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,   # ✅ improved quality
                    "top_p": 0.9
                }
            },
            timeout=120
        )

        raw = response.json().get("response", "")
        return parse_response(raw, title)

    except requests.exceptions.Timeout:
        return fallback("Request timed out. The model took too long.")
    except Exception as e:
        return fallback(str(e))


# ═══════════════════════════════════════════════════════════════
# RESPONSE PARSER (ROBUST)
# ═══════════════════════════════════════════════════════════════

def parse_response(raw: str, title: str) -> dict:
    text = raw.strip()

    # Remove markdown code blocks
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()

    # Extract JSON object
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return fallback("No JSON found in response.")
    text = match.group(0)

    # Try parsing directly
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try fixing JSON
    text = fix_json(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Last fallback
    return extract_fields(text, title)


# ═══════════════════════════════════════════════════════════════
# JSON FIXER
# ═══════════════════════════════════════════════════════════════

def fix_json(text: str) -> str:
    # Fix quotes
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")

    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f]', ' ', text)

    # Remove trailing commas
    text = re.sub(r',\s*([}\]])', r'\1', text)

    return text


# ═══════════════════════════════════════════════════════════════
# FIELD EXTRACTION (LAST RESORT)
# ═══════════════════════════════════════════════════════════════

def extract_fields(text: str, title: str) -> dict:

    def get_field(key):
        pattern = rf'"{key}"\s*:\s*"([^"]*)"'
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    def get_array(key):
        pattern = rf'"{key}"\s*:\s*\[([^\]]*)\]'
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            return re.findall(r'"([^"]*)"', m.group(1))
        return []

    summary = get_field("summary") or f"Analysis of: {title[:80]}"
    explanation = get_field("explanation") or "Explanation unavailable."
    category = get_field("category") or "General"
    sentiment = get_field("sentiment") or "Neutral"
    key_points = get_array("key_points")

    # Validate values
    valid_sentiments = ["Positive", "Negative", "Neutral"]
    valid_categories = ["Politics", "Technology", "Business", "Health",
                        "Sports", "Science", "World", "Environment", "General"]

    if sentiment not in valid_sentiments:
        sentiment = "Neutral"
    if category not in valid_categories:
        category = "General"

    return {
        "summary": summary,
        "explanation": explanation,
        "category": category,
        "sentiment": sentiment,
        "key_points": key_points
    }


# ═══════════════════════════════════════════════════════════════
# FALLBACK
# ═══════════════════════════════════════════════════════════════

def fallback(reason: str) -> dict:
    return {
        "summary": "Summary unavailable.",
        "explanation": reason,
        "category": "General",
        "sentiment": "Neutral",
        "key_points": []
    }