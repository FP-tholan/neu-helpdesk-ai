import json
import re
import sys
import time

import requests

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 90

_CHINESE_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")
_ENGLISH_HEAVY_RE = re.compile(r"\b(the|this|that|with|from|which|please|user)\b", re.IGNORECASE)


def health():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        data = r.json()
        print(f"  status: {r.status_code}")
        print(f"  response: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data.get("ok", False)
    except requests.RequestException as e:
        print(f"  ERROR: {e}")
        return False


def ask(query: str, session_id: str = "test_s1"):
    payload = {
        "query": query,
        "session_id": session_id,
        "user_id": "test_user",
        "metadata": {},
    }
    start = time.time()
    try:
        r = requests.post(f"{BASE_URL}/ai/query", json=payload, timeout=TIMEOUT)
        elapsed = (time.time() - start) * 1000
        return r.status_code, r.json(), elapsed
    except requests.RequestException as e:
        return 0, {"error": str(e)}, (time.time() - start) * 1000


def _check_chinese(text: str) -> tuple[bool, str]:
    if _CHINESE_RE.search(text):
        return False, "Answer contains Chinese characters"
    return True, ""


def _check_no_english_heavy(text: str) -> tuple[bool, str]:
    # Cho phép tên riêng, thuật ngữ (HDMI, Wifi, App), nhưng không cho câu tiếng Anh
    matches = _ENGLISH_HEAVY_RE.findall(text)
    if len(matches) >= 3:
        return False, f"Answer contains too much English ({len(matches)} matches)"
    return True, ""


def _check_answer_not_empty(text: str) -> tuple[bool, str]:
    if not text or len(text.strip()) < 10:
        return False, "Answer too short"
    return True, ""


def run_test(label: str, query: str, expect_route: str | None = None,
             expect_intent: str | None = None,
             expect_category: str | None = None,
             expect_room: str | None = None,
             expect_ticket_mention: bool = False,
             expect_needs_clarification: bool | None = None,
             expect_no_hallucinated_team: bool = False) -> bool:
    print(f"\n{'=' * 70}")
    print(f"[{label}] {query}")
    print(f"{'=' * 70}")

    status, data, elapsed = ask(query)

    if not data.get("success"):
        print(f"  ❌ API FAILED ({status}): {json.dumps(data, ensure_ascii=False)[:200]}")
        return False

    resp = data["data"]
    meta = resp.get("metadata", {})
    decision = meta.get("route_decision", {})
    actual_route = decision.get("route", "?")
    answer = resp.get("answer", "")

    print(f"  Route:     {actual_route}")
    print(f"  Intent:    {meta.get('intent', '?')}")
    print(f"  Category:  {meta.get('category')}")
    print(f"  Room:      {meta.get('room_code')}")
    print(f"  Latency:   {elapsed:.0f}ms")
    print(f"  Sources:   {len(resp.get('sources', []))}")

    preview = answer[:200] + ("..." if len(answer) > 200 else "")
    print(f"  Answer:    {preview}")

    checks = []

    # Quality checks (universal)
    checks.append(("No Chinese chars", *_check_chinese(answer)))
    checks.append(("Answer not empty", *_check_answer_not_empty(answer)))
    checks.append(("Not too much English", *_check_no_english_heavy(answer)))

    # Route check
    if expect_route:
        ok = actual_route == expect_route
        checks.append((f"Route = {expect_route}", ok, "" if ok else f"got {actual_route}"))

    # Intent check
    if expect_intent:
        actual = meta.get("intent")
        ok = actual == expect_intent
        checks.append((f"Intent = {expect_intent}", ok, "" if ok else f"got {actual}"))

    # Category check
    if expect_category:
        actual = meta.get("category")
        ok = actual == expect_category
        checks.append((f"Category = {expect_category}", ok, "" if ok else f"got {actual}"))

    # Room check
    if expect_room:
        actual = meta.get("room_code")
        ok = actual == expect_room
        checks.append((f"Room = {expect_room}", ok, "" if ok else f"got {actual}"))

    # Ticket mention
    if expect_ticket_mention:
        ok = "tạo ticket" in answer.lower() or "tạo phiếu" in answer.lower()
        checks.append(("Mentions 'tạo ticket'", ok, "" if ok else "missing"))

    # Needs clarification check
    if expect_needs_clarification is not None:
        actual = meta.get("needs_clarification")
        ok = actual == expect_needs_clarification
        checks.append((f"needs_clarification = {expect_needs_clarification}",
                       ok, "" if ok else f"got {actual}"))

    # No hallucinated team names check
    if expect_no_hallucinated_team:
        bad_teams = ["HVAC", "Facility", "Maintenance Team", "Operations Team"]
        found = [t for t in bad_teams if t.lower() in answer.lower()]
        ok = len(found) == 0
        checks.append(("No hallucinated team", ok, f"found {found}" if found else ""))

    print()
    all_pass = True
    for name, ok, detail in checks:
        mark = "✅" if ok else "❌"
        suffix = f" — {detail}" if detail else ""
        print(f"  {mark} {name}{suffix}")
        if not ok:
            all_pass = False

    return all_pass


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--health":
        sys.exit(0 if health() else 1)

    print("=" * 70)
    print("NEU HelpDesk AI — Quality Test Suite")
    print("=" * 70)

    print("\n[Health] Checking service...")
    if not health():
        print("\n❌ Service không sẵn sàng.")
        sys.exit(1)

    if len(sys.argv) > 1:
        run_test("CUSTOM", " ".join(sys.argv[1:]))
        sys.exit(0)

    tests = [
        # RAG — quality answers, no Chinese
        dict(label="RAG-1", query="Làm sao khởi động lại máy chiếu?",
             expect_route="rag"),
        dict(label="RAG-2", query="Cách tự xử lý khi điều hòa không mát?",
             expect_route="rag"),
        dict(label="RAG-3", query="Làm thế nào để restart wifi trên laptop?",
             expect_route="rag"),

        # AGENT — phải suggest ticket + metadata structured
        dict(label="AGENT-1", query="Máy chiếu phòng B102 không lên hình, đang trong giờ học",
             expect_route="agent", expect_intent="report_issue",
             expect_category="PROJECTOR", expect_room="B102",
             expect_ticket_mention=True),
        dict(label="AGENT-2", query="Wifi phòng A2.202 không kết nối được",
             expect_route="agent", expect_intent="report_issue",
             expect_category="WIFI", expect_room="A2.202",
             expect_ticket_mention=True),
        dict(label="AGENT-3", query="Tạo ticket giúp tôi sự cố điều hòa phòng A2.201",
             expect_route="agent", expect_intent="report_issue",
             expect_category="AIR_CONDITIONER",
             expect_ticket_mention=True),
        dict(label="AGENT-SEVERE", query="Máy chiếu phòng B102 bốc khói, mùi khét",
             expect_route="agent", expect_intent="report_issue",
             expect_category="PROJECTOR", expect_room="B102",
             expect_ticket_mention=True),

        # CLARIFY — thiếu phòng, yêu cầu AI hỏi lại và không bịa tên team nước ngoài
        dict(label="CLARIFY", query="điều hòa phòng tôi mở không lên",
             expect_route="agent", expect_intent="report_issue",
             expect_category="AIR_CONDITIONER",
             expect_needs_clarification=True,
             expect_no_hallucinated_team=True),

        # OOD
        dict(label="OOD", query="Thời tiết Hà Nội hôm nay thế nào?",
             expect_route="ood", expect_intent="out_of_scope"),
    ]

    results = []
    for t in tests:
        ok = run_test(**t)
        results.append((t["label"], t["query"], ok))

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    passed = sum(1 for _, _, ok in results if ok)
    total = len(results)
    for label, q, ok in results:
        mark = "✅" if ok else "❌"
        print(f"  {mark} [{label}] {q[:55]}")

    print(f"\n  {passed}/{total} tests passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()