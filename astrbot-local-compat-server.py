"""Local protocol stub for the prompt-cache UI review; no model inference."""

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

LOG = Path(__file__).with_name("astrbot-local-compat-requests.jsonl")
REPLY = "Local protocol test: accepted this request without cache_control. This is a canned response."


def has_cache_marker(value):
    if isinstance(value, dict):
        return "cache_control" in value or any(has_cache_marker(v) for v in value.values())
    return isinstance(value, list) and any(has_cache_marker(v) for v in value)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def send_json(self, status, value):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.send_json(200, {
            "data": [{"id": "claude-local-protocol-test", "display_name": "Local protocol stub", "type": "model", "created_at": "2026-01-01T00:00:00Z"}],
            "first_id": "claude-local-protocol-test", "last_id": "claude-local-protocol-test", "has_more": False,
        })

    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        if size > 1_000_000:
            self.send_json(413, {"error": "local test payload limit"})
            return
        body = json.loads(self.rfile.read(size))
        marked = has_cache_marker(body)
        streaming = bool(body.get("stream"))
        with LOG.open("a") as stream:
            stream.write(json.dumps({
                "time": datetime.now(timezone.utc).isoformat(), "mode": "local-protocol-stub",
                "path": self.path, "streaming": streaming, "has_cache_control": marked,
                "http_status": 400 if marked else 200,
            }) + "\n")
        if marked:
            self.send_json(400, {"type": "error", "error": {"type": "invalid_request_error", "message": "cache_control is not supported by this local protocol test endpoint"}})
            return
        usage = {"input_tokens": 1, "output_tokens": 8}
        message = {"id": "msg_local_probe", "type": "message", "role": "assistant", "model": "claude-local-protocol-test", "content": [{"type": "text", "text": REPLY}], "stop_reason": "end_turn", "stop_sequence": None, "usage": usage}
        if not streaming:
            self.send_json(200, message)
            return
        events = [
            ("message_start", {"type": "message_start", "message": {**message, "content": [], "stop_reason": None, "usage": {"input_tokens": 1, "output_tokens": 0}}}),
            ("content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}),
            ("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": REPLY}}),
            ("content_block_stop", {"type": "content_block_stop", "index": 0}),
            ("message_delta", {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None}, "usage": {"output_tokens": 8}}),
            ("message_stop", {"type": "message_stop"}),
        ]
        data = "".join(f"event: {name}\ndata: {json.dumps(event)}\n\n" for name, event in events).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    print("Local protocol stub on 127.0.0.1:16186; no live model inference", flush=True)
    ThreadingHTTPServer(("127.0.0.1", 16186), Handler).serve_forever()
