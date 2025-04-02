from fastapi import FastAPI
from routers import search
from src.discon_analyzer.router import router as discon_analyzer_router


app = FastAPI(title="Journal Search API", description="Find similar journals using Scopus API")

# Register Routers
app.include_router(search.router, prefix="/api", tags=["Search"])
app.include_router(discon_analyzer_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Journal Search API", 
        "docs" : "/docs"
        }
