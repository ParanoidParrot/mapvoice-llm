from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run MapVoice-LLM locally."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=3000)
    parser.add_argument(
        "--pack-id",
        default=os.getenv("MAPVOICE_PACK_ID"),
        help="Regional pack ID, e.g. blr-kn.",
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Disable Uvicorn auto-reload.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.pack_id:
        os.environ["MAPVOICE_PACK_ID"] = args.pack_id

    import uvicorn

    print()
    print("MapVoice-LLM")
    print(f"  UI:       http://localhost:{args.port}")
    print(f"  API docs: http://localhost:{args.port}/docs")
    if args.pack_id:
        print(f"  Pack:     {args.pack_id}")
    print()

    uvicorn.run(
        "mapvoice_llm.api:app",
        host=args.host,
        port=args.port,
        reload=not args.no_reload,
        app_dir=str(SRC),
    )


if __name__ == "__main__":
    main()
