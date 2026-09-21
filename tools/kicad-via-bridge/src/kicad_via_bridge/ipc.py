from __future__ import annotations

import glob
import os
import subprocess
import time
from collections.abc import Callable
from typing import Any, TypeVar

from kipy import KiCad
from kipy.board_types import Via
from kipy.errors import ApiError, ApiStatusCode, ConnectionError
from kipy.proto.common.types import KIID
from kipy.util import to_mm

T = TypeVar("T")

_CLIENT_NAME = "neoplc-via-bridge"
_BUSY_ATTEMPTS = 16
_BUSY_DELAY_S = 0.45


def discover_socket() -> str:
    """Prefer the live pcbnew PID socket; never guess the project-manager api.sock first."""
    override = os.environ.get("KICAD_VIA_BRIDGE_SOCKET")
    if override:
        return _as_ipc(override)

    pcbnew_pids = _pids_matching("pcbnew")
    for pid in pcbnew_pids:
        path = f"/tmp/kicad/api-{pid}.sock"
        if os.path.exists(path):
            return f"ipc://{path}"

    env = os.environ.get("KICAD_API_SOCKET")
    if env:
        raw = env.replace("ipc://", "", 1)
        if os.path.exists(raw):
            return _as_ipc(env)

    matches = sorted(glob.glob("/tmp/kicad/api-*.sock"))
    for path in matches:
        base = os.path.basename(path)
        if base == "api.sock":
            continue
        return f"ipc://{path}"

    default = "/tmp/kicad/api.sock"
    if os.path.exists(default):
        return f"ipc://{default}"

    raise ConnectionError(
        "No KiCad IPC socket found. Open the PCB in pcbnew and leave it idle (Esc)."
    )


def _as_ipc(value: str) -> str:
    return value if value.startswith("ipc://") else f"ipc://{value}"


def _pids_matching(name: str) -> list[int]:
    try:
        out = subprocess.check_output(["pgrep", "-f", name], text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    pids: list[int] = []
    for line in out.splitlines():
        line = line.strip()
        if line.isdigit():
            pids.append(int(line))
    return pids


def _kiid_str(kiid: KIID) -> str:
    return str(kiid.value)


def connect() -> tuple[KiCad, Any, str]:
    socket = discover_socket()
    kicad = KiCad(socket_path=socket, client_name=_CLIENT_NAME, timeout_ms=8000)
    try:
        board = _with_busy_retry(kicad.get_board)
    except Exception:
        _disconnect(kicad)
        raise
    return kicad, board, socket


def _disconnect(kicad: KiCad) -> None:
    client = getattr(kicad, "_client", None)
    conn = getattr(client, "_conn", None) if client is not None else None
    if conn is not None:
        try:
            conn.close()
        except Exception:
            pass
    if client is not None:
        client._connected = False


def _with_busy_retry(fn: Callable[[], T]) -> T:
    last: Exception | None = None
    for _ in range(_BUSY_ATTEMPTS):
        try:
            return fn()
        except ApiError as exc:
            last = exc
            if exc.code != ApiStatusCode.AS_BUSY:
                raise
            time.sleep(_BUSY_DELAY_S)
    raise ApiError(
        "KiCad is busy (AS_BUSY). Press Esc in pcbnew so no tool is active, then retry.",
        code=ApiStatusCode.AS_BUSY,
    ) from last


def _via_record(via: Via) -> dict[str, Any]:
    x = round(to_mm(via.position.x), 4)
    y = round(to_mm(via.position.y), 4)
    rec: dict[str, Any] = {
        "uuid": _kiid_str(via.id),
        "net": via.net.name,
        "x": x,
        "y": y,
        "locked": bool(via.locked),
    }
    try:
        rec["pad_size_mm"] = round(to_mm(via.diameter), 4)
        rec["drill_mm"] = round(to_mm(via.drill_diameter), 4)
    except Exception:
        pass
    return rec


def list_vias(
    net_name: str | None = None,
    x: float | None = None,
    y: float | None = None,
    radius_mm: float = 1.0,
) -> dict[str, Any]:
    kicad, board, socket = connect()
    try:
        vias = _with_busy_retry(board.get_vias)
        rows = [_via_record(v) for v in vias]
        if net_name:
            rows = [r for r in rows if r["net"] == net_name]
        if x is not None and y is not None:
            r2 = radius_mm * radius_mm
            rows = [
                rec
                for rec in rows
                if (rec["x"] - x) ** 2 + (rec["y"] - y) ** 2 <= r2
            ]
        rows.sort(key=lambda rec: (rec["y"], rec["x"], rec["net"]))
        return {
            "socket": socket,
            "count": len(rows),
            "vias": rows,
        }
    finally:
        _disconnect(kicad)


def delete_via(uuid: str, expected_net: str | None = None) -> dict[str, Any]:
    target = uuid.strip().lower()
    if not target:
        raise ValueError("uuid is required")

    kicad, board, socket = connect()
    try:
        vias = _with_busy_retry(board.get_vias)
        match = next((v for v in vias if _kiid_str(v.id).lower() == target), None)
        if match is None:
            kiid = KIID()
            kiid.value = uuid.strip()
            try:
                found = _with_busy_retry(lambda: board.get_items_by_id(kiid))
            except ApiError as exc:
                # An unknown ID is an API error in KiCad 10, not an empty list;
                # that just means nothing on the board carries this UUID.
                if "none of the requested ids" not in str(exc).lower():
                    raise
                found = []
            if found:
                kind = type(found[0]).__name__
                raise ValueError(
                    f"UUID {uuid} is a {kind}, not a via. delete_via refuses non-via items."
                )
            raise ValueError(f"No via with UUID {uuid} on the open board.")

        rec = _via_record(match)
        if expected_net and rec["net"] != expected_net:
            raise ValueError(
                f"Via {uuid} is on net {rec['net']!r}, expected {expected_net!r}."
            )
        if rec["locked"]:
            raise ValueError(f"Via {uuid} is locked; unlock it in pcbnew first.")

        def _commit_delete() -> None:
            commit = board.begin_commit()
            try:
                board.remove_items(match)
                board.push_commit(commit, f"delete_via {uuid}")
            except Exception:
                try:
                    board.drop_commit(commit)
                except Exception:
                    pass
                raise

        _with_busy_retry(_commit_delete)

        kiid = match.id
        try:
            leftover = _with_busy_retry(lambda: board.get_items_by_id(kiid))
        except ApiError as exc:
            # KiCad 10 treats a missing ID as an API error, not an empty list.
            # Only str(exc) is safe to read here: kipy's ApiError.raw_message is
            # `return self.raw_message`, so touching it recurses until
            # RecursionError and a successful delete looks like a failure.
            blob = str(exc).lower()
            if "none of the requested ids" in blob:
                leftover = []
            else:
                raise
        if leftover:
            raise RuntimeError(
                f"KiCad still has item {uuid} after delete_via; deletion did not commit."
            )

        rec["deleted"] = True
        rec["socket"] = socket
        return rec
    finally:
        _disconnect(kicad)
