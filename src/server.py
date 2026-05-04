"""
洛克王国战斗模拟系统 - Web 图形界面后端 (FastAPI + WebSocket)
"""

import sys
import os
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
    auto_switch
)

app = FastAPI()

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")

_db_loaded = False
_skill_meta_cache: Optional[dict] = None
_SKILL_ICON_CACHE: dict = {}

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
    if t == E.SLUGGISH_MARK:
        return f"迟缓印记×{params.get('stacks', 1)}"
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
                _ICON_CACHE[name] = f"/icons/{fname}"

def _get_icon_url(name: str) -> str:
    _build_icon_cache()
    return _ICON_CACHE.get(name, "")

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
        "attribute_icon_url": meta["attribute_icon_url"],
        "category_icon_url":  meta["category_icon_url"],
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
        team_a_data.append(d)

    team_b_data = []
    for i, p in enumerate(state.team_b):
        d = serialize_pokemon(p, is_current=(i == state.current_b))
        d["is_current"] = (i == state.current_b)
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
            pokemon_type=type_map.get(data["属性"], Type.NORMAL),
            hp=stats["hp"],
            attack=stats["atk"],
            defense=stats["def"],
            sp_attack=stats["spatk"],
            sp_defense=stats["spdef"],
            speed=stats["speed"],
            ability=ability,
            skills=[get_skill(n) for n in skill_names],
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


def _parse_side_action(state: BattleState, side: str, action_data: dict):
    team = state.team_a if side == "a" else state.team_b
    current_idx = state.current_a if side == "a" else state.current_b
    current = team[current_idx]
    side_name = "我方" if side == "a" else "对方"

    action_type = action_data.get("type")
    if action_type == "charge":
        return (-1,), None
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
    )
    session.state = state
    session.game_over = False
    session.waiting_for_player = True

    session.add_log("═══════════════════════════")
    session.add_log("⚔️  手动模拟对战开始！")
    session.add_log(f"🟦 我方: {', '.join(p.name for p in team_a)}")
    session.add_log(f"🟥 对方: {', '.join(p.name for p in team_b)}")
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
            "base_def, base_spdef, base_speed, base_total "
            "FROM pokemon WHERE name LIKE ? OR element LIKE ? "
            "ORDER BY name",
            (f"%{q}%", f"%{q}%"),
        )
    else:
        c.execute(
            "SELECT id, name, element, ability, base_hp, base_atk, base_spatk, "
            "base_def, base_spdef, base_speed, base_total "
            "FROM pokemon ORDER BY name"
        )
    rows = c.fetchall()
    result = []
    for r in rows:
        # 提取简短特性名（去掉冒号后的描述）
        ability_short = r["ability"].split(":")[0].split("：")[0] if r["ability"] else ""
        result.append({
            "id":      r["id"],
            "name":    r["name"],
            "element": r["element"],
            "icon_url": _get_icon_url(r["name"]),
            "ability": ability_short,
            "base_total": r["base_total"],
            "base_hp":    r["base_hp"],
            "base_atk":   r["base_atk"],
            "base_spatk": r["base_spatk"],
            "base_def":   r["base_def"],
            "base_spdef": r["base_spdef"],
            "base_speed": r["base_speed"],
        })
    return JSONResponse(result)


@app.get("/api/pokemon/skills")
async def api_pokemon_skills(name: str):
    """获取指定精灵可学技能列表（优先精确匹配，其次前缀匹配）"""
    _ensure_loaded()
    from src.pokemon_db import _get_conn
    conn = _get_conn()
    c = conn.cursor()

    # 精确匹配 → 前缀匹配（取进化阶段最高的）
    c.execute("SELECT id FROM pokemon WHERE name = ?", (name,))
    row = c.fetchone()
    if not row:
        c.execute(
            "SELECT id FROM pokemon WHERE name LIKE ? ORDER BY evo_stage DESC LIMIT 1",
            (f"{name}%",),
        )
        row = c.fetchone()
    if not row:
        return JSONResponse([])

    pokemon_id = row["id"]
    c.execute(
        "SELECT DISTINCT s.name, s.element, s.category, s.energy_cost, s.power, s.description, "
        "s.icon_url, s.attribute_icon_url, s.category_icon_url, s.skill_group, s.wiki_url, "
        "COALESCE(ps.learn_group, '') AS learn_group "
        "FROM skill s "
        "JOIN pokemon_skill ps ON ps.skill_id = s.id "
        "WHERE ps.pokemon_id = ? "
        "ORDER BY ps.learn_group, s.energy_cost, s.name",
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
            "attribute_icon_url": r["attribute_icon_url"] or "",
            "category_icon_url": r["category_icon_url"] or "",
            "skill_group": r["skill_group"] or "",
            "learn_group": r["learn_group"] or "",
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
        LEFT JOIN pokemon_skill ps ON ps.skill_id = s.id
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
            "attribute_icon_url": r["attribute_icon_url"] or "",
            "category_icon_url": r["category_icon_url"] or "",
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
        SELECT p.name, p.element, p.base_total, COALESCE(ps.learn_group, '') AS learn_group
        FROM pokemon p
        JOIN pokemon_skill ps ON ps.pokemon_id = p.id
        JOIN skill s ON s.id = ps.skill_id
        WHERE s.name = ?
        ORDER BY ps.learn_group, p.name
    """, (name,))
    learners = [
        {
            "name": row["name"],
            "element": row["element"],
            "base_total": row["base_total"],
            "learn_group": row["learn_group"] or "可学习",
            "icon_url": _get_icon_url(row["name"]),
        }
        for row in c.fetchall()
    ]
    return JSONResponse({
        "id": r["id"],
        "name": r["name"],
        "element": r["element"],
        "category": r["category"],
        "energy_cost": r["energy_cost"],
        "power": r["power"],
        "description": r["description"] or "",
        "icon_url": local_icon or r["icon_url"] or "",
        "attribute_icon_url": r["attribute_icon_url"] or "",
        "category_icon_url": r["category_icon_url"] or "",
        "skill_group": r["skill_group"] or "",
        "wiki_url": r["wiki_url"] or "",
        "source": r["source"] or "",
        "learners": learners,
        "effect_tags": effect_view["tags"],
        "effect_details": effect_view["details"],
        "effect_summary": effect_view["summary"],
        "has_effects": effect_view["has_effects"],
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

if __name__ == "__main__":
    import uvicorn
    print("启动战斗服务器: http://localhost:8765")
    uvicorn.run(app, host="0.0.0.0", port=8765)
