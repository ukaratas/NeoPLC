from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from kicad_via_bridge.ipc import delete_via as ipc_delete_via
from kicad_via_bridge.ipc import list_vias as ipc_list_vias

mcp = FastMCP(
    "kicad-via-bridge",
    instructions=(
        "KiCad via escape hatch only. Use list_vias and delete_via. "
        "Do not route, place, or edit files here — that stays in Konnect."
    ),
)


@mcp.tool()
def list_vias(
    net_name: str | None = None,
    x: float | None = None,
    y: float | None = None,
    radius_mm: float = 1.0,
) -> dict:
    """List vias on the open pcbnew board.

    Optional exact net_name (e.g. '/DI Field/DI3'). Optional x,y,radius_mm
    keeps vias whose center is within radius_mm of that point.
    """
    return ipc_list_vias(net_name=net_name, x=x, y=y, radius_mm=radius_mm)


@mcp.tool()
def delete_via(uuid: str, expected_net: str | None = None) -> dict:
    """Delete one via by UUID on the live pcbnew board.

    Refuses non-via UUIDs, locked vias, and net mismatch when expected_net
    is set. Does not save; Konnect save_project after a batch.
    """
    return ipc_delete_via(uuid=uuid, expected_net=expected_net)
