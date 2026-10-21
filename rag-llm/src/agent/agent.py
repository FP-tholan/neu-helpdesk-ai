import logging
from typing import Any

from src import llm
from src.agent.schemas import AgentState
from src.agent.tools import ToolRegistry

logger = logging.getLogger(__name__)


class NativeAgent:
    """Agent dùng native function calling của Ollama."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def step(self, state: AgentState) -> AgentState:
        try:
            resp = llm.chat_with_tools(
                state.messages,
                tools=self.registry.get_all_definitions(),
                temperature=0.1,
                request_id=state.request_id,
            )
            message = resp.get("message", {})
            state.messages.append(message)

            if message.get("tool_calls"):
                for call in message["tool_calls"]:
                    func = call.get("function", {})
                    args = func.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            import json
                            args = json.loads(args)
                        except Exception:
                            args = {}
                    state.intermediate_steps.append({
                        "type": "tool_call",
                        "id": call.get("id", ""),
                        "name": func.get("name"),
                        "args": args,
                    })
            elif message.get("content"):
                state.final_answer = message["content"]
            else:
                state.error = "Agent trả về response rỗng."

        except Exception as e:
            logger.exception("Agent step failed [%s]", state.request_id)
            state.error = f"Agent execution error: {e}"

        return state