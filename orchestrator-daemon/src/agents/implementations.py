from .base import BaseAgent, AgentResponse
from ..ollama.client import generate_completion, list_models

class CodeReaderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="CodeReader", role="Explains code and project structure")

    def execute(self, task: str, context: str = "") -> AgentResponse:
        models = list_models()
        model_name = models[0].name if models else "llama2"
        
        prompt = f"""You are a code reader agent. Explain the following code or project structure request.
Context:
{context}

Request: {task}
"""
        response_text = generate_completion(model_name, prompt)
        
        return AgentResponse(
            agent_name=self.name,
            content=response_text,
            metadata={"type": "explanation", "model": model_name}
        )

class RefactorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="RefactorAgent", role="Suggests code improvements")

    def execute(self, task: str, context: str = "") -> AgentResponse:
        models = list_models()
        model_name = models[0].name if models else "llama2"

        prompt = f"""You are a code refactoring expert. Suggest improvements for the following code.
Context:
{context}

Request: {task}
"""
        response_text = generate_completion(model_name, prompt)

        return AgentResponse(
            agent_name=self.name,
            content=response_text,
            metadata={"type": "refactor_plan", "model": model_name}
        )

class TestWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="TestWriterAgent", role="Generates pytest cases")

    def execute(self, task: str, context: str = "") -> AgentResponse:
        models = list_models()
        model_name = models[0].name if models else "llama2"

        prompt = f"""You are a QA automation engineer. Write a pytest case for the following scenario.
Context:
{context}

Request: {task}
"""
        response_text = generate_completion(model_name, prompt)

        return AgentResponse(
            agent_name=self.name,
            content=response_text,
            metadata={"type": "test_code", "model": model_name}
        )

class DocWriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="DocWriterAgent", role="Generates documentation")

    def execute(self, task: str, context: str = "") -> AgentResponse:
        models = list_models()
        model_name = models[0].name if models else "llama2"

        prompt = f"""You are a technical writer. Write documentation for the following code.
Context:
{context}

Request: {task}
"""
        response_text = generate_completion(model_name, prompt)

        return AgentResponse(
            agent_name=self.name,
            content=response_text,
            metadata={"type": "documentation", "model": model_name}
        )
