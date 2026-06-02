"""Continuous Lantern listen-and-converse loop.

Mic stays open indefinitely. Each silence-boundary utterance is transcribed
by Vosk, sent to Lantern's local /chat backend, and logged with her reply
to ~/.lantern/state/convo-stream.jsonl.

Run:
    python scripts/listen_stream.py                # default 600s window (10 minutes)
    python scripts/listen_stream.py --duration 180 # one 180s window

Stop with Ctrl+C or by deleting the .running flag at ~/.lantern/state/listen.running.

Boundary:
- Every loop is bounded. "Infinite" is an immortality claim and Lantern is
  not immortal. Respawn is the operator's job (or the watchdog's), not a
  claim of forever. Operator taught this directly: "infinite is immortal,
  0, 100 absolutely not."
- mic capture is local; transcripts written to operator-private journal
- /chat call is to localhost only (LM Studio loopback when substrate is on)
- voice rule still applies: Lantern's text out is hers; no synthesis
- minimum utterance length filter avoids storing accidental coughs
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import sounddevice as sd
import vosk

MODELS_DIR = Path.home() / ".lantern" / "models"
LOG_PATH = Path.home() / ".lantern" / "state" / "convo-stream.jsonl"
FLAG_PATH = Path.home() / ".lantern" / "state" / "listen.running"
CHAT_URL = "http://127.0.0.1:8766/chat"

SAMPLE_RATE = 16000
BLOCK = 4000
MIN_UTTERANCE_CHARS = 3


def resolve_model() -> Path:
    for name in ("vosk-model-en-us-0.22", "vosk-model-small-en-us-0.15"):
        p = MODELS_DIR / name
        if (p / "conf").exists():
            return p
    raise SystemExit(f"No Vosk model at {MODELS_DIR}. Run scripts/install_vosk_*.")


def send_to_lantern(text: str, mode: str = "engineer") -> tuple[str, str]:
    body = json.dumps({"message": text, "mode": mode}).encode("utf-8")
    req = urllib.request.Request(
        CHAT_URL,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("voice", "?"), (data.get("answer") or "")[:600]
    except Exception as exc:  # noqa: BLE001
        return "err", f"{type(exc).__name__}: {exc}"[:300]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=600,
                        help="seconds to listen (bounded; default 600 = 10 minutes)")
    parser.add_argument("--mode", default="engineer")
    args = parser.parse_args()
    if args.duration <= 0:
        raise SystemExit("duration must be positive; infinite is an immortality claim — Lantern is bounded")

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    FLAG_PATH.write_text(f"started {time.time()}\n", encoding="utf-8")

    model_path = resolve_model()
    model = vosk.Model(str(model_path))
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)

    queue: list[tuple[bytes, float]] = []

    def callback(indata, frames, time_info, status):  # type: ignore[no-untyped-def]
        pcm = (indata[:, 0] * 32767).astype(np.int16).tobytes()
        queue.append((pcm, float(np.abs(indata).max())))

    print(f">>> LISTEN_STREAM model={model_path.name} duration={args.duration}s (bounded) <<<",
          flush=True)
    print(f">>> log: {LOG_PATH}", flush=True)
    print(f">>> stop: delete {FLAG_PATH} or Ctrl+C", flush=True)

    t0 = time.time()
    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32",
                            blocksize=BLOCK, callback=callback):
            while True:
                if not FLAG_PATH.exists():
                    print(">>> flag removed — stopping <<<", flush=True)
                    break
                if (time.time() - t0) >= args.duration:
                    print(f">>> duration {args.duration}s reached — stopping <<<", flush=True)
                    break
                if queue:
                    pcm, peak = queue.pop(0)
                    if rec.AcceptWaveform(pcm):
                        text = (json.loads(rec.Result()).get("text") or "").strip()
                        if text and len(text) >= MIN_UTTERANCE_CHARS:
                            ts = round(time.time() - t0, 1)
                            print(f"[+{ts:7.1f}s peak={peak:.2f}] HEARD: {text}", flush=True)
                            voice, reply = send_to_lantern(text, args.mode)
                            print(f"               LANTERN[{voice}]: {reply[:240]}", flush=True)
                            with LOG_PATH.open("a", encoding="utf-8") as fh:
                                fh.write(json.dumps({
                                    "t": ts,
                                    "peak": peak,
                                    "heard": text,
                                    "voice": voice,
                                    "reply": reply,
                                }, ensure_ascii=False) + "\n")
                else:
                    time.sleep(0.05)
    except KeyboardInterrupt:
        print(">>> interrupted <<<", flush=True)
    finally:
        FLAG_PATH.unlink(missing_ok=True)
        print(">>> STOPPED <<<", flush=True)


if __name__ == "__main__":
    main()
