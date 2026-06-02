#!/usr/bin/env python3
"""Generate original non-voice Lantern soundscapes.

Creates WAV files in ~/.lantern/sounds using only Python's standard library.
No downloads, no samples, no voice cloning, no impersonation.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import struct
import wave
from pathlib import Path

RATE = 44100
AMP = 32767


def env(i: int, n: int, fade: float = 1.0) -> float:
    f = max(1, int(RATE * fade))
    if i < f:
        return i / f
    if i > n - f:
        return max(0.0, (n - i) / f)
    return 1.0


def s(freq: float, t: float) -> float:
    return math.sin(2 * math.pi * freq * t)


def tri(freq: float, t: float) -> float:
    p = (freq * t) % 1.0
    return 4 * abs(p - 0.5) - 1


def write(path: Path, data: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        frames = bytearray()
        for x in data:
            x = max(-1.0, min(1.0, x))
            frames.extend(struct.pack("<h", int(x * AMP)))
        w.writeframes(bytes(frames))


def pad(seconds: int, base: float, seed: int) -> list[float]:
    r = random.Random(seed)
    n = seconds * RATE
    out = []
    for i in range(n):
        t = i / RATE
        drift = 1 + 0.004 * s(0.06, t + r.random())
        x = 0.0
        for d in (-0.009, 0, 0.011):
            x += 0.16 * s(base * (1 + d) * drift, t)
            x += 0.07 * s(base * 1.5 * (1 + d), t)
            x += 0.04 * s(base * 2.0 * (1 + d), t)
        out.append(x * env(i, n, 2.0))
    return out


def chimes(seconds: int, base: float, seed: int) -> list[float]:
    r = random.Random(seed)
    n = seconds * RATE
    hits = [0.2, 1.1, 2.6, 4.8, 7.2, 9.1]
    ratios = [1, 1.25, 1.5, 2, 2.5]
    out = []
    for i in range(n):
        t = i / RATE
        x = 0.0
        for h in hits:
            a = t - h
            if a < 0:
                continue
            decay = math.exp(-a * 1.4)
            for k, rr in enumerate(ratios):
                x += 0.18 / (k + 1) * decay * s(base * rr, a)
        x += 0.002 * r.uniform(-1, 1)
        out.append(x * env(i, n, 0.4))
    return out


def rain(seconds: int, seed: int) -> list[float]:
    r = random.Random(seed)
    n = seconds * RATE
    low = 0.0
    out = []
    for i in range(n):
        noise = r.uniform(-1, 1)
        low = 0.996 * low + 0.004 * noise
        tick = r.uniform(0.05, 0.25) if r.random() < 0.0015 else 0.0
        out.append((0.16 * low + 0.035 * noise + tick) * env(i, n, 1.5))
    return out


def frogs(seconds: int, seed: int) -> list[float]:
    r = random.Random(seed)
    n = seconds * RATE
    events = []
    t = 0.3
    while t < seconds - 0.5:
        t += r.uniform(0.2, 0.95)
        events.append((t, r.choice([88, 103, 119, 141, 166]), r.uniform(0.08, 0.28)))
    out = []
    for i in range(n):
        now = i / RATE
        x = 0.0
        for start, freq, length in events:
            a = now - start
            if 0 <= a <= length:
                e = math.sin(math.pi * a / length) ** 0.7
                x += 0.22 * e * (0.7 * tri(freq, a) + 0.3 * s(freq * 2, a))
        out.append(x * env(i, n, 0.8))
    return out


def pulse(seconds: int, base: float, seed: int) -> list[float]:
    n = seconds * RATE
    out = []
    beat = 60 / 54
    for i in range(n):
        t = i / RATE
        ph = t % beat
        x = 0.03 * s(base, t)
        for off, a in ((0.0, 0.45), (0.18, 0.28)):
            age = ph - off
            if 0 <= age < 0.14:
                x += a * math.exp(-age * 30) * s(58, age)
        out.append(x * env(i, n, 1.0))
    return out


def build(out: Path, seconds: int, seed: int) -> None:
    specs = [
        ("lantern_01_calm_lake_pad.wav", pad(seconds, 146.83, seed + 1), "calm lake pad"),
        ("lantern_02_door_chimes.wav", chimes(12, 523.25, seed + 2), "door chimes"),
        ("lantern_03_rain_on_tardis.wav", rain(seconds, seed + 3), "rain texture"),
        ("lantern_04_synthetic_frogs.wav", frogs(seconds, seed + 4), "synthetic frogs"),
        ("lantern_05_heartbeat_door.wav", pulse(seconds, 110, seed + 5), "soft pulse"),
        ("lantern_06_guardian_pad.wav", pad(seconds, 196.00, seed + 6), "guardian pad"),
        ("lantern_07_brave_chimes.wav", chimes(12, 392.00, seed + 7), "brave chimes"),
        ("lantern_08_safe_fun_pad.wav", pad(seconds, 174.61, seed + 8), "safe fun pad"),
        ("lantern_09_frog_rain_mix.wav", [0.65*a + 0.35*b for a, b in zip(rain(seconds, seed + 9), frogs(seconds, seed + 10))], "frog rain mix"),
        ("lantern_10_quantum_dust.wav", rain(seconds, seed + 11), "dust shimmer"),
        ("lantern_11_lamp_warmup.wav", pulse(seconds, 73.42, seed + 12), "lamp warmup"),
        ("lantern_12_return_door.wav", chimes(14, 329.63, seed + 13), "return door"),
    ]
    manifest = []
    for name, data, desc in specs:
        write(out / name, data)
        manifest.append({"file": name, "description": desc, "source": "procedural original", "voice": "none"})
    (out / "lantern_soundscape_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated {len(specs)} original non-voice WAV files in {out}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=Path.home() / ".lantern" / "sounds")
    p.add_argument("--seconds", type=int, default=45)
    p.add_argument("--seed", type=int, default=5173)
    a = p.parse_args()
    build(a.out, a.seconds, a.seed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
