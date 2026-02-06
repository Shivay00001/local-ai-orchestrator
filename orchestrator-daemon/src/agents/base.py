from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentResponse:
    agent_name: str
    content: str
    metadata: Optional[dict] = None

class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    @abstractmethod
    def execute(self, task: str, context: Optional[str] = None) -> AgentResponse:
        """
        Execute the agent's specific task.
        :param task: The user's input/request.
        :param context: Retrieved context from vector DB (optional).
        :return: AgentResponse
        """
        pass
