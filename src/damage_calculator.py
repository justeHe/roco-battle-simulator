"""伤害计算器后端逻辑。

这个模块只负责把现有战斗公式做成可展示的预览结果，方便工具页调用。
"""

from __future__ import annotations

from typing import Any, Optional

from src.models import SkillCategory, TYPE_CHART, Type
from src.pokemon_db import calc_combat_stats, get_pokemon
from src.skill_db import get_skill


TYPE_LABELS = {
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

TYPE_NAME_TO_ID = {
    **{label: type_id for type_id, label in TYPE_LABELS.items()},
    **{f"{label}系": type_id for type_id, label in TYPE_LABELS.items()},
    "格斗": "fighting",
    "格斗系": "fighting",
    "飞行": "flying",
    "飞行系": "flying",
    "超能": "psychic",
    "超能系": "psychic",
    "幽灵": "ghost",
    "幽灵系": "ghost",
    "钢": "steel",
    "钢系": "steel",
    "妖精": "fairy",
    "妖精系": "fairy",
    "地面": "ground",
    "地面系": "ground",
}

CATEGORY_NAME_TO_VALUE = {
    "物攻": SkillCategory.PHYSICAL.value,
    "物理": SkillCategory.PHYSICAL.value,
    "魔攻": SkillCategory.MAGICAL.value,
    "魔法": SkillCategory.MAGICAL.value,
    "防御": SkillCategory.DEFENSE.value,
    "状态": SkillCategory.STATUS.value,
    "变化": SkillCategory.STATUS.value,
}

WEATHER_LABELS = {
    "": "无天气",
    "rain": "雨天",
    "sandstorm": "沙暴",
    "snow": "暴风雪",
}

WEATHER_DAMAGE_MULT = {
    "rain": {"water": 1.5},
    "sandstorm": {},
    "snow": {},
}


class DamageCalculatorError(ValueError):
    """伤害计算器输入错误。"""


def _float(value: Any, default: float = 0.0) -> float:
    try:
        num = float(value)
    except (TypeError, ValueError):
        return default
    return num


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _ratio(value: Any, default: float = 0.0, *, minimum: float = 0.0, maximum: float = 4.0) -> float:
    num = _float(value, default)
    if abs(num) > 5:
        num = num / 100.0
    return max(minimum, min(maximum, num))


def _multiplier(value: Any, default: float = 1.0, *, minimum: float = 0.0, maximum: float = 10.0) -> float:
    num = _float(value, default)
    return max(minimum, min(maximum, num))


def _type_id(value: Any, default: str = "normal") -> str:
    text = str(value or "").strip()
    if not text:
        return default
    if text in TYPE_LABELS:
        return text
    if text in TYPE_NAME_TO_ID:
        return TYPE_NAME_TO_ID[text]
    primary = text.replace("，", ",").split(",")[0].strip()
    return TYPE_NAME_TO_ID.get(primary, default)


def _type_enum(type_id: str) -> Type:
    for item in Type:
        if item.value == type_id:
            return item
    return Type.NORMAL


def _category_value(value: Any, default: str = SkillCategory.PHYSICAL.value) -> str:
    text = str(value or "").strip()
    if not text:
        return default
    if text in {item.value for item in SkillCategory}:
        return text
    return CATEGORY_NAME_TO_VALUE.get(text, default)


def _iv_config(payload: dict[str, Any] | None) -> dict[str, int]:
    payload = payload or {}
    return {
        "hp": max(0, min(60, _int(payload.get("hp"), 0))),
        "atk": max(0, min(60, _int(payload.get("atk"), 0))),
        "spatk": max(0, min(60, _int(payload.get("spatk"), 0))),
        "def": max(0, min(60, _int(payload.get("def"), 0))),
        "spdef": max(0, min(60, _int(payload.get("spdef"), 0))),
        "speed": max(0, min(60, _int(payload.get("speed"), 0))),
    }


def _load_pokemon_stats(payload: dict[str, Any], role: str) -> dict[str, Any]:
    name = str(payload.get("name") or "").strip()
    if not name:
        raise DamageCalculatorError(f"{role}未选择精灵")

    data = get_pokemon(name)
    if not data:
        raise DamageCalculatorError(f"未找到精灵：{name}")

    iv = _iv_config(payload.get("iv"))
    nature = str(payload.get("nature") or "坦率").strip() or "坦率"
    stats = calc_combat_stats(
        base_hp=data["生命种族值"],
        base_atk=data["物攻种族值"],
        base_spatk=data["魔攻种族值"],
        base_def=data["物防种族值"],
        base_spdef=data["魔防种族值"],
        base_speed=data["速度种族值"],
        iv_config=iv,
        nature_name=nature,
    )
    type_id = _type_id(data["属性"])
    return {
        "name": data["名称"],
        "type": type_id,
        "type_name": TYPE_LABELS.get(type_id, type_id),
        "nature": nature,
        "iv": iv,
        "base": {
            "hp": data["生命种族值"],
            "atk": data["物攻种族值"],
            "spatk": data["魔攻种族值"],
            "def": data["物防种族值"],
            "spdef": data["魔防种族值"],
            "speed": data["速度种族值"],
        },
        "stats": {
            "hp": int(stats["hp"]),
            "atk": int(stats["atk"]),
            "spatk": int(stats["spatk"]),
            "def": int(stats["def"]),
            "spdef": int(stats["spdef"]),
            "speed": int(stats["speed"]),
        },
    }


def _bloodline_type(value: Any) -> Optional[str]:
    text = str(value or "").strip()
    if not text:
        return None
    text = text.replace("血脉", "").replace("系", "").strip()
    if "首领" in text:
        return None
    return _type_id(text, default="")


def _single_effectiveness(attack_type: str, defense_type: str) -> float:
    return TYPE_CHART.get(attack_type, {}).get(defense_type, 1.0)


def _combined_effectiveness(attack_type: str, defense_types: list[str]) -> tuple[float, list[dict[str, Any]]]:
    clean = list(dict.fromkeys(type_id for type_id in defense_types if type_id in TYPE_LABELS))
    if not clean:
        clean = ["normal"]
    parts = [
        {
            "type": type_id,
            "type_name": TYPE_LABELS.get(type_id, type_id),
            "multiplier": _single_effectiveness(attack_type, type_id),
        }
        for type_id in clean
    ]
    values = [item["multiplier"] for item in parts]
    if len(values) == 1:
        return values[0], parts
    if any(value > 1 for value in values) and any(value < 1 for value in values):
        return 1.0, parts
    return round(max(0.5, sum(values) - (len(values) - 1)), 3), parts


def _skill_payload(payload: dict[str, Any], attacker: dict[str, Any]) -> dict[str, Any]:
    skill_input = payload.get("skill") or {}
    will_impact = bool(skill_input.get("will_impact"))
    skill_name = str(skill_input.get("name") or "").strip()

    if skill_name and skill_name != "__manual__":
        base_skill = get_skill(skill_name)
        default_type = base_skill.skill_type.value
        default_category = base_skill.category.value
        default_power = base_skill.power
        default_hit_count = base_skill.hit_count
        default_energy = base_skill.energy_cost
    else:
        base_skill = None
        default_type = attacker["type"]
        default_category = SkillCategory.PHYSICAL.value
        default_power = 80
        default_hit_count = 1
        default_energy = 0

    if will_impact:
        blood_type = _bloodline_type(skill_input.get("bloodline")) or attacker["type"]
        atk_for_axis = attacker["stats"]["atk"] * (
            1 + _ratio(payload.get("attacker_mods", {}).get("atk_up"), 0)
        ) / max(0.1, 1 + _ratio(payload.get("attacker_mods", {}).get("atk_down"), 0, maximum=0.9))
        spatk_for_axis = attacker["stats"]["spatk"] * (
            1 + _ratio(payload.get("attacker_mods", {}).get("spatk_up"), 0)
        ) / max(0.1, 1 + _ratio(payload.get("attacker_mods", {}).get("spatk_down"), 0, maximum=0.9))
        category = SkillCategory.PHYSICAL.value if atk_for_axis >= spatk_for_axis else SkillCategory.MAGICAL.value
        return {
            "name": "愿力冲击",
            "type": blood_type,
            "type_name": TYPE_LABELS.get(blood_type, blood_type),
            "category": category,
            "power": 80,
            "energy_cost": default_energy,
            "hit_count": 1,
            "will_impact": True,
            "counter_status": bool(skill_input.get("counter_status")),
        }

    type_id = _type_id(skill_input.get("type"), default_type)
    category = _category_value(skill_input.get("category"), default_category)
    return {
        "name": skill_name if skill_name and skill_name != "__manual__" else "自定义技能",
        "type": type_id,
        "type_name": TYPE_LABELS.get(type_id, type_id),
        "category": category,
        "power": max(0, _int(skill_input.get("power"), default_power)),
        "energy_cost": max(0, _int(skill_input.get("energy_cost"), default_energy)),
        "hit_count": max(1, min(10, _int(skill_input.get("hit_count"), default_hit_count or 1))),
        "will_impact": False,
        "counter_status": False,
        "from_db": base_skill is not None,
    }


def calculate_damage_preview(payload: dict[str, Any]) -> dict[str, Any]:
    """根据工具页配置计算伤害预览。"""
    attacker = _load_pokemon_stats(payload.get("attacker") or {}, "攻击方")
    defender = _load_pokemon_stats(payload.get("defender") or {}, "防御方")
    skill = _skill_payload(payload, attacker)

    attacker_mods = payload.get("attacker_mods") or {}
    defender_mods = payload.get("defender_mods") or {}
    field = payload.get("field") or {}

    is_magical = skill["category"] == SkillCategory.MAGICAL.value
    if is_magical:
        attack_stat_key = "spatk"
        defense_stat_key = "spdef"
        attack_label = "魔攻"
        defense_label = "魔防"
        atk_up = _ratio(attacker_mods.get("spatk_up"), 0)
        atk_down = _ratio(attacker_mods.get("spatk_down"), 0, maximum=0.9)
        def_up = _ratio(defender_mods.get("spdef_up"), 0)
        def_down = _ratio(defender_mods.get("spdef_down"), 0, maximum=0.9)
    else:
        attack_stat_key = "atk"
        defense_stat_key = "def"
        attack_label = "物攻"
        defense_label = "物防"
        atk_up = _ratio(attacker_mods.get("atk_up"), 0)
        atk_down = _ratio(attacker_mods.get("atk_down"), 0, maximum=0.9)
        def_up = _ratio(defender_mods.get("def_up"), 0)
        def_down = _ratio(defender_mods.get("def_down"), 0, maximum=0.9)

    base_atk = float(attacker["stats"][attack_stat_key])
    base_def = max(1.0, float(defender["stats"][defense_stat_key]))
    ability_level = (1.0 + atk_up + def_down) / max(0.1, 1.0 + atk_down + def_up)
    effective_atk = base_atk * ability_level

    power_bonus = _int(attacker_mods.get("skill_power_bonus"), 0)
    power_pct = _ratio(attacker_mods.get("skill_power_pct_mod"), 0, minimum=-0.95, maximum=4.0)
    final_power = max(0, skill["power"] + power_bonus)
    power_multiplier = 1.0 + power_pct
    if skill["will_impact"] and skill["counter_status"]:
        power_multiplier *= 2.5
    final_power = max(0, int(final_power * power_multiplier))

    if final_power <= 0:
        base_damage = 0.0
    else:
        base_damage = (effective_atk / base_def) * final_power * 0.9

    defense_types = [
        _type_id(field.get("defense_type1"), defender["type"]),
        _type_id(field.get("defense_type2"), ""),
    ]
    effectiveness, effectiveness_parts = _combined_effectiveness(skill["type"], defense_types)
    if bool(field.get("barrel_active")):
        effectiveness = 1.0

    stab_enabled = bool(field.get("stab_enabled", True))
    stab = 1.25 if stab_enabled and skill["type"] == attacker["type"] else 1.0

    weather = str(field.get("weather") or "").strip()
    weather_mult = WEATHER_DAMAGE_MULT.get(weather, {}).get(skill["type"], 1.0)

    hit_count = max(1, _int(skill.get("hit_count"), 1))
    independent_power_mult = _multiplier(attacker_mods.get("power_multiplier"), 1.0)

    raw_damage = base_damage * effectiveness * stab * weather_mult * hit_count * independent_power_mult
    rounded_before_reduction = 0 if final_power <= 0 else max(1, int(raw_damage))
    damage_reduction = _ratio(defender_mods.get("damage_reduction"), 0, minimum=0.0, maximum=1.0)
    final_damage = int(rounded_before_reduction * (1.0 - damage_reduction))
    if rounded_before_reduction > 0 and damage_reduction < 1.0:
        final_damage = max(1, final_damage)

    hp_percent = _ratio(defender_mods.get("hp_percent"), 1.0, minimum=0.01, maximum=1.0)
    current_hp = max(1, int(defender["stats"]["hp"] * hp_percent))
    remaining_hp = max(0, current_hp - final_damage)

    breakdown = [
        {
            "label": f"{attack_label}/{defense_label}",
            "value": f"{base_atk:.0f} / {base_def:.0f}",
            "multiplier": round(base_atk / base_def, 4),
        },
        {
            "label": "能力等级",
            "value": f"(1 + {atk_up:.2f} + {def_down:.2f}) / (1 + {atk_down:.2f} + {def_up:.2f})",
            "multiplier": round(ability_level, 4),
        },
        {"label": "最终威力", "value": str(final_power), "multiplier": final_power},
        {"label": "对应倍率", "value": f"x{effectiveness:g}", "multiplier": effectiveness},
        {"label": "本系加成", "value": f"x{stab:g}", "multiplier": stab},
        {"label": "天气影响", "value": f"{WEATHER_LABELS.get(weather, weather or '无天气')} x{weather_mult:g}", "multiplier": weather_mult},
        {"label": "连击", "value": f"x{hit_count}", "multiplier": hit_count},
        {"label": "威力提升buff", "value": f"x{independent_power_mult:g}", "multiplier": independent_power_mult},
        {"label": "减伤", "value": f"-{damage_reduction * 100:.0f}%", "multiplier": round(1.0 - damage_reduction, 4)},
    ]

    formula = {
        "detail": (
            f"({base_atk:.2f} / {base_def:.2f}) x 0.9 x "
            f"({final_power} x {effectiveness:g}) x {ability_level:.4f} x "
            f"{stab:g} x {weather_mult:g} x {hit_count} x {independent_power_mult:g}"
        ),
        "ability_level": ability_level,
        "raw_damage": raw_damage,
        "rounded_before_reduction": rounded_before_reduction,
    }

    return {
        "ok": True,
        "damage": final_damage,
        "damage_before_reduction": rounded_before_reduction,
        "raw_damage": round(raw_damage, 3),
        "current_hp": current_hp,
        "remaining_hp": remaining_hp,
        "hp_percent": round(final_damage / max(1, defender["stats"]["hp"]), 4),
        "current_hp_percent": round(final_damage / max(1, current_hp), 4),
        "ko": final_damage >= current_hp,
        "attacker": attacker,
        "defender": defender,
        "skill": skill,
        "axis": {"attack": attack_label, "defense": defense_label},
        "field": {
            "weather": weather,
            "weather_name": WEATHER_LABELS.get(weather, weather or "无天气"),
            "stab": stab,
            "effectiveness": effectiveness,
            "effectiveness_parts": effectiveness_parts,
            "barrel_active": bool(field.get("barrel_active")),
        },
        "breakdown": breakdown,
        "formula": formula,
    }
