import re
from typing import Dict, Type
from .base import BaseAgent, AgentResponse
from .implementations import CodeReaderAgent, RefactorAgent, TestWriterAgent, DocWriterAgent
from ..vector.store import VectorStore

class AgentCoordinator:
    def __init__(self):
        self.vector_store = VectorStore()
        self.agents: Dict[str, BaseAgent] = {
            "reader": CodeReaderAgent(),
            "refactor": RefactorAgent(),
            "test": TestWriterAgent(),
            "doc": DocWriterAgent()
        }

    def _classify_task(self, task: str) -> str:
        """
        Rule-based intent classification.
        """
        task_lower = task.lower()
        
        if any(w in task_lower for w in ["refactor", "optimize", "rewrite", "improve"]):
            return "refactor"
        if any(w in task_lower for w in ["test", "verify", "unittest", "pytest"]):
            return "test"
        if any(w in task_lower for w in ["doc", "explain", "readme", "comment"]):
            if "explain" in task_lower and len(task_lower.split()) > 3:
                return "reader" # "Explain how X works" -> Reader
            return "doc"
        
        # Default fallback
        return "reader"

    def route_task(self, task: str) -> AgentResponse:
        """
        1. Classify intent.
        2. Retrieve context (RAG).
        3. Dispatch to agent.
        """
        # 1. Classify
        agent_key = self._classify_task(task)
        agent = self.agents.get(agent_key)
        
        if not agent:
             return AgentResponse("System", "No suitable agent found.")

        # 2. Retrieve Context (Naive RAG for all agents for now)
        # In a real system, some agents might not need RAG, or need specific RAG strategies.
        rag_results = self.vector_store.query_similar(task, n_results=3)
        context_str = "\n".join([f"File: {r['metadata']['filepath']}\nContent:\n{r['content']}" for r in rag_results])
        
        # 3. Execute
        response = agent.execute(task, context=context_str)
        return response
