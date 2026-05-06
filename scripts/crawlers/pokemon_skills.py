"""
scripts/crawl_pokemon_skills.py

从 wiki.biligame.com/rocom 爬取每只精灵的完整技能列表，
更新 SQLite 数据库中的 pokemon_skill 关联表。

用法:
    python3 scripts/crawl_pokemon_skills.py [--test 圣羽翼王] [--limit N]
"""

import sys, os, time, json, sqlite3, re, argparse
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import requests
from bs4 import BeautifulSoup

# ── 配置 ──
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                       "data", "nrc.db")
BASE_URL = "https://wiki.biligame.com/rocom/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://wiki.biligame.com/rocom/",
}
DELAY = 0.8   # 请求间隔秒数，避免被封

# ── 数据库连接 ──
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_pokemon(conn):
    """从DB获取所有精灵的 id 和 name"""
    c = conn.cursor()
    c.execute("SELECT id, name FROM pokemon ORDER BY id")
    return [(r["id"], r["name"]) for r in c.fetchall()]


def get_pokemon_missing_skill_metadata(conn):
    """获取已有技能关联但缺少学习分组/等级的精灵。"""
    c = conn.cursor()
    c.execute(
        """
        SELECT p.id, p.name
        FROM pokemon p
        JOIN pokemon_skill ps ON ps.pokemon_id = p.id
        GROUP BY p.id, p.name
        HAVING SUM(CASE WHEN COALESCE(ps.learn_group, '') <> '' THEN 1 ELSE 0 END) = 0
        ORDER BY p.id
        """
    )
    return [(r["id"], r["name"]) for r in c.fetchall()]


def ensure_schema(conn):
    """确保精灵-技能关联表能记录学习来源分组。"""
    c = conn.cursor()
    c.execute("PRAGMA table_info(pokemon_skill)")
    columns = {r["name"] for r in c.fetchall()}
    changed = False
    if "learn_group" not in columns:
        c.execute("ALTER TABLE pokemon_skill ADD COLUMN learn_group TEXT DEFAULT ''")
        changed = True
    if "learn_level" not in columns:
        c.execute("ALTER TABLE pokemon_skill ADD COLUMN learn_level TEXT DEFAULT ''")
        changed = True
    if changed:
        conn.commit()
    print("[OK] pokemon_skill learn metadata columns checked")


def get_skill_id(conn, name: str):
    """根据技能名查找技能ID，不存在返回None"""
    c = conn.cursor()
    c.execute("SELECT id FROM skill WHERE name = ?", (name,))
    r = c.fetchone()
    return r["id"] if r else None


def insert_skill(conn, name: str, element: str = "普通", category: str = "状态",
                 energy_cost: int = 0, power: int = 0, description: str = "") -> int:
    """新增技能，返回新技能ID"""
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO skill (name, element, category, energy_cost, power, description, source) "
        "VALUES (?, ?, ?, ?, ?, ?, 'wiki_crawl')",
        (name, element, category, energy_cost, power, description)
    )
    conn.commit()
    c.execute("SELECT id FROM skill WHERE name = ?", (name,))
    r = c.fetchone()
    return r["id"] if r else None


def get_existing_skills_for_pokemon(conn, pokemon_id: int):
    """获取某精灵已有的技能ID集合"""
    c = conn.cursor()
    c.execute("SELECT skill_id FROM pokemon_skill WHERE pokemon_id = ?", (pokemon_id,))
    return {r["skill_id"] for r in c.fetchall()}


def upsert_pokemon_skill(conn, pokemon_id: int, skill_id: int,
                         learn_group: str = "", learn_level: str = ""):
    """插入精灵-技能关联，并记录技能组/学习来源。"""
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO pokemon_skill (pokemon_id, skill_id, learn_group, learn_level) "
        "VALUES (?, ?, ?, ?)",
        (pokemon_id, skill_id, learn_group, learn_level)
    )
    if learn_group or learn_level:
        c.execute(
            "UPDATE pokemon_skill SET learn_group = ?, learn_level = ? "
            "WHERE pokemon_id = ? AND skill_id = ?",
            (learn_group, learn_level, pokemon_id, skill_id)
        )


# ── 爬取单只精灵的技能 ──
def crawl_pokemon_skills(name: str, session: requests.Session, retries: int = 0,
                         retry_delay: float = 1.5) -> dict:
    """
    返回 {tab_name: [{"name": skill_name, "level": "LV1"}]}。
    """
    encoded_name = quote(name, safe='')
    url = BASE_URL + encoded_name
    text = ""
    for attempt in range(retries + 1):
        try:
            r = session.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                r.encoding = 'utf-8'
                text = r.text
                if 'rocom_sprite_skill_tabBox' in text:
                    break
        except Exception as e:
            if attempt >= retries:
                print(f"  ❌ 请求失败: {e}")
                return {}
        if attempt < retries:
            time.sleep(retry_delay)
    if not text:
        return {}

    soup = BeautifulSoup(text, 'lxml')
    result = {}

    # 找技能 tabBox
    tabbox = soup.find('div', class_='rocom_sprite_skill_tabBox')
    if not tabbox:
        # 有些精灵没有技能页面（非战斗精灵）
        return {}

    tabs = tabbox.find_all('div', class_='tabbertab')
    for tab in tabs:
        title = tab.get('title', '').strip()
        if not title:
            continue
        skill_items = []
        seen = set()
        for box in tab.find_all('div', class_='rocom_sprite_skill_box'):
            name_el = box.find('div', class_='rocom_sprite_skillName')
            if not name_el:
                continue
            skill_name = name_el.get_text(strip=True)
            if not skill_name or skill_name in seen:
                continue
            level_el = box.find('div', class_='rocom_sprite_skill_level')
            level = level_el.get_text(" ", strip=True).replace("\xa0", " ") if level_el else ""
            skill_items.append({"name": skill_name, "level": level})
            seen.add(skill_name)

        if not skill_items:
            skill_divs = tab.find_all('div', class_='rocom_sprite_skillName')
            for s in skill_divs:
                skill_name = s.get_text(strip=True)
                if skill_name and skill_name not in seen:
                    skill_items.append({"name": skill_name, "level": ""})
                    seen.add(skill_name)
        skills = skill_items
        if skills:
            result[title] = skills

    return result


# ── 主流程 ──
def main():
    parser = argparse.ArgumentParser(description="爬取 Wiki 精灵技能数据")
    parser.add_argument("--test", metavar="NAME", help="只测试一只精灵（如 '圣羽翼王'）")
    parser.add_argument("--limit", type=int, default=0, help="限制爬取数量（0=全部）")
    parser.add_argument("--delay", type=float, default=DELAY, help="每只精灵请求后的间隔秒数")
    parser.add_argument("--retries", type=int, default=2, help="技能页为空时重试次数")
    parser.add_argument("--missing-only", action="store_true", help="只补齐缺少技能分组的精灵")
    parser.add_argument("--dry-run", action="store_true", help="只打印，不写入DB")
    parser.add_argument("--resume", metavar="FILE", help="从上次保存的进度文件继续")
    args = parser.parse_args()

    conn = get_conn()
    ensure_schema(conn)
    session = requests.Session()

    # ── 测试模式 ──
    if args.test:
        print(f"=== 测试爬取: {args.test} ===")
        result = crawl_pokemon_skills(args.test, session, retries=args.retries)
        total = sum(len(v) for v in result.values())
        print(f"共 {total} 个技能:")
        for tab_name, skills in result.items():
            preview = [f"{s['level'] or '-'} {s['name']}" for s in skills]
            print(f"  [{tab_name}]({len(skills)}个): {preview}")
        return

    # ── 全量爬取 ──
    all_pokemon = get_pokemon_missing_skill_metadata(conn) if args.missing_only else get_all_pokemon(conn)
    if args.limit > 0:
        all_pokemon = all_pokemon[:args.limit]

    total_pokemon = len(all_pokemon)
    print(f"共 {total_pokemon} 只精灵需要处理")

    # 进度存储
    progress_file = args.resume or "data/crawl_progress.json"
    done_names = set()
    if args.resume and os.path.exists(progress_file):
        with open(progress_file) as f:
            done_names = set(json.load(f).get("done", []))
        print(f"恢复进度: 已完成 {len(done_names)} 只")

    stats = {
        "processed": 0, "skipped": 0, "errors": 0,
        "new_skills_added": 0, "new_relations_added": 0,
    }
    done_list = list(done_names)

    for i, (pid, pname) in enumerate(all_pokemon):
        if pname in done_names:
            continue

        print(f"[{i+1}/{total_pokemon}] {pname}...", end=" ", flush=True)

        skills_data = crawl_pokemon_skills(pname, session, retries=args.retries)
        if not skills_data:
            print("(无技能页面)")
            stats["skipped"] += 1
            done_list.append(pname)
            time.sleep(args.delay * 0.5)
            continue

        total_skills = sum(len(v) for v in skills_data.values())
        print(f"{total_skills}个技能", end=" ")

        if not args.dry_run:
            existing = get_existing_skills_for_pokemon(conn, pid)
            new_relations = 0
            for tab_name, skill_items in skills_data.items():
                for item in skill_items:
                    sk_name = item["name"]
                    learn_level = item.get("level", "")
                    sk_id = get_skill_id(conn, sk_name)
                    if sk_id is None:
                        # 技能不在DB里，跳过（不自动新增，避免引入脏数据）
                        continue
                    if sk_id not in existing:
                        upsert_pokemon_skill(conn, pid, sk_id, tab_name, learn_level)
                        new_relations += 1
                        existing.add(sk_id)
                    else:
                        upsert_pokemon_skill(conn, pid, sk_id, tab_name, learn_level)
            conn.commit()
            if new_relations > 0:
                print(f"(+{new_relations}条关联)", end=" ")
                stats["new_relations_added"] += new_relations

        print()
        stats["processed"] += 1
        done_list.append(pname)

        # 定期保存进度
        if (i + 1) % 20 == 0:
            with open(progress_file, "w") as f:
                json.dump({"done": done_list}, f, ensure_ascii=False)
            print(f"  → 进度已保存 ({i+1}/{total_pokemon})")

        time.sleep(args.delay)

    # 最终保存进度
    with open(progress_file, "w") as f:
        json.dump({"done": done_list}, f, ensure_ascii=False)

    conn.close()
    print(f"\n=== 完成 ===")
    print(f"  处理: {stats['processed']} 只")
    print(f"  跳过: {stats['skipped']} 只")
    print(f"  新增关联: {stats['new_relations_added']} 条")


if __name__ == "__main__":
    main()
