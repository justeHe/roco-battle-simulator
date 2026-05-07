#!/usr/bin/env python3
"""
爬取洛克工具箱蛋组数据与头像缩略图。

数据源:
    https://roco.gptvip.chat/egg-group-query

输出:
    data/egg_groups.json
    data/egg_group_avatars/
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
API_BASE = "https://roco.gptvip.chat"
EGG_GROUPS_API = f"{API_BASE}/api/egg-groups"
EGG_MEMBERS_API = f"{API_BASE}/api/egg-group-members"
OUTPUT_JSON = ROOT / "data" / "egg_groups.json"
AVATAR_DIR = ROOT / "data" / "egg_group_avatars"
SPIRIT_MANIFEST_CSV = ROOT / "data" / "spirit_icons_manifest.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://roco.gptvip.chat/egg-group-query",
}


def fetch_json(url: str, params: dict | None = None, retries: int = 3) -> dict:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"fetch failed: {url}") from exc
            time.sleep(1 + attempt)
    return {}


def fetch_bytes(url: str, retries: int = 3) -> bytes:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={**HEADERS, "Accept": "image/avif,image/webp,image/*,*/*"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception:
            if attempt == retries - 1:
                return b""
            time.sleep(1 + attempt)
    return b""


def safe_stem(name: str) -> str:
    return re.sub(r"[^\w\u4e00-\u9fff（）()·.-]+", "_", str(name or "")).strip("_") or "egg_avatar"


def safe_ext(url: str) -> str:
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if ext not in {".webp", ".png", ".jpg", ".jpeg", ".gif"}:
        ext = ".webp"
    return ext


def load_spirit_numbers() -> dict[str, str]:
    if not SPIRIT_MANIFEST_CSV.exists():
        return {}
    numbers: dict[str, str] = {}
    with SPIRIT_MANIFEST_CSV.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            name = (row.get("名字") or "").strip()
            number = (row.get("编号") or "").strip().replace(".", "")
            if name and number:
                numbers[name] = number
    return numbers


def local_avatar_url(filename: str) -> str:
    return f"/egg-group-avatars/{urllib.parse.quote(filename)}" if filename else ""


def family_members(chain: str) -> list[str]:
    members: list[str] = []
    for stage in re.split(r"\s*→\s*", chain or ""):
        for name in re.split(r"\s*[,，]\s*", stage):
            name = name.strip()
            if name and name not in members:
                members.append(name)
    return members


def base_name(name: str) -> str:
    return re.sub(r"（.*?）|\(.*?\)", "", name or "").strip()


def normalize_variant_words(name: str) -> str:
    return (name or "").replace("储水时", "储水期")


def resolve_representative_name(card: dict, rep: dict, spirit_numbers: dict[str, str]) -> str:
    page_name = str(rep.get("page_name") or "").strip()
    display_name = str(rep.get("display_name") or "").strip()
    if page_name in spirit_numbers:
        return page_name

    normalized_page = normalize_variant_words(page_name)
    if normalized_page in spirit_numbers:
        return normalized_page

    names = family_members(str(card.get("family_chain") or ""))
    for candidate in names:
        if candidate in spirit_numbers:
            if page_name and (base_name(page_name) == base_name(candidate) or page_name in candidate):
                return candidate
            if display_name and (base_name(display_name) == base_name(candidate) or display_name in candidate):
                return candidate
    for candidate in names:
        normalized = normalize_variant_words(candidate)
        if normalized in spirit_numbers:
            if page_name and base_name(page_name) == base_name(normalized):
                return normalized
            if display_name and base_name(display_name) == base_name(normalized):
                return normalized

    return page_name or display_name or str(rep.get("base_id") or "egg_avatar")


def avatar_filename(card: dict, rep: dict, spirit_numbers: dict[str, str]) -> str:
    avatar_url = str(rep.get("avatar_url") or "").strip()
    name = resolve_representative_name(card, rep, spirit_numbers)
    number = spirit_numbers.get(name)
    if number:
        return f"{number}_{safe_stem(name)}{safe_ext(avatar_url)}"
    base_id = rep.get("base_id") or "egg"
    return f"ID{safe_stem(base_id)}_{safe_stem(name)}{safe_ext(avatar_url)}"


def root_family(card: dict) -> str:
    family_key = str(card.get("family_key") or "")
    match = re.search(r"root:([^|]+)", family_key)
    if match:
        return match.group(1).strip()
    members = family_members(str(card.get("family_chain") or ""))
    return members[0] if members else ""


def download_avatar(card: dict, rep: dict, spirit_numbers: dict[str, str], skip_existing: bool = True) -> None:
    avatar_url = str(rep.get("avatar_url") or "").strip()
    if not avatar_url:
        return
    filename = avatar_filename(card, rep, spirit_numbers)
    target = AVATAR_DIR / filename
    if not (skip_existing and target.exists()):
        old_base = rep.get("base_id") or rep.get("page_name") or rep.get("display_name") or ""
        old_file = AVATAR_DIR / f"{safe_stem(old_base)}{safe_ext(avatar_url)}"
        if skip_existing and old_file.exists() and old_file != target:
            old_file.rename(target)
        else:
            data = fetch_bytes(avatar_url)
            if not data:
                return
            target.write_bytes(data)
    rep["avatar_file"] = filename
    rep["local_avatar_url"] = local_avatar_url(filename)


def crawl(page_size: int = 30, delay: float = 0.12, skip_existing: bool = True) -> dict:
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    group_payload = fetch_json(EGG_GROUPS_API)
    groups = group_payload.get("groups") or []
    cards: list[dict] = []
    spirit_numbers = load_spirit_numbers()

    for group in groups:
        gid = group.get("group_id")
        if not gid:
            continue
        print(f"爬取蛋组 {group.get('group_display')} ({gid})")
        page = 1
        total_pages = 1
        while page <= total_pages:
            payload = fetch_json(EGG_MEMBERS_API, {
                "group_id": gid,
                "page": page,
                "page_size": page_size,
            })
            total_pages = int(payload.get("total_pages") or 1)
            for card in payload.get("cards") or []:
                rep = card.get("representative") or {}
                download_avatar(card, rep, spirit_numbers, skip_existing=skip_existing)
                card["representative"] = rep
                card["group_id"] = gid
                card["group_display"] = group.get("group_display") or ""
                card["group_description"] = group.get("description") or ""
                card["mother_family"] = root_family(card)
                card["family_members"] = family_members(str(card.get("family_chain") or ""))
                cards.append(card)
            page += 1
            if delay:
                time.sleep(delay)

    result = {
        "ok": True,
        "source": "https://roco.gptvip.chat/egg-group-query",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "groups": groups,
        "cards": cards,
    }
    OUTPUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="爬取蛋组分类、母族和头像缩略图")
    parser.add_argument("--page-size", type=int, default=30, help="接口分页大小，参考站点当前上限为 30")
    parser.add_argument("--delay", type=float, default=0.12, help="请求间隔秒数")
    parser.add_argument("--refresh", action="store_true", help="重新下载已存在的头像")
    args = parser.parse_args()

    payload = crawl(page_size=args.page_size, delay=args.delay, skip_existing=not args.refresh)
    print(f"完成: 蛋组 {len(payload['groups'])} 个，折叠母族 {len(payload['cards'])} 个")
    print(f"数据: {OUTPUT_JSON}")
    print(f"头像: {AVATAR_DIR}")


if __name__ == "__main__":
    main()
