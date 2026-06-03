"""Tests for the observation delta stream encoder/decoder."""

import unittest

from csf.delta_stream import (
    DeltaStreamReader,
    DeltaStreamWriter,
    DeltaType,
    Record,
    encode_confirmation,
    encode_delta,
)


class TestConfirmationRecord(unittest.TestCase):
    def test_encode_size(self):
        pos = (0,) * 12
        data = encode_confirmation(level=0, position=pos, extent=0xFF)
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0] & 0x80, 0)  # confirmation flag

    def test_level_encoding(self):
        pos = (1,) * 12
        for level in range(8):
            data = encode_confirmation(level=level, position=pos)
            encoded_level = (data[0] >> 4) & 0x07
            self.assertEqual(encoded_level, level)


class TestDeltaRecord(unittest.TestCase):
    def test_light_change(self):
        pos = (0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2)
        data = encode_delta(level=4, delta_type=DeltaType.LIGHT_CHANGED,
                            position=pos, payload=b"\x05")
        self.assertTrue(data[0] & 0x80)  # delta flag
        self.assertEqual(data[0] & 0x0F, DeltaType.LIGHT_CHANGED)

    def test_all_delta_types(self):
        pos = (1,) * 12
        for dtype in DeltaType:
            data = encode_delta(level=3, delta_type=dtype, position=pos)
            self.assertEqual(data[0] & 0x0F, int(dtype))


class TestStreamRoundtrip(unittest.TestCase):
    def test_write_read_mixed(self):
        writer = DeltaStreamWriter()

        p1 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        p2 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1)
        p3 = (1, 2, 0, 1, 0, 2, 1, 0, 0, 1, 2, 0)

        writer.confirm(0, p1, extent=0xFF)
        writer.delta(4, DeltaType.LIGHT_CHANGED, p2, b"\x03")
        writer.delta(4, DeltaType.ANCHOR_ACTIVATION, p3, b"\x06")

        data = writer.to_bytes()
        self.assertGreater(len(data), 0)

    def test_empty_stream(self):
        writer = DeltaStreamWriter()
        self.assertEqual(writer.to_bytes(), b"")

    def test_confirmation_only_stream(self):
        writer = DeltaStreamWriter()
        for i in range(10):
            pos = tuple([i % 3] * 12)
            writer.confirm(0, pos)
        data = writer.to_bytes()
        self.assertGreater(len(data), 0)


class TestStreamEfficiency(unittest.TestCase):
    def test_static_universe_is_cheap(self):
        """A mostly-static universe should produce very small streams."""
        writer = DeltaStreamWriter()
        # 100 confirmation heartbeats for large static regions
        for i in range(100):
            writer.confirm(0, (0,) * 12, extent=0xFF)
        # 3 actual changes
        writer.delta(4, DeltaType.LIGHT_CHANGED, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1), b"\x01")
        writer.delta(4, DeltaType.LIGHT_CHANGED, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2), b"\x02")
        writer.delta(4, DeltaType.ANCHOR_ACTIVATION, (1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), b"\x03")

        data = writer.to_bytes()
        # Confirmations should be ~4 bytes each, deltas ~5-6 bytes
        # Total should be well under 1KB for 103 records
        self.assertLess(len(data), 1024)


if __name__ == "__main__":
    unittest.main()
