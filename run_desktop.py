#!/usr/bin/env python3
"""
Desktop launcher for the local Roco simulator.

This entry is intentionally separate from run_web.py so PyInstaller can bundle
the FastAPI app together with the local web/ and data/ folders.
"""

from __future__ import annotations

import argparse
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_PAGE = "/dex"


def app_root() -> Path:
    """Return the source root, or PyInstaller's bundled resource root."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent


def port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def choose_port(host: str, preferred: int) -> int:
    if port_available(host, preferred):
        return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return int(sock.getsockname()[1])


def open_browser_later(url: str, delay: float = 1.2) -> None:
    time.sleep(delay)
    webbrowser.open(url)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start the local Roco simulator desktop build.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--page", default=DEFAULT_PAGE)
    parser.add_argument("--no-browser", action="store_true", help="Start the server without opening a browser.")
    parser.add_argument("--log-level", default="warning")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = app_root()
    os.chdir(root)
    sys.path.insert(0, str(root))

    port = choose_port(args.host, args.port)
    page = args.page if args.page.startswith("/") else f"/{args.page}"
    url = f"http://{args.host}:{port}{page}"

    print("=" * 58)
    print("  洛克王国本地模拟器")
    print(f"  资源目录: {root}")
    print(f"  访问地址: {url}")
    if port != args.port:
        print(f"  提示: 端口 {args.port} 被占用，已改用 {port}")
    print("  关闭此窗口即可退出")
    print("=" * 58)

    if not args.no_browser:
        threading.Thread(target=open_browser_later, args=(url,), daemon=True).start()

    import uvicorn
    from src.server import app

    uvicorn.run(
        app,
        host=args.host,
        port=port,
        log_level=args.log_level,
        access_log=False,
    )


if __name__ == "__main__":
    main()
