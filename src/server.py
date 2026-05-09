"""
洛克王国战斗模拟系统 - Web 图形界面后端 (FastAPI + WebSocket)
"""

import sys
import os
import csv
import json
import re
import urllib.parse
from typing import Optional, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from src.skill_db import load_skills
from src.models import BattleState
from src.effect_models import E, Timing
from src.effect_engine import EffectExecutor
from src.team_builder import TeamBuilder
from src.battle import (
    execute_full_turn, check_winner,
    auto_switch, leader_evolution_status
)

app = FastAPI()

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")

_db_loaded = False
_skill_meta_cache: Optional[dict] = None
_SKILL_ICON_CACHE: dict = {}
_SKILL_META_ICON_CACHE: Optional[dict] = None
_SPIRIT_ICON_META_CACHE: Optional[dict] = None
_MECHANICS_CACHE: Optional[list[dict]] = None
_ABILITY_ICON_CACHE: Optional[dict[str, str]] = None
_EGG_GROUPS_CACHE: Optional[dict] = None
_EGG_MEASUREMENTS_CACHE: Optional[dict] = None
_MECHANIC_ICON_CACHE: Optional[dict[str, str]] = None
_PVP_LINEUPS_CACHE: Optional[dict] = None

_MECHANIC_EXCLUDED_TITLES = {
    "传说印记",
    "命定印记",
    "帕尔印记",
    "技能石/湿润印记",
    "能力等级",
}

_POSITIVE_MARKS = ["湿润印记", "龙噬印记", "蓄势印记", "风起印记", "蓄电印记", "光合印记", "攻击印记"]
_NEGATIVE_MARKS = ["减速印记", "降灵印记", "星陨印记", "中毒印记", "棘刺印记"]
_BATTLE_MARKS = _POSITIVE_MARKS + _NEGATIVE_MARKS

_MECHANIC_SKILL_ICON_MAP = {
    "光合印记": "光合作用",
    "攻击印记": "主场优势",
    "湿润印记": "打湿",
    "蓄势印记": "蓄势待发",
    "风起印记": "风起",
    "龙噬印记": "龙威",
    "蓄电印记": "增程电池",
    "减速印记": "速冻",
    "中毒印记": "疫病吐息",
    "降灵印记": "降灵",
    "星陨印记": "星轨裂变",
    "棘刺印记": "棘刺",
}

_MECHANIC_ELEMENT_ICON_MAP = {
    "中毒": "毒",
    "灼烧": "火",
    "冰冻": "冰",
    "萌化": "萌",
    "奉献": "虫",
    "迅捷": "翼",
    "传动": "机械",
}

_MECHANIC_LOCAL_ICON_MAP = {
    "印记": "/mechanic-icons/%E5%8D%B0%E8%AE%B0.svg",
    "机制": "/mechanic-icons/%E6%9C%BA%E5%88%B6.svg",
    "状态": "/mechanic-icons/%E7%8A%B6%E6%80%81.svg",
}

_POSITIVE_STATUS_TITLES = {
    "物攻等级提升",
    "物防等级提升",
    "魔攻等级提升",
    "魔防等级提升",
    "防御等级提升",
    "速度提升",
    "威力提升",
    "连击等级提升",
    "能耗降低",
    "吸血",
    "先手加一",
}

_NEGATIVE_STATUS_TITLES = {
    "物攻等级降低",
    "物防等级降低",
    "魔攻等级降低",
    "魔防等级降低",
    "速度降低",
    "威力降低",
    "能耗增加",
    "中毒",
    "冻结",
    "灼烧",
    "萌化",
    "寄生",
    "先手减一",
}

_STATUS_CATEGORIES = {"增益状态", "负面状态"}

_TYPE_LABELS = {
    "normal": "普通",
    "grass": "草",
    "fire": "火",
    "water": "水",
    "light": "光",
    "ground": "地",
    "ice": "冰",
    "dragon": "龙",
    "electric": "电",
    "poison": "毒",
    "bug": "虫",
    "fighting": "武",
    "flying": "翼",
    "fairy": "萌",
    "ghost": "幽",
    "dark": "恶",
    "steel": "机械",
    "psychic": "幻",
}

_TYPE_ORDER = [
    "normal", "grass", "fire", "water", "light", "ground", "ice", "dragon", "electric",
    "poison", "bug", "fighting", "flying", "fairy", "ghost", "dark", "steel", "psychic",
]

def _ensure_loaded():
    global _db_loaded
    if not _db_loaded:
        _ensure_metadata_schema()
        load_skills()
        from src.pokemon_db import load_pokemon_db
        load_pokemon_db()
        _db_loaded = True


def _ensure_metadata_schema():
    """让旧数据库兼容新 UI 需要的技能图标/分组字段。"""
    from src.skill_db import _get_conn
    conn = _get_conn()
    c = conn.cursor()

    def columns(table: str) -> set:
        c.execute(f"PRAGMA table_info({table})")
        return {r["name"] for r in c.fetchall()}

    skill_cols = columns("skill")
    for col, ddl in [
        ("icon_url", "TEXT DEFAULT ''"),
        ("attribute_icon_url", "TEXT DEFAULT ''"),
        ("category_icon_url", "TEXT DEFAULT ''"),
        ("skill_group", "TEXT DEFAULT ''"),
        ("wiki_url", "TEXT DEFAULT ''"),
    ]:
        if col not in skill_cols:
            c.execute(f"ALTER TABLE skill ADD COLUMN {col} {ddl}")

    ps_cols = columns("pokemon_skill")
    if "learn_group" not in ps_cols:
        c.execute("ALTER TABLE pokemon_skill ADD COLUMN learn_group TEXT DEFAULT ''")
    if "learn_level" not in ps_cols:
        c.execute("ALTER TABLE pokemon_skill ADD COLUMN learn_level TEXT DEFAULT ''")

    conn.commit()


def _safe_skill_icon_stem(name: str) -> str:
    return re.sub(r'[^\w\u4e00-\u9fff]+', '_', name).strip('_') or "skill"


def _build_skill_icon_cache():
    """扫描本地 data/skill_icons，生成技能名 -> /skill-icons URL。"""
    global _SKILL_ICON_CACHE
    if _SKILL_ICON_CACHE:
        return
    icon_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "skill_icons")
    if not os.path.exists(icon_dir):
        return
    for fname in os.listdir(icon_dir):
        if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            continue
        stem, _ = os.path.splitext(fname)
        _SKILL_ICON_CACHE[stem] = f"/skill-icons/{urllib.parse.quote(fname)}"


def _get_skill_icon_url(name: str) -> str:
    _build_skill_icon_cache()
    return _SKILL_ICON_CACHE.get(_safe_skill_icon_stem(name), "")


def _build_skill_meta_icon_cache() -> dict:
    """扫描本地 data/skill_meta_icons，生成系别/分类/耗能图标映射。"""
    global _SKILL_META_ICON_CACHE
    if _SKILL_META_ICON_CACHE is not None:
        return _SKILL_META_ICON_CACHE

    root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "skill_meta_icons",
    )
    cache = {"elements": {}, "categories": {}, "misc": {}}
    for kind in cache:
        icon_dir = os.path.join(root, kind)
        if not os.path.exists(icon_dir):
            continue
        for fname in os.listdir(icon_dir):
            if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")):
                continue
            stem, _ = os.path.splitext(fname)
            cache[kind][stem] = f"/skill-meta-icons/{kind}/{urllib.parse.quote(fname)}"
    _SKILL_META_ICON_CACHE = cache
    return cache


def _get_skill_meta_icon_url(kind: str, name: str) -> str:
    cache = _build_skill_meta_icon_cache()
    return cache.get(kind, {}).get(name or "", "")


def _build_mechanic_icon_cache() -> dict[str, str]:
    """扫描本地 data/mechanic_icons，生成词条名 -> /mechanic-icons URL。"""
    global _MECHANIC_ICON_CACHE
    if _MECHANIC_ICON_CACHE is not None:
        return _MECHANIC_ICON_CACHE

    root = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "mechanic_icons",
    )
    cache: dict[str, str] = {}
    if os.path.exists(root):
        for current, _, files in os.walk(root):
            for fname in files:
                if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")):
                    continue
                stem, _ = os.path.splitext(fname)
                rel = os.path.relpath(os.path.join(current, fname), root)
                url_path = "/".join(urllib.parse.quote(part) for part in rel.split(os.sep))
                cache.setdefault(stem, f"/mechanic-icons/{url_path}")
    _MECHANIC_ICON_CACHE = cache
    return _MECHANIC_ICON_CACHE


def _get_mechanic_icon_url(title: str) -> str:
    cache = _build_mechanic_icon_cache()
    return cache.get(title or "", "")


def _build_ability_icon_cache() -> dict[str, str]:
    """读取本地特性图标清单，生成 特性名 -> /ability-icons URL。"""
    global _ABILITY_ICON_CACHE
    if _ABILITY_ICON_CACHE is not None:
        return _ABILITY_ICON_CACHE

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest = os.path.join(root, "data", "ability_icons_manifest.csv")
    icon_dir = os.path.join(root, "data", "ability_icons")
    cache: dict[str, str] = {}

    if os.path.exists(manifest):
        with open(manifest, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                name = (row.get("特性名") or "").strip()
                local_url = (row.get("本地URL") or "").strip()
                filename = (row.get("图标文件") or "").strip()
                if name and not local_url and filename:
                    local_url = f"/ability-icons/{urllib.parse.quote(filename)}"
                if name and local_url:
                    cache[name] = local_url

    if os.path.exists(icon_dir):
        for fname in os.listdir(icon_dir):
            if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")):
                continue
            stem, _ = os.path.splitext(fname)
            cache.setdefault(stem, f"/ability-icons/{urllib.parse.quote(fname)}")

    _ABILITY_ICON_CACHE = cache
    return _ABILITY_ICON_CACHE


def _get_ability_icon_url(name: str) -> str:
    if not name:
        return ""
    return _build_ability_icon_cache().get(name, "")


def _egg_groups_data() -> dict:
    """读取本地蛋组数据。"""
    global _EGG_GROUPS_CACHE
    if _EGG_GROUPS_CACHE is not None:
        return _EGG_GROUPS_CACHE

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "data", "egg_groups.json")
    if not os.path.exists(path):
        _EGG_GROUPS_CACHE = {"ok": True, "groups": [], "cards": []}
        return _EGG_GROUPS_CACHE

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("groups", [])
    data.setdefault("cards", [])
    _EGG_GROUPS_CACHE = data
    return _EGG_GROUPS_CACHE


def _egg_card_search_text(card: dict) -> str:
    rep = card.get("representative") or {}
    parts = [
        card.get("group_display", ""),
        card.get("group_description", ""),
        card.get("mother_family", ""),
        card.get("family_chain", ""),
        card.get("family_key", ""),
        rep.get("display_name", ""),
        rep.get("page_name", ""),
        rep.get("class_name", ""),
        rep.get("type_name", ""),
        rep.get("hatch_status_text", ""),
        " ".join(card.get("family_members") or []),
    ]
    return " ".join(str(p or "") for p in parts).casefold()


def _egg_group_map(data: dict) -> dict[int, dict]:
    return {
        int(group.get("group_id")): group
        for group in data.get("groups", [])
        if group.get("group_id") is not None
    }


def _egg_measurements_data() -> dict:
    """读取本地孵蛋尺寸反查数据。"""
    global _EGG_MEASUREMENTS_CACHE
    if _EGG_MEASUREMENTS_CACHE is not None:
        return _EGG_MEASUREMENTS_CACHE

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "data", "egg_measurements.json")
    if not os.path.exists(path):
        _EGG_MEASUREMENTS_CACHE = {"total": 0, "totalPets": 0, "groups": []}
        return _EGG_MEASUREMENTS_CACHE

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("groups", [])
    _EGG_MEASUREMENTS_CACHE = data
    return _EGG_MEASUREMENTS_CACHE


def _parse_measure_range(value: str) -> tuple[Optional[float], Optional[float]]:
    nums = re.findall(r"\d+(?:\.\d+)?", str(value or ""))
    if not nums:
        return None, None
    if len(nums) == 1:
        val = float(nums[0])
        return val, val
    first = float(nums[0])
    second = float(nums[1])
    return min(first, second), max(first, second)


def _range_item_payload(item: dict) -> dict:
    diameter_min, diameter_max = _parse_measure_range(item.get("eggDiameter", ""))
    weight_min, weight_max = _parse_measure_range(item.get("eggWeight", ""))
    return {
        "id": item.get("id"),
        "eggDiameter": item.get("eggDiameter", ""),
        "eggWeight": item.get("eggWeight", ""),
        "diameter_min": diameter_min,
        "diameter_max": diameter_max,
        "weight_min": weight_min,
        "weight_max": weight_max,
    }


def _hatch_pet_icon_url(pet_id: str, pet_name: str) -> str:
    cache = _build_spirit_icon_meta_cache()
    number = _normalize_spirit_no(pet_id)
    variants = cache["by_number"].get(number, [])
    for item in variants:
        if item.get("name") == pet_name:
            return item.get("icon_url", "")
    for item in variants:
        if str(item.get("name", "")).startswith(pet_name):
            return item.get("icon_url", "")
    return _get_icon_url(pet_name) or (variants[0].get("icon_url", "") if variants else "")


def _resolve_hatch_pet_meta(pet_id: str, pet_name: str) -> dict:
    cache = _build_spirit_icon_meta_cache()
    by_name = cache.get("by_name", {})
    number = _normalize_spirit_no(pet_id)
    variants = cache.get("by_number", {}).get(number, [])

    meta = by_name.get(pet_name)
    if meta:
        return {
            "dex_name": meta.get("name") or pet_name,
            "icon_url": meta.get("icon_url", ""),
            "number": number or meta.get("number", ""),
            "element": meta.get("element", ""),
        }

    for item in variants:
        item_name = str(item.get("name", ""))
        if item_name.startswith(pet_name) or pet_name in item_name:
            return {
                "dex_name": item_name,
                "icon_url": item.get("icon_url", ""),
                "number": number,
                "element": item.get("element", ""),
            }

    if variants:
        item = variants[0]
        return {
            "dex_name": item.get("name") or pet_name,
            "icon_url": item.get("icon_url", ""),
            "number": number,
            "element": item.get("element", ""),
        }

    return {
        "dex_name": pet_name,
        "icon_url": _hatch_pet_icon_url(pet_id, pet_name),
        "number": number,
        "element": "",
    }


def _measurement_matches(value: float, minimum: Optional[float], maximum: Optional[float]) -> bool:
    if minimum is None or maximum is None:
        return False
    epsilon = 1e-9
    return minimum - epsilon <= value <= maximum + epsilon


def _range_score(diameter: float, weight: float, item: dict) -> tuple[float, float]:
    dmin = item.get("diameter_min")
    dmax = item.get("diameter_max")
    wmin = item.get("weight_min")
    wmax = item.get("weight_max")
    dspan = (dmax - dmin) if dmin is not None and dmax is not None else 9999.0
    wspan = (wmax - wmin) if wmin is not None and wmax is not None else 9999.0
    area = dspan * wspan
    mid_d = ((dmin + dmax) / 2) if dmin is not None and dmax is not None else diameter
    mid_w = ((wmin + wmax) / 2) if wmin is not None and wmax is not None else weight
    distance = abs(diameter - mid_d) + abs(weight - mid_w)
    return area, distance


def _type_items() -> list[dict]:
    return [
        {
            "id": type_id,
            "name": _TYPE_LABELS[type_id],
            "icon_url": _get_skill_meta_icon_url("elements", _TYPE_LABELS[type_id]),
        }
        for type_id in _TYPE_ORDER
    ]


def _type_single_effectiveness(attack_id: str, defense_id: str) -> float:
    from src.models import TYPE_CHART
    return TYPE_CHART.get(attack_id, {}).get(defense_id, 1.0)


def _type_combined_effectiveness(attack_id: str, defense_ids: list[str]) -> float:
    clean = list(dict.fromkeys(type_id for type_id in defense_ids if type_id in _TYPE_LABELS))
    if not clean:
        return 1.0
    values = [_type_single_effectiveness(attack_id, defense_id) for defense_id in clean]
    if len(values) == 1:
        return values[0]
    if any(value > 1 for value in values) and any(value < 1 for value in values):
        return 1.0
    total = sum(values) - (len(values) - 1)
    return round(max(0.5, total), 3)


def _skill_metadata_cache() -> dict:
    """返回 name -> 技能展示元数据。"""
    global _skill_meta_cache
    if _skill_meta_cache is not None:
        return _skill_meta_cache
    from src.skill_db import _get_conn
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT name, description, icon_url, attribute_icon_url,
               category_icon_url, skill_group, wiki_url, source
        FROM skill
    """)
    _skill_meta_cache = {}
    for r in c.fetchall():
        local_icon = _get_skill_icon_url(r["name"])
        _skill_meta_cache[r["name"]] = {
            "description": r["description"] or "",
            "icon_url": local_icon or r["icon_url"] or "",
            "attribute_icon_url": r["attribute_icon_url"] or "",
            "category_icon_url": r["category_icon_url"] or "",
            "skill_group": r["skill_group"] or "",
            "wiki_url": r["wiki_url"] or "",
            "source": r["source"] or "",
        }
    return _skill_meta_cache


def _get_skill_metadata(name: str) -> dict:
    _ensure_loaded()
    return _skill_metadata_cache().get(name, {
        "description": "",
        "icon_url": "",
        "attribute_icon_url": "",
        "category_icon_url": "",
        "skill_group": "",
        "wiki_url": "",
        "source": "",
    })


def _pct_text(value: float) -> str:
    """将比例值转成更适合 UI 展示的百分比文本。"""
    if value == int(value):
        return f"{int(value)}%"
    return f"{value:.0f}%"


def _format_buff_parts(params: dict, prefix: str) -> str:
    parts = []
    for key, label in [
        ("atk", "物攻"),
        ("def", "物防"),
        ("spatk", "魔攻"),
        ("spdef", "魔防"),
        ("speed", "速度"),
    ]:
        if key in params:
            parts.append(f"{label}{prefix}{_pct_text(params[key] * 100)}")
    if "all_atk" in params:
        parts.append(f"双攻{prefix}{_pct_text(params['all_atk'] * 100)}")
    if "all_def" in params:
        parts.append(f"双防{prefix}{_pct_text(params['all_def'] * 100)}")
    return "，".join(parts)


def _effect_tag_text(tag) -> str:
    """把 EffectTag 翻译成前端更易读的短文本。"""
    params = getattr(tag, "params", {}) or {}
    t = getattr(tag, "type", None)

    if t == E.DAMAGE:
        return "造成伤害"
    if t == E.HEAL_HP:
        return f"回复{_pct_text(params.get('pct', 0) * 100)}HP"
    if t == E.HEAL_ENERGY:
        return f"回能+{params.get('amount', 1)}"
    if t == E.STEAL_ENERGY:
        return f"偷能+{params.get('amount', 1)}"
    if t == E.ENEMY_LOSE_ENERGY:
        return f"敌方失能-{params.get('amount', 1)}"
    if t == E.LIFE_DRAIN:
        return f"吸血{_pct_text(params.get('pct', 0) * 100)}"
    if t == E.SELF_BUFF:
        detail = _format_buff_parts(params, "+")
        return f"自增益{('：' + detail) if detail else ''}"
    if t == E.ENEMY_DEBUFF:
        detail = _format_buff_parts(params, "-")
        return f"敌减益{('：' + detail) if detail else ''}"
    if t == E.POISON:
        return f"中毒×{params.get('stacks', 1)}"
    if t == E.BURN:
        return f"灼烧×{params.get('stacks', 1)}"
    if t == E.FREEZE:
        return f"冻结×{params.get('stacks', 1)}"
    if t == E.LEECH:
        return f"寄生×{params.get('stacks', 1)}"
    if t == E.METEOR:
        return f"星陨×{params.get('stacks', 1)}"
    if t == E.POISON_MARK:
        return f"中毒印记×{params.get('stacks', 1)}"
    if t == E.MOISTURE_MARK:
        return f"湿润印记×{params.get('stacks', 1)}"
    if t == E.DRAGON_MARK:
        return f"龙噬印记×{params.get('stacks', 1)}"
    if t == E.WIND_MARK:
        return f"风起印记×{params.get('stacks', 1)}"
    if t == E.CHARGE_MARK:
        return f"蓄电印记×{params.get('stacks', 1)}"
    if t == E.SOLAR_MARK:
        return f"光合印记×{params.get('stacks', 1)}"
    if t == E.ATTACK_MARK:
        return f"攻击印记×{params.get('stacks', 1)}"
    if t == E.SLOW_MARK:
        return f"减速印记×{params.get('stacks', 1)}"
    if t == E.SPIRIT_MARK:
        return f"降灵印记×{params.get('stacks', 1)}"
    if t == E.METEOR_MARK:
        return f"星陨印记×{params.get('stacks', 1)}"
    if t == E.THORN_MARK:
        return f"荆刺印记×{params.get('stacks', 1)}"
    if t == E.DISPEL_ENEMY_MARKS:
        return "驱散敌方印记"
    if t == E.CONVERT_MARKS_TO_BURN:
        return f"印记→灼烧×{params.get('ratio', 3)}"
    if t == E.DISPEL_MARKS_TO_BURN:
        return f"驱散印记→灼烧×{params.get('burn_per_mark', 5)}"
    if t == E.CONSUME_MARKS_HEAL:
        return "食腐(驱散回血)"
    if t == E.MARKS_TO_METEOR:
        return "印记→星陨"
    if t == E.STEAL_MARKS:
        return "偷取印记"
    if t == E.ENERGY_COST_PER_ENEMY_MARK:
        return "印记减能耗"
    if t == E.DAMAGE_REDUCTION:
        return f"减伤{_pct_text(params.get('pct', 0) * 100)}"
    if t == E.FORCE_SWITCH:
        return "强制换人"
    if t == E.FORCE_ENEMY_SWITCH:
        return "逼退对手"
    if t == E.AGILITY:
        return "先制"
    if t == E.INTERRUPT:
        return "打断"
    if t == E.POWER_DYNAMIC:
        condition = params.get("condition", "")
        if condition == "first_strike":
            return f"先手威力+{_pct_text(params.get('bonus_pct', 0) * 100)}"
        if condition == "per_poison":
            return f"每层中毒增威{params.get('bonus_per_stack', 0)}"
        if condition == "counter":
            return f"应对威力×{params.get('multiplier', 1.0)}"
        return "动态威力"
    if t == E.ENERGY_COST_DYNAMIC:
        return f"动态减耗：每层减{params.get('reduce', 0)}"
    if t == E.PERMANENT_MOD:
        target = params.get("target", "")
        delta = params.get("delta", 0)
        if target == "cost":
            return f"永久能耗{delta:+d}"
        if target == "power":
            return f"永久威力{delta:+d}"
        return "永久修正"
    if t == E.POSITION_BUFF:
        positions = params.get("positions", [])
        return f"位置增益{positions}"
    if t == E.DRIVE:
        return f"传动{params.get('value', 1)}"
    if t == E.PASSIVE_ENERGY_REDUCE:
        return f"连带减耗-{params.get('reduce', 0)}"
    if t == E.REPLAY_AGILITY:
        return "重复先制"
    if t == E.AGILITY_COST_SHARE:
        return f"先制分摊/{params.get('divisor', 2)}"
    if t == E.ENERGY_COST_ACCUMULATE:
        return f"每次能耗+{params.get('delta', 1)}"
    if t == E.ENEMY_ENERGY_COST_UP:
        return f"敌方能耗+{params.get('amount', 0)}"
    if t == E.MIRROR_DAMAGE:
        return "反弹原始伤害"
    if t == E.CONVERT_BUFF_TO_POISON:
        return "增益转中毒"
    if t == E.CONVERT_POISON_TO_MARK:
        return "中毒转印记"
    if t == E.DISPEL_MARKS:
        return "驱散印记"
    if t == E.CONDITIONAL_BUFF:
        return "条件增益"
    # Legacy COUNTER_* tags (保留兼容)
    if t == E.COUNTER_ATTACK:
        base = "应对攻击"
        subs = getattr(tag, "sub_effects", None) or []
        if subs:
            sub_text = "，".join(_effect_tag_text(sub) for sub in subs)
            return f"{base}：{sub_text}" if sub_text else base
        return base
    if t == E.COUNTER_STATUS:
        base = "应对状态"
        subs = getattr(tag, "sub_effects", None) or []
        if subs:
            sub_text = "，".join(_effect_tag_text(sub) for sub in subs)
            return f"{base}：{sub_text}" if sub_text else base
        return base
    if t == E.COUNTER_DEFENSE:
        base = "应对防御"
        subs = getattr(tag, "sub_effects", None) or []
        if subs:
            sub_text = "，".join(_effect_tag_text(sub) for sub in subs)
            return f"{base}：{sub_text}" if sub_text else base
        return base
    if t == E.WEATHER:
        return f"天气：{params.get('type', 'unknown')}"
    if t == E.ABILITY_COMPUTE:
        return f"特性计算：{params.get('action', '')}"
    if t == E.ABILITY_INCREMENT_COUNTER:
        return "特性计数+1"
    if t == E.TRANSFER_MODS:
        return "离场传递增益"
    if t == E.BURN_NO_DECAY:
        return "灼烧不衰减"
    return getattr(t, "name", "未知效果")


def _skill_effect_display(skill) -> dict:
    """生成前端展示用的技能效果摘要。"""
    from src.effect_models import SkillEffect as _SE, SkillTiming as _ST
    tags = []
    details = []
    if getattr(skill, "effects", None):
        for item in skill.effects:
            if isinstance(item, _SE):
                # SE 格式: 展示每个 EffectTag
                prefix = ""
                if item.timing == _ST.ON_COUNTER:
                    cat = item.filter.get("category", "")
                    cat_name = {"attack": "攻击", "status": "状态", "defense": "防御"}.get(cat, cat)
                    prefix = f"应对{cat_name}："
                for tag in item.effects:
                    text = _effect_tag_text(tag)
                    full = f"{prefix}{text}" if prefix else text
                    details.append(full)
                    tags.append(full.split("：", 1)[0] if prefix else text.split("：", 1)[0])
                if not item.effects and prefix:
                    details.append(prefix.rstrip("："))
                    tags.append(prefix.rstrip("："))
            else:
                text = _effect_tag_text(item)
                details.append(text)
                tags.append(text.split("：", 1)[0])

    if skill.life_drain > 0:
        tags.append(f"吸血{int(skill.life_drain * 100)}%")
    if skill.damage_reduction > 0:
        tags.append(f"减伤{int(skill.damage_reduction * 100)}%")
    if skill.self_heal_hp > 0:
        tags.append(f"回HP{int(skill.self_heal_hp * 100)}%")
    if skill.self_heal_energy > 0:
        tags.append(f"回能+{skill.self_heal_energy}")
    if skill.poison_stacks > 0:
        tags.append(f"中毒×{skill.poison_stacks}")
    if skill.burn_stacks > 0:
        tags.append(f"灼烧×{skill.burn_stacks}")
    if skill.freeze_stacks > 0:
        tags.append(f"冻结×{skill.freeze_stacks}")
    if skill.leech_stacks > 0:
        tags.append(f"寄生×{skill.leech_stacks}")
    if skill.meteor_stacks > 0:
        tags.append(f"星陨×{skill.meteor_stacks}")
    if skill.hit_count > 1:
        tags.append(f"{skill.hit_count}连击")
    if skill.force_switch:
        tags.append("强制换人")
    if skill.agility:
        tags.append("先制")
    if skill.charge:
        tags.append("蓄力")
    if skill.priority_mod > 0:
        tags.append("先手")
    if skill.is_mark:
        tags.append("印记")

    tags = list(dict.fromkeys([t for t in tags if t]))
    details = list(dict.fromkeys([d for d in details if d]))
    return {
        "tags": tags,
        "details": details,
        "summary": "；".join(details) if details else "",
        "has_effects": bool(details),
    }


# ═══════════════════════════════════════
# 精准战报：执行前后状态快照 + diff
# ═══════════════════════════════════════

def _snapshot(state: BattleState) -> dict:
    """记录战斗关键数值快照，用于 diff 生成战报"""
    snap = {
        "mp_a": state.mp_a, "mp_b": state.mp_b,
        "current_a": state.current_a, "current_b": state.current_b,
    }
    for team_key, team_list in [("a", state.team_a), ("b", state.team_b)]:
        for i, p in enumerate(team_list):
            snap[f"{team_key}_{i}_hp"]       = max(0, round(p.current_hp, 2))
            snap[f"{team_key}_{i}_energy"]   = p.energy
            snap[f"{team_key}_{i}_fainted"]  = p.is_fainted
            snap[f"{team_key}_{i}_poison"]   = p.poison_stacks
            snap[f"{team_key}_{i}_burn"]     = p.burn_stacks
            snap[f"{team_key}_{i}_leech"]    = p.leech_stacks
            snap[f"{team_key}_{i}_frost"]    = p.frostbite_damage
            snap[f"{team_key}_{i}_meteor"]   = p.meteor_stacks
            snap[f"{team_key}_{i}_atk_mod"]  = round((p.atk_up - p.atk_down) * 100)
            snap[f"{team_key}_{i}_def_mod"]  = round((p.def_up - p.def_down) * 100)
    return snap


def _diff_to_logs(before: dict, after: dict, state: BattleState) -> List[str]:
    """比对快照，生成详细战报日志"""
    logs = []

    def pname(team, idx):
        team_list = state.team_a if team == "a" else state.team_b
        return team_list[idx].name

    def side_label(team):
        return "🟦我方" if team == "a" else "🟥对方"

    n = len(state.team_a)

    for team in ["a", "b"]:
        for i in range(n):
            label = side_label(team)
            name  = pname(team, i)
            max_hp = (state.team_a if team == "a" else state.team_b)[i].hp

            hp_before = before.get(f"{team}_{i}_hp", 0)
            hp_after  = after.get(f"{team}_{i}_hp", 0)
            dmg = round(hp_before - hp_after, 2)
            if dmg > 0:
                logs.append(
                    f"  💥 {label} {name} 受到 {dmg} 伤害 → 剩余 HP {round(hp_after, 2)}/{max_hp}"
                )
            elif dmg < 0:
                logs.append(
                    f"  💚 {label} {name} 回复 {-dmg} HP → {round(hp_after, 2)}/{max_hp}"
                )

            # 倒地
            was_fainted  = before.get(f"{team}_{i}_fainted", False)
            now_fainted  = after.get(f"{team}_{i}_fainted", False)
            if not was_fainted and now_fainted:
                logs.append(f"  ☠️  {label} {name} 倒下了！")

            # 能量变化
            e_before = before.get(f"{team}_{i}_energy", 0)
            e_after  = after.get(f"{team}_{i}_energy", 0)
            if e_after > e_before:
                logs.append(f"  ⚡ {label} {name} 能量 +{e_after - e_before} → {e_after}")
            elif e_after < e_before:
                logs.append(f"  ⚡ {label} {name} 能量 -{e_before - e_after} → {e_after}")

            # 状态层数变化
            for key, icon, label_cn in [
                ("poison", "🟣", "中毒"),
                ("burn",   "🔥", "燃烧"),
                ("leech",  "🌿", "寄生"),
                ("meteor", "☄️", "星陨"),
            ]:
                b_val = before.get(f"{team}_{i}_{key}", 0)
                a_val = after.get(f"{team}_{i}_{key}", 0)
                if a_val > b_val:
                    logs.append(f"  {icon} {label} {name} 附加{label_cn} ×{a_val - b_val}（共{a_val}层）")
                elif a_val < b_val and a_val == 0:
                    logs.append(f"  {icon} {label} {name} {label_cn}消除")

            # 冻伤
            f_before = before.get(f"{team}_{i}_frost", 0)
            f_after  = after.get(f"{team}_{i}_frost", 0)
            if f_after > f_before:
                logs.append(f"  🧊 {label} {name} 冻伤累计 +{f_after - f_before}")

            # 属性变化
            for stat_key, stat_name in [("atk_mod", "物攻"), ("def_mod", "物防")]:
                sv_before = before.get(f"{team}_{i}_{stat_key}", 0)
                sv_after  = after.get(f"{team}_{i}_{stat_key}", 0)
                delta = sv_after - sv_before
                if abs(delta) >= 5:
                    sign = "+" if delta > 0 else ""
                    logs.append(f"  📈 {label} {name} {stat_name} {sign}{delta}%")

    # MP 变化
    mp_a_before = before.get("mp_a", 4)
    mp_a_after  = after.get("mp_a", 4)
    mp_b_before = before.get("mp_b", 4)
    mp_b_after  = after.get("mp_b", 4)
    if mp_a_after < mp_a_before:
        logs.append(f"  💔 {side_label('a')} MP -{mp_a_before - mp_a_after} → {mp_a_after}")
    if mp_b_after < mp_b_before:
        logs.append(f"  💔 {side_label('b')} MP -{mp_b_before - mp_b_after} → {mp_b_after}")

    # 换人（换人优先级最高，提到结算日志最前以反映真实执行顺序）
    switch_logs = []
    ca_before = before.get("current_a")
    ca_after  = after.get("current_a")
    cb_before = before.get("current_b")
    cb_after  = after.get("current_b")
    if ca_before != ca_after and ca_after is not None:
        switch_logs.append(f"  🔄 {side_label('a')} 换上 {pname('a', ca_after)}")
    if cb_before != cb_after and cb_after is not None:
        switch_logs.append(f"  🔄 {side_label('b')} 换上 {pname('b', cb_after)}")

    return switch_logs + logs


# ═══════════════════════════════════════
# 全局战斗会话
# ═══════════════════════════════════════

class BattleSession:
    def __init__(self):
        self.state: Optional[BattleState] = None
        self.mode = "manual"
        self.waiting_for_player = False
        self.game_over = False
        self.logs: List[str] = []

    def reset(self):
        self.state = None
        self.mode = "manual"
        self.waiting_for_player = False
        self.game_over = False
        self.logs = []

    def add_log(self, text: str):
        self.logs.append(text)


session = BattleSession()


# ═══════════════════════════════════════
# 序列化
# ═══════════════════════════════════════
# 精灵图标映射（名字 → /icons/NOxxx_名字.png）
# ═══════════════════════════════════════
_ICON_CACHE: dict = {}
_ALLOWED_LINEUP_MAGIC = {"强化术", "进化之力"}


def _lineup_magic_label(value: str) -> str:
    value = (value or "").strip()
    return "愿力冲击" if value == "强化术" else value

def _build_icon_cache():
    global _ICON_CACHE
    if _ICON_CACHE:
        return
    icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "spirit_icons")
    if not os.path.exists(icons_dir):
        return
    import re
    for fname in os.listdir(icons_dir):
        m = re.match(r'(NO\d+)_(.+)\.png$', fname)
        if m:
            name = m.group(2)
            # 只存第一个（原始形态优先）
            if name not in _ICON_CACHE:
                _ICON_CACHE[name] = f"/icons/{urllib.parse.quote(fname)}"

def _get_icon_url(name: str) -> str:
    _build_icon_cache()
    if name in _ICON_CACHE:
        return _ICON_CACHE[name]
    base = re.split(r"[（(]", name or "", 1)[0].strip()
    if base and base in _ICON_CACHE:
        return _ICON_CACHE[base]
    if base:
        for key, url in _ICON_CACHE.items():
            if key.startswith(base):
                return url
    return ""


def _lineup_icon_url(filename: str) -> str:
    filename = (filename or "").strip()
    return f"/lineup-icons/{urllib.parse.quote(filename)}" if filename else ""


def _pvp_lineups_data() -> dict:
    """读取本地 PVP 阵容库。"""
    global _PVP_LINEUPS_CACHE
    if _PVP_LINEUPS_CACHE is not None:
        return _PVP_LINEUPS_CACHE

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "data", "pvp_lineups.json")
    if not os.path.exists(path):
        _PVP_LINEUPS_CACHE = {"ok": True, "lineups": [], "magic_icons": []}
        return _PVP_LINEUPS_CACHE

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("lineups", [])
    data.setdefault("magic_icons", [])
    _PVP_LINEUPS_CACHE = data
    return _PVP_LINEUPS_CACHE


def _pokemon_row_for_name(name: str):
    from src.pokemon_db import _get_conn
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, element, ability, base_total, spirit_no, evo_stage
        FROM pokemon WHERE name = ?
    """, (name,))
    row = c.fetchone()
    if row:
        return row
    base = re.split(r"[（(]", name or "", 1)[0].strip()
    if base:
        c.execute("""
            SELECT id, name, element, ability, base_total, spirit_no, evo_stage
            FROM pokemon WHERE name LIKE ?
            ORDER BY CASE WHEN evo_stage LIKE '%最终%' THEN 0 ELSE 1 END, id
            LIMIT 1
        """, (f"{base}%",))
        return c.fetchone()
    return None


def _lineup_skill_payload(name: str) -> dict:
    from src.skill_db import _get_conn
    if not name:
        return {"name": ""}
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT name, element, category, energy_cost, power, description
        FROM skill WHERE name = ?
    """, (name,))
    row = c.fetchone()
    if not row:
        return {"name": name, "icon_url": _get_skill_icon_url(name)}
    return {
        "name": row["name"],
        "element": row["element"],
        "category": row["category"],
        "energy_cost": row["energy_cost"],
        "power": row["power"],
        "description": row["description"] or "",
        "icon_url": _get_skill_icon_url(row["name"]),
        "attribute_icon_url": _get_skill_meta_icon_url("elements", row["element"]),
        "category_icon_url": _get_skill_meta_icon_url("categories", row["category"]),
        "energy_icon_url": _get_skill_meta_icon_url("misc", "energy"),
    }


def _enrich_lineup_member(member: dict) -> dict:
    item = dict(member)
    row = _pokemon_row_for_name(item.get("name", ""))
    if row:
        ability_name, ability_effect = _split_ability_text(row["ability"])
        meta = _get_spirit_icon_meta(row["name"])
        number = _normalize_spirit_no(row["spirit_no"] or meta.get("number", ""))
        item.update({
            "dex_name": row["name"],
            "number": number,
            "element": row["element"],
            "element_icons": _element_icon_payload(row["element"]),
            "ability": ability_name,
            "ability_effect": ability_effect,
            "ability_icon_url": _get_ability_icon_url(ability_name),
            "base_total": row["base_total"],
            "is_leader": _is_leader_form(row["name"], row["evo_stage"]),
            "icon_url": _get_icon_url(item.get("name", "")) or _get_icon_url(row["name"]) or meta.get("icon_url", ""),
        })
    else:
        item.setdefault("element", "")
        item.setdefault("element_icons", [])
        item.setdefault("icon_url", _get_icon_url(item.get("name", "")))
    item["skill_details"] = [_lineup_skill_payload(name) for name in item.get("skills", [])]
    return item


def _enrich_lineup(lineup: dict) -> dict:
    item = dict(lineup)
    item["magic_label"] = _lineup_magic_label(item.get("magic", item.get("magic_label", "")))
    item["members"] = [_enrich_lineup_member(member) for member in lineup.get("members", [])]
    return item


def _displayable_lineup(lineup: dict) -> dict | None:
    """阵容页只展示当前能完整复用的 PVP 配队。"""
    if lineup.get("magic") not in _ALLOWED_LINEUP_MAGIC:
        return None
    item = _enrich_lineup(lineup)
    members = item.get("members", [])
    if len(members) != 6 or any(not member.get("icon_url") for member in members):
        return None
    return item


def _normalize_spirit_no(value: str) -> str:
    if not value:
        return ""
    m = re.search(r"(\d+)", str(value))
    return f"NO.{int(m.group(1)):03d}" if m else str(value)


def _split_ability_text(value: str) -> tuple[str, str]:
    """把数据库里的“特性名:效果描述”拆成前端可直接展示的两段。"""
    text = (value or "").strip()
    if not text:
        return "", ""
    parts = re.split(r"[:：]", text, 1)
    if len(parts) == 1:
        return parts[0].strip(), ""
    return parts[0].strip(), parts[1].strip()


def _split_element_names(value: str) -> list[str]:
    return [x.strip() for x in re.split(r"[,，/、]", value or "") if x.strip()]


def _element_icon_payload(value: str) -> list[dict]:
    return [
        {"name": name, "icon_url": _get_skill_meta_icon_url("elements", name)}
        for name in _split_element_names(value)
    ]


def _clean_mechanic_body(text: str) -> str:
    body = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    body = re.sub(r"\n==\s*参考资料\s*==[\s\S]*$", "", body)
    body = body.replace("<references />", "")
    body = body.replace("**", "")
    body = body.replace("`", "")
    replacements = {
        "nextTurn": "回合开始",
        "buildMoveRequest": "出招请求构建",
        "|request|": "出招请求",
        "disabled / energyCost UI 字段": "可用状态和能耗显示",
        "disabled": "可用状态",
        "energyCost": "能耗",
        "budget": "剩余移动次数",
        "wrap(S+1)": "下一格",
        "wrap": "环绕",
        "chain": "连锁",
        "forceSwitch": "强制换宠",
        "priority desc → speed desc → 随机 tiebreak": "先按优先级，再按速度，仍相同则随机",
        "priority": "优先级",
        "attacker": "攻击方",
        "getStat('spe')": "当前速度",
        "counter": "应对",
        "lead": "首发",
        "no-op": "不触发",
        "moveSlots": "技能槽",
        "meta-move": "引用型技能",
        "MoveAction": "技能动作",
        "moveid": "技能编号",
        "slot.mods": "技能槽修正",
        "shift": "移动",
        "grant 招": "累积奉献的技能",
        "Grant 招": "累积奉献的技能",
        "STAB": "本系加成",
        "basePower": "基础威力",
        "mods": "修正",
        "UI": "界面",
    }
    for src, dst in replacements.items():
        body = body.replace(src, dst)
    body = re.sub(r"（[A-Za-z0-9_\- /|().:+]+）", "", body)
    body = re.sub(r"\(([A-Za-z0-9_\- /|().:+]+)\)", "", body)
    body = "\n".join(line[1:].strip() if line.lstrip().startswith(">") else line for line in body.split("\n"))
    body = body.replace("[[防御姿态]]", "[[防御]]")
    body = body.replace("[[冰冻]]", "[[冻结]]")
    return body.strip()


def _manual_mechanic_entries() -> list[dict]:
    return [
        {
            "id": "迸发",
            "title": "迸发",
            "category": "关键词",
            "polarity": "positive",
            "meta": "关键词机制",
            "body": """== 迸发 ==
'''迸发''' 是技能关键字。精灵入场后的首次行动窗口中，使用带迸发标记的技能，会获得额外效果。

=== 触发口径 ===
* 技能描述中包含“迸发”的技能会被标记为迸发技能。
* 系统会记录每只精灵入场的回合号；通常只有入场回合使用迸发技能时才会触发。
* [[连续负荷]] 可以把迸发窗口额外延长1回合。

=== 当前特性联动 ===
* [[电流刺激]]：迸发技能威力+40。
* [[超负荷]]：迸发技能会让敌方全技能能耗+1。
* [[生物电]]：电系技能获得迸发时，能耗-2。
* [[连续负荷]]：自己技能的迸发效果延长1回合。

=== 当前迸发技能 ===
* [[电弧]]、[[超导]]、[[引雷]]、[[雷暴]]、[[双联脉冲]]、[[天旋地转]]。""",
            "is_overview": False,
        },
        {
            "id": "雨天",
            "title": "雨天",
            "category": "天气",
            "polarity": "system",
            "meta": "天气",
            "body": """== 雨天 ==
'''雨天''' 是战场天气。

=== 基础效果 ===
* 天气为雨天时，双方的水系技能威力+50%。
* 火系技能不会因为雨天降低威力。

=== 持续时间 ===
* 由[[求雨]]或[[落雨]]设置时，当前实现持续8回合。
* 新天气会覆盖旧天气。""",
            "is_overview": False,
        },
        {
            "id": "沙暴",
            "title": "沙暴",
            "category": "天气",
            "polarity": "system",
            "meta": "天气",
            "body": """== 沙暴 ==
'''沙暴''' 是战场天气。

=== 基础效果 ===
* 天气为沙暴时，双方的地系技能能耗减半。
* 能耗减半按向下取整处理，但最低保留1点能耗。
* 沙暴结束时，会恢复地系技能的原始能耗。

=== 持续时间 ===
* 由[[沙涌]]设置时，当前实现持续8回合。
* 新天气会覆盖旧天气。""",
            "is_overview": False,
        },
        {
            "id": "暴风雪",
            "title": "暴风雪",
            "category": "天气",
            "polarity": "system",
            "meta": "天气",
            "body": """== 暴风雪 ==
'''暴风雪''' 是战场天气。

=== 基础效果 ===
* 天气为暴风雪时，双方每回合结束获得2层[[冻结]]。
* 冰系精灵免疫暴风雪提供的冻结。
* 拥有冻结免疫的精灵同样不会获得这部分冻结。

=== 持续时间 ===
* 由[[冬至]]设置时，当前实现持续8回合。
* 新天气会覆盖旧天气。""",
            "is_overview": False,
        },
        {
            "id": "蓄电印记",
            "title": "蓄电印记",
            "category": "印记",
            "polarity": "positive",
            "meta": "正面印记",
            "body": """== 蓄电印记 ==
'''蓄电印记''' 是战斗中的一种[[印记|正面印记]]。

=== 基础效果 ===
* 攻击技能获得进发：本次威力+10。

=== 机制说明 ===
* 属于正面印记，同一阵营同时只能存在1种正面印记，新正面印记会覆盖旧正面印记。
* 常驻战场，直到被其他正面印记覆盖或被驱散。

=== 可施加该印记的技能 ===
* [[增程电池]]：自己获得1层蓄电印记。""",
            "is_overview": False,
        },
        {
            "id": "减速印记",
            "title": "减速印记",
            "category": "印记",
            "polarity": "negative",
            "meta": "负面印记",
            "body": """== 减速印记 ==
'''减速印记''' 是战斗中的一种[[印记|负面印记]]。

=== 基础效果 ===
* 速度-10。

=== 机制说明 ===
* 属于负面印记，同一阵营同时只能存在1种负面印记，新负面印记会覆盖旧负面印记。
* 常驻战场，直到被其他负面印记覆盖或被驱散。

=== 可施加该印记的技能 ===
* [[速冻]]：敌方获得2层减速印记。
* [[冰蛋壳]]：减伤60%，应对攻击：敌方获得2层减速印记。""",
            "is_overview": False,
        },
    ]


def _classify_local_status_icon(title: str) -> Optional[tuple[str, str, str]]:
    """把本地机制图标拆成独立状态词条。返回 category/polarity/meta。"""
    if not title or title in {"印记", "机制", "状态"} or "印记" in title:
        return None
    if title in _POSITIVE_STATUS_TITLES or "提升" in title:
        return "增益状态", "positive", "增益状态"
    if title in _NEGATIVE_STATUS_TITLES or "降低" in title:
        return "负面状态", "negative", "负面状态"
    return None


def _status_entry_effect_text(title: str, polarity: str) -> str:
    effects = {
        "物攻等级提升": "物攻提高，通常会提升物理攻击类技能的伤害。",
        "物攻等级降低": "物攻降低，通常会削弱物理攻击类技能的伤害。",
        "物防等级提升": "物防提高，通常会降低受到的物理攻击伤害。",
        "物防等级降低": "物防降低，通常会提高受到的物理攻击伤害。",
        "魔攻等级提升": "魔攻提高，通常会提升魔法攻击类技能的伤害。",
        "魔攻等级降低": "魔攻降低，通常会削弱魔法攻击类技能的伤害。",
        "魔防等级提升": "魔防提高，通常会降低受到的魔法攻击伤害。",
        "魔防等级降低": "魔防降低，通常会提高受到的魔法攻击伤害。",
        "防御等级提升": "防御相关能力提高，通常会降低本体受到的伤害。",
        "速度提升": "速度提高，会影响同优先级行动的出手顺序。",
        "速度降低": "速度降低，会影响同优先级行动的出手顺序。",
        "威力提升": "技能威力提高，结算时会抬高本次或后续技能伤害。",
        "威力降低": "技能威力降低，结算时会压低本次或后续技能伤害。",
        "连击等级提升": "连击次数提高，使对应技能获得更多段数。",
        "能耗降低": "技能能耗降低，释放时需要消耗的能量减少。",
        "能耗增加": "技能能耗增加，释放时需要消耗的能量增加。",
        "吸血": "根据实际造成的伤害回复自身生命。",
        "寄生": "持续扣除目标生命，通常会将部分生命转化为回复。",
        "先手加一": "技能优先级提高1级，更容易先于同速段技能行动。",
        "先手减一": "技能优先级降低1级，更容易晚于同速段技能行动。",
        "中毒": "回合结束受到毒系持续伤害，层数越高伤害越明显。",
        "冻结": "形成冻结线或冻结伤害记录，生命低于冻结线时会触发对应结算。",
        "灼烧": "回合结束受到火系持续伤害，并可能影响部分技能或特性结算。",
        "萌化": "使精灵向更早阶段退化，按退化后的形态和数值参与战斗。",
    }
    if title in effects:
        return effects[title]
    return "增益状态会强化己方结算。" if polarity == "positive" else "负面状态会削弱或消耗目标。"


def _build_local_status_entry(title: str, category: str, polarity: str, meta: str) -> dict:
    return {
        "id": title,
        "title": title,
        "category": category,
        "polarity": polarity,
        "meta": meta,
        "body": f"""== {title} ==
'''{title}''' 是战斗中的一种[[状态|{meta}]]。

=== 基础效果 ===
* {_status_entry_effect_text(title, polarity)}

=== 结算口径 ===
* 技能造成的数值类状态通常属于临时变化，会被换宠、反场或驱散类技能清除。
* 特性造成的五维变化通常按特性描述结算，是否持续保留以具体特性为准。

=== 页面关联 ===
* 下方会列出描述中涉及“{title}”或对应数值变化的技能与特性来源。""",
        "is_overview": False,
    }


def _local_status_icon_entries() -> list[dict]:
    entries = []
    for title in sorted(_build_mechanic_icon_cache()):
        classified = _classify_local_status_icon(title)
        if not classified:
            continue
        category, polarity, meta = classified
        entries.append(_build_local_status_entry(title, category, polarity, meta))
    return entries


def _override_mechanic_entry(entry: dict) -> dict:
    item = dict(entry)
    title = item.get("title", "")

    if title == "状态":
        item.update({
            "category": "关键词",
            "polarity": "system",
            "meta": "状态系统总览",
        })
        item["body"] = """== 状态 ==
'''状态''' 是挂在精灵身上的战斗效果。

=== 增益状态 ===
* 强化己方结算，例如[[物攻等级提升]]、[[威力提升]]、[[能耗降低]]、[[先手加一]]。
* 技能造成的数值变化通常属于临时变化，会被换宠、反场或驱散类技能清除。
* 特性造成的五维变化是否持续保留，以具体特性描述为准。

=== 负面状态 ===
* 削弱、限制或消耗目标，例如[[中毒]]、[[灼烧]]、[[冻结]]、[[速度降低]]、[[能耗增加]]。
* 负面状态会随具体技能或特性结算，有些按回合消耗，有些直接改变行动或伤害参数。

=== 与印记的区别 ===
* 印记挂在阵营上，每方一正一负两个槽位，与当前是哪只精灵在场无关。
* 状态挂在精灵身上，通常跟着精灵自身结算。"""

    if title == "防御姿态":
        item.update({
            "id": "防御",
            "title": "防御",
            "category": "增益状态",
            "polarity": "positive",
            "meta": "增益状态",
            "body": """== 防御 ==
'''防御''' 是由防御类技能产生的本回合减伤状态。

=== 基础效果 ===
* 减伤比例由技能决定，常见为50%、60%、70%、80%，部分技能可以完全免伤。
* 防御成立时，可以触发技能描述中的“应对防御”或“应对攻击”分支。

=== 冷却规则 ===
* 每使用一次防御技能，会产生1回合冷却。
* 这一回合必须按该精灵自己的回合计算。
* 如果使用防御后换下，再换该精灵上场，上场后的该精灵回合才会推进冷却。

=== 关联口径 ===
* 技能或特性描述中出现“防御”的，都会列在本页下方。""",
        })

    if title == "冰冻":
        item.update({
            "id": "冻结",
            "title": "冻结",
            "category": "负面状态",
            "polarity": "negative",
            "meta": "负面状态",
        })
        item["body"] = (item.get("body") or "").replace("冰冻", "冻结").replace("[[冰冻]]", "[[冻结]]")
    elif item.get("category") == "状态":
        polarity = item.get("polarity", "negative")
        item["category"] = "增益状态" if polarity == "positive" else "负面状态"
        item["meta"] = "增益状态" if polarity == "positive" else "负面状态"

    item["body"] = _clean_mechanic_body(item.get("body", ""))
    return item


def _prepare_mechanics_entries(raw_entries: list[dict]) -> list[dict]:
    entries = []
    seen = set()
    for raw in raw_entries:
        title = raw.get("title", "")
        if title in _MECHANIC_EXCLUDED_TITLES:
            continue
        item = _override_mechanic_entry(raw)
        if item["title"] in seen:
            continue
        seen.add(item["title"])
        entries.append(item)

    for item in _manual_mechanic_entries():
        if item["title"] not in seen:
            entries.append(_override_mechanic_entry(item))
            seen.add(item["title"])

    for item in _local_status_icon_entries():
        if item["title"] not in seen:
            entries.append(_override_mechanic_entry(item))
            seen.add(item["title"])

    cat_order = {"印记": 0, "增益状态": 1, "负面状态": 2, "天气": 3, "关键词": 4}
    pol_order = {"positive": 0, "negative": 1, "system": 2}
    entries.sort(key=lambda e: (
        cat_order.get(e.get("category"), 9),
        0 if e.get("is_overview") else 1,
        pol_order.get(e.get("polarity"), 2),
        _BATTLE_MARKS.index(e["title"]) if e.get("title") in _BATTLE_MARKS else 99,
        e.get("title", ""),
    ))
    return entries


def _mechanics_entries() -> list[dict]:
    global _MECHANICS_CACHE
    if _MECHANICS_CACHE is not None:
        return _MECHANICS_CACHE
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "mechanics_entries.json",
    )
    if not os.path.exists(path):
        _MECHANICS_CACHE = []
        return _MECHANICS_CACHE
    with open(path, encoding="utf-8") as f:
        raw_entries = json.load(f)
        _MECHANICS_CACHE = _prepare_mechanics_entries(raw_entries)
    return _MECHANICS_CACHE


def _wiki_link_targets(text: str) -> set[str]:
    targets = set()
    for raw in re.findall(r"\[\[([^\]]+)\]\]", text or ""):
        page = raw.split("|", 1)[0].strip()
        display = raw.split("|", 1)[-1].strip()
        if page:
            targets.add(page)
        if display:
            targets.add(display)
    return targets


def _mechanic_exact_keywords(entry: dict) -> list[str]:
    title = entry.get("title", "")
    aliases = {
        "冻结": ["冻结", "冰冻"],
        "防御": ["防御"],
    }
    if entry.get("is_overview"):
        if title == "印记":
            return ["印记"]
        return []
    words = aliases.get(title, [title])
    return [w for w in dict.fromkeys(words) if w]


def _text_mentions_any(text: str, words: list[str]) -> bool:
    return any(w and w in (text or "") for w in words)


def _strip_mark_suffix_mentions(text: str, title: str) -> str:
    return (text or "").replace(f"{title}印记", "")


def _has_stat_change(text: str) -> bool:
    if not text:
        return False
    stat = r"(物攻|魔攻|物防|魔防|速度|双攻|双防|攻防|攻防速|全属性|全能力)"
    sign = r"[+\-＋－]"
    return bool(
        re.search(stat + r"(?:和" + stat + r")?" + sign + r"\d+", text)
        or re.search(r"提升\d+%?(?:攻防|双攻|双防|物攻|魔攻|物防|魔防|速度)", text)
        or re.search(r"(?:攻防|双攻|双防|物攻|魔攻|物防|魔防|速度)" + r".{0,8}" + sign + r"\d+", text)
    )


def _match_stat_direction(text: str, stat: str, positive: bool) -> bool:
    if not text:
        return False
    sign = r"[+＋]" if positive else r"[\-－]"
    verbs = r"(提升|提高|增加|上升)" if positive else r"(降低|下降|减少|削弱)"
    return bool(
        re.search(stat + r".{0,8}" + sign + r"\d+", text)
        or re.search(stat + r".{0,8}" + verbs, text)
        or re.search(verbs + r".{0,8}" + stat, text)
    )


def _status_entry_matches(title: str, text: str) -> bool:
    if not text:
        return False
    if title in {"中毒", "灼烧", "萌化"}:
        return title in _strip_mark_suffix_mentions(text, title)
    if title == "冻结":
        return "冻结" in text or "冰冻" in text
    if title in {"吸血", "寄生", "防御"}:
        return title in text
    if title.endswith("等级提升"):
        stat = title.removesuffix("等级提升")
        return _match_stat_direction(text, stat, True)
    if title.endswith("等级降低"):
        stat = title.removesuffix("等级降低")
        return _match_stat_direction(text, stat, False)
    if title in {"速度提升", "威力提升"}:
        return _match_stat_direction(text, title.removesuffix("提升"), True)
    if title in {"速度降低", "威力降低"}:
        return _match_stat_direction(text, title.removesuffix("降低"), False)
    if title == "能耗降低":
        return bool(re.search(r"(能耗|耗能|能量消耗).{0,8}([\-－]\d+|降低|减少)", text) or "减耗" in text)
    if title == "能耗增加":
        return bool(re.search(r"(能耗|耗能|能量消耗).{0,8}([+＋]\d+|增加|提高|上升)", text))
    if title == "先手加一":
        return bool(re.search(r"(先手|先制|优先级).{0,4}([+＋]1|加一|提高|提升)", text))
    if title == "先手减一":
        return bool(re.search(r"(先手|先制|优先级).{0,4}([\-－]1|减一|降低|下降)", text))
    return title in text


def _contains_specific_mark(text: str) -> bool:
    return any(mark in (text or "") for mark in _BATTLE_MARKS)


def _mechanic_skill_matches(entry: dict, description: str) -> bool:
    title = entry.get("title", "")
    category = entry.get("category", "")
    if not description or entry.get("is_overview"):
        return title == "印记" and "印记" in (description or "")
    if category == "印记":
        return title in description
    if category in _STATUS_CATEGORIES:
        return _status_entry_matches(title, description)
    return _text_mentions_any(description, _mechanic_exact_keywords(entry))


def _mechanic_ability_matches(entry: dict, ability_text: str) -> bool:
    title = entry.get("title", "")
    category = entry.get("category", "")
    if not ability_text:
        return False
    if category == "印记":
        if title == "印记":
            return "印记" in ability_text
        if title in ability_text:
            return True
        if "所有印记" in ability_text:
            return True
        if "正面印记" in ability_text or "负面印记" in ability_text:
            return (
                ("正面印记" in ability_text and entry.get("polarity") == "positive")
                or ("负面印记" in ability_text and entry.get("polarity") == "negative")
            )
        return "印记" in ability_text and not _contains_specific_mark(ability_text)
    if category in _STATUS_CATEGORIES:
        return _status_entry_matches(title, ability_text)
    return _text_mentions_any(ability_text, _mechanic_exact_keywords(entry))


def _mechanic_icon_url(entry: dict) -> str:
    title = entry.get("title", "")
    icon = _get_mechanic_icon_url(title)
    if icon:
        return icon
    if title == "冰冻":
        icon = _get_mechanic_icon_url("冻结")
        if icon:
            return icon
    if title in _MECHANIC_LOCAL_ICON_MAP:
        return _MECHANIC_LOCAL_ICON_MAP[title]
    skill_name = _MECHANIC_SKILL_ICON_MAP.get(title)
    if skill_name:
        icon = _get_skill_icon_url(skill_name)
        if icon:
            return icon
    element = _MECHANIC_ELEMENT_ICON_MAP.get(title)
    if element:
        icon = _get_skill_meta_icon_url("elements", element)
        if icon:
            return icon
    if title == "防御":
        return _get_skill_meta_icon_url("categories", "防御")
    return ""


def _build_spirit_icon_meta_cache() -> dict:
    """读取本地图鉴立绘清单，补充编号、形态和同编号变体信息。"""
    global _SPIRIT_ICON_META_CACHE
    if _SPIRIT_ICON_META_CACHE is not None:
        return _SPIRIT_ICON_META_CACHE

    manifest = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "spirit_icons_manifest.csv",
    )
    by_name: dict[str, dict] = {}
    by_number: dict[str, list[dict]] = {}
    if os.path.exists(manifest):
        with open(manifest, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                filename = row.get("图片文件名", "")
                local_url = row.get("本地URL") or (f"/icons/{urllib.parse.quote(filename)}" if filename else "")
                item = {
                    "number": row.get("编号", ""),
                    "name": row.get("名字", ""),
                    "stage": row.get("阶段", ""),
                    "element": row.get("属性", ""),
                    "form_type": row.get("形态分类", ""),
                    "form": row.get("形态", ""),
                    "has_variant": row.get("是否有异色", ""),
                    "icon_url": local_url,
                    "wiki_url": row.get("详情页URL", ""),
                }
                if item["name"]:
                    by_name[item["name"]] = item
                if item["number"]:
                    by_number.setdefault(item["number"], []).append(item)

    _SPIRIT_ICON_META_CACHE = {"by_name": by_name, "by_number": by_number}
    return _SPIRIT_ICON_META_CACHE


def _get_spirit_icon_meta(name: str) -> dict:
    cache = _build_spirit_icon_meta_cache()
    return cache["by_name"].get(name, {})


def _is_leader_form(name: str, evo_stage: str = "") -> bool:
    meta = _get_spirit_icon_meta(name)
    text = " ".join([
        evo_stage or "",
        meta.get("form_type", ""),
        meta.get("form", ""),
    ])
    return "首领" in text


def _get_spirit_variants(number: str) -> list[dict]:
    cache = _build_spirit_icon_meta_cache()
    return cache["by_number"].get(_normalize_spirit_no(number), [])

# ═══════════════════════════════════════

def serialize_pokemon(p, is_current=False):
    # ability_state 中有意义的 UI 字段
    ability_state = getattr(p, "ability_state", {}) or {}
    ability_info = []
    # 特性 buff 层数（如身经百练的应对计数）
    if ability_state.get("guard_counters", 0) > 0:
        ability_info.append(f"应对计数:{ability_state['guard_counters']}")
    if ability_state.get("undying_revive_in", 0) > 0:
        ability_info.append(f"复活倒计时:{ability_state['undying_revive_in']}")
    if ability_state.get("threat_speed_bonus_active"):
        ability_info.append("预警加速")
    if ability_state.get("cost_invert"):
        ability_info.append("能耗反转")
    cute = getattr(p, "cute_stacks", 0)
    if cute > 0:
        ability_info.append(f"萌化×{cute}")

    import math
    return {
        "name":            p.name,
        "type":            p.pokemon_type.value,
        "bloodline":       getattr(p, "bloodline", ""),
        "battle_item":     getattr(p, "battle_item", ""),
        "evo_stage":       getattr(p, "evo_stage", ""),
        "spirit_no":       getattr(p, "spirit_no", ""),
        "is_leader_evolved": getattr(p, "is_leader_evolved", False),
        "hp":              math.floor(p.hp * 100) / 100,
        "current_hp":      max(0, math.floor(p.current_hp * 100) / 100),
        "energy":          p.energy,
        "is_fainted":      p.is_fainted,
        "ability":         p.ability,
        "poison_stacks":   p.poison_stacks,
        "burn_stacks":     p.burn_stacks,
        "frostbite_damage":p.frostbite_damage,
        "leech_stacks":    p.leech_stacks,
        "meteor_stacks":   p.meteor_stacks,
        "meteor_countdown":p.meteor_countdown,
        "cute_stacks":     getattr(p, "cute_stacks", 0),
        "charging":        p.charging_skill_idx >= 0,
        # 净值（正=buff，负=debuff）
        "atk_mod":         round((p.atk_up - p.atk_down) * 100),
        "def_mod":         round((p.def_up - p.def_down) * 100),
        "spatk_mod":       round((p.spatk_up - p.spatk_down) * 100),
        "spdef_mod":       round((p.spdef_up - p.spdef_down) * 100),
        "speed_mod":       round((p.speed_up - p.speed_down) * 100),
        # 分向数值（供前端分色显示）
        "atk_up":    round(p.atk_up * 100),
        "atk_down":  round(p.atk_down * 100),
        "def_up":    round(p.def_up * 100),
        "def_down":  round(p.def_down * 100),
        "spatk_up":  round(p.spatk_up * 100),
        "spatk_down":round(p.spatk_down * 100),
        "spdef_up":  round(p.spdef_up * 100),
        "spdef_down":round(p.spdef_down * 100),
        "speed_up":  round(p.speed_up * 100),
        "speed_down":round(p.speed_down * 100),
        # 特性状态
        "ability_info": ability_info,
        "icon_url":        _get_icon_url(p.name),
        "skills":          [serialize_skill(s, p.energy, p.cooldowns.get(i, 0))
                            for i, s in enumerate(p.skills)] if is_current else [],
    }


def serialize_skill(s, current_energy, cooldown=0):
    effect_view = _skill_effect_display(s)
    meta = _get_skill_metadata(s.name)
    return {
        "name":        s.name,
        "type":        s.skill_type.value,
        "category":    s.category.value,
        "power":       s.power,
        "energy_cost": s.energy_cost,
        "description": meta["description"],
        "icon_url":    meta["icon_url"],
        "attribute_icon_url": _get_skill_meta_icon_url("elements", s.skill_type.value) or meta["attribute_icon_url"],
        "category_icon_url":  _get_skill_meta_icon_url("categories", s.category.value) or meta["category_icon_url"],
        "energy_icon_url": _get_skill_meta_icon_url("misc", "energy"),
        "skill_group": meta["skill_group"],
        "wiki_url":    meta["wiki_url"],
        "can_use":     current_energy >= s.energy_cost and cooldown <= 0,
        "on_cooldown": cooldown > 0,
        "cooldown":    cooldown,
        "tags":        _skill_tags(s),
        "effect_tags": effect_view["tags"],
        "effect_details": effect_view["details"],
        "effect_summary": effect_view["summary"],
        "has_effects": effect_view["has_effects"],
    }


def _skill_tags(s):
    tags = []
    if s.life_drain > 0:       tags.append(f"吸血{int(s.life_drain*100)}%")
    if s.damage_reduction > 0: tags.append(f"减伤{int(s.damage_reduction*100)}%")
    if s.self_heal_hp > 0:     tags.append(f"回血{int(s.self_heal_hp*100)}%")
    if s.poison_stacks > 0:    tags.append(f"中毒×{s.poison_stacks}")
    if s.burn_stacks > 0:      tags.append(f"燃烧×{s.burn_stacks}")
    if s.freeze_stacks > 0:    tags.append(f"冻结×{s.freeze_stacks}")
    if s.leech_stacks > 0:     tags.append(f"寄生×{s.leech_stacks}")
    if s.meteor_stacks > 0:    tags.append(f"星陨×{s.meteor_stacks}")
    if s.hit_count > 1:        tags.append(f"{s.hit_count}连击")
    if s.force_switch:         tags.append("折返")
    if s.agility:              tags.append("迅捷")
    if s.charge:               tags.append("蓄力")
    if s.priority_mod > 0:     tags.append("先手")
    if s.is_mark:              tags.append("印记")
    # 从 effects 读取更多标签，避免 UI 只看到基础数值
    if hasattr(s, "effects") and s.effects:
        from src.effect_models import SkillEffect as _SE, SkillTiming as _ST
        for item in s.effects:
            if isinstance(item, _SE):
                for tag in item.effects:
                    text = _effect_tag_text(tag)
                    if text:
                        tags.append(text.split(":", 1)[0].split("：", 1)[0])
            else:
                text = _effect_tag_text(item)
                if text:
                    tags.append(text.split("：", 1)[0])
    return list(dict.fromkeys(tags))  # 去重保序


def _get_type_effectiveness_for_display(attacker_type_val: str, defender_type_val: str) -> float:
    """计算技能对目标的克制倍率（用于换人提示）"""
    from src.models import get_type_effectiveness, Type
    try:
        atk_type = Type(attacker_type_val)
        def_type = Type(defender_type_val)
        return get_type_effectiveness(atk_type, def_type)
    except Exception:
        return 1.0


def _manual_switch_prompts(state: BattleState) -> List[dict]:
    """整理手动模式的待补位请求，每方最多保留一个，倒下优先。"""
    prompts_by_team = {}
    for req in getattr(state, "pending_switch_requests", []) or []:
        team = req.get("team")
        if team not in ("a", "b"):
            continue
        if team not in prompts_by_team or req.get("reason") == "fainted":
            prompts_by_team[team] = {
                "team": team,
                "reason": req.get("reason", "force_switch"),
                "alive": req.get("alive", []),
            }
    return [prompts_by_team[t] for t in ("a", "b") if t in prompts_by_team]


def serialize_state(state: BattleState, waiting: bool = False,
                    game_over: bool = False, winner: str = None,
                    events: List[dict] = None,
                    force_switch_prompt: bool = False,
                    force_switch_reason: str = "force_switch",
                    force_switch_alive: list = None):
    team_a_data = []
    for i, p in enumerate(state.team_a):
        d = serialize_pokemon(p, is_current=(i == state.current_a))
        d["is_current"] = (i == state.current_a)
        if i == state.current_a:
            d["leader_evolution"] = leader_evolution_status(state, "a")
        team_a_data.append(d)

    team_b_data = []
    for i, p in enumerate(state.team_b):
        d = serialize_pokemon(p, is_current=(i == state.current_b))
        d["is_current"] = (i == state.current_b)
        if i == state.current_b:
            d["leader_evolution"] = leader_evolution_status(state, "b")
        team_b_data.append(d)

    # 为 A 队每个精灵计算对当前 B 精灵的最高克制倍率
    enemy_b = state.team_b[state.current_b]
    for d in team_a_data:
        best_eff = 1.0
        for sk in (state.team_a[team_a_data.index(d)].skills if not d["is_current"]
                   else state.team_a[state.current_a].skills):
            eff = _get_type_effectiveness_for_display(sk.skill_type.value, enemy_b.pokemon_type.value)
            best_eff = max(best_eff, eff)
        d["type_advantage"] = best_eff  # 1.0=普通 2.0=克制 0.5=被克制

    return {
        "type":               "state",
        "turn":               state.turn,
        "mp_a":               state.mp_a,
        "mp_b":               state.mp_b,
        "team_item_a":        state.team_item_a,
        "team_item_b":        state.team_item_b,
        "team_a":             team_a_data,
        "team_b":             team_b_data,
        "current_a":          state.current_a,
        "current_b":          state.current_b,
        "waiting_for_player": waiting,
        "game_over":          game_over,
        "winner":             winner,
        "battle_mode":        session.mode,
        "logs":               session.logs,
        "events":             events or [],
        "force_switch_prompt":  force_switch_prompt,
        "force_switch_reason":  force_switch_reason,  # "fainted" | "force_switch"
        "force_switch_alive":   force_switch_alive,    # 后端计算好的可选精灵索引列表
        "manual_switch_prompts": _manual_switch_prompts(state) if session.mode == "manual" else [],
    }


def _manual_switch_callback(state, team_list, alive_indices):
    """手动模式下让双方都挂起补位选择。"""
    return None


def _apply_passive_ability_flags(pokemon, ability_effects):
    """加载需要在创建时立即生效的被动特性标记。"""
    pokemon.ability_state = getattr(pokemon, "ability_state", {}) or {}
    for ae in ability_effects:
        for tag in ae.effects:
            if tag.type == E.COST_INVERT:
                pokemon.ability_state["cost_invert"] = True
            elif tag.type == E.IMMUNE_ZERO_ENERGY_ATTACKER:
                pokemon.ability_state["immune_zero_energy_attacker"] = True
            elif tag.type == E.IMMUNE_LOW_COST_ATTACK:
                pokemon.ability_state["immune_low_cost_attack"] = tag.params.get("cost_threshold", 1)
            elif tag.type == E.FIXED_HIT_COUNT_ALL:
                pokemon.ability_state["fixed_hit_count_all"] = tag.params.get("count", 2)
            elif tag.type == E.HIT_COUNT_PER_POISON:
                pokemon.ability_state["hit_count_per_poison"] = True
            elif tag.type == E.FAINT_NO_MP_LOSS:
                pokemon.ability_state["faint_no_mp_loss"] = True
            elif tag.type == E.EXTRA_POISON_TICK:
                pokemon.ability_state["extra_poison_tick"] = True
            elif tag.type == E.HEAL_PER_TURN:
                pokemon.ability_state["heal_per_turn_pct"] = tag.params.get("heal_pct", 0.12)
            elif tag.type == E.SHARE_GAINS:
                pokemon.ability_state["share_gains"] = True
            elif tag.type == E.HALF_METEOR_FULL_DAMAGE:
                pokemon.ability_state["half_meteor_full_damage"] = True
            elif tag.type == E.CHARGE_FREE_SKILL:
                pokemon.ability_state["charge_free_skill"] = True
            elif tag.type == E.COST_CHANGE_DOUBLE:
                pokemon.ability_state["cost_change_double"] = True
            elif tag.type == E.TURN_END_REPEAT:
                delta = tag.params.get("delta", 1)
                pokemon.ability_state["turn_end_repeat"] = pokemon.ability_state.get("turn_end_repeat", 0) + delta
            elif tag.type == E.TURN_END_SKIP:
                delta = tag.params.get("delta", 1)
                pokemon.ability_state["turn_end_skip"] = pokemon.ability_state.get("turn_end_skip", 0) + delta
            elif tag.type == E.BUFF_EXTRA_LAYERS:
                pokemon.ability_state["buff_extra_layers"] = tag.params.get("extra", 2)
            elif tag.type == E.MARK_STACK_NO_REPLACE:
                pokemon.ability_state["mark_stack_additive"] = True
            elif tag.type == E.CUTE_NO_CAP:
                pokemon.ability_state["cute_no_cap"] = True
            elif tag.type == E.CUTE_HIT_PER_STACK:
                pokemon.ability_state["cute_hit_per_stack"] = tag.params.get("per", 2)


def _build_team_from_config(team_cfg: list, label: str):
    """从前端配置构造一方队伍。"""
    from src.pokemon_db import get_pokemon, calc_combat_stats
    from src.models import Pokemon, Type
    from src.skill_db import get_skill, load_ability_effects

    type_map = TeamBuilder.TYPE_MAP
    built_team = []
    errors = []

    for pos, entry in enumerate(team_cfg, start=1):
        pname = (entry.get("name") or "").strip()
        skill_names = [n for n in entry.get("skills", []) if n][:4]
        data = get_pokemon(pname)
        if not data:
            errors.append(f"{label}第{pos}位未找到精灵: {pname or '空'}")
            continue
        if not skill_names:
            errors.append(f"{label}{pname} 未配置技能")
            continue

        ability = (entry.get("ability") or data["特性"] or "").strip()
        nature = entry.get("nature", "坦率")
        iv_config = entry.get("iv_config")
        stats = calc_combat_stats(
            base_hp=data["生命种族值"],
            base_atk=data["物攻种族值"],
            base_spatk=data["魔攻种族值"],
            base_def=data["物防种族值"],
            base_spdef=data["魔防种族值"],
            base_speed=data["速度种族值"],
            iv_config=iv_config,
            nature_name=nature,
        )

        pokemon = Pokemon(
            name=pname,
            pokemon_type=type_map.get(str(data["属性"] or "").replace("，", ",").split(",")[0].strip(), Type.NORMAL),
            hp=stats["hp"],
            attack=stats["atk"],
            defense=stats["def"],
            sp_attack=stats["spatk"],
            sp_defense=stats["spdef"],
            speed=stats["speed"],
            ability=ability,
            skills=[get_skill(n) for n in skill_names],
            bloodline=(entry.get("bloodline") or "").strip(),
            battle_item=(entry.get("battle_item") or "").strip(),
            dex_name=data["名称"],
            evo_stage=data["进化阶段"],
            spirit_no=data.get("图鉴编号", ""),
            is_leader_evolved="首领" in (data["进化阶段"] or ""),
        )
        if iv_config:
            pokemon.iv_hp = iv_config.get("hp", 0)
            pokemon.iv_atk = iv_config.get("atk", 0)
            pokemon.iv_spatk = iv_config.get("spatk", 0)
            pokemon.iv_def = iv_config.get("def", 0)
            pokemon.iv_spdef = iv_config.get("spdef", 0)
            pokemon.iv_speed = iv_config.get("speed", 0)
        pokemon.nature = nature
        pokemon.ability_effects = load_ability_effects(ability) if ability else []
        _apply_passive_ability_flags(pokemon, pokemon.ability_effects)
        built_team.append(pokemon)

    if len(built_team) != 6:
        errors.append(f"{label}需要6只精灵，当前{len(built_team)}只")

    return built_team, errors


def _team_item_from_config(team_cfg: list, explicit: str = "") -> str:
    value = (explicit or "").strip()
    if value:
        return value
    for entry in team_cfg or []:
        value = (entry.get("battle_item") or entry.get("magic") or "").strip()
        if value:
            return value
    return ""


def _parse_side_action(state: BattleState, side: str, action_data: dict):
    team = state.team_a if side == "a" else state.team_b
    current_idx = state.current_a if side == "a" else state.current_b
    current = team[current_idx]
    side_name = "我方" if side == "a" else "对方"

    action_type = action_data.get("type")
    if action_type == "charge":
        return (-1,), None
    if action_type == "leader_evolve":
        status = leader_evolution_status(state, side)
        if not status.get("can_use"):
            return None, f"{side_name}{current.name} 无法首领进化：{status.get('reason', '')}"
        return (-3,), None
    if action_type == "skill":
        idx = int(action_data.get("index", -1))
        if idx < 0 or idx >= len(current.skills):
            return None, f"{side_name}技能序号无效"
        skill = current.skills[idx]
        cooldown = current.cooldowns.get(idx, 0)
        if current.energy < skill.energy_cost:
            return None, f"{side_name}{current.name} 能量不足，无法使用 {skill.name}"
        if cooldown > 0:
            return None, f"{side_name}{current.name} 的 {skill.name} 仍在冷却"
        return (idx,), None
    if action_type == "switch":
        target_idx = int(action_data.get("index", -1))
        if target_idx < 0 or target_idx >= len(team):
            return None, f"{side_name}换人序号无效"
        if target_idx == current_idx or team[target_idx].is_fainted:
            return None, f"{side_name}无法换上该精灵"
        return (-2, target_idx), None
    return None, f"{side_name}行动类型无效"


def _log_declared_action(state: BattleState, side: str, action):
    icon = "🟦" if side == "a" else "🟥"
    side_name = "我方" if side == "a" else "对方"
    team = state.team_a if side == "a" else state.team_b
    current_idx = state.current_a if side == "a" else state.current_b
    pokemon = team[current_idx]

    if action[0] == -1:
        session.add_log(f"  {icon} {side_name}选择：汇合聚能（+5能）")
    elif action[0] == -2:
        session.add_log(f"  {icon} {side_name}选择：换上 {team[action[1]].name}（优先执行）")
    elif action[0] == -3:
        status = leader_evolution_status(state, side)
        target = status.get("target_name", "下一形态")
        session.add_log(f"  {icon} {side_name}选择：{pokemon.name} 使用【进化之力】→ {target}")
    else:
        skill = pokemon.skills[action[0]]
        session.add_log(
            f"  {icon} {side_name}：{pokemon.name} 使用【{skill.name}】"
            f"（消耗{skill.energy_cost}能 威力{skill.power}）{_eff_preview(skill)}"
        )


def _resolve_manual_pending_switches(state: BattleState):
    """手动模式先用确定性被动换人收束 pending，后续可升级为弹窗选择。"""
    if not state.pending_switch_requests:
        return
    pending = state.pending_switch_requests
    state.pending_switch_requests = []
    for req in pending:
        alive = req.get("alive") or []
        if not alive:
            continue
        side = req["team"]
        chosen = alive[0]
        if side == "a":
            state.current_a = chosen
            pokemon = state.team_a[chosen]
            session.add_log(f"  🔄 我方自动补位：{pokemon.name}")
        else:
            state.current_b = chosen
            pokemon = state.team_b[chosen]
            session.add_log(f"  🔄 对方自动补位：{pokemon.name}")


# ═══════════════════════════════════════
# WebSocket
# ═══════════════════════════════════════

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg  = json.loads(data)
            try:
                await handle_message(websocket, msg)
            except Exception as e:
                import traceback as _tb
                err_detail = _tb.format_exc()
                print(f"[WS ERROR] {e}\n{err_detail}", flush=True)
                try:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"服务器内部错误: {e}"
                    }))
                    if session.state and not session.game_over:
                        session.waiting_for_player = True
                        await websocket.send_text(json.dumps(serialize_state(
                            session.state, waiting=True
                        )))
                except Exception:
                    pass
    except WebSocketDisconnect:
        pass
    except Exception:
        pass


async def handle_message(ws: WebSocket, msg: dict):
    cmd = msg.get("cmd")
    if   cmd == "start_manual_custom": await start_manual_custom_battle(ws, msg)
    elif cmd == "manual_turn":  await receive_manual_turn(ws, msg)
    elif cmd == "manual_switch": await receive_manual_switch(ws, msg)
    elif cmd == "get_state":
        if session.state:
            winner = check_winner(session.state)
            await ws.send_text(json.dumps(serialize_state(
                session.state,
                waiting=session.waiting_for_player,
                game_over=session.game_over,
                winner=winner,
            )))
        else:
            await ws.send_text(json.dumps({"type": "no_battle"}))
    elif cmd == "reset":
        session.reset()
        await ws.send_text(json.dumps({"type": "reset_ok"}))
    else:
        await ws.send_text(json.dumps({
            "type": "error",
            "message": "该对战入口只支持双方手动模拟，请先在队伍页配置双方阵容",
        }))


async def start_manual_custom_battle(ws: WebSocket, msg: dict):
    """启动双方均由用户手动控制的自定义模拟对战。"""
    _ensure_loaded()
    session.reset()
    session.mode = "manual"

    team_a_cfg = msg.get("team_a") or msg.get("player_team") or []
    team_b_cfg = msg.get("team_b") or msg.get("enemy_team") or []
    team_item_a = _team_item_from_config(team_a_cfg, msg.get("team_item_a", ""))
    team_item_b = _team_item_from_config(team_b_cfg, msg.get("team_item_b", ""))
    team_a, errors_a = _build_team_from_config(team_a_cfg, "我方")
    team_b, errors_b = _build_team_from_config(team_b_cfg, "对方")
    errors = errors_a + errors_b
    if errors:
        await ws.send_text(json.dumps({"type": "error", "message": "; ".join(errors)}))
        return

    state = BattleState(
        team_a=team_a,
        team_b=team_b,
        current_a=0,
        current_b=0,
        turn=1,
        team_item_a=team_item_a,
        team_item_b=team_item_b,
    )
    session.state = state
    session.game_over = False
    session.waiting_for_player = True

    session.add_log("═══════════════════════════")
    session.add_log("⚔️  手动模拟对战开始！")
    session.add_log(f"🟦 我方: {', '.join(p.name for p in team_a)}")
    session.add_log(f"🟥 对方: {', '.join(p.name for p in team_b)}")
    if team_item_a or team_item_b:
        session.add_log(f"🎒 携带物: 我方={_lineup_magic_label(team_item_a) or '无'} | 对方={_lineup_magic_label(team_item_b) or '无'}")
    session.add_log("═══════════════════════════")

    snap_before = _snapshot(state)
    auto_switch(state, _manual_switch_callback, _manual_switch_callback)
    _resolve_manual_pending_switches(state)
    snap_after = _snapshot(state)
    for line in _diff_to_logs(snap_before, snap_after, state):
        session.add_log(line)

    await ws.send_text(json.dumps(serialize_state(state, waiting=True)))


async def receive_manual_turn(ws: WebSocket, msg: dict):
    if not session.state or session.game_over:
        return
    if session.mode != "manual":
        await ws.send_text(json.dumps({"type": "error", "message": "当前不是手动模拟模式"}))
        return

    state = session.state
    action_a, err_a = _parse_side_action(state, "a", msg.get("action_a") or {})
    action_b, err_b = _parse_side_action(state, "b", msg.get("action_b") or {})
    if err_a or err_b:
        await ws.send_text(json.dumps({"type": "error", "message": err_a or err_b}))
        return

    session.waiting_for_player = False

    moisture_a = state.marks_a.get("moisture_mark", 0)
    moisture_b = state.marks_b.get("moisture_mark", 0)

    pa = state.team_a[state.current_a]
    pb = state.team_b[state.current_b]
    session.add_log("")
    session.add_log(f"─── 回合 {state.turn} ───")
    session.add_log(
        f"  📌 当前: 🟦{pa.name}（HP {round(pa.current_hp, 2)}/{pa.hp} E={pa.energy}）"
        f"  vs  🟥{pb.name}（HP {round(pb.current_hp, 2)}/{pb.hp} E={pb.energy}）"
    )
    _log_declared_action(state, "a", action_a)
    _log_declared_action(state, "b", action_b)

    snap_before = _snapshot(state)
    if state.energy_recharge_log:
        state.energy_recharge_log.clear()

    try:
        execute_full_turn(state, action_a, action_b, _manual_switch_callback, _manual_switch_callback)
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        session.add_log(f"  ❌ 战斗执行异常: {e}")
        await ws.send_text(json.dumps({"type": "error", "message": f"战斗异常: {e}\n{err_msg}"}))
        session.waiting_for_player = True
        await ws.send_text(json.dumps(serialize_state(state, waiting=True)))
        return

    snap_after = _snapshot(state)

    if getattr(state, "battle_event_log", None):
        for ev in state.battle_event_log:
            if ev.get("type") == "leader_evolve":
                side_str = "我方" if ev.get("team") == "a" else "对方"
                ability = ev.get("ability", "")
                ability_name = ability.split(":")[0].split("：")[0] if ability else ""
                detail = f"，特性变为【{ability_name}】" if ability_name else ""
                session.add_log(f"  👑 {side_str} {ev.get('from')} 进化为 {ev.get('to')}{detail}")
        state.battle_event_log.clear()

    for ev in state.energy_recharge_log:
        side_str = "我方" if ev["team"] == "a" else "对方"
        session.add_log(
            f"  ⚡ {side_str} {ev['pokemon']} 能量不足（需{ev['needed']}，有{ev['had']}），"
            f"自动聚能+5，{ev['skill']}未能释放"
        )

    if moisture_a > 0:
        session.add_log(f"  💧 湿润印记触发！我方全队技能能耗 -{moisture_a}")
    if moisture_b > 0:
        session.add_log(f"  💧 湿润印记触发！对方全队技能能耗 -{moisture_b}")

    for line in _diff_to_logs(snap_before, snap_after, state):
        session.add_log(line)

    pa2 = state.team_a[state.current_a]
    pb2 = state.team_b[state.current_b]
    session.add_log(
        f"  📊 结算 → 🟦{pa2.name} HP:{round(max(0, pa2.current_hp), 2)}/{pa2.hp} E={pa2.energy}"
        f"  |  🟥{pb2.name} HP:{round(max(0, pb2.current_hp), 2)}/{pb2.hp} E={pb2.energy}"
    )
    session.add_log(f"  🔷 MP → 我方={state.mp_a} | 对方={state.mp_b}")

    events = _build_events(snap_before, snap_after, state, action_a, action_b, pa, pb)

    if _manual_switch_prompts(state):
        session.waiting_for_player = True
        await ws.send_text(json.dumps(serialize_state(state, waiting=True, events=events)))
        return

    winner = check_winner(state)
    if winner:
        session.game_over = True
        session.add_log("")
        session.add_log("🏆 我方胜利！" if winner == "a" else "🏆 对方胜利！")
        await ws.send_text(json.dumps(serialize_state(
            state, waiting=False, game_over=True, winner=winner, events=events
        )))
        return

    session.waiting_for_player = True
    await ws.send_text(json.dumps(serialize_state(state, waiting=True, events=events)))


async def receive_manual_switch(ws: WebSocket, msg: dict):
    if not session.state or session.game_over:
        return
    if session.mode != "manual":
        await ws.send_text(json.dumps({"type": "error", "message": "当前不是手动模拟模式"}))
        return

    state = session.state
    prompts = _manual_switch_prompts(state)
    if not prompts:
        await ws.send_text(json.dumps(serialize_state(state, waiting=True)))
        return

    selections = msg.get("selections") or {}
    from src.battle import _apply_mark_on_enter

    for prompt in prompts:
        side = prompt["team"]
        alive = prompt.get("alive") or []
        if not alive:
            continue
        raw_choice = selections.get(side)
        try:
            chosen = int(raw_choice)
        except (TypeError, ValueError):
            chosen = alive[0]
        if chosen not in alive:
            await ws.send_text(json.dumps({
                "type": "error",
                "message": f"{'我方' if side == 'a' else '对方'}补位选择无效",
            }))
            return

        if side == "a":
            already_placed = chosen == state.current_a
            state.current_a = chosen
            new_pokemon = state.team_a[chosen]
            enemy = state.team_b[state.current_b]
            session.add_log(f"  ↩️  我方换上 {new_pokemon.name}")
        else:
            already_placed = chosen == state.current_b
            state.current_b = chosen
            new_pokemon = state.team_b[chosen]
            enemy = state.team_a[state.current_a]
            session.add_log(f"  ↩️  对方换上 {new_pokemon.name}")

        if not already_placed:
            _apply_mark_on_enter(state, side, new_pokemon)
            EffectExecutor.execute_agility_entry(state, new_pokemon, enemy, side)
            if new_pokemon.ability_effects:
                EffectExecutor.execute_ability(
                    state, new_pokemon, enemy,
                    Timing.ON_ENTER, new_pokemon.ability_effects, side,
                )

    state.pending_switch_requests = []
    winner = check_winner(state)
    if winner:
        session.game_over = True
        session.add_log("")
        session.add_log("🏆 我方胜利！" if winner == "a" else "🏆 对方胜利！")
        await ws.send_text(json.dumps(serialize_state(
            state, waiting=False, game_over=True, winner=winner
        )))
        return

    session.waiting_for_player = True
    await ws.send_text(json.dumps(serialize_state(state, waiting=True)))


def _eff_preview(s) -> str:
    """技能效果简短预览，附在战报行中"""
    parts = []
    if s.life_drain > 0:        parts.append(f"吸血{int(s.life_drain*100)}%")
    if s.damage_reduction > 0:  parts.append(f"减伤{int(s.damage_reduction*100)}%")
    if s.poison_stacks > 0:     parts.append(f"→中毒×{s.poison_stacks}")
    if s.burn_stacks > 0:       parts.append(f"→燃烧×{s.burn_stacks}")
    if s.leech_stacks > 0:      parts.append(f"→寄生×{s.leech_stacks}")
    if s.meteor_stacks > 0:     parts.append(f"→星陨×{s.meteor_stacks}")
    if s.force_switch:           parts.append("→折返")
    if s.agility:                parts.append("（迅捷）")
    if s.charge:                 parts.append("（蓄力）")
    # effects 里的应对标签
    if hasattr(s, "effects") and s.effects:
        from src.effect_models import E, SkillEffect, SkillTiming
        for item in s.effects:
            if isinstance(item, SkillEffect) and item.timing == SkillTiming.ON_COUNTER:
                cat = item.filter.get("category", "")
                if cat == "attack":   parts.append("[应对物/魔]")
                elif cat == "defense": parts.append("[应对防御]")
                elif cat == "status":  parts.append("[应对变化]")
            elif hasattr(item, "type"):
                if item.type == E.COUNTER_ATTACK:  parts.append("[应对物/魔]")
                if item.type == E.COUNTER_DEFENSE: parts.append("[应对防御]")
                if item.type == E.COUNTER_STATUS:  parts.append("[应对变化]")
    return "  " + " | ".join(parts) if parts else ""


def _build_events(snap_before, snap_after, state, action_a, action_b, pa_before, pb_before) -> List[dict]:
    """生成本回合前端动画事件列表（按先后手时序排列）"""

    ca_before = snap_before.get("current_a", 0)
    cb_before = snap_before.get("current_b", 0)
    ca_after  = snap_after.get("current_a", ca_before)
    cb_after  = snap_after.get("current_b", cb_before)

    # ── 判断先后手 ──
    is_switch_a = len(action_a) == 2 and action_a[0] == -2
    is_switch_b = len(action_b) == 2 and action_b[0] == -2
    spd_a = pa_before.speed if pa_before else 0
    spd_b = pb_before.speed if pb_before else 0
    pri_a = 99 if is_switch_a else spd_a
    pri_b = 99 if is_switch_b else spd_b
    a_first = pri_a >= pri_b

    # ── 伤害计算（用 after 时的在场精灵索引） ──
    def calc_dmg(side, cur_idx):
        snap_k = f"{side}_{cur_idx}_hp"
        hp_before_val = snap_before.get(snap_k, snap_after.get(snap_k, 0))
        hp_after_val  = snap_after.get(snap_k, 0)
        return max(0, hp_before_val - hp_after_val)

    dmg_a = calc_dmg("a", ca_after)
    dmg_b = calc_dmg("b", cb_after)

    eff_a = state.team_b[cb_after].ability_state.pop("_last_effectiveness_on_a", 1.0) if cb_after < len(state.team_b) else 1.0
    eff_b = state.team_a[ca_after].ability_state.pop("_last_effectiveness_on_b", 1.0) if ca_after < len(state.team_a) else 1.0
    if eff_a == 1.0:
        eff_a = state.team_b[cb_after].ability_state.pop("_last_effectiveness", 1.0) if cb_after < len(state.team_b) else 1.0
    if eff_b == 1.0:
        eff_b = state.team_a[ca_after].ability_state.pop("_last_effectiveness", 1.0) if ca_after < len(state.team_a) else 1.0

    # ── 检测某方在场精灵是否新增了 debuff（燃烧/中毒/寄生/冻结）──
    # 只检测在场精灵（ca_after / cb_after 对应的那只）
    def has_new_debuff(side, cur_idx):
        for key in ("poison", "burn", "leech", "frost"):
            before_val = snap_before.get(f"{side}_{cur_idx}_{key}", 0)
            after_val  = snap_after.get(f"{side}_{cur_idx}_{key}", 0)
            if after_val > before_val:
                return True
        return False

    a_got_debuff = has_new_debuff("a", ca_after)
    b_got_debuff = has_new_debuff("b", cb_after)

    # ── 检测某方在场精灵是否回血（HP 增加，如吸血/治愈）──
    def calc_heal(side, cur_idx):
        snap_k = f"{side}_{cur_idx}_hp"
        hp_before_val = snap_before.get(snap_k, snap_after.get(snap_k, 0))
        hp_after_val  = snap_after.get(snap_k, 0)
        return max(0, hp_after_val - hp_before_val)

    heal_a = calc_heal("a", ca_after)
    heal_b = calc_heal("b", cb_after)

    def mk_hit(side, dmg, eff, atk_anim):
        evt = {"type": "hit", "side": side, "dmg": dmg, "atk_anim": atk_anim}
        if eff >= 2.0:          evt["eff"] = "super"
        elif 0 < eff <= 0.5:    evt["eff"] = "resist"
        return evt

    def mk_debuff_hit(side, dmg):
        """状态 debuff 造成的受击：只有受击方闪烁，无冲刺"""
        return {"type": "hit", "side": side, "dmg": dmg, "atk_anim": False}

    def mk_shield(side):
        return {"type": "shield", "side": side}

    def get_shield(side):
        action = action_a if side == "a" else action_b
        poke   = pa_before if side == "a" else pb_before
        if action[0] >= 0 and poke and action[0] < len(poke.skills):
            sk = poke.skills[action[0]]
            if sk.damage_reduction > 0 or _has_counter(sk):
                return mk_shield(side)
        return None

    # ── 换宠事件 ──
    switch_events = []
    for side, before_idx, after_idx, team_list in [
        ("a", ca_before, ca_after, state.team_a),
        ("b", cb_before, cb_after, state.team_b),
    ]:
        if before_idx != after_idx:
            old_p = team_list[before_idx] if before_idx < len(team_list) else None
            new_p = team_list[after_idx]  if after_idx  < len(team_list) else None
            switch_events.append({"type": "switch_out", "side": side,
                                   "name": old_p.name if old_p else ""})
            switch_events.append({"type": "switch_in",  "side": side,
                                   "name": new_p.name if new_p else "",
                                   "icon_url": _get_icon_url(new_p.name) if new_p else ""})

    # ── 倒地事件 ──
    faint_events = []
    for team, n_count in [("a", len(state.team_a)), ("b", len(state.team_b))]:
        for i in range(n_count):
            if not snap_before.get(f"{team}_{i}_fainted") and snap_after.get(f"{team}_{i}_fainted"):
                faint_events.append({"type": "faint", "side": team, "idx": i})

    # ── 按时序组装 ──
    events = []
    events.extend(switch_events)

    first_side  = "a" if a_first else "b"
    second_side = "b" if a_first else "a"
    first_dmg    = dmg_b if first_side == "a" else dmg_a
    second_dmg   = dmg_a if first_side == "a" else dmg_b
    first_heal   = heal_a if first_side == "a" else heal_b   # 先手方自己是否回血
    second_heal  = heal_b if first_side == "a" else heal_a
    first_got_debuff  = b_got_debuff if first_side == "a" else a_got_debuff
    second_got_debuff = a_got_debuff if first_side == "a" else b_got_debuff

    sh_first  = get_shield(second_side)
    sh_second = get_shield(first_side)

    # 先手行动
    if sh_first:
        events.append(sh_first)
    if first_dmg > 0:
        eff = eff_b if first_side == "a" else eff_a
        events.append(mk_hit(second_side, first_dmg, eff, not first_got_debuff))
    if first_heal > 0:
        events.append({"type": "heal", "side": first_side, "amount": first_heal})

    # 后手行动
    if sh_second:
        events.append(sh_second)
    if second_dmg > 0:
        eff = eff_a if first_side == "a" else eff_b
        events.append(mk_hit(first_side, second_dmg, eff, not second_got_debuff))
    if second_heal > 0:
        events.append({"type": "heal", "side": second_side, "amount": second_heal})

    events.extend(faint_events)
    return events


def _has_counter(s) -> bool:
    if hasattr(s, "effects") and s.effects:
        from src.effect_models import E, SkillEffect, SkillTiming
        for item in s.effects:
            if isinstance(item, SkillEffect) and item.timing == SkillTiming.ON_COUNTER:
                return True
            if hasattr(item, "type") and item.type in (E.COUNTER_ATTACK, E.COUNTER_DEFENSE, E.COUNTER_STATUS):
                return True
    return (s.counter_physical_power_mult > 0 or s.counter_defense_power_mult > 0
            or s.counter_status_power_mult > 0)


# ═══════════════════════════════════════
# REST API — 阵容搭配器数据接口
# ═══════════════════════════════════════

# 内存存储队伍（临时，后续可改为数据库持久化）
_teams_cache: dict[str, dict] = {}


@app.get("/api/pokemon/list")
async def api_pokemon_list(q: str = ""):
    """搜索精灵列表（支持名称关键词/属性筛选），返回全部匹配结果"""
    _ensure_loaded()
    from src.pokemon_db import _get_conn
    conn = _get_conn()
    c = conn.cursor()
    if q:
        c.execute(
            "SELECT id, name, element, ability, base_hp, base_atk, base_spatk, "
            "base_def, base_spdef, base_speed, base_total, evo_stage, spirit_no "
            "FROM pokemon WHERE name LIKE ? OR element LIKE ? "
            "ORDER BY name",
            (f"%{q}%", f"%{q}%"),
        )
    else:
        c.execute(
            "SELECT id, name, element, ability, base_hp, base_atk, base_spatk, "
            "base_def, base_spdef, base_speed, base_total, evo_stage, spirit_no "
            "FROM pokemon ORDER BY name"
        )
    rows = c.fetchall()
    result = []
    for r in rows:
        ability_name, ability_effect = _split_ability_text(r["ability"])
        meta = _get_spirit_icon_meta(r["name"])
        number = _normalize_spirit_no(r["spirit_no"] or meta.get("number", ""))
        is_leader = _is_leader_form(r["name"], r["evo_stage"])
        result.append({
            "id":      r["id"],
            "name":    r["name"],
            "number":  number,
            "element": r["element"],
            "element_icons": _element_icon_payload(r["element"]),
            "icon_url": _get_icon_url(r["name"]) or meta.get("icon_url", ""),
            "ability": ability_name,
            "ability_effect": ability_effect,
            "ability_icon_url": _get_ability_icon_url(ability_name),
            "evo_stage": r["evo_stage"] or meta.get("stage", ""),
            "form_type": meta.get("form_type", ""),
            "form": meta.get("form", ""),
            "is_leader": is_leader,
            "base_total": r["base_total"],
            "base_hp":    r["base_hp"],
            "base_atk":   r["base_atk"],
            "base_spatk": r["base_spatk"],
            "base_def":   r["base_def"],
            "base_spdef": r["base_spdef"],
            "base_speed": r["base_speed"],
        })
    return JSONResponse(result)


@app.get("/api/pokemon/detail")
async def api_pokemon_detail(name: str):
    """精灵图鉴详情：基础数据 + 本地形态立绘列表。"""
    _ensure_loaded()
    from src.pokemon_db import _get_conn
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT id, name, element, ability, base_hp, base_atk, base_spatk, "
        "base_def, base_spdef, base_speed, base_total, evo_stage, spirit_no "
        "FROM pokemon WHERE name = ?",
        (name,),
    )
    r = c.fetchone()
    if not r:
        return JSONResponse({"error": "pokemon_not_found"}, status_code=404)

    ability_name, ability_effect = _split_ability_text(r["ability"])
    meta = _get_spirit_icon_meta(r["name"])
    number = _normalize_spirit_no(r["spirit_no"] or meta.get("number", ""))
    variants = _get_spirit_variants(number)
    is_leader = _is_leader_form(r["name"], r["evo_stage"])
    return JSONResponse({
        "id": r["id"],
        "name": r["name"],
        "number": number,
        "element": r["element"],
        "element_icons": _element_icon_payload(r["element"]),
        "ability": ability_name,
        "ability_effect": ability_effect,
        "ability_icon_url": _get_ability_icon_url(ability_name),
        "ability_full": r["ability"] or "",
        "evo_stage": r["evo_stage"] or meta.get("stage", ""),
        "form_type": meta.get("form_type", ""),
        "form": meta.get("form", ""),
        "is_leader": is_leader,
        "icon_url": _get_icon_url(r["name"]) or meta.get("icon_url", ""),
        "base_total": r["base_total"],
        "base_hp": r["base_hp"],
        "base_atk": r["base_atk"],
        "base_spatk": r["base_spatk"],
        "base_def": r["base_def"],
        "base_spdef": r["base_spdef"],
        "base_speed": r["base_speed"],
        "variants": variants,
    })


@app.get("/api/pokemon/skills")
async def api_pokemon_skills(name: str):
    """获取指定精灵可学技能列表（优先精确匹配，其次前缀匹配）"""
    _ensure_loaded()
    from src.pokemon_db import _get_conn
    conn = _get_conn()
    c = conn.cursor()

    # 精确匹配 → 前缀匹配（取进化阶段最高的）
    c.execute("SELECT id, name, evo_stage FROM pokemon WHERE name = ?", (name,))
    row = c.fetchone()
    if not row:
        c.execute(
            "SELECT id, name, evo_stage FROM pokemon WHERE name LIKE ? ORDER BY evo_stage DESC LIMIT 1",
            (f"{name}%",),
        )
        row = c.fetchone()
    if not row:
        return JSONResponse([])

    pokemon_id = row["id"]
    exclude_bloodline = _is_leader_form(row["name"], row["evo_stage"])
    learn_filter = "AND COALESCE(ps.learn_group, '') NOT LIKE '%血脉%'" if exclude_bloodline else ""
    c.execute(
        "SELECT DISTINCT s.name, s.element, s.category, s.energy_cost, s.power, s.description, "
        "s.icon_url, s.attribute_icon_url, s.category_icon_url, s.skill_group, s.wiki_url, "
        "COALESCE(ps.learn_group, '') AS learn_group, "
        "COALESCE(ps.learn_level, '') AS learn_level "
        "FROM skill s "
        "JOIN pokemon_skill ps ON ps.skill_id = s.id "
        f"WHERE ps.pokemon_id = ? {learn_filter} "
        "ORDER BY CASE "
        "WHEN ps.learn_group LIKE '%血脉%' THEN 3 "
        "WHEN ps.learn_group LIKE '%技能石%' OR ps.learn_group LIKE '%可学%' THEN 2 "
        "ELSE 1 END, ps.learn_level, s.energy_cost, s.name",
        (pokemon_id,),
    )
    rows = c.fetchall()
    from src.skill_db import get_skill
    result = []
    for r in rows:
        skill = get_skill(r["name"])
        effect_view = _skill_effect_display(skill)
        local_icon = _get_skill_icon_url(r["name"])
        result.append({
            "name":        r["name"],
            "element":     r["element"],
            "category":    r["category"],
            "energy_cost": r["energy_cost"],
            "power":       r["power"],
            "description": r["description"] or "",
            "icon_url":    local_icon or r["icon_url"] or "",
            "attribute_icon_url": _get_skill_meta_icon_url("elements", r["element"]) or r["attribute_icon_url"] or "",
            "category_icon_url": _get_skill_meta_icon_url("categories", r["category"]) or r["category_icon_url"] or "",
            "energy_icon_url": _get_skill_meta_icon_url("misc", "energy"),
            "skill_group": r["skill_group"] or "",
            "learn_group": r["learn_group"] or "",
            "learn_level": r["learn_level"] or "",
            "wiki_url": r["wiki_url"] or "",
            "tags":        effect_view["tags"],
            "effect_details": effect_view["details"],
            "effect_summary": effect_view["summary"],
            "has_effects": effect_view["has_effects"],
        })
    return JSONResponse(result)


@app.get("/api/skills/list")
async def api_skills_list(q: str = "", element: str = "", category: str = ""):
    """技能图鉴列表：支持名称/描述搜索，以及属性、分类筛选。"""
    _ensure_loaded()
    from src.skill_db import _get_conn, get_skill
    conn = _get_conn()
    c = conn.cursor()
    where = []
    params = []
    if q:
        where.append("(s.name LIKE ? OR s.description LIKE ? OR s.element LIKE ? OR s.category LIKE ?)")
        kw = f"%{q}%"
        params.extend([kw, kw, kw, kw])
    if element:
        where.append("s.element = ?")
        params.append(element)
    if category:
        where.append("s.category = ?")
        params.append(category)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    c.execute(f"""
        SELECT s.id, s.name, s.element, s.category, s.energy_cost, s.power, s.description,
               s.icon_url, s.attribute_icon_url, s.category_icon_url, s.skill_group, s.wiki_url, s.source,
               COUNT(DISTINCT ps.pokemon_id) AS learners_count
        FROM skill s
        JOIN pokemon_skill ps ON ps.skill_id = s.id
        {where_sql}
        GROUP BY s.id
        ORDER BY s.element, s.energy_cost, s.name
    """, params)
    result = []
    for r in c.fetchall():
        skill = get_skill(r["name"])
        effect_view = _skill_effect_display(skill)
        local_icon = _get_skill_icon_url(r["name"])
        result.append({
            "id": r["id"],
            "name": r["name"],
            "element": r["element"],
            "category": r["category"],
            "energy_cost": r["energy_cost"],
            "power": r["power"],
            "description": r["description"] or "",
            "icon_url": local_icon or r["icon_url"] or "",
            "attribute_icon_url": _get_skill_meta_icon_url("elements", r["element"]) or r["attribute_icon_url"] or "",
            "category_icon_url": _get_skill_meta_icon_url("categories", r["category"]) or r["category_icon_url"] or "",
            "energy_icon_url": _get_skill_meta_icon_url("misc", "energy"),
            "skill_group": r["skill_group"] or "",
            "wiki_url": r["wiki_url"] or "",
            "source": r["source"] or "",
            "learners_count": r["learners_count"] or 0,
            "effect_tags": effect_view["tags"],
            "effect_details": effect_view["details"],
            "effect_summary": effect_view["summary"],
            "has_effects": effect_view["has_effects"],
        })
    return JSONResponse(result)


@app.get("/api/skills/detail")
async def api_skill_detail(name: str):
    """技能详情：基础信息 + 可学习精灵，按技能组/学习来源分组。"""
    _ensure_loaded()
    from src.skill_db import _get_conn, get_skill
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, element, category, energy_cost, power, description,
               icon_url, attribute_icon_url, category_icon_url, skill_group, wiki_url, source
        FROM skill WHERE name = ?
    """, (name,))
    r = c.fetchone()
    if not r:
        return JSONResponse({"error": "skill_not_found"}, status_code=404)

    skill = get_skill(r["name"])
    effect_view = _skill_effect_display(skill)
    local_icon = _get_skill_icon_url(r["name"])
    c.execute("""
        SELECT p.name, p.element, p.base_total, p.spirit_no, p.evo_stage,
               COALESCE(ps.learn_group, '') AS learn_group,
               COALESCE(ps.learn_level, '') AS learn_level
        FROM pokemon p
        JOIN pokemon_skill ps ON ps.pokemon_id = p.id
        JOIN skill s ON s.id = ps.skill_id
        WHERE s.name = ?
        ORDER BY CASE
            WHEN ps.learn_group LIKE '%血脉%' THEN 3
            WHEN ps.learn_group LIKE '%技能石%' OR ps.learn_group LIKE '%可学%' THEN 2
            ELSE 1
        END, ps.learn_level, p.name
    """, (name,))
    learners = []
    for row in c.fetchall():
        is_leader = _is_leader_form(row["name"], row["evo_stage"])
        if is_leader and "血脉" in (row["learn_group"] or ""):
            continue
        meta = _get_spirit_icon_meta(row["name"])
        number = _normalize_spirit_no(row["spirit_no"] or meta.get("number", ""))
        learners.append({
            "name": row["name"],
            "number": number,
            "element": row["element"],
            "base_total": row["base_total"],
            "is_leader": is_leader,
            "learn_group": row["learn_group"] or "可学习",
            "learn_level": row["learn_level"] or "",
            "icon_url": _get_icon_url(row["name"]) or meta.get("icon_url", ""),
        })
    return JSONResponse({
        "id": r["id"],
        "name": r["name"],
        "element": r["element"],
        "category": r["category"],
        "energy_cost": r["energy_cost"],
        "power": r["power"],
        "description": r["description"] or "",
        "icon_url": local_icon or r["icon_url"] or "",
        "attribute_icon_url": _get_skill_meta_icon_url("elements", r["element"]) or r["attribute_icon_url"] or "",
        "category_icon_url": _get_skill_meta_icon_url("categories", r["category"]) or r["category_icon_url"] or "",
        "energy_icon_url": _get_skill_meta_icon_url("misc", "energy"),
        "skill_group": r["skill_group"] or "",
        "wiki_url": r["wiki_url"] or "",
        "source": r["source"] or "",
        "learners": learners,
        "effect_tags": effect_view["tags"],
        "effect_details": effect_view["details"],
        "effect_summary": effect_view["summary"],
        "has_effects": effect_view["has_effects"],
    })


@app.get("/api/mechanics/list")
async def api_mechanics_list():
    """机制百科：本地词条 + 自动关联技能/特性精灵。"""
    _ensure_loaded()
    from src.skill_db import _get_conn
    conn = _get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT id, name, element, category, energy_cost, power, description,
               icon_url, attribute_icon_url, category_icon_url
        FROM skill
        ORDER BY element, energy_cost, name
    """)
    skills = c.fetchall()
    skill_names = {r["name"] for r in skills}

    c.execute("""
        SELECT name, element, ability, base_total, spirit_no, evo_stage
        FROM pokemon
        WHERE COALESCE(ability, '') <> '' AND ability <> ':'
        ORDER BY name
    """)
    pokemon_rows = c.fetchall()

    entries = []
    for entry in _mechanics_entries():
        related_skills = []
        for r in skills:
            description = r["description"] or ""
            if _mechanic_skill_matches(entry, description):
                related_skills.append({
                    "name": r["name"],
                    "element": r["element"],
                    "category": r["category"],
                    "energy_cost": r["energy_cost"],
                    "power": r["power"],
                    "description": r["description"] or "",
                    "icon_url": _get_skill_icon_url(r["name"]) or r["icon_url"] or "",
                    "attribute_icon_url": _get_skill_meta_icon_url("elements", r["element"]) or r["attribute_icon_url"] or "",
                    "category_icon_url": _get_skill_meta_icon_url("categories", r["category"]) or r["category_icon_url"] or "",
                    "energy_icon_url": _get_skill_meta_icon_url("misc", "energy"),
                })

        abilities_by_key: dict[tuple[str, str], dict] = {}
        for row in pokemon_rows:
            ability_name, ability_effect = _split_ability_text(row["ability"])
            if not ability_name and not ability_effect:
                continue
            hay = " ".join([ability_name, ability_effect])
            if not _mechanic_ability_matches(entry, hay):
                continue
            key = (ability_name, ability_effect)
            item = abilities_by_key.setdefault(key, {
                "name": ability_name or "未命名特性",
                "effect": ability_effect,
                "icon_url": _get_ability_icon_url(ability_name),
                "pokemon": [],
            })
            meta = _get_spirit_icon_meta(row["name"])
            number = _normalize_spirit_no(row["spirit_no"] or meta.get("number", ""))
            item["pokemon"].append({
                "name": row["name"],
                "number": number,
                "element": row["element"],
                "element_icons": _element_icon_payload(row["element"]),
                "base_total": row["base_total"],
                "icon_url": _get_icon_url(row["name"]) or meta.get("icon_url", ""),
                "is_leader": _is_leader_form(row["name"], row["evo_stage"]),
            })

        related_abilities = sorted(
            abilities_by_key.values(),
            key=lambda item: (item["name"], item["pokemon"][0]["name"] if item["pokemon"] else ""),
        )

        payload = dict(entry)
        payload["icon_url"] = _mechanic_icon_url(entry)
        payload["related_skills"] = related_skills
        payload["related_abilities"] = related_abilities
        entries.append(payload)

    return JSONResponse({
        "entries": entries,
        "skill_names": sorted(skill_names),
        "mechanic_titles": [e.get("title", "") for e in entries],
    })


@app.get("/api/egg-groups")
async def api_egg_groups():
    """本地蛋组分类。"""
    data = _egg_groups_data()
    return JSONResponse({
        "ok": True,
        "groups": data.get("groups", []),
        "updated_at": data.get("updated_at", ""),
        "source": data.get("source", ""),
    })


@app.get("/api/egg-group-members")
async def api_egg_group_members(group_id: int = 0, q: str = "", page: int = 1, page_size: int = 30):
    """本地蛋组母族查询，group_id=0 表示全部蛋组。"""
    data = _egg_groups_data()
    group_map = _egg_group_map(data)
    cards = list(data.get("cards", []))

    if group_id:
        cards = [card for card in cards if int(card.get("group_id") or 0) == group_id]

    tokens = [token.casefold() for token in re.split(r"\s+", q.strip()) if token.strip()]
    if tokens:
        cards = [
            card for card in cards
            if all(token in _egg_card_search_text(card) for token in tokens)
        ]

    cards.sort(key=lambda card: (
        int(card.get("group_id") or 0),
        str(card.get("mother_family") or ""),
        str(card.get("family_chain") or ""),
    ))

    page_size = max(1, min(int(page_size or 30), 60))
    total_count = len(cards)
    total_pages = max(1, (total_count + page_size - 1) // page_size)
    page = max(1, min(int(page or 1), total_pages))
    start = (page - 1) * page_size
    page_cards = cards[start:start + page_size]

    return JSONResponse({
        "ok": True,
        "group": group_map.get(group_id) if group_id else None,
        "groups": data.get("groups", []),
        "cards": page_cards,
        "query": q,
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
    })


@app.get("/api/hatch-query")
async def api_hatch_query(diameter: float, weight: float):
    """根据蛋的直径和体重，用区间数据反查候选精灵。"""
    data = _egg_measurements_data()
    rows = []

    for group in data.get("groups", []):
        pet_id = str(group.get("petId") or "").strip()
        pet_name = str(group.get("pet") or "").strip()
        matched_ranges = []
        best_area = 9999.0
        best_distance = 9999.0

        for item in group.get("rangeItems") or []:
            payload = _range_item_payload(item)
            if not _measurement_matches(diameter, payload["diameter_min"], payload["diameter_max"]):
                continue
            if not _measurement_matches(weight, payload["weight_min"], payload["weight_max"]):
                continue
            matched_ranges.append(payload)
            area, distance = _range_score(diameter, weight, payload)
            best_area = min(best_area, area)
            best_distance = min(best_distance, distance)

        if not matched_ranges:
            continue

        pet_meta = _resolve_hatch_pet_meta(pet_id, pet_name)
        rows.append({
            "pet_id": pet_id,
            "name": pet_name,
            "dex_name": pet_meta["dex_name"],
            "number": pet_meta["number"],
            "element": pet_meta["element"],
            "icon_url": pet_meta["icon_url"],
            "match_count": len(matched_ranges),
            "matched_ranges": matched_ranges,
            "score_area": best_area,
            "score_distance": best_distance,
        })

    rows.sort(key=lambda row: (row["score_area"], row["score_distance"], row["number"], row["name"]))

    return JSONResponse({
        "ok": True,
        "diameter": diameter,
        "weight": weight,
        "total_count": len(rows),
        "rows": rows,
        "source": data.get("source", ""),
    })


@app.get("/api/hatch-query/meta")
async def api_hatch_query_meta():
    data = _egg_measurements_data()
    return JSONResponse({
        "ok": True,
        "total_pets": data.get("totalPets", 0),
        "total_measurements": data.get("total", 0),
        "source": data.get("source", ""),
    })


@app.get("/api/type-chart")
async def api_type_chart():
    types = _type_items()
    matrix = [
        {
            "defense": defense["id"],
            "values": {
                attack["id"]: _type_single_effectiveness(attack["id"], defense["id"])
                for attack in types
            },
        }
        for defense in types
    ]
    return JSONResponse({
        "ok": True,
        "types": types,
        "matrix": matrix,
    })


@app.get("/api/type-effectiveness")
async def api_type_effectiveness(attack: str = "", defense1: str = "", defense2: str = ""):
    types = _type_items()
    valid_ids = {item["id"] for item in types}
    attack = attack if attack in valid_ids else ""
    defenses = list(dict.fromkeys(value for value in [defense1, defense2] if value in valid_ids))

    attack_summary = None
    defense_summary = None
    result = None

    if attack:
        strong = []
        resist = []
        for defense in types:
            value = _type_single_effectiveness(attack, defense["id"])
            row = {"type": defense, "multiplier": value}
            if value > 1:
                strong.append(row)
            elif value < 1:
                resist.append(row)
        attack_summary = {"strong": strong, "resist": resist}

    if defenses:
        weak_to = []
        resist_from = []
        neutral_from = []
        for attack_type in types:
            value = _type_combined_effectiveness(attack_type["id"], defenses)
            row = {"type": attack_type, "multiplier": value}
            if value > 1:
                weak_to.append(row)
            elif value < 1:
                resist_from.append(row)
            else:
                neutral_from.append(row)
        weak_to.sort(key=lambda item: (-item["multiplier"], item["type"]["name"]))
        resist_from.sort(key=lambda item: (item["multiplier"], item["type"]["name"]))
        defense_summary = {
            "defenses": [item for item in types if item["id"] in defenses],
            "weak_to": weak_to,
            "resist_from": resist_from,
            "neutral_from": neutral_from,
        }

    if attack and defenses:
        result = {
            "attack": next(item for item in types if item["id"] == attack),
            "defenses": [item for item in types if item["id"] in defenses],
            "multiplier": _type_combined_effectiveness(attack, defenses),
        }

    return JSONResponse({
        "ok": True,
        "attack": attack,
        "defenses": defenses,
        "attack_summary": attack_summary,
        "defense_summary": defense_summary,
        "result": result,
    })


@app.get("/api/pokemon/calc-stats")
async def api_calc_combat_stats(
    base_hp: int, base_atk: int, base_spatk: int,
    base_def: int, base_spdef: int, base_speed: int,
    iv_hp: int = 0, iv_atk: int = 0, iv_spatk: int = 0,
    iv_def: int = 0, iv_spdef: int = 0, iv_speed: int = 0,
    nature: str = "坦率",
):
    """计算精灵战斗五维（根据种族值、个体值、性格）"""
    _ensure_loaded()
    from src.pokemon_db import calc_combat_stats

    stats = calc_combat_stats(
        base_hp=base_hp, base_atk=base_atk, base_spatk=base_spatk,
        base_def=base_def, base_spdef=base_spdef, base_speed=base_speed,
        iv_config={
            "hp": iv_hp, "atk": iv_atk, "spatk": iv_spatk,
            "def": iv_def, "spdef": iv_spdef, "speed": iv_speed,
        },
        nature_name=nature,
    )
    return JSONResponse({
        "hp": round(stats["hp"], 1),
        "atk": round(stats["atk"], 1),
        "spatk": round(stats["spatk"], 1),
        "def": round(stats["def"], 1),
        "spdef": round(stats["spdef"], 1),
        "speed": round(stats["speed"], 1),
    })


@app.get("/api/nature/list")
async def api_nature_list():
    """获取所有性格列表及加成"""
    from src.pokemon_nature_table import NATURE_BONUSES, ALL_NATURES, is_neutral_nature

    result = []
    for name in ALL_NATURES:
        bonus = NATURE_BONUSES[name]
        result.append({
            "name": name,
            "is_neutral": is_neutral_nature(name),
            "bonuses": bonus,
        })

    return JSONResponse(result)


@app.get("/api/lineups/pvp")
async def api_pvp_lineups(q: str = "", magic: str = "", limit: int = 0):
    """本地 PVP 阵容库，包含阵容配置和前端展示所需的本地图标。"""
    _ensure_loaded()
    data = _pvp_lineups_data()
    raw_lineups = list(data.get("lineups", []))
    lineups = [
        item for item in (_displayable_lineup(row) for row in raw_lineups)
        if item is not None
    ]
    displayable_count = len(lineups)

    if magic:
        lineups = [item for item in lineups if item.get("magic") == magic]

    tokens = [token.casefold() for token in re.split(r"\s+", q.strip()) if token.strip()]
    if tokens:
        def searchable(item: dict) -> str:
            parts = [
                item.get("name", ""),
                item.get("magic", ""),
                item.get("magic_label", ""),
                item.get("description", ""),
                item.get("author", ""),
            ]
            for member in item.get("members", []):
                parts.extend([
                    member.get("name", ""),
                    member.get("bloodline", ""),
                    member.get("nature", ""),
                    " ".join(member.get("iv_names", []) or []),
                    " ".join(member.get("skills", []) or []),
                ])
            return " ".join(str(part or "") for part in parts).casefold()

        lineups = [
            item for item in lineups
            if all(token in searchable(item) for token in tokens)
        ]

    if limit and limit > 0:
        lineups = lineups[:min(limit, 300)]

    magic_icons = []
    for icon in data.get("magic_icons", []):
        payload = dict(icon)
        if payload.get("name") not in _ALLOWED_LINEUP_MAGIC:
            continue
        payload["label"] = _lineup_magic_label(payload.get("name", ""))
        if not payload.get("local_url"):
            payload["local_url"] = _lineup_icon_url(payload.get("filename", ""))
        magic_icons.append(payload)

    return JSONResponse({
        "ok": True,
        "source": data.get("source", ""),
        "updated_at": data.get("updated_at", ""),
        "total_count": len(lineups),
        "all_count": displayable_count,
        "raw_count": len(raw_lineups),
        "magic_icons": magic_icons,
        "lineups": lineups,
    })


# ═══════════════════════════════════════
# 静态文件 & 路由
# ═══════════════════════════════════════

@app.get("/")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "dex.html"))

@app.get("/battle")
async def battle_page():
    return FileResponse(os.path.join(STATIC_DIR, "battle.html"))

@app.get("/dex")
async def dex_page():
    return FileResponse(os.path.join(STATIC_DIR, "dex.html"))

@app.get("/skills")
async def skills_page():
    return FileResponse(os.path.join(STATIC_DIR, "skills.html"))

@app.get("/mechanics")
async def mechanics_page():
    return FileResponse(os.path.join(STATIC_DIR, "mechanics.html"))

@app.get("/tools")
async def tools_page():
    return FileResponse(os.path.join(STATIC_DIR, "tools.html"))

@app.get("/storage")
async def storage_page():
    return FileResponse(os.path.join(STATIC_DIR, "storage.html"))

@app.get("/simulator")
async def simulator_page():
    return FileResponse(os.path.join(STATIC_DIR, "simulator.html"))

# Serve theme.css directly at /theme.css
@app.get("/theme.css")
async def theme_css():
    return FileResponse(os.path.join(STATIC_DIR, "theme.css"), media_type="text/css")

# Serve web/assets/ (fonts, images) at /assets/
ASSETS_DIR = os.path.join(STATIC_DIR, "assets")
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "spirit_icons")
if os.path.exists(ICONS_DIR):
    app.mount("/icons", StaticFiles(directory=ICONS_DIR), name="icons")

SKILL_ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "skill_icons")
if os.path.exists(SKILL_ICONS_DIR):
    app.mount("/skill-icons", StaticFiles(directory=SKILL_ICONS_DIR), name="skill-icons")

SKILL_META_ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "skill_meta_icons")
if os.path.exists(SKILL_META_ICONS_DIR):
    app.mount("/skill-meta-icons", StaticFiles(directory=SKILL_META_ICONS_DIR), name="skill-meta-icons")

ABILITY_ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ability_icons")
if os.path.exists(ABILITY_ICONS_DIR):
    app.mount("/ability-icons", StaticFiles(directory=ABILITY_ICONS_DIR), name="ability-icons")

LINEUP_ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "lineup_icons")
if os.path.exists(LINEUP_ICONS_DIR):
    app.mount("/lineup-icons", StaticFiles(directory=LINEUP_ICONS_DIR), name="lineup-icons")

EGG_GROUP_AVATARS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "egg_group_avatars")
if os.path.exists(EGG_GROUP_AVATARS_DIR):
    app.mount("/egg-group-avatars", StaticFiles(directory=EGG_GROUP_AVATARS_DIR), name="egg-group-avatars")

MECHANIC_ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "mechanic_icons")
if os.path.exists(MECHANIC_ICONS_DIR):
    app.mount("/mechanic-icons", StaticFiles(directory=MECHANIC_ICONS_DIR), name="mechanic-icons")

if __name__ == "__main__":
    import uvicorn
    print("启动战斗服务器: http://localhost:8765")
    uvicorn.run(app, host="0.0.0.0", port=8765)
