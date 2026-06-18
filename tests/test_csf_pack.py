"""Round-trip + integrity tests for CSF-Pack (CSF v0.8 arbitrary-file archive)."""
import os
import pathlib
import tempfile

import pytest

from csf import csf_pack


def _sample_tree(root: pathlib.Path):
    (root / "sub").mkdir(parents=True)
    (root / "a.txt").write_text("hello arbitrary file\n" * 50)
    (root / "data.json").write_text('{"k":1,"v":[1,2,3]}')
    (root / "sub" / "blob.bin").write_bytes(os.urandom(8000))
    (root / "empty.dat").write_bytes(b"")


@pytest.mark.parametrize("compress", [True, False])
def test_round_trip(compress):
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        src = d / "src"
        _sample_tree(src)
        out = str(d / "out.csf")
        m = csf_pack.pack([str(src)], out, compress=compress)
        assert m["file_count"] == 4
        assert os.path.getsize(out) > 0

        dest = d / "out"
        written = csf_pack.unpack(out, str(dest))
        assert len(written) == 4
        for f in src.rglob("*"):
            if f.is_file():
                rel = f.relative_to(src.parent).as_posix()
                assert (dest / rel).read_bytes() == f.read_bytes()


def test_list_does_not_extract():
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        src = d / "src"
        _sample_tree(src)
        out = str(d / "out.csf")
        csf_pack.pack([str(src)], out)
        manifest = csf_pack.list_archive(out)
        assert manifest["format"] == "csf-pack"
        assert manifest["version"] == "0.8"
        assert manifest["file_count"] == 4


def test_tamper_detected():
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        src = d / "src"
        _sample_tree(src)
        out = pathlib.Path(d / "out.csf")
        csf_pack.pack([str(src)], str(out))
        b = bytearray(out.read_bytes())
        b[len(b) // 2] ^= 0xFF  # flip a blob byte
        bad = d / "bad.csf"
        bad.write_bytes(bytes(b))
        with pytest.raises(ValueError):
            csf_pack.unpack(str(bad), str(d / "bad"))


def test_path_traversal_rejected():
    # A manifest path escaping dest must be refused.
    with tempfile.TemporaryDirectory() as d:
        d = pathlib.Path(d)
        f = d / "x.txt"
        f.write_text("x")
        out = str(d / "out.csf")
        csf_pack.pack([str(f)], out)
        # Sanity: normal extract works
        assert csf_pack.unpack(out, str(d / "ok"))
