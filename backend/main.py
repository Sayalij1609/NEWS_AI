from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from news_fetcher import fetch_news
from ai_agent import analyze_article
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class QueryRequest(BaseModel):
    topic: str
    num_articles: int = 5

@app.post("/analyze")
def analyze_news(req: QueryRequest):
    api_key = os.getenv("GNEWS_API_KEY")
    articles = fetch_news(req.topic, api_key, req.num_articles)
    if not articles:
        return {"topic": req.topic, "results": [], "message": "No articles found."}
    results = []
    for article in articles:
        content = article.get("content") or article.get("title", "")
        analysis = analyze_article(article["title"], content)
        results.append({
            "title": article["title"],
            "url": article["url"],
            "source": article.get("source", "RSS"),
            "analysis": analysis
        })
    return {"topic": req.topic, "total": len(results), "results": results}