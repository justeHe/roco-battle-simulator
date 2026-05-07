#!/usr/bin/env python3
"""
Build a PyInstaller desktop bundle for the local Roco simulator.

Usage:
    python3 scripts/build_desktop.py
    python3 scripts/build_desktop.py --windowed
    python3 scripts/build_desktop.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path


APP_NAME = "洛克模拟器"
ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "run_desktop.py"
SPEC_DIR = ROOT / "build" / "pyinstaller-spec"


HIDDEN_IMPORTS = [
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.lifespan.on",
]

EXCLUDED_MODULES = [
    # These packages are useful in the development environment or crawler scripts,
    # but the desktop app only needs the FastAPI server plus local data assets.
    "IPython",
    "PyQt5",
    "black",
    "bs4",
    "jupyter",
    "lxml",
    "matplotlib",
    "mypy",
    "notebook",
    "openpyxl",
    "pandas",
    "pytest",
    "requests",
    "sphinx",
    "tkinter",
]


def data_arg(source: str, target: str) -> str:
    sep = ";" if platform.system() == "Windows" else ":"
    return f"{source}{sep}{target}"


def build_command(args: argparse.Namespace) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "--onedir",
        "--name",
        args.name,
        "--specpath",
        str(SPEC_DIR),
        "--add-data",
        data_arg(str(ROOT / "web"), "web"),
        "--add-data",
        data_arg(str(ROOT / "data"), "data"),
    ]

    for module in HIDDEN_IMPORTS:
        command.extend(["--hidden-import", module])
    for module in EXCLUDED_MODULES:
        command.extend(["--exclude-module", module])

    if args.windowed:
        command.append("--windowed")
    if args.icon:
        command.extend(["--icon", args.icon])
    if args.contents_dir:
        command.extend(["--contents-directory", args.contents_dir])

    command.append(str(ENTRY))
    return command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the desktop PyInstaller bundle.")
    parser.add_argument("--name", default=APP_NAME, help="Application name shown in dist/.")
    parser.add_argument("--windowed", action="store_true", help="Hide the terminal window in the built app.")
    parser.add_argument("--icon", default="", help="Optional .icns/.ico icon path.")
    parser.add_argument(
        "--contents-dir",
        default="_internal",
        help="PyInstaller onedir contents directory. Use '.' for the old flat layout.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the command without running it.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not ENTRY.exists():
        print(f"Missing entry file: {ENTRY}", file=sys.stderr)
        return 1
    if not (ROOT / "web").exists() or not (ROOT / "data").exists():
        print("Missing web/ or data/ resource folder.", file=sys.stderr)
        return 1

    command = build_command(args)
    print("Build command:")
    print(" ".join(f'"{part}"' if " " in part else part for part in command))

    if args.dry_run:
        return 0

    SPEC_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    subprocess.run(command, cwd=ROOT, env=env, check=True)
    print()
    print(f"Done. Run: {ROOT / 'dist' / args.name / args.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
