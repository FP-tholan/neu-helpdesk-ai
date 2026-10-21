"""
Tool Registry chuẩn enterprise:
  - JSON Schema validation tự động
  - ToolResult envelope (không bao giờ raise)
  - Native function calling qua Ollama
"""
import json
import logging
from typing import Any, Callable

import jsonschema

from src.agent.schemas import ToolResult, ToolStatus

logger = logging.getLogger(__name__)


class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        func: Callable[[dict[str, Any]], ToolResult],
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def get_ollama_definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def run(self, arguments: dict[str, Any]) -> ToolResult:
        try:
            jsonschema.validate(instance=arguments, schema=self.parameters)
        except jsonschema.exceptions.ValidationError as e:
            logger.warning("Tool %s schema invalid: %s", self.name, e.message)
            return ToolResult(
                status=ToolStatus.ERROR,
                error=f"Tham số không hợp lệ: {e.message}",
            )

        try:
            return self.func(arguments)
        except Exception as e:
            logger.exception("Tool %s internal error", self.name)
            return ToolResult(
                status=ToolStatus.ERROR,
                error="Tool internal failure.",
                metadata={"error_code": "TOOL_INTERNAL_ERROR"},
            )


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def get_all_definitions(self) -> list[dict[str, Any]]:
        return [t.get_ollama_definition() for t in self._tools.values()]

    def execute(self, name: str, arguments: dict[str, Any]) -> ToolResult:
        tool = self.get(name)
        if not tool:
            return ToolResult(
                status=ToolStatus.ERROR,
                error=f"Tool '{name}' không tồn tại.",
            )
        return tool.run(arguments)

    def __len__(self) -> int:
        return len(self._tools)