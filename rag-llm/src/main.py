"""
AI Service REST API — Proxy cho Backend.

Endpoints:
  GET  /health              — health + readiness (không cần auth)
  POST /ai/query            — main entry (contract Query → Response)
  POST /ai/reload-kb        — reload knowledge base (admin only, cần token)
"""
import logging
import time
import uuid
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from pydantic import ValidationError

from src import llm
from src.agent.agent import NativeAgent
from src.agent.executor import AgentExecutor
from src.agent.tools import ToolRegistry
from src.config import settings
from src.logging_setup import setup_logging
from src.rag.pipeline import RAGPipeline
from src.rag.reranker import LLMReranker
from src.rag.retriever import Retriever
from src.router.router import route as router_route
from src.schemas import Query, Response
from src.tools.memory import memory as memory_store
from src.tools.memory.tool import build_memory_tool
from src.tools.reranker.reranker import build_reranker_tool
from src.tools.retriever.retriever import build_retriever_tool

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)
_GREETING_RE = re.compile(
    r"^\s*(?:hi|hello|hey|chào|xin chào|alo|hí|hế lô|hé lô|"
    r"good morning|good afternoon|good evening)\b",
    re.IGNORECASE,
)
# ─── Khởi tạo pipeline (singleton) ───
rag_pipeline = RAGPipeline()
rag_pipeline.ingest_dir()

reranker = LLMReranker()

# ─── Agent tool registry ───
registry = ToolRegistry()
registry.register(build_retriever_tool(rag_pipeline.retriever))
registry.register(build_reranker_tool(reranker))
registry.register(build_memory_tool())

agent_executor = AgentExecutor(
    NativeAgent(registry),
    max_iterations=settings.agent_max_iterations,
    timeout_sec=settings.agent_timeout_sec,
)

app = Flask(__name__)
app.config["SECRET_KEY"] = settings.secret_key
CORS(app, resources={r"/*": {"origins": "*"}})


# ═══════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════

@app.get("/health")
def health():
    llm_status = llm.health_check()
    return jsonify({
        "ok": llm_status["ok"],
        "service": "neu-helpdesk-rag-llm",
        "model": llm_status.get("model"),
        "kb": {
            "chunks": rag_pipeline.store.count(),
            "dir": str(settings.kb_path),
        },
        "tools": list(registry._tools.keys()),
    }), 200 if llm_status["ok"] else 503


# ═══════════════════════════════════════════════════════════
# MAIN QUERY
# ═══════════════════════════════════════════════════════════

@app.post("/ai/query")
def ai_query():
    request_id = str(uuid.uuid4())
    start = time.time()

    body = request.get_json(silent=True) or {}

    # Validate contract Query
    try:
        query = Query(**body)
    except ValidationError as e:
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_QUERY",
                "message": "Query không đúng contract.",
                "detail": e.errors(),
            },
        }), 400

    log_extra = {"request_id": request_id, "session_id": query.session_id}
    logger.info("Query received: %s", query.query[:100], extra=log_extra)

    try:
        # 1. Route
        decision = router_route(query, request_id=request_id)
        logger.info(
            "Route decision",
            extra={**log_extra, "route": decision.route},
        )

        # 2. Dispatch
        if decision.route == "agent":
            response_dict = agent_executor.execute(
                query=query.query,
                session_id=query.session_id,
                user_id=query.user_id,
                metadata=query.metadata,
                request_id=request_id,
            )
        elif decision.route == "rag":
            resp = rag_pipeline.query(query, request_id=request_id)
            response_dict = resp.model_dump()
        else:
            if _GREETING_RE.search(query.query):
                response_dict = {
                    "answer": (
                        "Xin chào! Tôi là trợ lý AI của NEU HelpDesk. "
                        "Bạn cần hỗ trợ gì về cơ sở vật chất, thiết bị, "
                        "hoặc quy trình báo cáo sự cố?"
                    ),
                    "sources": [],
                    "metadata": {
                        "route": "ood",
                        "intent": "greeting",
                        "status": "SUCCESS",
                    },
                }
            else:
                response_dict = {
                    "answer": (
                        "Xin lỗi, câu hỏi này nằm ngoài phạm vi hỗ trợ của NEU HelpDesk. "
                        "Vui lòng hỏi về sự cố cơ sở vật chất, thiết bị, hoặc quy trình hỗ trợ."
                    ),
                    "sources": [],
                    "metadata": {
                        "route": "ood",
                        "intent": "out_of_scope",
                        "status": "SUCCESS",
                    },
                }
        # 3. Ghi memory (service-level, không phải Agent)
        try:
            memory_store.append(
                session_id=query.session_id,
                content=f"User: {query.query}\nAI: {response_dict.get('answer', '')[:500]}",
                metadata={"route": decision.route},
            )
        except Exception:
            pass

        # 4. Gắn route decision vào metadata
        response_dict.setdefault("metadata", {})
        response_dict["metadata"]["route_decision"] = decision.model_dump()
        response_dict["metadata"]["request_id"] = request_id
        response_dict["metadata"]["latency_ms"] = int((time.time() - start) * 1000)

        # 5. Validate output theo contract Response
        try:
            validated = Response(**response_dict)
        except ValidationError:
            # Nếu output sai format → vẫn trả về nhưng log lại
            logger.error("Response schema mismatch", extra=log_extra)
            validated = Response(
                answer=response_dict.get("answer", ""),
                sources=[],
                metadata={"status": "CONTRACT_VIOLATION"},
            )

        logger.info(
            "Query completed",
            extra={
                **log_extra,
                "route": decision.route,
                "latency_ms": response_dict["metadata"]["latency_ms"],
                "status": "SUCCESS",
            },
        )

        return jsonify({"success": True, "data": validated.model_dump()}), 200

    except Exception as e:
        logger.exception("AI query error", extra=log_extra)
        return jsonify({
            "success": False,
            "error": {
                "code": "AI_INTERNAL_ERROR",
                "message": "Hệ thống AI đang gặp sự cố. Vui lòng thử lại sau.",
                "request_id": request_id,
            },
        }), 500


# ═══════════════════════════════════════════════════════════
# RELOAD KB (admin)
# ═══════════════════════════════════════════════════════════

@app.post("/ai/reload-kb")
def reload_kb():
    token = request.headers.get("X-Admin-Token", "")
    if token != settings.secret_key:
        return jsonify({"success": False, "error": {"code": "FORBIDDEN"}}), 403

    result = rag_pipeline.ingest_dir()
    return jsonify({"success": True, "data": result}), 200


# ═══════════════════════════════════════════════════════════
# ERROR HANDLERS
# ═══════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": {"code": "NOT_FOUND"}}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "error": {"code": "METHOD_NOT_ALLOWED"}}), 405


if __name__ == "__main__":
    logger.info(
        "Starting AI service on %s:%s, model=%s, KB chunks=%s",
        settings.host, settings.port, settings.ollama_model,
        rag_pipeline.store.count(),
    )
    app.run(host=settings.host, port=settings.port, debug=False)