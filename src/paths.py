"""Runtime resource path helpers for source, onedir, and macOS .app builds."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path


def _is_resource_root(path: Path) -> bool:
    return (path / "web").is_dir() and (path / "data").is_dir()


def _candidate_roots(base: Path):
    """Yield likely resource roots around a PyInstaller/source location."""
    try:
        base = base.resolve()
    except OSError:
        return

    nearby = (
        base,
        base / "_internal",
        base / "Resources",
        base / "Frameworks",
        base / "Frameworks" / "_internal",
    )
    for item in nearby:
        yield item

    for parent in base.parents:
        yield parent
        yield parent / "_internal"
        yield parent / "Resources"
        yield parent / "Frameworks"
        yield parent / "Frameworks" / "_internal"


@lru_cache(maxsize=1)
def project_root() -> Path:
    """Return the directory that contains bundled `web/` and `data/` resources."""
    env_root = os.environ.get("ROCO_APP_ROOT")
    if env_root:
        env_path = Path(env_root)
        if _is_resource_root(env_path):
            return env_path.resolve()

    seeds = [
        Path(__file__).resolve().parents[1],
        Path.cwd(),
    ]

    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", "")
        if meipass:
            seeds.append(Path(meipass))
        seeds.append(Path(sys.executable).resolve().parent)

    seen: set[Path] = set()
    for seed in seeds:
        for candidate in _candidate_roots(seed):
            if candidate in seen:
                continue
            seen.add(candidate)
            if _is_resource_root(candidate):
                return candidate.resolve()

    return Path(__file__).resolve().parents[1]


def data_path(*parts: str) -> Path:
    return project_root().joinpath("data", *parts)


def web_path(*parts: str) -> Path:
    return project_root().joinpath("web", *parts)
