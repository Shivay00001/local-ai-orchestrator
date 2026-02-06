import uvicorn
from fastapi import FastAPI
from src.api.routes import router as api_router

app = FastAPI(
    title="Local AI Orchestrator - Core Daemon",
    description="Privacy-first, hardware-aware local AI orchestration.",
    version="0.1.0"
)

# Register routes
app.include_router(api_router)

@app.get("/")
def root():
    return {"status": "running", "service": "Core Daemon"}

if __name__ == "__main__":
    # Localhost ONLY - strict requirement
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
