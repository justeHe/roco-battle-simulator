"""
洛克王国性格加成表

性格是战斗元素，对宠物的两项能力值产生修正效果。
修正作用于由种族值、个体值等要素计算出的最终面板。
"""

from typing import TypedDict


class NatureBonus(TypedDict):
    """性格加成数据结构。"""
    hp: float
    atk: float
    defense: float
    sp_atk: float
    sp_defense: float
    speed: float


def _bonus(
    *,
    hp: float = 0.0,
    atk: float = 0.0,
    defense: float = 0.0,
    sp_atk: float = 0.0,
    sp_defense: float = 0.0,
    speed: float = 0.0,
) -> NatureBonus:
    return {
        "hp": hp,
        "atk": atk,
        "defense": defense,
        "sp_atk": sp_atk,
        "sp_defense": sp_defense,
        "speed": speed,
    }


# 性格加成表
# 格式：性格名 -> {hp, atk, defense, sp_atk, sp_defense, speed}
# 正值表示 +20% 增益，负值表示 -10% 减益，0.0 表示无修正
NATURE_BONUSES: dict[str, NatureBonus] = {
    # ==================== 物攻型（+物攻）====================
    "大胆": _bonus(atk=0.2, defense=-0.1),
    "固执": _bonus(atk=0.2, sp_atk=-0.1),
    "调皮": _bonus(atk=0.2, sp_defense=-0.1),
    "勇敢": _bonus(atk=0.2, speed=-0.1),
    "逞强": _bonus(atk=0.2, hp=-0.1),

    # ==================== 物防型（+物防）====================
    "稳重": _bonus(defense=0.2, atk=-0.1),
    "天真": _bonus(defense=0.2, sp_atk=-0.1),
    "懒散": _bonus(defense=0.2, sp_defense=-0.1),
    "悠闲": _bonus(defense=0.2, speed=-0.1),
    "坦率": _bonus(defense=0.2, hp=-0.1),

    # ==================== 魔攻型（+魔攻）====================
    "聪明": _bonus(sp_atk=0.2, atk=-0.1),
    "专注": _bonus(sp_atk=0.2, defense=-0.1),
    "偏执": _bonus(sp_atk=0.2, sp_defense=-0.1),
    "冷静": _bonus(sp_atk=0.2, speed=-0.1),
    "理性": _bonus(sp_atk=0.2, hp=-0.1),

    # ==================== 魔防型（+魔防）====================
    "警惕": _bonus(sp_defense=0.2, atk=-0.1),
    "温顺": _bonus(sp_defense=0.2, defense=-0.1),
    "害羞": _bonus(sp_defense=0.2, sp_atk=-0.1),
    "慎重": _bonus(sp_defense=0.2, speed=-0.1),
    "焦虑": _bonus(sp_defense=0.2, hp=-0.1),

    # ==================== 速度型（+速度）====================
    "胆小": _bonus(speed=0.2, atk=-0.1),
    "急躁": _bonus(speed=0.2, defense=-0.1),
    "开朗": _bonus(speed=0.2, sp_atk=-0.1),
    "莽撞": _bonus(speed=0.2, sp_defense=-0.1),
    "热情": _bonus(speed=0.2, hp=-0.1),

    # ==================== 生命型（+生命）====================
    "忧郁": _bonus(hp=0.2, defense=-0.1),
    "粗心": _bonus(hp=0.2, sp_defense=-0.1),
    "沉默": _bonus(hp=0.2, atk=-0.1),
    "平和": _bonus(hp=0.2, sp_atk=-0.1),
    "踏实": _bonus(hp=0.2, speed=-0.1),
}

NATURE_NAME_ALIASES = {
    "实干": "逞强",
    "孤僻": "稳重",
    "淘气": "天真",
    "无虑": "懒散",
    "保守": "聪明",
    "马虎": "偏执",
    "沉着": "警惕",
    "狂妄": "慎重",
    "浮躁": "焦虑",
    "认真": "热情",
    "紧张": "急躁",
}

# 所有性格名称列表（按主加成分类）
NATURES_BY_CATEGORY = {
    "attack": ["大胆", "固执", "调皮", "勇敢", "逞强"],
    "defense": ["稳重", "天真", "懒散", "悠闲", "坦率"],
    "sp_attack": ["聪明", "专注", "偏执", "冷静", "理性"],
    "sp_defense": ["警惕", "温顺", "害羞", "慎重", "焦虑"],
    "speed": ["胆小", "急躁", "开朗", "莽撞", "热情"],
    "hp": ["忧郁", "粗心", "沉默", "平和", "踏实"],
}

# 所有性格名称（平铺列表）
ALL_NATURES = [
    "大胆", "固执", "调皮", "勇敢", "逞强",
    "稳重", "天真", "懒散", "悠闲", "坦率",
    "聪明", "专注", "偏执", "冷静", "理性",
    "警惕", "温顺", "害羞", "慎重", "焦虑",
    "胆小", "急躁", "开朗", "莽撞", "热情",
    "忧郁", "粗心", "沉默", "平和", "踏实",
]


def normalize_nature_name(nature: str) -> str:
    """把旧/错误性格名映射到当前正确性格表。"""
    return NATURE_NAME_ALIASES.get(nature, nature)


def get_nature_bonus(nature: str) -> NatureBonus:
    """
    根据性格名称获取对应的加成效果。

    Args:
        nature: 性格名称，如 "固执"、"坦率"、"忧郁" 等。

    Returns:
        NatureBonus 字典，包含 hp, atk, defense, sp_atk, sp_defense, speed 的修正值。

    Raises:
        KeyError: 如果性格名称不存在。
    """
    normalized = normalize_nature_name(nature)
    if normalized not in NATURE_BONUSES:
        raise KeyError(f"未知的性格：{nature}")
    return NATURE_BONUSES[normalized]


def is_neutral_nature(nature: str) -> bool:
    """
    判断是否为无修正性格。

    目前平衡型性格已移除，因此正常配置下都会返回 False。
    """
    return nature in NATURE_BONUSES and all(
        v == 0.0 for v in NATURE_BONUSES[nature].values()
    )
