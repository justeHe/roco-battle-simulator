"""
scripts/scrape_skills_bilibili.py

从 wiki.biligame.com/rocom 批量抓取技能数据
参照 scrape_skills.py 的爬取方式，目标网站为 biligame 洛克王国手游 WIKI

输出 CSV: 技能名，属性，分类，耗能，威力，技能描述，可学习精灵列表

工作流程:
1. 从技能图鉴页面 (wiki.biligame.com/rocom/技能图鉴) 获取最新技能名称列表
2. 遍历每个技能名称，爬取对应的技能详情页
3. 解析属性、分类、耗能、威力、技能描述、可学习精灵
4. 保存到 CSV 文件和进度文件

页面结构解析:
- 属性：从 rocom_skill_template_skillAttribute 中的图片 alt 提取
- 分类：从 rocom_skill_template_skillSort 中的图片 alt 提取
- 耗能：从 rocom_skill_template_skillConsume_box 中的数字提取
- 威力：从 rocom_skill_template_skillPower 中的 <b> 标签提取
- 技能描述：从 rocom_skill_template_skillEffect 提取
- 可学习精灵：从 rocom_canlearn_img_box 中的 title 属性提取

用法:
    # 测试单个技能
    python3 scripts/scrape_skills_bilibili.py --test 冰锋横扫

    # 爬取全部技能
    python3 scripts/scrape_skills_bilibili.py

    # 限制爬取数量
    python3 scripts/scrape_skills_bilibili.py --limit 50

    # 从上次进度继续
    python3 scripts/scrape_skills_bilibili.py --resume

    # 干运行（不写入文件）
    python3 scripts/scrape_skills_bilibili.py --dry-run

输出文件:
    - data/skills_bilibili.csv: 爬取的技能数据
    - data/skill_icons_manifest.csv: --icons-only 生成的图标清单
    - data/skill_icons/: 本地技能图标
    - data/scrape_bilibili_progress.json: 爬取进度（用于断点续爬）

对比 scrape_skills.py:
    - scrape_skills.py: 爬取 rocoworldwiki.com，使用 browser 自动化
    - scrape_skills_bilibili.py: 爬取 wiki.biligame.com，使用 urllib 直接请求
"""

import argparse
import csv
import html as html_lib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional

# 项目根目录
ROOT = Path(__file__).resolve().parents[2]
OUTPUT_CSV = ROOT / "data" / "skills_bilibili.csv"
ICON_MANIFEST_CSV = ROOT / "data" / "skill_icons_manifest.csv"
PROGRESS_FILE = ROOT / "data" / "scrape_bilibili_progress.json"
SKILL_ICON_DIR = ROOT / "data" / "skill_icons"
SKILL_META_ICON_DIR = ROOT / "data" / "skill_meta_icons"
META_ICON_MANIFEST_CSV = ROOT / "data" / "skill_meta_icons_manifest.csv"

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://wiki.biligame.com/",
}

DELAY = 0.5  # 技能详情请求间隔秒数
ICON_DELAY = 0.03  # 图标下载间隔秒数

# 技能图鉴页面 URL
SKILL_LIST_URL = "https://wiki.biligame.com/rocom/%E6%8A%80%E8%83%BD%E5%9B%BE%E9%89%B4"
FIELDNAMES = [
    '技能名', '属性', '分类', '耗能', '威力', '技能描述', '可学习精灵',
    '技能图标', '技能图标文件', '属性图标', '分类图标', '技能组', 'Wiki地址',
]


def normalize_url(url: str) -> str:
    """把 Wiki 中的相对/协议相对资源地址转成完整 URL。"""
    if not url:
        return ""
    url = html_lib.unescape(url.strip())
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return "https://wiki.biligame.com" + url
    return url


def get_full_img_url(url: str) -> str:
    """
    从缩略图 URL 获取原始图 URL。
    缩略图: .../thumb/9/9b/file.png/35px-name.png
    原图:   .../9/9b/file.png
    """
    url = normalize_url(url)
    if "/thumb/" not in url:
        return url
    before, after = url.split("/thumb/", 1)
    pieces = after.rsplit("/", 1)
    if len(pieces) == 2:
        return before + "/" + pieces[0]
    return url


def safe_filename(name: str, url: str = "") -> str:
    """生成稳定的本地图标文件名。"""
    safe_name = re.sub(r'[^\w\u4e00-\u9fff]+', '_', name).strip('_')
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        ext = ".png"
    return f"{safe_name or 'skill'}{ext}"


def local_skill_icon_url(filename: str) -> str:
    return f"/skill-icons/{urllib.parse.quote(filename)}" if filename else ""


def local_meta_icon_url(kind: str, filename: str) -> str:
    return f"/skill-meta-icons/{kind}/{urllib.parse.quote(filename)}" if filename else ""


def safe_meta_filename(name: str, url: str = "") -> str:
    safe_name = re.sub(r'[^\w\u4e00-\u9fff]+', '_', name).strip('_')
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
        ext = ".png"
    return f"{safe_name or 'icon'}{ext}"


def extract_data_param(text: str, key: str) -> str:
    match = re.search(rf'{key}="([^"]*)"', text)
    return html_lib.unescape(match.group(1).strip()) if match else ""


def extract_img_src(html: str, class_name: str) -> str:
    """按 class 名提取图片 src，兼容 src 在 class 前后的两种写法。"""
    for img_match in re.finditer(r'<img\b[^>]*>', html, re.DOTALL):
        tag = img_match.group(0)
        if class_name not in tag:
            continue
        src_match = re.search(r'\bsrc="([^"]+)"', tag)
        if src_match:
            return get_full_img_url(src_match.group(1))
    return ""


def parse_skill_catalog(html: str) -> List[Dict[str, str]]:
    """
    从技能图鉴页解析技能卡片元数据。

    data-param0 目前 Wiki 多数为 0，保留为“技能组”原始字段，方便后续 Wiki
    若补充分组时无需再改 CSV 结构。真正的精灵学习来源分组由
    scripts/crawl_pokemon_skills.py 写入 pokemon_skill.learn_group。
    """
    entries: List[Dict[str, str]] = []
    for card_html in re.split(r'(?=<div\s+class="divsort")', html):
        if 'class="divsort"' not in card_html or 'rocom_skill_bg_img' not in card_html:
            continue
        div_match = re.search(r'<div\s+class="divsort"([^>]*)>', card_html)
        attrs = div_match.group(1) if div_match else ""
        link_match = re.search(r'<a\s+href="(/rocom/[^"]+)"\s+title="([^"]+)"', card_html)
        if not link_match:
            continue
        name = html_lib.unescape(link_match.group(2).strip())
        if not name or len(name) > 30:
            continue
        skill_icon = extract_img_src(card_html, "rocom_skill_bg_img")
        attribute_icon = extract_img_src(card_html, "rocom_skill_attribute_icon")
        entries.append({
            "技能名": name,
            "分类": extract_data_param(attrs, "data-param1"),
            "属性": extract_data_param(attrs, "data-param2"),
            "技能组": extract_data_param(attrs, "data-param0"),
            "技能图标": skill_icon,
            "技能图标文件": "",
            "属性图标": attribute_icon,
            "Wiki地址": normalize_url(link_match.group(1)),
        })

    # 去重并保持顺序
    deduped: List[Dict[str, str]] = []
    seen = set()
    for entry in entries:
        name = entry["技能名"]
        if name in seen:
            continue
        seen.add(name)
        deduped.append(entry)
    return deduped


def fetch_skill_catalog_from_wiki() -> List[Dict[str, str]]:
    """从 wiki.biligame.com/rocom/技能图鉴 获取技能卡片元数据。"""
    print("正在从技能图鉴页面获取技能列表...")

    html = fetch(SKILL_LIST_URL)
    if not html:
        print("[ERROR] 无法获取技能图鉴页面")
        return []

    catalog = parse_skill_catalog(html)
    if catalog:
        print(f"  共找到 {len(catalog)} 个技能卡片")
        return catalog

    # 兜底：旧版 title 链接提取
    skill_matches = re.findall(r'href="/rocom/[^"]+"\s+title="([^"]+)"', html)
    unique_skills = list(dict.fromkeys(skill_matches))
    catalog = [{"技能名": name} for name in unique_skills]
    print(f"  共找到 {len(catalog)} 个技能链接（兜底模式）")
    return catalog


def fetch_skill_list_from_wiki() -> List[str]:
    """从 wiki.biligame.com/rocom/技能图鉴 获取所有技能名称列表"""
    catalog = fetch_skill_catalog_from_wiki()
    filtered_skills = []
    for entry in catalog:
        name = entry.get("技能名", "")
        # 排除明显的非技能项
        if name in ["首页", "图鉴", "技能图鉴"]:
            continue
        # 长度限制：2-15（留有余量，实际最长技能名为 11）
        if len(name) < 2 or len(name) > 15:
            continue
        # 排除包含特殊字符的项（如"本页面过去的版本 [h]"）
        if '[' in name or ']' in name:
            continue
        # 排除包含"版本"或"页面"的项（WIKI 系统页面）
        if "版本" in name or "页面" in name:
            continue
        filtered_skills.append(name)

    print(f"  过滤后 {len(filtered_skills)} 个技能")
    return filtered_skills


def fetch(url: str, retries: int = 3) -> str:
    """带重试的 HTTP GET"""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1 + attempt)
            else:
                print(f"请求失败：{e}")
                return ""


def fetch_bytes(url: str, retries: int = 3) -> bytes:
    """带重试的二进制 HTTP GET，用于下载图标。"""
    url = normalize_url(url)
    if not url:
        return b""
    for attempt in range(retries):
        try:
            headers = dict(HEADERS)
            headers["Accept"] = "image/avif,image/webp,image/apng,image/png,image/*,*/*;q=0.8"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1 + attempt)
            else:
                print(f"下载失败：{url} ({e})")
                return b""


def download_skill_icon(entry: Dict[str, str], force: bool = False) -> str:
    """下载单个技能图标，返回保存文件名。"""
    icon_url = entry.get("技能图标", "")
    name = entry.get("技能名", "")
    if not icon_url or not name:
        return ""

    SKILL_ICON_DIR.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(name, icon_url)
    path = SKILL_ICON_DIR / filename
    if path.exists() and not force:
        entry["技能图标文件"] = filename
        return filename

    data = fetch_bytes(icon_url)
    if not data:
        return ""
    path.write_bytes(data)
    entry["技能图标文件"] = filename
    return filename


def download_meta_icon(kind: str, name: str, url: str, force: bool = False) -> str:
    """下载技能元信息图标（属性/分类），返回保存文件名。"""
    if not name or not url:
        return ""
    icon_dir = SKILL_META_ICON_DIR / kind
    icon_dir.mkdir(parents=True, exist_ok=True)
    filename = safe_meta_filename(name, url)
    path = icon_dir / filename
    if path.exists() and not force:
        return filename
    data = fetch_bytes(url)
    if not data:
        return ""
    path.write_bytes(data)
    return filename


def write_energy_icon(force: bool = False) -> str:
    """Wiki 的耗能是样式化数字块，这里保存一个本地等价 SVG 图标。"""
    icon_dir = SKILL_META_ICON_DIR / "misc"
    icon_dir.mkdir(parents=True, exist_ok=True)
    path = icon_dir / "energy.svg"
    if path.exists() and not force:
        return path.name
    path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
<defs><linearGradient id="g" x1="10" y1="4" x2="38" y2="44" gradientUnits="userSpaceOnUse"><stop stop-color="#ffe07a"/><stop offset="1" stop-color="#f5a623"/></linearGradient></defs>
<rect x="7" y="7" width="34" height="34" rx="10" fill="url(#g)" stroke="#8a5a00" stroke-width="3"/>
<path d="M26 11 15 27h8l-2 10 12-17h-8l1-9Z" fill="#fff8cf" stroke="#8a5a00" stroke-linejoin="round" stroke-width="2"/>
</svg>
""",
        encoding="utf-8",
    )
    return path.name


def collect_category_icon_entries(catalog: List[Dict[str, str]]) -> Dict[str, str]:
    """通过少量详情页收集物攻/魔攻/状态/防御等分类图标。"""
    category_icons: Dict[str, str] = {}
    for entry in catalog:
        category = entry.get("分类", "")
        if not category or category in category_icons:
            continue
        data = scrape_skill(entry.get("技能名", ""), entry)
        if data and data.get("分类") and data.get("分类图标"):
            category_icons[data["分类"]] = data["分类图标"]
        time.sleep(DELAY)
    return category_icons


def download_meta_icons(catalog: List[Dict[str, str]], force: bool = False,
                        dry_run: bool = False) -> List[Dict[str, str]]:
    """下载系别、技能分类和耗能图标，返回清单行。"""
    rows: List[Dict[str, str]] = []
    element_icons: Dict[str, str] = {}
    for entry in catalog:
        element = entry.get("属性", "")
        icon_url = entry.get("属性图标", "")
        if element and icon_url and element not in element_icons:
            element_icons[element] = icon_url

    print(f"正在整理 {len(element_icons)} 个系别图标...")
    for element, icon_url in sorted(element_icons.items()):
        filename = safe_meta_filename(element, icon_url) if dry_run else download_meta_icon("elements", element, icon_url, force)
        rows.append({
            "类型": "element",
            "名称": element,
            "远程URL": icon_url,
            "本地文件": filename,
            "本地URL": local_meta_icon_url("elements", filename),
        })

    print("正在从技能详情页整理分类图标...")
    category_icons = collect_category_icon_entries(catalog)
    for category, icon_url in sorted(category_icons.items()):
        filename = safe_meta_filename(category, icon_url) if dry_run else download_meta_icon("categories", category, icon_url, force)
        rows.append({
            "类型": "category",
            "名称": category,
            "远程URL": icon_url,
            "本地文件": filename,
            "本地URL": local_meta_icon_url("categories", filename),
        })

    energy_file = "energy.svg" if dry_run else write_energy_icon(force)
    rows.append({
        "类型": "misc",
        "名称": "耗能",
        "远程URL": "",
        "本地文件": energy_file,
        "本地URL": local_meta_icon_url("misc", energy_file),
    })
    return rows


def download_catalog_icons(catalog: List[Dict[str, str]], names: Optional[set] = None,
                           force: bool = False, dry_run: bool = False) -> int:
    """从技能图鉴卡片元数据批量下载技能图标。"""
    targets = [entry for entry in catalog if (not names or entry.get("技能名") in names)]
    if dry_run:
        for entry in targets:
            if entry.get("技能图标"):
                entry["技能图标文件"] = safe_filename(entry.get("技能名", ""), entry.get("技能图标", ""))
        print(f"  [dry-run] 将下载 {sum(1 for e in targets if e.get('技能图标'))} 个技能图标到 {SKILL_ICON_DIR}")
        return 0

    print(f"正在下载技能图标到 {SKILL_ICON_DIR} ...")
    success = 0
    failed = 0
    for i, entry in enumerate(targets, start=1):
        if not entry.get("技能图标"):
            failed += 1
            continue
        filename = download_skill_icon(entry, force=force)
        if filename:
            success += 1
        else:
            failed += 1
        if i % 50 == 0 or i == len(targets):
            print(f"  图标进度 {i}/{len(targets)}，成功 {success}，失败 {failed}")
        time.sleep(ICON_DELAY)
    return success


def extract_text(html: str, pattern: str) -> str:
    """提取文本并清理"""
    match = re.search(pattern, html)
    if match:
        text = match.group(1)
        # 去掉 HTML 标签
        text = re.sub(r'<[^>]+>', '', text)
        # 清理空白
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    return ""


def parse_skill_page(html: str, skill_name: str) -> Optional[Dict]:
    """
    从技能详情页解析数据

    页面结构:
    - rocom_skill_template_skillAttribute: 属性 (如"冰系")
    - rocom_skill_template_skillConsume_box: 耗能 (如"<span>4</span>")
    - rocom_skill_template_skillSort: 分类 (如"魔攻" 带图片)
    - rocom_skill_template_skillPower: 威力 (如"<b>0</b>")
    - rocom_skill_template_skillEffect: 技能效果描述
    - rocom_skill_template_skillDescribe: 技能简介 (可选)

    返回 {
        "技能名": str,
        "属性": str,
        "分类": str,
        "耗能": str,
        "威力": str,
        "技能描述": str,
        "可学习精灵": str (用 | 分隔),
    }
    """
    result = {
        "技能名": skill_name,
        "属性": "",
        "分类": "",
        "耗能": "",
        "威力": "",
        "技能描述": "",
        "可学习精灵": "",
        "技能图标": "",
        "技能图标文件": "",
        "属性图标": "",
        "分类图标": "",
        "技能组": "",
        "Wiki地址": f"https://wiki.biligame.com/rocom/{urllib.parse.quote(skill_name, safe='')}",
    }

    # 技能图标：详情页顶部大图
    icon_match = re.search(
        r'class="rocom_skill_template_skillIcon"[^>]*>.*?<img[^>]*src="([^"]+)"',
        html, re.DOTALL
    )
    if icon_match:
        result["技能图标"] = get_full_img_url(icon_match.group(1))

    # 属性：从图片 alt 提取，如"图标 宠物 属性 冰.png" → "冰"
    attr_match = re.search(
        r'class="rocom_skill_template_skillAttribute"[^>]*>.*?<img[^>]*alt="图标 宠物 属性 ([^".]+)\.png"[^>]*src="([^"]+)"',
        html, re.DOTALL
    )
    if attr_match:
        result["属性"] = attr_match.group(1)
        result["属性图标"] = get_full_img_url(attr_match.group(2))

    # 耗能：rocom_skill_template_skillConsume_box 中的数字
    energy_match = re.search(
        r'class="rocom_skill_template_skillConsume_box"[^>]*>\s*<span>(\d+)</span>',
        html
    )
    if energy_match:
        result["耗能"] = energy_match.group(1)

    # 分类：从图片 alt 提取，如"图标 技能 技能分类 魔攻.png" → "魔攻"
    sort_match = re.search(
        r'class="rocom_skill_template_skillSort"[^>]*>.*?<img[^>]*alt="图标 技能 技能分类 ([^".]+)\.png"[^>]*src="([^"]+)"',
        html, re.DOTALL
    )
    if sort_match:
        result["分类"] = sort_match.group(1)
        result["分类图标"] = get_full_img_url(sort_match.group(2))

    # 威力：rocom_skill_template_skillPower 中的 <b> 数字
    power_match = re.search(
        r'class="rocom_skill_template_skillPower"[^>]*>.*?<b[^>]*>(\d+)</b>',
        html, re.DOTALL
    )
    if power_match:
        result["威力"] = power_match.group(1)

    # 技能效果：rocom_skill_template_skillEffect
    effect_match = re.search(
        r'class="rocom_skill_template_skillEffect"[^>]*>([\s\S]*?)</div>',
        html
    )
    if effect_match:
        effect_html = effect_match.group(1)
        # 去掉 HTML 标签和特殊符号
        effect_text = re.sub(r'<[^>]+>', '', effect_html)
        effect_text = re.sub(r'[✦◆★]\s*', '', effect_text)
        effect_text = re.sub(r'\s+', ' ', effect_text).strip()
        result["技能描述"] = effect_text

    # 技能简介：rocom_skill_template_skillDescribe (可选)
    if not result["技能描述"]:
        desc_match = re.search(
            r'class="rocom_skill_template_skillDescribe"[^>]*>([\s\S]*?)</div>',
            html
        )
        if desc_match:
            desc_html = desc_match.group(1)
            desc_text = re.sub(r'<[^>]+>', '', desc_html)
            desc_text = re.sub(r'\s+', ' ', desc_text).strip()
            if desc_text:
                result["技能描述"] = desc_text

    # 可学习精灵：找"可以学会的精灵"部分 (rocom_canlearn_box)
    # 结构：<div class="rocom_canlearn_img_box"><a href="..." title="电企鹅"><img alt="..." .../></a></div>
    pet_matches = re.findall(
        r'class="rocom_canlearn_img_box"[^>]*>.*?<a[^>]*title="([^"]+)"',
        html, re.DOTALL
    )
    if pet_matches:
        # 去重并保持顺序
        unique_pets = list(dict.fromkeys(pet_matches))
        result["可学习精灵"] = "|".join(unique_pets)

    return result


def scrape_skill(name: str, catalog_entry: Optional[Dict[str, str]] = None) -> Optional[Dict]:
    """爬取单个技能"""
    encoded = urllib.parse.quote(name, safe='')
    url = f"https://wiki.biligame.com/rocom/{encoded}"

    try:
        html = fetch(url)
        if not html:
            return None

        data = parse_skill_page(html, name)
        if data and catalog_entry:
            for key in ["技能图标", "技能图标文件", "属性图标", "分类", "属性", "技能组", "Wiki地址"]:
                if catalog_entry.get(key) and not data.get(key):
                    data[key] = catalog_entry[key]
        return data
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def write_csv(results: List[Dict], path: Path) -> None:
    """写入 CSV 文件"""
    with open(path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)


def load_progress() -> tuple:
    """加载进度"""
    done_names = set()
    results = []
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            done_names = set(data.get("done", []))
            results = data.get("results", [])
    return done_names, results


def save_progress(done_names: set, results: List[Dict]) -> None:
    """保存进度"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"done": list(done_names), "results": results}, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="从 BiliGame Wiki 爬取技能数据")
    parser.add_argument("--test", metavar="NAME", help="只测试单个技能（如 '冰锋横扫'）")
    parser.add_argument("--limit", type=int, default=0, help="限制爬取数量（0=全部）")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不写入文件")
    parser.add_argument("--resume", action="store_true", help="从上次进度继续")
    parser.add_argument("--no-retry", action="store_true", help="不重试失败的条目（默认模式会自动重试直到全部成功）")
    parser.add_argument("--icons-only", action="store_true", help="只下载技能图鉴页中的技能图标，不爬取详情页")
    parser.add_argument("--meta-icons-only", action="store_true", help="只下载系别、技能分类和耗能图标")
    parser.add_argument("--skip-icons", action="store_true", help="不下载技能图标，仅写远程图标 URL")
    parser.add_argument("--force-icons", action="store_true", help="强制重新下载已存在的技能图标")
    args = parser.parse_args()

    # 从 Wiki 获取最新技能列表及卡片元数据
    catalog = fetch_skill_catalog_from_wiki()
    if not catalog:
        print("[ERROR] 无法从 Wiki 获取技能列表，请检查网络连接或网站状态")
        sys.exit(1)
    catalog_by_name = {entry["技能名"]: entry for entry in catalog}
    all_skills = []
    for entry in catalog:
        name = entry.get("技能名", "")
        if name in ["首页", "图鉴", "技能图鉴"]:
            continue
        if len(name) < 2 or len(name) > 15:
            continue
        if '[' in name or ']' in name:
            continue
        if "版本" in name or "页面" in name:
            continue
        all_skills.append(name)
    print(f"  过滤后 {len(all_skills)} 个技能")

    # 测试模式
    if args.test:
        print(f"=== 测试爬取：{args.test} ===")
        data = scrape_skill(args.test, catalog_by_name.get(args.test))
        if data:
            print(f"技能名：{data['技能名']}")
            print(f"属性：{data['属性']}")
            print(f"分类：{data['分类']}")
            print(f"耗能：{data['耗能']}")
            print(f"威力：{data['威力']}")
            print(f"描述：{data['技能描述']}")
            print(f"技能图标：{data.get('技能图标', '')}")
            if not args.skip_icons:
                filename = download_skill_icon(data, force=args.force_icons)
                data["技能图标文件"] = filename
            print(f"技能图标文件：{data.get('技能图标文件', '')}")
            print(f"属性图标：{data.get('属性图标', '')}")
            print(f"分类图标：{data.get('分类图标', '')}")
            print(f"技能组：{data.get('技能组', '')}")
            print(f"Wiki地址：{data.get('Wiki地址', '')}")
            pets = data.get('可学习精灵', '')
            if pets:
                print(f"可学习精灵：{pets[:50]}..." if len(pets) > 50 else f"可学习精灵：{pets}")
        else:
            print("爬取失败")
        return

    # 限制数量
    if args.limit > 0:
        all_skills = all_skills[:args.limit]
    target_names = set(all_skills)

    if args.meta_icons_only:
        rows = download_meta_icons(catalog, force=args.force_icons, dry_run=args.dry_run)
        if not args.dry_run:
            with open(META_ICON_MANIFEST_CSV, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["类型", "名称", "远程URL", "本地文件", "本地URL"])
                writer.writeheader()
                writer.writerows(rows)
        print(f"技能元图标清单保存在：{META_ICON_MANIFEST_CSV}")
        print(f"技能元图标保存在：{SKILL_META_ICON_DIR}")
        return

    if not args.skip_icons:
        download_catalog_icons(
            catalog,
            names=target_names,
            force=args.force_icons,
            dry_run=args.dry_run,
        )

    if args.icons_only:
        icon_rows = []
        for entry in catalog:
            if entry.get("技能名") not in target_names:
                continue
            icon_rows.append({
                "技能名": entry.get("技能名", ""),
                "属性": entry.get("属性", ""),
                "分类": entry.get("分类", ""),
                "耗能": "",
                "威力": "",
                "技能描述": "",
                "可学习精灵": "",
                "技能图标": entry.get("技能图标", ""),
                "技能图标文件": entry.get("技能图标文件", ""),
                "属性图标": entry.get("属性图标", ""),
                "分类图标": entry.get("分类图标", ""),
                "技能组": entry.get("技能组", ""),
                "Wiki地址": entry.get("Wiki地址", ""),
            })
        if not args.dry_run:
            write_csv(icon_rows, ICON_MANIFEST_CSV)
        print(f"图标清单保存在：{ICON_MANIFEST_CSV}")
        print(f"技能图标保存在：{SKILL_ICON_DIR}")
        return

    # 加载进度
    done_names = set()
    results = []
    if args.resume:
        done_names, results = load_progress()
        print(f"恢复进度：已完成 {len(done_names)} 个")

    total = len(all_skills)

    # 主循环：爬取所有技能
    print(f"开始爬取 {len(all_skills)} 个技能...")

    try:
        while True:
            failed_names = []
            round_stats = {"success": 0, "failed": 0, "skipped": 0}

            for i, name in enumerate(all_skills):
                if name in done_names:
                    round_stats["skipped"] += 1
                    continue

                progress = f"[{i+1}/{total}]"
                print(f"{progress} {name}...", end=" ", flush=True)

                data = scrape_skill(name, catalog_by_name.get(name))
                if data and data.get("技能描述"):
                    # 检查是否已存在，存在则更新
                    existing_idx = next((idx for idx, r in enumerate(results) if r["技能名"] == name), None)
                    if existing_idx is not None:
                        results[existing_idx] = data
                    else:
                        results.append(data)
                    done_names.add(name)
                    round_stats["success"] += 1
                    print(f"OK (描述长度={len(data['技能描述'])})")
                else:
                    round_stats["failed"] += 1
                    print(f"FAILED")
                    failed_names.append(name)

                # 定期保存进度
                if (i + 1) % 50 == 0:
                    if not args.dry_run:
                        save_progress(done_names, results)
                        write_csv(results, OUTPUT_CSV)
                        print(f"  >> 已保存 {len(results)} 条记录")

                time.sleep(DELAY)

            # 最终保存
            if not args.dry_run:
                save_progress(done_names, results)
                write_csv(results, OUTPUT_CSV)

            # 打印统计
            print(f"\n本轮完成：共 {len(results)} 条记录")
            print(f"  本轮成功：{round_stats['success']}")
            print(f"  本轮失败：{round_stats['failed']}")
            print(f"  本轮跳过：{round_stats['skipped']}")

            # 如果没有失败项，或者启用了 --no-retry，则退出循环
            if not failed_names or args.no_retry:
                break

            # 否则，准备重试失败的条目
            print(f"\n{len(failed_names)} 个技能爬取失败，准备重试：{', '.join(failed_names)}")
            print("按 Ctrl+C 可中断...")
            time.sleep(2)

            # 重置失败项的完成状态，以便重试
            for name in failed_names:
                done_names.discard(name)
                # 从结果中移除失败的条目（如果存在）
                results = [r for r in results if r["技能名"] != name]

            print(f"开始重试 {len(failed_names)} 个技能...")
            time.sleep(DELAY * 2)  # 重试前等待一下

    except KeyboardInterrupt:
        print("\n\n用户中断爬取")
        if not args.dry_run:
            save_progress(done_names, results)
            write_csv(results, OUTPUT_CSV)
            print(f"进度已保存，共 {len(results)} 条记录")
        print(f"CSV 保存在：{OUTPUT_CSV}")
        print("使用 --resume 参数可从上次进度继续")
        return

    # 全部成功，删除进度文件
    if not args.dry_run and PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()
        print(f"\n进度文件已删除：{PROGRESS_FILE}")

    print(f"CSV 保存在：{OUTPUT_CSV}")


if __name__ == "__main__":
    main()
