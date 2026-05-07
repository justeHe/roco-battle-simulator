#!/usr/bin/env python3
"""
下载孵蛋尺寸反查数据。

数据源:
    https://github.com/mfskys/rocomegg/blob/main/public/data/egg-measurements-final.json

输出:
    data/egg_measurements.json
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE_URL = "https://raw.githubusercontent.com/mfskys/rocomegg/main/public/data/egg-measurements-final.json"
OUTPUT_JSON = ROOT / "data" / "egg_measurements.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
}


def fetch_json(retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(SOURCE_URL, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"fetch failed: {SOURCE_URL}") from exc
            time.sleep(1 + attempt)
    return {}


def main() -> None:
    parser = argparse.ArgumentParser(description="下载孵蛋尺寸反查数据")
    parser.parse_args()

    payload = fetch_json()
    payload["source"] = SOURCE_URL
    payload["downloaded_at"] = datetime.now(timezone.utc).isoformat()
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"完成: {payload.get('totalPets', 0)} 个精灵，{payload.get('total', 0)} 条测量记录")
    print(f"数据: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
