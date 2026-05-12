import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.battle import DamageCalculator
from src.damage_calculator import calculate_damage_preview
from src.server import app
from src.skill_db import get_skill
from src.team_builder import TeamBuilder

from fastapi.testclient import TestClient


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


def test_damage_preview_dual_type_double_resist_is_triple_resist():
    result = calculate_damage_preview({
        "attacker": {"name": "音速犬", "nature": "固执"},
        "defender": {"name": "魔力猫", "nature": "坦率"},
        "skill": {
            "name": "__manual__",
            "type": "normal",
            "category": "物攻",
            "power": 80,
            "hit_count": 1,
        },
        "attacker_mods": {"power_multiplier": 1},
        "defender_mods": {"hp_percent": 1},
        "field": {
            "defense_type1": "ground",
            "defense_type2": "ghost",
            "stab_enabled": True,
        },
    })

    assert result["field"]["effectiveness"] == 0.333
    assert any(item["label"] == "克制倍率" and item["value"] == "x0.333" for item in result["breakdown"])


def test_type_effectiveness_api_reports_triple_resist():
    client = TestClient(app)
    response = client.get("/api/type-effectiveness", params={
        "attack": "normal",
        "defense1": "ground",
        "defense2": "ghost",
    })
    response.raise_for_status()
    payload = response.json()

    assert payload["result"]["multiplier"] == 0.333
    assert any(
        row["type"]["id"] == "normal" and row["multiplier"] == 0.333
        for row in payload["defense_summary"]["resist_from"]
    )


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
    assert result["field"]["counter_multiplier"] == 2.5
    assert any(item["label"] == "应对倍率" and item["value"] == "x2.5" for item in result["breakdown"])
    assert result["formula"]["panel_power"] < result["formula"]["resolved_power"]
    assert "总伤害" in result["formula"]["steps"][-1]["label"]


if __name__ == "__main__":
    test_damage_preview_matches_battle_formula_without_extra_mods()
    test_damage_preview_dual_type_one_resist_one_weak_is_neutral()
    test_damage_preview_dual_type_double_resist_is_triple_resist()
    test_type_effectiveness_api_reports_triple_resist()
    test_damage_preview_will_impact_uses_bloodline_and_counter_power()
    print("damage calculator tool tests OK")
