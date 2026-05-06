#!/usr/bin/env python3
"""
从 BiliGame 洛克王国手游 Wiki 爬取精灵特性图标。

入口页:
    https://wiki.biligame.com/rocom/精灵图鉴

输出:
    data/ability_icons/
    data/ability_icons_manifest.csv
"""

from __future__ import annotations

import argparse
import csv
import html as html_lib
import re
import sqlite3
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
BASE_URL = "https://wiki.biligame.com"
SPIRIT_DEX_URL = f"{BASE_URL}/rocom/%E7%B2%BE%E7%81%B5%E5%9B%BE%E9%89%B4"
ABILITY_ICON_DIR = ROOT / "data" / "ability_icons"
ABILITY_MANIFEST_CSV = ROOT / "data" / "ability_icons_manifest.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://wiki.biligame.com/rocom/",
}


def normalize_url(url: str) -> str:
    url = html_lib.unescape((url or "").strip())
    if not url:
        return ""
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return BASE_URL + url
    return url


def get_full_img_url(url: str) -> str:
    url = normalize_url(url)
    if "/thumb/" not in url:
        return url
    before, after = url.split("/thumb/", 1)
    parts = after.rsplit("/", 1)
    return before + "/" + parts[0] if len(parts) == 2 else url


def safe_filename(name: str, url: str = "") -> str:
    stem = re.sub(r"[^\w\u4e00-\u9fff]+", "_", name or "").strip("_") or "ability"
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
        ext = ".png"
    return f"{stem}{ext}"


def local_icon_url(filename: str) -> str:
    return f"/ability-icons/{urllib.parse.quote(filename)}" if filename else ""


def fetch_text(url: str, retries: int = 3, timeout: int = 30) -> str:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except Exception as exc:
            if attempt + 1 >= retries:
                print(f"  [ERROR] 获取失败 {url}: {exc}")
                return ""
            time.sleep(1 + attempt)
    return ""


def fetch_bytes(url: str, retries: int = 3, timeout: int = 30) -> bytes:
    url = normalize_url(url)
    if not url:
        return b""
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


def parse_spirit_detail_links(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    entries: list[dict] = []
    seen: set[str] = set()
    for card in soup.select("div.divsort"):
        text = card.get_text(" ", strip=True)
        number_match = re.search(r"NO\.\d+", text)
        if not number_match:
            continue
        link = card.find("a", href=re.compile(r"^/rocom/"), title=True)
        if not link:
            continue
        name = (link.get("title") or "").strip()
        detail_url = urljoin(BASE_URL, link.get("href", ""))
        if not name or not detail_url:
            continue
        key = f"{name}|{detail_url}"
        if key in seen:
            continue
        seen.add(key)
        entries.append({
            "number": number_match.group(0),
            "name": name,
            "detail_url": detail_url,
        })
    return entries


def parse_abilities_from_detail(html: str, pokemon_name: str, detail_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    rows: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for box in soup.select(".rocom_sprite_info_characteristic_content"):
        title_el = box.select_one(".rocom_sprite_info_characteristic_title")
        effect_el = box.select_one(".rocom_sprite_info_characteristic_text")
        img = box.select_one(".rocom_sprite_info_characteristic_content_icon img")
        ability_name = (title_el.get_text(" ", strip=True) if title_el else "") or (img.get("alt", "") if img else "")
        effect = effect_el.get_text(" ", strip=True) if effect_el else ""
        icon_url = get_full_img_url(img.get("src", "")) if img else ""
        ability_name = ability_name.strip()
        if not ability_name or not icon_url:
            continue
        key = (ability_name, icon_url)
        if key in seen:
            continue
        seen.add(key)
        rows.append({
            "ability_name": ability_name,
            "effect": effect,
            "icon_url": icon_url,
            "source_pokemon": pokemon_name,
            "detail_url": detail_url,
        })
    return rows


def download_icon(ability_name: str, icon_url: str, force: bool = False) -> str:
    ABILITY_ICON_DIR.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(ability_name, icon_url)
    path = ABILITY_ICON_DIR / filename
    if path.exists() and not force:
        return filename
    data = fetch_bytes(icon_url)
    if not data:
        return ""
    path.write_bytes(data)
    return filename


def collect_ability_rows(entries: list[dict], workers: int, limit: int = 0) -> list[dict]:
    targets = entries[:limit] if limit > 0 else entries
    rows: list[dict] = []
    done = 0
    failed = 0

    def crawl_one(entry: dict) -> list[dict]:
        html = fetch_text(entry["detail_url"])
        if not html:
            return []
        return parse_abilities_from_detail(html, entry["name"], entry["detail_url"])

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(crawl_one, entry): entry for entry in targets}
        for future in as_completed(futures):
            entry = futures[future]
            try:
                found = future.result()
            except Exception as exc:
                print(f"  [ERROR] {entry['name']}: {exc}")
                found = []
            if found:
                rows.extend(found)
            else:
                failed += 1
            done += 1
            if done % 40 == 0 or done == len(targets):
                print(f"  详情页 {done}/{len(targets)}，失败 {failed}，已发现 {len(rows)} 条特性记录")
    return rows


def dedupe_abilities(rows: list[dict]) -> list[dict]:
    by_name: dict[str, dict] = {}
    for row in rows:
        name = row["ability_name"]
        item = by_name.setdefault(name, {
            "ability_name": name,
            "effect": row.get("effect", ""),
            "icon_url": row.get("icon_url", ""),
            "source_pokemon": [],
            "detail_urls": [],
            "icon_file": "",
            "local_url": "",
        })
        if not item["effect"] and row.get("effect"):
            item["effect"] = row["effect"]
        if not item["icon_url"] and row.get("icon_url"):
            item["icon_url"] = row["icon_url"]
        if row.get("source_pokemon") and row["source_pokemon"] not in item["source_pokemon"]:
            item["source_pokemon"].append(row["source_pokemon"])
        if row.get("detail_url") and row["detail_url"] not in item["detail_urls"]:
            item["detail_urls"].append(row["detail_url"])
    return sorted(by_name.values(), key=lambda item: item["ability_name"])


def split_ability_name(raw: str) -> str:
    if not raw:
        return ""
    return re.split(r"[:：]", raw, 1)[0].strip()


def load_db_ability_sources() -> dict[str, list[str]]:
    db_path = ROOT / "data" / "nrc.db"
    if not db_path.exists():
        return {}
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        c = conn.cursor()
        c.execute("""
            SELECT name, ability
            FROM pokemon
            WHERE COALESCE(ability, '') <> '' AND ability <> ':'
            ORDER BY id
        """)
        sources: dict[str, list[str]] = {}
        for row in c.fetchall():
            ability_name = split_ability_name(row["ability"])
            if not ability_name:
                continue
            sources.setdefault(ability_name, [])
            if row["name"] not in sources[ability_name]:
                sources[ability_name].append(row["name"])
        return sources
    finally:
        conn.close()


def supplement_from_db(abilities: list[dict], workers: int) -> list[dict]:
    """用本地 DB 的特性名回补 Wiki 图鉴页并发漏抓的详情页。"""
    db_sources = load_db_ability_sources()
    if not db_sources:
        return abilities
    found_names = {item["ability_name"] for item in abilities}
    missing_names = sorted(set(db_sources) - found_names)
    if not missing_names:
        return abilities

    print(f"  本地 DB 中还有 {len(missing_names)} 个特性缺少图标，开始回补...")
    rows = collect_db_ability_rows(
        {name: db_sources[name] for name in missing_names},
        workers=min(workers, 2),
    )
    merged = {item["ability_name"]: item for item in abilities}
    for item in dedupe_abilities(rows):
        merged.setdefault(item["ability_name"], item)
    still_missing = sorted(set(db_sources) - set(merged))
    if still_missing:
        print(f"  [WARN] 仍缺少 {len(still_missing)} 个特性图标: {', '.join(still_missing[:20])}")
    return sorted(merged.values(), key=lambda item: item["ability_name"])


def collect_db_ability_rows(db_sources: dict[str, list[str]], workers: int = 2) -> list[dict]:
    targets = []
    for ability_name, pokemon_names in db_sources.items():
        for pokemon_name in pokemon_names[:4]:
            targets.append({
                "ability_name": ability_name,
                "pokemon_name": pokemon_name,
                "detail_url": f"{BASE_URL}/rocom/{urllib.parse.quote(pokemon_name, safe='')}",
            })

    rows: list[dict] = []

    def crawl_one(target: dict) -> list[dict]:
        time.sleep(0.08)
        html = fetch_text(target["detail_url"], retries=4)
        if not html:
            return []
        parsed = parse_abilities_from_detail(html, target["pokemon_name"], target["detail_url"])
        return [row for row in parsed if row["ability_name"] == target["ability_name"]]

    done = 0
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(crawl_one, target): target for target in targets}
        for future in as_completed(futures):
            target = futures[future]
            try:
                found = future.result()
            except Exception as exc:
                print(f"  [ERROR] 回补 {target['ability_name']} / {target['pokemon_name']}: {exc}")
                found = []
            rows.extend(found)
            done += 1
            if done % 30 == 0 or done == len(targets):
                print(f"  回补详情页 {done}/{len(targets)}，新增记录 {len(rows)}")
    return rows


def write_manifest(rows: list[dict]) -> None:
    ABILITY_MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(ABILITY_MANIFEST_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["特性名", "效果", "图标文件", "本地URL", "远程URL", "来源精灵", "详情页"])
        for row in rows:
            writer.writerow([
                row["ability_name"],
                row.get("effect", ""),
                row.get("icon_file", ""),
                row.get("local_url", ""),
                row.get("icon_url", ""),
                "|".join(row.get("source_pokemon", [])),
                "|".join(row.get("detail_urls", [])),
            ])


def main() -> None:
    parser = argparse.ArgumentParser(description="爬取 BiliGame Wiki 精灵特性图标")
    parser.add_argument("--limit", type=int, default=0, help="限制处理精灵详情页数量，0=全部")
    parser.add_argument("--workers", type=int, default=8, help="详情页并发请求数")
    parser.add_argument("--force-icons", action="store_true", help="重新下载已存在图标")
    parser.add_argument("--dry-run", action="store_true", help="只解析并打印，不下载/写入")
    parser.add_argument("--db-only", action="store_true", help="只按本地 data/nrc.db 中的精灵特性回补图标")
    args = parser.parse_args()

    if args.db_only:
        db_sources = load_db_ability_sources()
        if not db_sources:
            print("[ERROR] 未找到本地 DB 特性数据")
            sys.exit(1)
        print(f"本地 DB 特性: {len(db_sources)}")
        raw_rows = collect_db_ability_rows(db_sources, workers=min(args.workers, 2))
        abilities = dedupe_abilities(raw_rows)
        print(f"  DB 回补解析到特性: {len(abilities)}")
    else:
        print("正在读取精灵图鉴页...")
        html = fetch_text(SPIRIT_DEX_URL)
        if not html:
            print("[ERROR] 无法获取精灵图鉴页")
            sys.exit(1)

        entries = parse_spirit_detail_links(html)
        print(f"  图鉴卡片详情链接: {len(entries)}")
        if not entries:
            print("[ERROR] 未解析到精灵详情链接")
            sys.exit(1)

        raw_rows = collect_ability_rows(entries, workers=args.workers, limit=args.limit)
        abilities = dedupe_abilities(raw_rows)
        print(f"  去重后特性: {len(abilities)}")
        if args.limit <= 0:
            abilities = supplement_from_db(abilities, workers=args.workers)
            print(f"  回补后特性: {len(abilities)}")

    if args.dry_run:
        for item in abilities[:20]:
            print(f"  {item['ability_name']}: {item['icon_url']}")
        print("  [dry-run] 未下载或写入文件")
        return

    success = 0
    for i, item in enumerate(abilities, start=1):
        filename = download_icon(item["ability_name"], item["icon_url"], force=args.force_icons)
        item["icon_file"] = filename
        item["local_url"] = local_icon_url(filename)
        if filename:
            success += 1
        if i % 50 == 0 or i == len(abilities):
            print(f"  图标 {i}/{len(abilities)}，成功 {success}")

    write_manifest(abilities)
    print(f"完成：下载 {success}/{len(abilities)} 个特性图标")
    print(f"图标目录：{ABILITY_ICON_DIR}")
    print(f"清单文件：{ABILITY_MANIFEST_CSV}")


if __name__ == "__main__":
    main()
