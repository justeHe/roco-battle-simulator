"""
从 RocoMaster 的公开 wiki 源文件同步机制百科文本。

输出:
    data/mechanics_entries.json
"""

import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "data" / "mechanics_entries.json"
SOURCE_BASE = "https://rocomaster.com"
WIKI_BASE = f"{SOURCE_BASE}/@fs/root/projects/RocoMaster/env/wiki"
MECH_INDEX_URL = f"{WIKI_BASE}/mechanics/_index.json"
MECH_SOURCE_URL = f"{SOURCE_BASE}/src/dex/mechanics-dex.ts"
EXCLUDED_MARK_TITLES = {"传说印记", "命定印记", "帕尔印记", "技能石/湿润印记", "迟缓印记"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def wiki_url(folder: str, filename: str) -> str:
    return f"{WIKI_BASE}/{folder}/{urllib.parse.quote(filename)}"


def classify_mark_polarity(text: str) -> str:
    if "正面印记" in text and "负面印记" not in text:
        return "positive"
    if "负面印记" in text and "正面印记" not in text:
        return "negative"
    return "system"


def load_mark_files() -> list[str]:
    source = fetch_text(MECH_SOURCE_URL)
    files = sorted(set(re.findall(r"wiki/marks/([^\"?]+\.wiki)", source)))
    return [
        urllib.parse.unquote(name)
        for name in files
        if urllib.parse.unquote(name).removesuffix(".wiki").replace("_", "/") not in EXCLUDED_MARK_TITLES
    ]


def load_entries() -> list[dict]:
    entries: list[dict] = []

    for file in load_mark_files():
        text = fetch_text(wiki_url("marks", file))
        title = file.removesuffix(".wiki").replace("_", "/")
        polarity = classify_mark_polarity(text)
        entries.append({
            "id": title,
            "title": title,
            "category": "印记",
            "polarity": polarity,
            "meta": "印记系统总览" if title == "印记" else (
                "正面印记" if polarity == "positive" else "负面印记" if polarity == "negative" else "印记"
            ),
            "body": text,
            "is_overview": title == "印记",
        })

    index = json.loads(fetch_text(MECH_INDEX_URL))
    for item in index:
        text = fetch_text(wiki_url("mechanics", item["file"]))
        entries.append({
            "id": item["title"],
            "title": item["title"],
            "category": item.get("category", "关键词"),
            "polarity": item.get("polarity", "system"),
            "meta": item.get("subtype") or item.get("category") or "",
            "body": text,
            "is_overview": bool(item.get("overview", False)),
        })

    pol_order = {"positive": 0, "negative": 1, "system": 2}
    entries.sort(key=lambda e: (
        0 if e.get("is_overview") else 1,
        pol_order.get(e.get("polarity"), 2),
        e.get("title", ""),
    ))
    return entries


def main():
    entries = load_entries()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(entries)} entries to {OUT_PATH}")


if __name__ == "__main__":
    main()
