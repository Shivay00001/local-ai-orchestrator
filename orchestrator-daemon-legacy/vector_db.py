import chromadb
from chromadb.utils import embedding_functions
import os

class VectorDB:
    def __init__(self, persist_directory: str):
        self.client = chromadb.PersistentClient(path=persist_directory)
        # Use a local embedding model (Sentence Transformers)
        # 'all-MiniLM-L6-v2' is small, fast, and runs entirely locally
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="project_context",
            embedding_function=self.embedding_fn
        )

    def add_documents(self, chunks: list, metadatas: list, ids: list):
        """Adds or updates documents in the collection."""
        self.collection.upsert(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 5):
        """Searches for relevant chunks."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

    def clear(self):
        """Resets the collection."""
        try:
            self.client.delete_collection("project_context")
            self.collection = self.client.get_or_create_collection(
                name="project_context",
                embedding_function=self.embedding_fn
            )
        except Exception:
            pass
