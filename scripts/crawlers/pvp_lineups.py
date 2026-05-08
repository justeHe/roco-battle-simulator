#!/usr/bin/env python3
"""
从 BiliGame 洛克王国手游 Wiki 爬取 PVP 阵容库。

入口页:
    https://wiki.biligame.com/rocom/阵容一览

输出:
    data/pvp_lineups.json
    data/lineup_icons/
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[2]
BASE_URL = "https://wiki.biligame.com"
API_URL = f"{BASE_URL}/rocom/api.php"
LINEUP_LIST_URL = f"{BASE_URL}/rocom/%E9%98%B5%E5%AE%B9%E4%B8%80%E8%A7%88"
OUTPUT_JSON = ROOT / "data" / "pvp_lineups.json"
ICON_DIR = ROOT / "data" / "lineup_icons"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://wiki.biligame.com/rocom/",
}

IV_KEY_MAP = {
    "生命": "hp",
    "精力": "hp",
    "HP": "hp",
    "物攻": "atk",
    "攻击": "atk",
    "物防": "def",
    "防御": "def",
    "魔攻": "spatk",
    "魔防": "spdef",
    "速度": "speed",
}


def fetch_text(url: str, retries: int = 3, timeout: int = 30) -> str:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception as exc:
            if attempt + 1 >= retries:
                print(f"  [ERROR] 获取失败 {url}: {exc}")
                return ""
            time.sleep(1 + attempt)
    return ""


def fetch_json(url: str, retries: int = 3, timeout: int = 30) -> dict:
    text = fetch_text(url, retries=retries, timeout=timeout)
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"  [ERROR] JSON 解析失败 {url}: {exc}")
        return {}


def fetch_bytes(url: str, retries: int = 3, timeout: int = 30) -> bytes:
    headers = dict(HEADERS)
    headers["Accept"] = "image/avif,image/webp,image/apng,image/png,image/*,*/*;q=0.8"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as exc:
            if attempt + 1 >= retries:
                print(f"  [ERROR] 下载失败 {url}: {exc}")
                return b""
            time.sleep(1 + attempt)
    return b""


def normalize_image_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if url.startswith("//"):
        return "https:" + url
    return urljoin(BASE_URL, url)


def safe_filename(name: str, url: str = "") -> str:
    stem = re.sub(r"[^\w\u4e00-\u9fff]+", "_", name or "").strip("_") or "lineup_icon"
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
        ext = ".png"
    return f"{stem}{ext}"


def local_lineup_icon_url(filename: str) -> str:
    return f"/lineup-icons/{urllib.parse.quote(filename)}" if filename else ""


def parse_pvp_cards(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    cards: list[dict] = []
    seen: set[str] = set()

    for box in soup.select(".rocom_lineup_list_box_pvp_content .rocom_lineup_line_pet_list_box"):
        title_el = box.select_one(".rocom_lineup_line_pet_edit")
        title = title_el.get_text(" ", strip=True) if title_el else ""
        href = ""
        for link in box.find_all("a"):
            if (link.get("title") or "").startswith("精灵阵容/"):
                href = link.get("href") or ""
                break
        if not title or not href:
            continue
        source_url = urljoin(BASE_URL, href)
        lineup_id = href.rstrip("/").split("/")[-1]
        if lineup_id in seen:
            continue
        seen.add(lineup_id)

        items = box.select(".rocom_lineup_line_pet_item")
        magic_name = ""
        magic_icon_source_url = ""
        members_preview = []
        for item in items:
            name_el = item.select_one(".rocom_lineup_line_pet_name")
            name = name_el.get_text(" ", strip=True) if name_el else ""
            img = item.select_one("img")
            img_url = normalize_image_url(img.get("src") if img else "")
            number_el = item.select_one(".rocom_lineup_line_pet_num")
            if number_el:
                members_preview.append({
                    "slot": int(number_el.get_text(" ", strip=True) or len(members_preview) + 1),
                    "card_name": name,
                    "card_avatar_source_url": img_url,
                })
            elif not magic_name:
                magic_name = name
                magic_icon_source_url = img_url

        date_el = box.select_one(".rocom_lineup_list_date")
        card_updated_at = ""
        if date_el:
            card_updated_at = date_el.get_text(" ", strip=True).replace("最后更新日期:", "").strip()

        cards.append({
            "id": lineup_id,
            "name": title,
            "source_url": source_url,
            "source_title": f"精灵阵容/{lineup_id}",
            "magic": magic_name,
            "magic_icon_source_url": magic_icon_source_url,
            "card_updated_at": card_updated_at,
            "members_preview": members_preview,
        })

    return cards


def fetch_lineup_wikitext(source_title: str) -> str:
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": source_title,
        "rvprop": "content",
        "formatversion": "2",
        "format": "json",
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    data = fetch_json(url)
    try:
        return data["query"]["pages"][0]["revisions"][0].get("content", "")
    except Exception:
        return ""


def parse_template_fields(wikitext: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in wikitext.splitlines():
        if not line.startswith("|"):
            continue
        key, sep, value = line[1:].partition("=")
        if not sep:
            continue
        fields[key.strip()] = value.strip()
    return fields


def iv_config_from_names(iv_names: list[str]) -> dict[str, int]:
    config = {"hp": 0, "atk": 0, "def": 0, "spatk": 0, "spdef": 0, "speed": 0}
    for name in iv_names:
        key = IV_KEY_MAP.get(name.strip())
        if key:
            config[key] = 60
    return config


def parse_member(fields: dict[str, str], index: int, preview: dict | None = None) -> dict:
    prefix = f"阵容精灵{index}"
    iv_names = [part.strip() for part in fields.get(f"{prefix}个体值", "").split(",") if part.strip()]
    skills = [
        fields.get(f"{prefix}技能{i}", "").strip()
        for i in range(1, 5)
        if fields.get(f"{prefix}技能{i}", "").strip()
    ]
    preview = preview or {}
    return {
        "slot": index,
        "name": fields.get(prefix, "").strip(),
        "card_name": preview.get("card_name", ""),
        "bloodline": fields.get(f"{prefix}血脉", "").strip(),
        "nature": fields.get(f"{prefix}性格", "").strip(),
        "iv_names": iv_names,
        "iv_config": iv_config_from_names(iv_names),
        "skills": skills,
        "card_avatar_source_url": preview.get("card_avatar_source_url", ""),
    }


def merge_detail(card: dict) -> dict:
    wikitext = fetch_lineup_wikitext(card["source_title"])
    fields = parse_template_fields(wikitext)
    previews = {
        int(item.get("slot") or 0): item
        for item in card.get("members_preview", [])
        if item.get("slot")
    }
    members = [
        parse_member(fields, i, previews.get(i))
        for i in range(1, 7)
        if fields.get(f"阵容精灵{i}", "").strip()
    ]
    return {
        "id": fields.get("阵容编号", card["id"]).strip() or card["id"],
        "name": fields.get("阵容标题", card["name"]).strip() or card["name"],
        "type": fields.get("阵容类型", "pvp").strip() or "pvp",
        "magic": fields.get("阵容血脉魔法", card.get("magic", "")).strip() or card.get("magic", ""),
        "magic_label": "愿力冲击" if (fields.get("阵容血脉魔法", card.get("magic", ""))).strip() == "强化术" else (fields.get("阵容血脉魔法", card.get("magic", "")).strip() or card.get("magic", "")),
        "description": fields.get("阵容介绍", "").strip(),
        "author": fields.get("阵容作者", "").strip(),
        "updated_at": fields.get("阵容上传日期", card.get("card_updated_at", "")).strip() or card.get("card_updated_at", ""),
        "source_url": card["source_url"],
        "source_title": card["source_title"],
        "members": members,
    }


def download_magic_icons(cards: list[dict], force: bool = False) -> dict[str, dict]:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    icon_map: dict[str, dict] = {}
    for card in cards:
        name = card.get("magic", "").strip()
        url = card.get("magic_icon_source_url", "").strip()
        if not name or not url or name in icon_map:
            continue
        filename = safe_filename(name, url)
        path = ICON_DIR / filename
        if force or not path.exists():
            data = fetch_bytes(url)
            if data:
                path.write_bytes(data)
        if path.exists():
            icon_map[name] = {
                "name": name,
                "filename": filename,
                "local_url": local_lineup_icon_url(filename),
                "source_url": url,
            }
    return icon_map


def crawl(limit: int = 0, workers: int = 8, force_icons: bool = False) -> dict:
    html = fetch_text(LINEUP_LIST_URL)
    if not html:
        raise RuntimeError("阵容一览页面获取失败")
    cards = parse_pvp_cards(html)
    if limit > 0:
        cards = cards[:limit]
    print(f"[INFO] 发现 PVP 阵容 {len(cards)} 个")

    icon_map = download_magic_icons(cards, force=force_icons)
    lineups: list[dict] = []
    done = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(merge_detail, card): card for card in cards}
        for future in as_completed(futures):
            card = futures[future]
            try:
                item = future.result()
            except Exception as exc:
                print(f"  [ERROR] {card['name']}: {exc}")
                failed += 1
                continue
            magic_icon = icon_map.get(item.get("magic", ""))
            if magic_icon:
                item["magic_icon_url"] = magic_icon["local_url"]
                item["magic_icon_source_url"] = magic_icon["source_url"]
            else:
                item["magic_icon_url"] = ""
                item["magic_icon_source_url"] = card.get("magic_icon_source_url", "")
            if len(item.get("members") or []) == 6:
                lineups.append(item)
            else:
                failed += 1
            done += 1
            if done % 20 == 0 or done == len(cards):
                print(f"  详情 {done}/{len(cards)}，有效 {len(lineups)}，失败 {failed}")

    lineups.sort(key=lambda row: (row.get("updated_at", ""), row.get("name", "")), reverse=True)
    return {
        "ok": True,
        "source": LINEUP_LIST_URL,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(lineups),
        "magic_icons": sorted(icon_map.values(), key=lambda item: item["name"]),
        "lineups": lineups,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl BiliGame Roco PVP lineups.")
    parser.add_argument("--limit", type=int, default=0, help="只抓前 N 个阵容，用于调试。")
    parser.add_argument("--workers", type=int, default=8, help="并发详情页数量。")
    parser.add_argument("--force-icons", action="store_true", help="重新下载血脉魔法图标。")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = crawl(limit=args.limit, workers=args.workers, force_icons=args.force_icons)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 写入 {OUTPUT_JSON}，阵容 {data['total']} 个，图标 {len(data['magic_icons'])} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
