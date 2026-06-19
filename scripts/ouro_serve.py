"""
Ouro server — runs the real Ouro LoopLM (weight-tied recurrent transformer with
adaptive depth) locally and speaks the **Ollama HTTP API**, so Lantern OS's
existing chat path works unchanged with NO Ollama binary. This replaces Ollama
for local inference.

Endpoints (Ollama-compatible):
  GET  /api/tags        list the served model
  GET  /api/version
  POST /api/chat        {model, messages, stream}  -> NDJSON stream or single JSON
  POST /api/generate    {model, prompt, stream}

Config (env):
  OURO_MODEL     HF id or local path (default ByteDance/Ouro-1.4B-Thinking)
  OURO_ADAPTER   optional LoRA adapter dir (our Claude-session tune) — applied if set
  OURO_PORT      default 11434 (drop-in for Ollama; stop the Ollama binary first)
  OURO_UT_STEPS  recurrent steps override (else model default)
  HF_HOME        default D:/hf-cache

Run:  .venv-train/Scripts/python scripts/ouro_serve.py
"""
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

os.environ.setdefault("HF_HOME", "D:/hf-cache")

import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer  # noqa: E402

MODEL_ID = os.environ.get("OURO_MODEL", "ByteDance/Ouro-1.4B-Thinking")
ADAPTER = os.environ.get("OURO_ADAPTER", "")
PORT = int(os.environ.get("OURO_PORT", "11434"))
MODEL_NAME = "ouro:latest"  # what the Ollama API advertises

print(f"[ouro] loading {MODEL_ID} (cuda={torch.cuda.is_available()})…", flush=True)
_tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
_model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID, trust_remote_code=True, torch_dtype=torch.float16, device_map="auto")
if ADAPTER:
    from peft import PeftModel
    _model = PeftModel.from_pretrained(_model, ADAPTER)
    print(f"[ouro] LoRA adapter applied: {ADAPTER}", flush=True)
_steps = os.environ.get("OURO_UT_STEPS")
if _steps:
    for attr in ("total_ut_steps", "num_recurrent_steps"):
        if hasattr(_model.config, attr):
            setattr(_model.config, attr, int(_steps))
_model.eval()
print(f"[ouro] ready on :{PORT} as '{MODEL_NAME}'", flush=True)


def _prompt_from_messages(messages):
    try:
        return _tok.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
    except Exception:
        return "\n".join(f"{m.get('role')}: {m.get('content','')}" for m in messages) + "\nassistant:"


def _generate(prompt, max_new_tokens=512, stream_cb=None):
    ids = _tok(prompt, return_tensors="pt").to(_model.device)
    kw = dict(max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=_tok.eos_token_id)
    if stream_cb is None:
        with torch.no_grad():
            out = _model.generate(**ids, **kw)
        return _tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True)
    streamer = TextIteratorStreamer(_tok, skip_prompt=True, skip_special_tokens=True)
    th = threading.Thread(target=lambda: _model.generate(**ids, streamer=streamer, **kw))
    th.start()
    full = []
    for piece in streamer:
        full.append(piece)
        stream_cb(piece)
    th.join()
    return "".join(full)


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path.startswith("/api/tags"):
            return self._json({"models": [{"name": MODEL_NAME, "model": MODEL_NAME,
                "details": {"family": "ouro-looplm", "parameter_size": "1.4B"}}]})
        if self.path.startswith("/api/version"):
            return self._json({"version": "ouro-shim-0.1"})
        if self.path in ("/", "/api/health"):
            return self._json({"status": "ok", "model": MODEL_ID})
        return self._json({"error": "not found"}, 404)

    def do_POST(self):
        ln = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(ln) or b"{}")
        except Exception:
            return self._json({"error": "bad json"}, 400)
        is_chat = self.path.startswith("/api/chat")
        prompt = _prompt_from_messages(body.get("messages", [])) if is_chat else body.get("prompt", "")
        stream = body.get("stream", True)
        max_tok = int((body.get("options") or {}).get("num_predict", 512))

        def pack(content, done):
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            return (json.dumps({"model": MODEL_NAME, "created_at": now,
                **({"message": {"role": "assistant", "content": content}} if is_chat else {"response": content}),
                "done": done}) + "\n").encode()

        if stream:
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.end_headers()
            try:
                _generate(prompt, max_tok, stream_cb=lambda p: (self.wfile.write(pack(p, False)), self.wfile.flush()))
                self.wfile.write(pack("", True)); self.wfile.flush()
            except Exception as e:
                try: self.wfile.write(pack(f"[ouro error: {e}]", True))
                except Exception: pass
        else:
            try:
                text = _generate(prompt, max_tok)
                self._json(json.loads(pack(text, True).decode()))
            except Exception as e:
                self._json({"error": str(e)}, 500)


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
