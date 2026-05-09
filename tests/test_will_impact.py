from src.battle import (
    ACTION_WILL_IMPACT,
    DamageCalculator,
    _build_will_impact_skill,
    execute_full_turn,
    will_impact_status,
)
from src.models import BattleState, Pokemon, Skill, SkillCategory, Type


def _pokemon(name: str, ptype: Type = Type.NORMAL, bloodline: str = "") -> Pokemon:
    return Pokemon(
        name=name,
        pokemon_type=ptype,
        hp=500,
        attack=220,
        defense=160,
        sp_attack=120,
        sp_defense=160,
        speed=100,
        skills=[
            Skill(
                name="一号位",
                skill_type=ptype,
                category=SkillCategory.PHYSICAL,
                power=40,
                energy_cost=3,
            )
        ],
        bloodline=bloodline,
    )


def _status_skill() -> Skill:
    return Skill(
        name="状态测试",
        skill_type=Type.NORMAL,
        category=SkillCategory.STATUS,
        power=0,
        energy_cost=0,
    )


def test_will_impact_requires_item_and_elemental_bloodline():
    user = _pokemon("愿力手", Type.FIRE, "火")
    enemy = _pokemon("靶子", Type.NORMAL, "普通")
    state = BattleState(team_a=[user], team_b=[enemy], team_item_a="")
    assert will_impact_status(state, "a")["can_use"] is False

    state.team_item_a = "强化术"
    user.bloodline = "首领"
    assert will_impact_status(state, "a")["can_use"] is False

    user.bloodline = "火"
    assert will_impact_status(state, "a")["can_use"] is True


def test_will_impact_uses_bloodline_type_category_and_first_slot_cost():
    user = _pokemon("愿力手", Type.NORMAL, "火")
    enemy = _pokemon("靶子", Type.GRASS, "草")
    state = BattleState(team_a=[user], team_b=[enemy], team_item_a="愿力冲击")

    status = will_impact_status(state, "a")
    skill = _build_will_impact_skill(user)

    assert status["type"] == "fire"
    assert status["category"] == "物攻"
    assert status["energy_cost"] == 3
    assert skill.skill_type == Type.FIRE
    assert skill.category == SkillCategory.PHYSICAL
    assert skill.power == 80
    assert skill.energy_cost == 3


def test_will_impact_counters_status_for_two_point_five_damage():
    user = _pokemon("愿力手", Type.NORMAL, "火")
    user.energy = 10
    enemy = _pokemon("靶子", Type.GRASS, "草")
    enemy.skills = [_status_skill()]
    state = BattleState(team_a=[user], team_b=[enemy], team_item_a="强化术")

    skill = _build_will_impact_skill(user)
    expected = DamageCalculator.calculate(user, enemy, skill, power_override=200)

    execute_full_turn(state, (ACTION_WILL_IMPACT,), (0,))

    assert state.counter_count_a == 1
    assert enemy.current_hp == enemy.hp - expected
    assert user.skills[0].name == "一号位"
    assert user.energy == 7
