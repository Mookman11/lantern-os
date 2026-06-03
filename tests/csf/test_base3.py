"""Tests for base-3 positional encoding with cyclic delta wrap-around."""

import unittest

from csf.base3 import (
    Base3Codec,
    DIMENSIONS,
    TOTAL_POSITIONS,
    _cyclic_delta,
    _from_scalar,
    _to_scalar,
    decode_absolute,
    decode_delta,
    encode_absolute,
    encode_delta,
)


class TestScalarConversion(unittest.TestCase):
    def test_origin(self):
        origin = (0,) * DIMENSIONS
        self.assertEqual(_to_scalar(origin), 0)
        self.assertEqual(_from_scalar(0), origin)

    def test_max_position(self):
        max_pos = (2,) * DIMENSIONS
        scalar = _to_scalar(max_pos)
        self.assertEqual(scalar, TOTAL_POSITIONS - 1)
        self.assertEqual(_from_scalar(scalar), max_pos)

    def test_roundtrip_samples(self):
        samples = [
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            (1, 2, 0, 1, 0, 2, 1, 0, 0, 1, 2, 0),
            (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1),
        ]
        for coords in samples:
            with self.subTest(coords=coords):
                self.assertEqual(_from_scalar(_to_scalar(coords)), coords)


class TestCyclicDelta(unittest.TestCase):
    """The core fix: cyclic shortest-path delta on Z/3Z."""

    def test_no_change(self):
        self.assertEqual(_cyclic_delta(0, 0), 0)
        self.assertEqual(_cyclic_delta(1, 1), 0)
        self.assertEqual(_cyclic_delta(2, 2), 0)

    def test_forward_one(self):
        self.assertEqual(_cyclic_delta(1, 0), 1)
        self.assertEqual(_cyclic_delta(2, 1), 1)

    def test_backward_one(self):
        self.assertEqual(_cyclic_delta(0, 1), -1)
        self.assertEqual(_cyclic_delta(1, 2), -1)

    def test_wrap_forward(self):
        # 2 → 0 is +1 cyclically (not -2)
        self.assertEqual(_cyclic_delta(0, 2), +1)

    def test_wrap_backward(self):
        # 0 → 2 is -1 cyclically (not +2)
        self.assertEqual(_cyclic_delta(2, 0), -1)

    def test_all_pairs(self):
        """Exhaustive: every pair of base-3 digits produces delta in {-1,0,+1}."""
        for a in range(3):
            for b in range(3):
                d = _cyclic_delta(a, b)
                self.assertIn(d, (-1, 0, 1),
                              f"cyclic_delta({a},{b})={d}, expected -1..+1")
                self.assertEqual((b + d) % 3, a,
                                 f"recovery failed: ({b}+{d})%3 != {a}")


class TestAbsoluteEncoding(unittest.TestCase):
    def test_origin_size(self):
        data = encode_absolute((0,) * 12)
        self.assertEqual(len(data), 2)  # header + 1 byte payload

    def test_max_position_size(self):
        data = encode_absolute((2,) * 12)
        self.assertLessEqual(len(data), 4)  # header + up to 3 bytes

    def test_roundtrip(self):
        for coords in [
            (0,) * 12,
            (2,) * 12,
            (1, 0, 2, 1, 0, 2, 1, 0, 2, 1, 0, 2),
        ]:
            data = encode_absolute(coords)
            decoded, offset = decode_absolute(data)
            self.assertEqual(decoded, coords)
            self.assertEqual(offset, len(data))

    def test_rejects_invalid(self):
        with self.assertRaises(ValueError):
            encode_absolute((0, 0, 0))  # wrong dimension
        with self.assertRaises(ValueError):
            encode_absolute((3,) * 12)  # out of range


class TestDeltaEncoding(unittest.TestCase):
    def test_identical_positions(self):
        pos = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
        data = encode_delta(pos, pos)
        self.assertEqual(len(data), 4)  # header + 3 packed bytes
        decoded, _ = decode_delta(data, 0, pos)
        self.assertEqual(decoded, pos)

    def test_adjacent_positions(self):
        prev = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        curr = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
        data = encode_delta(curr, prev)
        decoded, _ = decode_delta(data, 0, prev)
        self.assertEqual(decoded, curr)

    def test_wrap_around_encode_decode(self):
        """The key test: 2→0 wraps forward (+1), 0→2 wraps backward (-1)."""
        prev = (2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0)
        curr = (0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0, 2)
        data = encode_delta(curr, prev)
        decoded, _ = decode_delta(data, 0, prev)
        self.assertEqual(decoded, curr)

    def test_all_wraps(self):
        prev = (0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2)
        curr = (2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1)
        data = encode_delta(curr, prev)
        decoded, _ = decode_delta(data, 0, prev)
        self.assertEqual(decoded, curr)

    def test_delta_is_compact(self):
        prev = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
        curr = (2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1)
        data = encode_delta(curr, prev)
        self.assertEqual(len(data), 4)  # always 4 bytes for delta


class TestBase3Codec(unittest.TestCase):
    def test_first_encode_is_absolute(self):
        codec = Base3Codec()
        pos = (1, 0, 2, 1, 0, 2, 1, 0, 2, 1, 0, 2)
        data = codec.encode(pos)
        self.assertFalse(data[0] & 0x80)  # absolute flag

    def test_second_encode_is_delta(self):
        codec = Base3Codec()
        codec.encode((0,) * 12)
        data = codec.encode((0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1))
        self.assertTrue(data[0] & 0x80)  # delta flag

    def test_roundtrip_sequence(self):
        positions = [
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2),
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # wraps
            (2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2),  # big jump → absolute
            (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),  # wraps back
        ]
        enc = Base3Codec()
        dec = Base3Codec()

        buf = bytearray()
        for p in positions:
            buf.extend(enc.encode(p))

        offset = 0
        decoded = []
        for _ in positions:
            coords, offset = dec.decode(bytes(buf), offset)
            decoded.append(coords)

        self.assertEqual(decoded, positions)

    def test_reset_clears_state(self):
        codec = Base3Codec()
        codec.encode((1,) * 12)
        codec.reset()
        self.assertIsNone(codec.last_position)

    def test_exhaustive_neighbor_roundtrip(self):
        """Every single-dimension change from center roundtrips correctly."""
        center = (1,) * 12
        enc = Base3Codec()
        dec = Base3Codec()

        for dim in range(12):
            for target_val in range(3):
                enc.reset()
                dec.reset()
                neighbor = list(center)
                neighbor[dim] = target_val
                neighbor = tuple(neighbor)

                buf = enc.encode(center) + enc.encode(neighbor)
                c1, off = dec.decode(buf, 0)
                c2, _ = dec.decode(buf, off)

                self.assertEqual(c1, center)
                self.assertEqual(c2, neighbor,
                                 f"dim={dim} val={target_val} failed")


if __name__ == "__main__":
    unittest.main()
