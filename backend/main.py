from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from news_fetcher import fetch_news
from ai_agent import analyze_article
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="NewsAI Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class QueryRequest(BaseModel):
    topic: str
    num_articles: int = 5
    source: str = "rss"
    include_wikipedia: bool = True   # ✅ keep only this


@app.get("/")
def root():
    return {"message": "NewsAI Agent is running"}


@app.post("/analyze")
def analyze_news(req: QueryRequest):
    api_key = os.getenv("GNEWS_API_KEY")

    articles = fetch_news(
        topic=req.topic,
        api_key=api_key,
        max_articles=req.num_articles,
        source=req.source,
        include_wikipedia=req.include_wikipedia   # ✅ valid now
    )

    if not articles:
        return {
            "topic": req.topic,
            "total": 0,
            "results": [],
            "message": "No articles found. Try a different topic."
        }

    results = []
    for article in articles:
        content = article.get("content") or article.get("title", "")
        analysis = analyze_article(article["title"], content)

        results.append({
            "title": article["title"],
            "url": article["url"],
            "source": article.get("source", "Web"),
            "analysis": analysis
        })

    return {
        "topic": req.topic,
        "total": len(results),
        "results": results
    }