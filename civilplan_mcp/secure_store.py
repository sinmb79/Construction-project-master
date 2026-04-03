from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import sys
from typing import Any


DEFAULT_KEY_FILE_NAME = "api-keys.dpapi.json"


class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_char)),
    ]


def default_key_store_path() -> Path:
    key_root = Path(os.getenv("CIVILPLAN_KEY_DIR", Path.home() / "key"))
    return key_root / "civilplan-mcp" / DEFAULT_KEY_FILE_NAME


def _require_windows() -> None:
    if sys.platform != "win32":
        raise RuntimeError("Windows DPAPI storage is only available on Windows.")


def _blob_from_bytes(data: bytes) -> tuple[DATA_BLOB, ctypes.Array[ctypes.c_char]]:
    raw_buffer = ctypes.create_string_buffer(data, len(data))
    blob = DATA_BLOB(
        cbData=len(data),
        pbData=ctypes.cast(raw_buffer, ctypes.POINTER(ctypes.c_char)),
    )
    return blob, raw_buffer


def _bytes_from_blob(blob: DATA_BLOB) -> bytes:
    return ctypes.string_at(blob.pbData, blob.cbData)


def _protect_bytes(raw: bytes) -> bytes:
    _require_windows()
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32

    input_blob, input_buffer = _blob_from_bytes(raw)
    output_blob = DATA_BLOB()

    success = crypt32.CryptProtectData(
        ctypes.byref(input_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(output_blob),
    )
    if not success:
        raise ctypes.WinError()

    try:
        return _bytes_from_blob(output_blob)
    finally:
        if output_blob.pbData:
            kernel32.LocalFree(output_blob.pbData)
        del input_buffer


def _unprotect_bytes(raw: bytes) -> bytes:
    _require_windows()
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32

    input_blob, input_buffer = _blob_from_bytes(raw)
    output_blob = DATA_BLOB()

    success = crypt32.CryptUnprotectData(
        ctypes.byref(input_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(output_blob),
    )
    if not success:
        raise ctypes.WinError()

    try:
        return _bytes_from_blob(output_blob)
    finally:
        if output_blob.pbData:
            kernel32.LocalFree(output_blob.pbData)
        del input_buffer


def save_api_keys(keys: dict[str, str], path: Path | None = None) -> Path:
    target = path or default_key_store_path()
    payload = {
        "version": 1,
        "keys": {key: value for key, value in keys.items() if value},
    }
    protected = _protect_bytes(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    envelope = {
        "scheme": "windows-dpapi-base64",
        "ciphertext": base64.b64encode(protected).decode("ascii"),
    }

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def load_api_keys(path: Path | None = None) -> dict[str, str]:
    target = path or default_key_store_path()
    if not target.exists():
        return {}

    envelope = json.loads(target.read_text(encoding="utf-8"))
    ciphertext = base64.b64decode(envelope["ciphertext"])
    payload = json.loads(_unprotect_bytes(ciphertext).decode("utf-8"))
    keys: dict[str, Any] = payload.get("keys", {})
    return {str(key): str(value) for key, value in keys.items() if value}
