from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ToolStatus(str, Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    NO_RESULT = "NO_RESULT"


@dataclass
class ToolResult:
    status: ToolStatus
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    user_query: str
    request_id: str
    messages: list[dict[str, Any]] = field(default_factory=list)
    intermediate_steps: list[dict[str, Any]] = field(default_factory=list)
    final_answer: Optional[str] = None
    sources: list[dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    iteration: int = 0