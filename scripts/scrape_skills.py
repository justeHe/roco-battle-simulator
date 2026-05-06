#!/usr/bin/env python3
"""兼容入口：实际爬虫代码位于 scripts/crawlers/skills_rocoworld.py。"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.crawlers.skills_rocoworld import main


if __name__ == "__main__":
    main()
