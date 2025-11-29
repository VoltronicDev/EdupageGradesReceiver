"""Simple local credential store using Windows DPAPI (CryptProtectData).

This stores a JSON blob encrypted with the current user's Windows DPAPI so only
the same Windows user account can decrypt it. No external dependencies.

Functions:
- save_creds(data: dict) -> bool
- load_creds() -> dict | None
- remove_creds() -> None

Note: This is Windows-only. On other OSes this module will raise RuntimeError.
"""
from pathlib import Path
import json
import base64
import ctypes
from ctypes import wintypes
import sys

_CREDS_FILE = Path(__file__).parent / ".edupage_creds"


def _ensure_windows():
    if sys.platform != "win32":
        raise RuntimeError("creds_store is only supported on Windows in this implementation")


def _protect(data: bytes) -> bytes:
    # CryptProtectData wraps the data for the current user
    _ensure_windows()
    # Define a minimal DATA_BLOB structure
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    def _make_blob(buf: bytes):
        blob = DATA_BLOB()
        blob.cbData = len(buf)
        blob.pbData = ctypes.cast(ctypes.create_string_buffer(buf), ctypes.POINTER(ctypes.c_char))
        return blob

    in_blob = _make_blob(data)
    out_blob = DATA_BLOB()

    if not ctypes.windll.crypt32.CryptProtectData(ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)):
        raise ctypes.WinError()

    protected = ctypes.string_at(out_blob.pbData, out_blob.cbData)
    ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    return protected


def _unprotect(protected: bytes) -> bytes:
    _ensure_windows()
    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    def _make_blob(buf: bytes):
        blob = DATA_BLOB()
        blob.cbData = len(buf)
        blob.pbData = ctypes.cast(ctypes.create_string_buffer(buf), ctypes.POINTER(ctypes.c_char))
        return blob

    in_blob = _make_blob(protected)
    out_blob = DATA_BLOB()

    if not ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)):
        raise ctypes.WinError()

    data = ctypes.string_at(out_blob.pbData, out_blob.cbData)
    ctypes.windll.kernel32.LocalFree(out_blob.pbData)
    return data


def save_creds(data: dict) -> bool:
    """Save credentials dict encrypted to disk. Returns True on success."""
    _ensure_windows()
    raw = json.dumps(data).encode("utf-8")
    try:
        protected = _protect(raw)
        b64 = base64.b64encode(protected).decode("ascii")
        _CREDS_FILE.write_text(json.dumps({"blob": b64}))
        return True
    except Exception:
        return False


def load_creds() -> dict | None:
    _ensure_windows()
    if not _CREDS_FILE.exists():
        return None
    try:
        j = json.loads(_CREDS_FILE.read_text())
        b64 = j.get("blob")
        if not b64:
            return None
        protected = base64.b64decode(b64)
        raw = _unprotect(protected)
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


def remove_creds() -> None:
    try:
        if _CREDS_FILE.exists():
            _CREDS_FILE.unlink()
    except Exception:
        pass
