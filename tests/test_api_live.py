"""
ML Engineering Copilot - Live API Endpoints Verification
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from starlette.testclient import TestClient
from backend.api.main import app


def test_api_pipeline():
    print("=" * 60)
    print("TESTING FASTAPI BACKEND SUITE")
    print("=" * 60)

    with TestClient(app) as client:
        # 1. Health check
        print("\n[1] Testing GET /health...")
        resp = client.get("/health")
        print(f"  Status: {resp.status_code}")
        print(f"  Response: {resp.json()}")
        assert resp.status_code == 200, "Health check failed"

        # 2. Create Session
        print("\n[2] Testing POST /api/sessions...")
        sess_resp = client.post("/api/sessions", json={"title": "PyTorch Debugging Session"})
        print(f"  Status: {sess_resp.status_code}")
        sess_data = sess_resp.json()
        print(f"  Response: {sess_data}")
        assert sess_resp.status_code == 201
        session_id = sess_data["session_id"]

        # 3. List Sessions
        print("\n[3] Testing GET /api/sessions...")
        list_resp = client.get("/api/sessions")
        print(f"  Status: {list_resp.status_code}")
        all_sessions = list_resp.json().get("sessions", [])
        print(f"  Total sessions retrieved: {len(all_sessions)}")
        assert any(s.get("session_id") == session_id for s in all_sessions)

        # 4. Synchronous Chat (General ML mode)
        print("\n[4] Testing POST /api/chat (Synchronous with Memory)...")
        chat_req = {
            "query": "In Python, what is the time complexity of dictionary lookup?",
            "session_id": session_id,
            "mode": "general_ml",
            "use_rag": False,  # Testing LLM + Memory first
        }
        chat_resp = client.post("/api/chat", json=chat_req)
        print(f"  Status: {chat_resp.status_code}")
        ans_data = chat_resp.json()
        print(f"  Model Used: {ans_data.get('model')}")
        print(f"  Answer Snippet: {ans_data.get('answer', '')[:120]}...\n")
        assert chat_resp.status_code == 200

        # 5. Get Session History
        print("\n[5] Testing GET /api/sessions/{session_id} (Verifying Memory Persistence)...")
        hist_resp = client.get(f"/api/sessions/{session_id}")
        print(f"  Status: {hist_resp.status_code}")
        hist_data = hist_resp.json()
        messages = hist_data.get("messages", [])
        print(f"  Stored messages count: {len(messages)}")
        assert len(messages) >= 2, "Expected at least user and assistant messages stored"

        # 6. Stream Chat Endpoint
        print("\n[6] Testing POST /api/chat/stream (SSE Stream)...")
        stream_req = {
            "query": "Explain O(1) in one short sentence.",
            "session_id": session_id,
            "mode": "explainer",
            "use_rag": False,
        }
        with client.stream("POST", "/api/chat/stream", json=stream_req) as s_resp:
            print(f"  Status: {s_resp.status_code}")
            assert s_resp.status_code == 200
            print("  Streamed Chunks Preview: ", end="", flush=True)
            chunk_count = 0
            for line in s_resp.iter_lines():
                if line.startswith("data: ") and chunk_count < 5:
                    print(".", end="", flush=True)
                    chunk_count += 1
            print(" [Done]")

    print("\n" + "=" * 60)
    print("[✓] All API endpoints (Health, Sessions, Chat, SSE Stream) PASSED!")
    print("=" * 60)


if __name__ == "__main__":
    test_api_pipeline()
