"""Vector store backed by ChromaDB + sentence-transformers.

Heavy embedding dependencies (chromadb, sentence-transformers/torch) are
imported LAZILY inside VectorStore.__init__, so importing this module never
requires them. They are only needed when VectorStore is actually constructed
(by the /project/index, /project/query, /agent/task endpoints).
"""
from typing import List, Dict

EMBED_DEPS_ERROR = (
    "Embedding dependencies are not installed (chromadb, sentence-transformers, torch). "
    "Install them with: pip install -r requirements-embeddings.txt"
)


class VectorStore:
    def __init__(self, persist_path: str = "./vector_db"):
        try:
            import chromadb
            from chromadb.config import Settings
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(f"{EMBED_DEPS_ERROR} (original error: {e})") from e

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
