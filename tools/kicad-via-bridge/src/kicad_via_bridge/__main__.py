from __future__ import annotations

import argparse
import json
import sys

from kicad_via_bridge.ipc import delete_via, list_vias
from kicad_via_bridge.server import mcp


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in {"list", "delete"}:
        _cli()
        return
    mcp.run(transport="stdio")


def _cli() -> None:
    parser = argparse.ArgumentParser(prog="kicad-via-bridge")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_list = sub.add_parser("list")
    p_list.add_argument("--net")
    p_list.add_argument("--x", type=float)
    p_list.add_argument("--y", type=float)
    p_list.add_argument("--radius", type=float, default=1.0)
    p_del = sub.add_parser("delete")
    p_del.add_argument("uuid")
    p_del.add_argument("--net")
    args = parser.parse_args()
    if args.cmd == "list":
        result = list_vias(net_name=args.net, x=args.x, y=args.y, radius_mm=args.radius)
    else:
        result = delete_via(uuid=args.uuid, expected_net=args.net)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
