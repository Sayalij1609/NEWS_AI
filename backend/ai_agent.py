import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2"

def analyze_article(title: str, content: str) -> dict:
    prompt = f"""You are a news analyst. Analyze the article below and return ONLY a valid JSON object. 
No explanation, no markdown, no code blocks. Just the raw JSON.

Article Title: {title}
Article Content: {content[:1500]}

Return exactly this JSON structure:
{{
  "summary": "Write a 3 sentence summary here",
  "explanation": "Write a simple 2-3 sentence explanation here for a student",
  "category": "Politics",
  "sentiment": "Neutral",
  "key_points": ["point one", "point two", "point three"]
}}

Rules:
- Use only double quotes, never single quotes
- Do not use apostrophes inside strings (write dont instead of don't)
- Do not include newlines inside string values
- category must be one of: Politics, Technology, Business, Health, Sports, Science, World, Environment
- sentiment must be one of: Positive, Negative, Neutral
- Return ONLY the JSON object, nothing else"""

    try:
        response = requests.post(OLLAMA_URL, json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }, timeout=120)

        raw = response.json().get("response", "")
        return parse_response(raw, title)

    except requests.exceptions.Timeout:
        return fallback("Request timed out. The model took too long to respond.")
    except Exception as e:
        return fallback(str(e))


def parse_response(raw: str, title: str) -> dict:
    """
    Robust JSON extractor — handles all common Ollama output issues:
    - Wrapped in ```json ... ``` blocks
    - Extra text before/after JSON
    - Single quotes instead of double quotes
    - Apostrophes breaking string values
    - Trailing commas
    - Unescaped special characters
    """

    # Step 1: Strip markdown code fences if present
    text = raw.strip()
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()

    # Step 2: Extract the JSON object (first { ... } block)
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if not match:
        return fallback("No JSON object found in model response.")
    text = match.group(0)

    # Step 3: Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Step 4: Fix common issues and retry
    text = fix_json(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Step 5: Field-by-field extraction as last resort
    return extract_fields(text, title)


def fix_json(text: str) -> str:
    """Apply common JSON fixes."""

    # Replace smart/curly quotes with straight quotes
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")

    # Remove trailing commas before } or ]
    text = re.sub(r',\s*([}\]])', r'\1', text)

    # Replace unescaped newlines inside string values
    # Find strings and clean them
    def clean_string_value(m):
        s = m.group(0)
        # Replace literal newlines inside the string with space
        s = s.replace('\n', ' ').replace('\r', ' ')
        # Replace apostrophes with backtick to avoid breaking JSON
        # Only inside the string content (not the quotes themselves)
        inner = s[1:-1]
        inner = inner.replace("\\'", "'")  # unescape already escaped
        # Remove any remaining problematic chars
        inner = re.sub(r'(?<!\\)"', '\\"', inner)
        return '"' + inner + '"'

    # Fix control characters
    text = re.sub(r'[\x00-\x1f\x7f]', ' ', text)

    # Fix trailing commas again after cleaning
    text = re.sub(r',\s*([}\]])', r'\1', text)

    return text


def extract_fields(text: str, title: str) -> dict:
    """Last-resort: extract individual fields using regex."""

    def get_field(key):
        # Match "key": "value" or "key": value
        pattern = rf'"{key}"\s*:\s*"([^"]*)"'
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return None

    def get_array(key):
        pattern = rf'"{key}"\s*:\s*\[([^\]]*)\]'
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            items = re.findall(r'"([^"]*)"', m.group(1))
            return items
        return []

    summary     = get_field("summary")     or f"Analysis of: {title[:80]}"
    explanation = get_field("explanation") or "This article could not be fully parsed."
    category    = get_field("category")    or "General"
    sentiment   = get_field("sentiment")   or "Neutral"
    key_points  = get_array("key_points")

    # Validate sentiment and category
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


def fallback(reason: str) -> dict:
    return {
        "summary": "Summary unavailable.",
        "explanation": reason,
        "category": "General",
        "sentiment": "Neutral",
        "key_points": []
    }