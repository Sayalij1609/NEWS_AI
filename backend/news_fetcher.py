import feedparser
import requests

RSS_FEEDS = {
    "BBC":     "http://feeds.bbci.co.uk/news/rss.xml",
    "Reuters": "https://feeds.reuters.com/reuters/topNews",
    "Hindu":   "https://www.thehindu.com/feeder/default.rss",
    "TOI":     "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
}

def fetch_from_rss(topic: str, max_articles: int = 5):
    results = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                if topic.lower() in title.lower() or topic.lower() in summary.lower():
                    results.append({
                        "title": title,
                        "content": summary,
                        "url": link,
                        "source": source
                    })
                if len(results) >= max_articles:
                    return results
        except Exception:
            continue
    return results[:max_articles]

def fetch_from_gnews(topic: str, api_key: str, max_articles: int = 5):
    url = "https://gnews.io/api/v4/search"
    params = {"q": topic, "lang": "en", "max": max_articles, "apikey": api_key}
    resp = requests.get(url, params=params, timeout=10)
    articles = resp.json().get("articles", [])
    return [
        {"title": a["title"], "content": a["description"], "url": a["url"], "source": a["source"]["name"]}
        for a in articles
    ]

def fetch_news(topic: str, api_key: str = None, max_articles: int = 5):
    if api_key:
        return fetch_from_gnews(topic, api_key, max_articles)
    return fetch_from_rss(topic, max_articles)