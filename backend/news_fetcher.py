import os
import re
import requests
import feedparser
from dotenv import load_dotenv

# LangChain
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper, WikipediaAPIWrapper

load_dotenv()

# ── RSS FEEDS ────────────────────────────────────────────────
RSS_FEEDS = {
    "BBC": "http://feeds.bbci.co.uk/news/rss.xml",
    "Reuters": "https://feeds.reuters.com/reuters/topNews",
    "The Hindu": "https://www.thehindu.com/feeder/default.rss",
    "TOI": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
    "NDTV": "https://feeds.feedburner.com/ndtvnews-top-stories",
    "Indian Express": "https://indianexpress.com/feed/",
    "TechCrunch": "https://techcrunch.com/feed/",
}

# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-zA-Z]+;|&#\d+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_domain(url: str) -> str:
    try:
        match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        if match:
            domain = match.group(1)
            domain = re.sub(r"\.(com|org|net|io|in|co\.in|co\.uk)$", "", domain)
            return domain.title()
    except:
        pass
    return "Web"


# ═══════════════════════════════════════════════════════════════
# DUCKDUCKGO (PRIMARY)
# ═══════════════════════════════════════════════════════════════

def fetch_from_duckduckgo(topic: str, max_results: int = 5) -> list:
    results = []
    try:
        wrapper = DuckDuckGoSearchAPIWrapper(
            max_results=max_results,
            time="m",
            region="wt-wt",
            source="news"
        )

        raw_results = wrapper.results(f"{topic} news", max_results=max_results)

        for r in raw_results:
            results.append({
                "title": clean_text(r.get("title", "")),
                "content": clean_text(r.get("snippet", "")),
                "url": r.get("link", ""),
                "source": extract_domain(r.get("link", ""))
            })

    except Exception as e:
        print(f"[DuckDuckGo Error] {e}")

    return results


# ═══════════════════════════════════════════════════════════════
# WIKIPEDIA
# ═══════════════════════════════════════════════════════════════

def fetch_from_wikipedia(topic: str) -> list:
    try:
        wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1200)
        tool = WikipediaQueryRun(api_wrapper=wrapper)
        content = tool.run(topic)

        if not content or len(content) < 50:
            return []

        return [{
            "title": f"{topic} — Overview",
            "content": clean_text(content),
            "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "source": "Wikipedia"
        }]

    except Exception as e:
        print(f"[Wikipedia Error] {e}")
        return []


# ═══════════════════════════════════════════════════════════════
# GNEWS
# ═══════════════════════════════════════════════════════════════

def fetch_from_gnews(topic: str, api_key: str, max_articles: int = 5) -> list:
    try:
        url = "https://gnews.io/api/v4/search"
        params = {
            "q": topic,
            "lang": "en",
            "max": max_articles,
            "apikey": api_key,
        }

        response = requests.get(url, params=params)
        articles = response.json().get("articles", [])

        return [{
            "title": a["title"],
            "content": a.get("description", ""),
            "url": a["url"],
            "source": a["source"]["name"]
        } for a in articles]

    except Exception as e:
        print(f"[GNews Error] {e}")
        return []


# ═══════════════════════════════════════════════════════════════
# RSS
# ═══════════════════════════════════════════════════════════════

def fetch_from_rss(topic: str, max_articles: int = 5) -> list:
    results = []

    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:5]:
                if topic.lower() in entry.title.lower():
                    results.append({
                        "title": clean_text(entry.title),
                        "content": clean_text(entry.summary),
                        "url": entry.link,
                        "source": source
                    })

        except:
            continue

    return results[:max_articles]


# ═══════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════

def fetch_news(
    topic: str,
    api_key: str = None,
    max_articles: int = 5,
    source: str = "auto",
    include_wikipedia: bool = True   # ✅ FIX ADDED
) -> list:

    articles = []

    print(f"\n[NewsAI] Fetching: {topic}")

    # 1. DuckDuckGo
    articles.extend(fetch_from_duckduckgo(topic, max_articles))

    # 2. GNews
    if api_key:
        articles.extend(fetch_from_gnews(topic, api_key, 3))

    # 3. RSS fallback
    if len(articles) < 3:
        articles.extend(fetch_from_rss(topic, max_articles))

    # 4. Wikipedia (controlled now)
    if include_wikipedia:
        wiki = fetch_from_wikipedia(topic)
        articles = wiki + articles

    # Deduplicate
    seen = set()
    unique = []

    for a in articles:
        key = a["title"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(a)

    print(f"[NewsAI] Total articles: {len(unique)}\n")

    return unique