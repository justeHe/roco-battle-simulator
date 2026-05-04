#!/usr/bin/env python3
"""
洛克王国精灵图鉴爬虫
从 wiki.biligame.com 爬取所有精灵的：
1. 立绘图片（icon）
2. 进化链信息
3. 身高体重区间
输出：
- data/spirit_icons/ 目录下所有精灵图片
- data/spirit_evolution.csv 记录进化链+身高体重
"""

import csv
import argparse
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

BASE_URL = "https://wiki.biligame.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://wiki.biligame.com/",
}

# 项目根目录
ROOT = Path(__file__).resolve().parent.parent
ICON_DIR = ROOT / "data" / "spirit_icons"
CSV_PATH = ROOT / "data" / "spirit_evolution.csv"
ICON_MANIFEST_PATH = ROOT / "data" / "spirit_icons_manifest.csv"


def fetch(url: str, retries: int = 3) -> str:
    """带重试的 HTTP GET"""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1 + attempt)
            else:
                print(f"  [ERROR] Failed to fetch {url}: {e}")
                return ""


def fetch_bytes(url: str, retries: int = 3) -> bytes:
    """带重试的二进制下载"""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1 + attempt)
            else:
                print(f"  [ERROR] Failed to download {url}: {e}")
                return b""


def parse_spirit_list(html: str) -> list[dict]:
    """
    从精灵图鉴主页解析精灵卡片。

    当前 Wiki 卡片中每个 divsort 下有一张宠物立绘：
      alt="页面 宠物 立绘 鸭吉吉（蓬松的样子） 1.png"

    这里以图片 alt/title 为准，保留不同形态、不同样子、异色等完整展示名。
    """
    spirits = []
    soup = BeautifulSoup(html, "lxml")
    seen = set()

    for card in soup.select("div.divsort"):
        text = card.get_text(" ", strip=True)
        m_num = re.search(r"NO\.\d+", text)
        if not m_num:
            continue
        number = m_num.group(0)

        for img in card.find_all("img"):
            alt = (img.get("alt") or "").strip()
            if "页面 宠物 立绘" not in alt:
                continue

            m_alt = re.match(r"页面\s+宠物\s+立绘\s+(.+?)\s+\d+\.png$", alt)
            if not m_alt:
                continue
            name = m_alt.group(1).strip()
            if name.endswith(" 异色"):
                name = name[:-3].strip() + "（异色）"

            link = img.find_parent("a")
            if not link:
                link = card.find("a", href=re.compile(r"^/rocom/"))
            detail_path = link.get("href", "") if link else ""
            detail_url = urljoin(BASE_URL, detail_path) if detail_path else ""

            img_url = img.get("src") or img.get("data-src") or ""
            img_url = urljoin(BASE_URL, img_url)

            key = (number, name, img_url)
            if key in seen:
                continue
            seen.add(key)

            spirits.append({
                "number": number,
                "name": name,
                "stage": card.get("data-param1", ""),
                "element": card.get("data-param2", ""),
                "form_type": card.get("data-param4", ""),
                "form": card.get("data-param5", ""),
                "has_variant": card.get("data-param6", ""),
                "img_url": img_url,
                "detail_url": detail_url,
            })

    return spirits


def get_full_img_url(thumb_url: str) -> str:
    """
    从缩略图 URL 获取原始大图 URL
    缩略图: .../thumb/2/25/xxx.png/180px-yyy.png
    原图:   .../2/25/xxx.png
    """
    if "/thumb/" in thumb_url:
        # 去掉 /thumb/ 前缀和末尾的 /NNNpx-xxx.png
        parts = thumb_url.split("/thumb/")
        if len(parts) == 2:
            after_thumb = parts[1]
            # 找到最后一个 / 之前的部分
            segments = after_thumb.rsplit("/", 1)
            if len(segments) == 2:
                return parts[0] + "/" + segments[0]
    return thumb_url


def safe_icon_filename(spirit: dict) -> str:
    """生成本地精灵图标文件名，保留形态括号以便按完整名称匹配。"""
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]+', "_", spirit["name"]).strip()
    return f"{spirit['number'].replace('.', '')}_{name}.png"


def write_icon_manifest(spirits: list[dict], path: Path = ICON_MANIFEST_PATH) -> None:
    """记录图鉴页解析到的全部本地立绘映射，供后续 UI 展示不同形态。"""
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "编号", "名字", "阶段", "属性", "形态分类", "形态", "是否有异色",
            "图片文件名", "本地URL", "来源图片URL", "详情页URL",
        ])
        for s in spirits:
            filename = safe_icon_filename(s)
            writer.writerow([
                s["number"],
                s["name"],
                s["stage"],
                s["element"],
                s["form_type"],
                s["form"],
                s["has_variant"],
                filename,
                f"/icons/{urllib.parse.quote(filename)}",
                get_full_img_url(s.get("img_url", "")),
                s.get("detail_url", ""),
            ])


def parse_detail_page(html: str, name: str) -> dict:
    """
    从精灵详情页解析进化链和身高体重
    """
    result = {
        "height_range": "",
        "weight_range": "",
        "evolution_chain": "",
        "evolution_levels": "",
        "evolution_condition": "",
    }

    # === 身高体重 ===
    # 身高在"图标 宠物 体质 身高.png"后面的<p>标签中
    height_match = re.search(
        r'alt="图标 宠物 体质 身高\.png".*?</div>\s*<p>([^<]+)</p>\s*<p[^>]*>([^<]*)</p>',
        html, re.DOTALL
    )
    if height_match:
        result["height_range"] = height_match.group(1).strip() + height_match.group(2).strip()

    weight_match = re.search(
        r'alt="图标 宠物 体质 体重\.png".*?</div>\s*<p>([^<]+)</p>\s*<p[^>]*>([^<]*)</p>',
        html, re.DOTALL
    )
    if weight_match:
        result["weight_range"] = weight_match.group(1).strip() + weight_match.group(2).strip()

    # === 进化链 ===
    evo_box = re.search(
        r'<div class="rocom_spirit_evolution_box">(.*?)</div>\s*</div>\s*</div>',
        html, re.DOTALL
    )
    if not evo_box:
        # 尝试更宽松的匹配
        evo_box = re.search(
            r'进化链(.*?)进化条件',
            html, re.DOTALL
        )

    if evo_box:
        evo_html = evo_box.group(1) if evo_box else ""

        # 提取进化链中的精灵名称
        evo_names = re.findall(r'title="([^"]+)"', evo_html)
        # 去重保持顺序
        seen = set()
        unique_names = []
        for n in evo_names:
            if n not in seen:
                seen.add(n)
                unique_names.append(n)
        result["evolution_chain"] = " → ".join(unique_names) if unique_names else name

        # 提取进化等级
        evo_levels = re.findall(
            r'rocom_spirit_evolution_level_num">(\d+)</p>',
            evo_html
        )
        result["evolution_levels"] = ",".join(evo_levels)

    # 进化条件
    cond_match = re.search(
        r'进化条件:\s*<p[^>]*>([^<]+)</p>',
        html
    )
    if cond_match:
        result["evolution_condition"] = cond_match.group(1).strip()

    return result


def download_image(spirit: dict, icon_dir: Path, force: bool = False) -> str:
    """下载精灵图片，返回保存文件名"""
    img_url = spirit.get("img_url", "")
    if not img_url:
        return ""

    # 获取原始大图
    full_url = get_full_img_url(img_url)

    # 文件名：编号_完整形态名.png
    filename = safe_icon_filename(spirit)
    filepath = icon_dir / filename

    if filepath.exists() and not force:
        return filename

    data = fetch_bytes(full_url)
    if data:
        filepath.write_bytes(data)
        return filename
    return ""


def main():
    parser = argparse.ArgumentParser(description="爬取洛克王国精灵图鉴与本地立绘")
    parser.add_argument("--icons-only", action="store_true", help="只解析图鉴主页并下载精灵图标，不爬详情页")
    parser.add_argument("--force-icons", action="store_true", help="重新下载已存在的图标文件")
    parser.add_argument("--workers", type=int, default=5, help="图片并发下载数")
    args = parser.parse_args()

    ICON_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: 获取主页精灵列表
    print("=" * 60)
    print("Step 1: 爬取精灵图鉴主页...")
    print("=" * 60)
    list_url = BASE_URL + "/rocom/%E7%B2%BE%E7%81%B5%E5%9B%BE%E9%89%B4"
    list_html = fetch(list_url)
    if not list_html:
        print("ERROR: 无法获取精灵图鉴主页")
        sys.exit(1)

    spirits = parse_spirit_list(list_html)
    print(f"  共找到 {len(spirits)} 个精灵")

    # 去掉 logo 等非精灵项（编号应为 NO.xxx）
    spirits = [s for s in spirits if s["number"].startswith("NO.")]
    print(f"  过滤后: {len(spirits)} 个有效精灵")

    if args.icons_only:
        print("\n" + "=" * 60)
        print("Step 2: 只下载精灵图标...")
        print("=" * 60)

        downloaded = 0
        failed = 0
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {
                pool.submit(download_image, s, ICON_DIR, args.force_icons): s
                for s in spirits
            }
            for i, future in enumerate(as_completed(futures)):
                name, number = futures[future]["name"], futures[future]["number"]
                try:
                    filename = future.result()
                except Exception as e:
                    filename = ""
                    print(f"  [ERROR] {number} {name}: {e}")
                if filename:
                    downloaded += 1
                else:
                    failed += 1
                if (i + 1) % 50 == 0:
                    print(f"  已处理 {i+1}/{len(spirits)}，成功 {downloaded}，失败 {failed}")

        print(f"  完成: 成功 {downloaded} 张，失败 {failed} 张")
        print(f"  图片保存在: {ICON_DIR}")
        write_icon_manifest(spirits)
        print(f"  图标清单: {ICON_MANIFEST_PATH}")
        print("=" * 60)
        return

    # 先按 detail_url 分组，同一个详情页只爬一次
    detail_urls = {}
    for s in spirits:
        if s["detail_url"] and s["detail_url"] not in detail_urls:
            detail_urls[s["detail_url"]] = s["name"]

    print(f"  独立详情页: {len(detail_urls)} 个")

    # Step 2: 爬取每个精灵的详情页
    print("\n" + "=" * 60)
    print("Step 2: 爬取精灵详情页（进化链 + 身高体重）...")
    print("=" * 60)

    detail_data = {}  # name -> {height, weight, evolution, ...}
    total = len(detail_urls)

    for i, (url, name) in enumerate(detail_urls.items()):
        progress = f"[{i+1}/{total}]"
        print(f"  {progress} 爬取: {name} ...", end="", flush=True)

        html = fetch(url)
        if html:
            info = parse_detail_page(html, name)
            detail_data[name] = info
            evo = info.get("evolution_chain", "")
            h = info.get("height_range", "")
            w = info.get("weight_range", "")
            print(f" ✓ 身高={h} 体重={w} 进化链={evo}")
        else:
            detail_data[name] = {
                "height_range": "",
                "weight_range": "",
                "evolution_chain": name,
                "evolution_levels": "",
                "evolution_condition": "",
            }
            print(" ✗ 失败")

        # 请求间隔，避免被限流
        if (i + 1) % 10 == 0:
            time.sleep(1)
        else:
            time.sleep(0.3)

    # Step 3: 下载所有精灵图片
    print("\n" + "=" * 60)
    print("Step 3: 下载精灵图片...")
    print("=" * 60)

    def download_one(spirit):
        filename = download_image(spirit, ICON_DIR, args.force_icons)
        return spirit["name"], filename

    downloaded = 0
    failed = 0
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {pool.submit(download_one, s): s for s in spirits}
        for i, future in enumerate(as_completed(futures)):
            name, filename = future.result()
            if filename:
                downloaded += 1
            else:
                failed += 1
            if (i + 1) % 50 == 0:
                print(f"  已下载 {downloaded}/{i+1}，失败 {failed}")

    print(f"  完成: 下载 {downloaded} 张，失败 {failed} 张")
    print(f"  图片保存在: {ICON_DIR}")

    # Step 4: 写入 CSV
    print("\n" + "=" * 60)
    print("Step 4: 生成 CSV 文件...")
    print("=" * 60)

    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "编号", "名字", "阶段", "属性",
            "形态分类", "形态", "是否有异色",
            "身高范围", "体重范围",
            "进化链", "进化等级", "进化条件",
            "图片文件名"
        ])

        for s in spirits:
            info = detail_data.get(s["name"], {})
            filename = safe_icon_filename(s)
            img_exists = (ICON_DIR / filename).exists()

            writer.writerow([
                s["number"],
                s["name"],
                s["stage"],
                s["element"],
                s["form_type"],
                s["form"],
                s["has_variant"],
                info.get("height_range", ""),
                info.get("weight_range", ""),
                info.get("evolution_chain", ""),
                info.get("evolution_levels", ""),
                info.get("evolution_condition", ""),
                filename if img_exists else "",
            ])

    print(f"  CSV 保存在: {CSV_PATH}")
    write_icon_manifest(spirits)
    print(f"  图标清单: {ICON_MANIFEST_PATH}")
    print("\n" + "=" * 60)
    print("全部完成!")
    print(f"  精灵总数: {len(spirits)}")
    print(f"  图片目录: {ICON_DIR}")
    print(f"  CSV文件: {CSV_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
