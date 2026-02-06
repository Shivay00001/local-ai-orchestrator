import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict

class VectorStore:
    def __init__(self, persist_path: str = "./vector_db"):
        self.client = chromadb.PersistentClient(path=persist_path, settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection("project_code")
        # Load local model (CPU optimized)
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

    def add_chunks(self, chunks: List[Dict]):
        """
        chunks: List of specific format from Chunker
        """
        if not chunks:
            return
            
        texts = [c["content"] for c in chunks]
        metadatas = [{
            "filepath": c["filepath"],
            "start_line": c["start_line"],
            "end_line": c["end_line"]
        } for c in chunks]
        ids = [f"{c['filepath']}:{c['start_line']}" for c in chunks]
        
        embeddings = self.model.encode(texts).tolist()
        
        self.collection.upsert(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def query_similar(self, query: str, n_results: int = 5) -> List[Dict]:
        query_embedding = self.model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        output = []
        if results["ids"]:
            for i in range(len(results["ids"][0])):
                output.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results["distances"] else 0.0
                })
        return output
