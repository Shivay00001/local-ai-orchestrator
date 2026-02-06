from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from ..hardware.detection import detect_hardware
from ..models.selection import select_model_tier
from ..ollama.client import is_ollama_running, list_models

# Phase 2 Imports
from ..indexing.crawler import crawl_project
from ..indexing.chunker import chunk_file
from ..vector.store import VectorStore

router = APIRouter()
vector_store = VectorStore() # Global instance (singleton-ish)

class IndexRequest(BaseModel):
    path: str

class QueryRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5

def background_index_project(path: str):
    # This should be robust, handle errors, logs, etc.
    print(f"Starting index for {path}")
    chunks_batch = []
    
    for filepath in crawl_project(path):
        new_chunks = chunk_file(filepath)
        for c in new_chunks:
            chunks_batch.append({
                "filepath": c.filepath,
                "content": c.content,
                "start_line": c.start_line,
                "end_line": c.end_line
            })
            
            # Batch upsert
            if len(chunks_batch) >= 100:
                 vector_store.add_chunks(chunks_batch)
                 chunks_batch = []
                 
    if chunks_batch:
        vector_store.add_chunks(chunks_batch)
    print(f"Finished index for {path}")

@router.post("/project/index")
def index_project_endpoint(req: IndexRequest, bg_tasks: BackgroundTasks):
    bg_tasks.add_task(background_index_project, req.path)
    return {"status": "indexing_started", "path": req.path}

@router.post("/project/query")
def query_project_endpoint(req: QueryRequest):
    results = vector_store.query_similar(req.query, n_results=req.n_results)
    return {"results": results}

# Phase 3 Agent API
from ..agents.coordinator import AgentCoordinator
coordinator = AgentCoordinator()

class AgentTaskRequest(BaseModel):
    task: str

@router.post("/agent/task")
def agent_task_endpoint(req: AgentTaskRequest):
    response = coordinator.route_task(req.task)
    return {
        "agent": response.agent_name,
        "content": response.content,
        "metadata": response.metadata
    }

@router.get("/ollama/status")
def get_ollama_status():
    return {"running": is_ollama_running()}

@router.get("/ollama/models")
def get_ollama_models():
    if not is_ollama_running():
         raise HTTPException(status_code=503, detail="Ollama is not running")
    return list_models()

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/system/hardware")
def get_hardware():
    try:
        hw = detect_hardware()
        return hw
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/recommended")
def get_model_recommendation():
    try:
        hw = detect_hardware()
        rec = select_model_tier(hw)
        return rec
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
