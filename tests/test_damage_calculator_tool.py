import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.battle import DamageCalculator
from src.damage_calculator import calculate_damage_preview
from src.skill_db import get_skill
from src.team_builder import TeamBuilder


def test_damage_preview_matches_battle_formula_without_extra_mods():
    iv_attack = {"hp": 60, "atk": 60, "spatk": 0, "def": 0, "spdef": 0, "speed": 60}
    iv_defense = {"hp": 60, "atk": 0, "spatk": 0, "def": 60, "spdef": 60, "speed": 0}
    attacker = TeamBuilder._p("音速犬", ["猛烈撞击"], iv_attack, nature="固执")
    defender = TeamBuilder._p("魔力猫", ["猛烈撞击"], iv_defense, nature="坦率")
    expected = DamageCalculator.calculate(attacker, defender, get_skill("猛烈撞击"))

    result = calculate_damage_preview({
        "attacker": {"name": "音速犬", "nature": "固执", "iv": iv_attack},
        "defender": {"name": "魔力猫", "nature": "坦率", "iv": iv_defense},
        "skill": {"name": "猛烈撞击"},
        "attacker_mods": {"power_multiplier": 1},
        "defender_mods": {"hp_percent": 1},
        "field": {"stab_enabled": True},
    })

    assert result["damage"] == expected
    assert result["axis"]["attack"] == "物攻"


def test_damage_preview_dual_type_one_resist_one_weak_is_neutral():
    result = calculate_damage_preview({
        "attacker": {"name": "音速犬", "nature": "固执"},
        "defender": {"name": "魔力猫", "nature": "坦率"},
        "skill": {
            "name": "__manual__",
            "type": "fire",
            "category": "魔攻",
            "power": 80,
            "hit_count": 1,
        },
        "attacker_mods": {"power_multiplier": 1},
        "defender_mods": {"hp_percent": 1},
        "field": {
            "defense_type1": "grass",
            "defense_type2": "water",
            "stab_enabled": True,
        },
    })

    assert result["field"]["effectiveness"] == 1.0
    assert result["damage"] > 0


def test_damage_preview_will_impact_uses_bloodline_and_counter_power():
    result = calculate_damage_preview({
        "attacker": {"name": "音速犬", "nature": "固执"},
        "defender": {"name": "魔力猫", "nature": "坦率"},
        "skill": {
            "name": "猛烈撞击",
            "will_impact": True,
            "bloodline": "火",
            "counter_status": True,
        },
        "attacker_mods": {"power_multiplier": 1},
        "defender_mods": {"hp_percent": 1},
        "field": {"stab_enabled": True},
    })

    assert result["skill"]["name"] == "愿力冲击"
    assert result["skill"]["type"] == "fire"
    assert result["skill"]["power"] == 80
    assert any(item["label"] == "最终威力" and item["value"] == "200" for item in result["breakdown"])


if __name__ == "__main__":
    test_damage_preview_matches_battle_formula_without_extra_mods()
    test_damage_preview_dual_type_one_resist_one_weak_is_neutral()
    test_damage_preview_will_impact_uses_bloodline_and_counter_power()
    print("damage calculator tool tests OK")
