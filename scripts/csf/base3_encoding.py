#!/usr/bin/env python3
"""
Variable-length base-3 positional encoding for CSF v0.3.

Designed for a 3^12 normalized light matrix (531,441 positions across 12 dimensions).
Supports absolute encoding and delta encoding with correct toroidal wrap-around.

Key fix: the delta encoder uses minimum-distance (toroidal) deltas so adjacent
positions in a base-3 dimension always produce deltas in {-1, 0, +1}, never ±2.
The decoder applies explicit positive modulo so wrap-around is always correct
regardless of sign conventions in the host language.
"""

from __future__ import annotations

from typing import Tuple, Optional

Coords = Tuple[int, ...]  # 12 base-3 digits, each in {0, 1, 2}

BASE = 3
DIMS = 12

# Max absolute value that fits in 3 bytes: 3^12 = 531441 < 2^24 = 16777216
_MAX_VALUE = BASE ** DIMS  # 531441


# ── Internal helpers ────────────────────────────────────────────────────────

def _validate(coords: Coords) -> None:
    if len(coords) != DIMS:
        raise ValueError(f"coords must have {DIMS} elements, got {len(coords)}")
    for i, v in enumerate(coords):
        if not (0 <= v < BASE):
            raise ValueError(f"coords[{i}]={v} is not a valid base-{BASE} digit")


def _coords_to_int(coords: Coords) -> int:
    value = 0
    for d in coords:
        value = value * BASE + d
    return value


def _int_to_coords(value: int) -> Coords:
    digits = []
    for _ in range(DIMS):
        digits.append(value % BASE)
        value //= BASE
    digits.reverse()
    return tuple(digits)


def _min_dist_delta(current: int, previous: int) -> int:
    """
    Compute the minimum-distance (toroidal) delta between two base-3 digits.

    For BASE=3 the result is always in {-1, 0, +1}:
      current=0, previous=2  →  delta=+1 (short path 2→0, not -2)
      current=2, previous=0  →  delta=-1 (short path 0→2, not +2)
    """
    d = current - previous
    half = BASE // 2  # 1 for BASE=3
    if d > half:
        d -= BASE
    elif d < -half:
        d += BASE
    return d


# ── Encoding ────────────────────────────────────────────────────────────────

def _encode_absolute(coords: Coords) -> bytes:
    """Absolute: header byte (bit7=0, lower7=payload_len) + 1-3 payload bytes."""
    value = _coords_to_int(coords)
    if value < 0x100:
        return bytes([1, value])
    elif value < 0x10000:
        return bytes([2, value >> 8, value & 0xFF])
    else:
        return bytes([3, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])


def _encode_compact_delta(coords: Coords, previous: Coords) -> bytes:
    """
    Compact delta: header byte (bit7=1, lower7=DIMS=12) + 12 payload bytes.

    Each payload byte stores one per-dimension delta mapped as:
        delta -1 → 1,  delta 0 → 2,  delta +1 → 3
    (stored in the low 3 bits; upper bits are zero).

    Falls back to absolute encoding if any delta exceeds ±(BASE//2).
    """
    deltas = [_min_dist_delta(c, p) for c, p in zip(coords, previous)]
    # With minimum-distance deltas and BASE=3, all values are in {-1, 0, +1}
    # so the bounds check below is just a safety guard.
    if any(d < -(BASE // 2) or d > (BASE // 2) for d in deltas):
        return _encode_absolute(coords)
    payload = bytearray((d + (BASE // 2 + 1)) & 0b111 for d in deltas)
    return bytes([0b10000000 | DIMS]) + bytes(payload)


# ── Decoding ────────────────────────────────────────────────────────────────

def _decode_absolute(payload: bytes) -> Coords:
    value = 0
    for b in payload:
        value = (value << 8) | b
    return _int_to_coords(value)


def _decode_compact_delta(payload: bytes, previous: Coords) -> Coords:
    """
    Reverse of _encode_compact_delta.

    Explicit positive modulo ensures correct toroidal wrap-around for all
    sign combinations, including Python's floor-division edge cases on
    ports to other languages.
    """
    if len(payload) != DIMS:
        raise ValueError(f"Delta payload must be {DIMS} bytes, got {len(payload)}")
    coords = []
    for i, p in enumerate(previous):
        raw = payload[i] & 0b111          # 0-7
        delta = raw - (BASE // 2 + 1)    # undo the +2 offset → {-1, 0, +1}
        # Explicit positive modulo: always returns a value in [0, BASE)
        new_val = ((p + delta) % BASE + BASE) % BASE
        coords.append(new_val)
    return tuple(coords)


# ── Public codec ────────────────────────────────────────────────────────────

class Base3PositionCodec:
    """
    Stateful codec that remembers the last position for delta encoding.

    Usage::

        codec = Base3PositionCodec()
        raw1 = codec.encode((0,)*12)
        raw2 = codec.encode((0,0,0,0,0,0,0,0,0,0,0,1))  # compact delta

        codec2 = Base3PositionCodec()
        c1, _ = codec2.decode(raw1)   # absolute
        c2, _ = codec2.decode(raw2)   # delta decoded using c1 as previous
    """

    def __init__(self) -> None:
        self._last: Optional[Coords] = None

    def encode(self, coords: Coords) -> bytes:
        _validate(coords)
        if self._last is None:
            data = _encode_absolute(coords)
        else:
            data = _encode_compact_delta(coords, self._last)
        self._last = coords
        return data

    def decode(self, data: bytes, offset: int = 0) -> Tuple[Coords, int]:
        """Return (coords, new_offset)."""
        if offset >= len(data):
            raise ValueError("No data at offset")

        header = data[offset]
        offset += 1
        is_delta = bool(header & 0b10000000)
        payload_len = header & 0b01111111

        payload = data[offset: offset + payload_len]
        offset += payload_len

        if is_delta:
            if self._last is None:
                raise ValueError("Cannot decode delta without a previous position")
            coords = _decode_compact_delta(payload, self._last)
        else:
            coords = _decode_absolute(payload)

        self._last = coords
        return coords, offset

    def reset(self) -> None:
        self._last = None


# ── Convenience wrappers ─────────────────────────────────────────────────────

def encode_position(coords: Coords, previous: Optional[Coords] = None) -> bytes:
    codec = Base3PositionCodec()
    if previous is not None:
        codec._last = previous
    return codec.encode(coords)


def decode_position(
    data: bytes,
    offset: int = 0,
    previous: Optional[Coords] = None,
) -> Tuple[Coords, int]:
    codec = Base3PositionCodec()
    if previous is not None:
        codec._last = previous
    return codec.decode(data, offset)


# ── Self-test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== base3_encoding self-test ===\n")

    origin  = (0,) * DIMS
    nearby  = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
    wrapped = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)   # back to origin

    codec = Base3PositionCodec()
    b_origin  = codec.encode(origin)
    b_nearby  = codec.encode(nearby)
    b_wrapped = codec.encode(wrapped)

    print(f"origin  → {b_origin.hex()!s:12s}  ({len(b_origin)} bytes, absolute)")
    print(f"nearby  → {b_nearby.hex()!s:12s}  ({len(b_nearby)} bytes, compact delta)")
    print(f"wrapped → {b_wrapped.hex()!s:12s}  ({len(b_wrapped)} bytes, compact delta)")

    codec2 = Base3PositionCodec()
    c1, off1 = codec2.decode(b_origin)
    c2, off2 = codec2.decode(b_nearby)
    c3, off3 = codec2.decode(b_wrapped)
    assert c1 == origin,  f"Round-trip failed: {c1}"
    assert c2 == nearby,  f"Round-trip failed: {c2}"
    assert c3 == wrapped, f"Round-trip failed: {c3}"
    print("\nAll round-trips passed ✓")

    # Verify toroidal wrap-around: from (2) → (0) should delta +1, not -2
    a = (0,) * (DIMS - 1) + (2,)
    b = (0,) * DIMS
    enc_a = encode_position(a)
    enc_b = encode_position(b, previous=a)
    _, decoded_b = decode_position(enc_a + enc_b, previous=None)
    decoded_b_coords, _ = decode_position(enc_b, previous=a)
    assert decoded_b_coords == b, f"Toroidal wrap failed: {decoded_b_coords}"
    print("Toroidal wrap-around correct ✓\n")

    # Edge case: all-twos → all-zeros (max toroidal wrap)
    all_two  = (2,) * DIMS
    all_zero = (0,) * DIMS
    enc_t  = encode_position(all_two)
    enc_tz = encode_position(all_zero, previous=all_two)
    dec_tz, _ = decode_position(enc_tz, previous=all_two)
    assert dec_tz == all_zero, f"All-twos→all-zeros failed: {dec_tz}"
    print("Edge case (2,2,...,2) → (0,0,...,0) correct ✓")
