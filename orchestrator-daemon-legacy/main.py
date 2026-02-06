from fastapi import FastAPI, HTTPException
import logging
from hardware import HardwareDetector
from models import ModelSelector, ModelTier
from ollama import OllamaManager
from indexer import ProjectIndexer
from vector_db import VectorDB
import os
import uvicorn
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("orchestrator-daemon")

app = FastAPI(title="Local AI Orchestrator Core Daemon")

# Global instances for indexer/db
# Persistence in the same scratch dir
DB_PATH = "C:\\Users\\shiva\\Wait_Actually_Detect_Proper_Path" # Fixing this below
DB_PATH = os.path.join(os.getcwd(), "vector_storage")
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

vdb = VectorDB(DB_PATH)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "orchestrator-daemon"}

@app.get("/v1/system/hardware")
async def get_hardware():
    try:
        hw_info = HardwareDetector.get_system_info()
        return hw_info
    except Exception as e:
        logger.error(f"Hardware detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/system/recommendation")
async def get_recommendation():
    try:
        hw_info = HardwareDetector.get_system_info()
        tier = ModelSelector.select_best_tier(hw_info)
        model = ModelSelector.get_model_for_tier(tier)
        return {
            "tier": tier.value,
            "recommended_model": model,
            "hw_summary": {
                "ram": hw_info["total_ram_gb"],
                "cpu": hw_info["cpu_cores"]
            }
        }
    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/system/ollama")
async def get_ollama_status():
    installed = await OllamaManager.check_installation()
    return {"installed": installed, "url": OllamaManager.BASE_URL}

@app.post("/v1/models/prepare")
async def prepare_recommended_model():
    """Detects best model and pulls it."""
    hw_info = HardwareDetector.get_system_info()
    tier = ModelSelector.select_best_tier(hw_info)
    model = ModelSelector.get_model_for_tier(tier)
    
    success = await OllamaManager.pull_model(model)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to pull {model}")
    return {"status": "pulled", "model": model}

@app.post("/v1/models/load")
async def load_model(model: str):
    success = await OllamaManager.start_model(model)
    return {"status": "loaded" if success else "failed"}

@app.post("/v1/index/folder")
async def index_folder(payload: dict):
    folder_path = payload.get("path")
    if not folder_path or not os.path.exists(folder_path):
        raise HTTPException(status_code=400, detail="Invalid folder path")
    
    logger.info(f"Indexing folder: {folder_path}")
    indexer = ProjectIndexer(folder_path)
    files = indexer.scan_project()
    
    total_chunks = 0
    for file_data in files:
        chunks = indexer.chunk_content(file_data["content"])
        if not chunks:
            continue
            
        metadatas = [{"path": file_data["path"], "type": "code"} for _ in chunks]
        ids = [f"{file_data['path']}_{i}" for i in range(len(chunks))]
        
        vdb.add_documents(chunks, metadatas, ids)
        total_chunks += len(chunks)
        
    return {"status": "indexed", "files_found": len(files), "total_chunks": total_chunks}

@app.post("/v1/query/context")
async def query_context(payload: dict):
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Missing query")
        
    results = vdb.query(query, n_results=5)
    
    # Format context for Ollama
    context_text = "\n\n".join(results['documents'][0])
    
    if not context_text.strip():
        return {"answer": "Unknown", "context": []}
        
    # Get recommended model
    hw_info = HardwareDetector.get_system_info()
    tier = ModelSelector.select_best_tier(hw_info)
    model_name = ModelSelector.get_model_for_tier(tier)
    
    # Prompt construction
    prompt = f"""Use the following context to answer the question. If the answer is not in the context, say 'Unknown'.
    
    CONTEXT:
    {context_text}
    
    QUESTION: {query}
    
    ANSWER:"""
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{OllamaManager.BASE_URL}/api/generate", json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            })
            data = response.json()
            return {
                "answer": data.get("response", "Unknown"),
                "context": results['metadatas'][0],
                "model_used": model_name
            }
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return {"answer": "Error during inference", "error": str(e)}

if __name__ == "__main__":
    logger.info("Starting Core Daemon on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
