from src.battle import execute_leader_evolution, leader_evolution_status
from src.models import BattleState, Pokemon, Type
from src.pokemon_db import calc_combat_stats, get_leader_evolution_target, get_pokemon
from src.skill_db import get_skill, load_ability_effects
from src.team_builder import TeamBuilder


def _make_pokemon(name: str, bloodline: str = "首领") -> Pokemon:
    data = get_pokemon(name)
    stats = calc_combat_stats(
        data["生命种族值"],
        data["物攻种族值"],
        data["魔攻种族值"],
        data["物防种族值"],
        data["魔防种族值"],
        data["速度种族值"],
        {"hp": 60, "atk": 60, "spatk": 0, "def": 0, "spdef": 0, "speed": 60},
        "坦率",
    )
    p = Pokemon(
        name=name,
        pokemon_type=TeamBuilder.TYPE_MAP.get(data["属性"], Type.NORMAL),
        hp=stats["hp"],
        attack=stats["atk"],
        defense=stats["def"],
        sp_attack=stats["spatk"],
        sp_defense=stats["spdef"],
        speed=stats["speed"],
        ability=data["特性"],
        skills=[get_skill("猛烈撞击")],
        bloodline=bloodline,
        dex_name=data["名称"],
        evo_stage=data["进化阶段"],
        spirit_no=data.get("图鉴编号", ""),
        is_leader_evolved="首领" in (data["进化阶段"] or ""),
    )
    p.iv_hp = 60
    p.iv_atk = 60
    p.iv_speed = 60
    p.nature = "坦率"
    p.ability_effects = load_ability_effects(p.ability) if p.ability else []
    return p


def _state(active: Pokemon, item: str = "进化之力") -> BattleState:
    team_a = [active] + [_make_pokemon("迪莫", "光") for _ in range(5)]
    team_b = [_make_pokemon("迪莫", "光") for _ in range(6)]
    return BattleState(team_a=team_a, team_b=team_b, team_item_a=item)


def test_leader_evolution_target_progresses_by_stage_then_leader_form():
    assert get_leader_evolution_target("喵喵")["名称"] == "喵呜"
    assert get_leader_evolution_target("喵呜")["名称"] == "魔力猫"
    assert get_leader_evolution_target("魔力猫")["名称"] == "叶冕魔力猫"
    assert get_leader_evolution_target("叶冕魔力猫") is None


def test_leader_evolution_requires_item_and_leader_bloodline():
    no_item = _state(_make_pokemon("火神"), item="")
    assert not leader_evolution_status(no_item, "a")["can_use"]

    no_bloodline = _state(_make_pokemon("火神", "火"))
    assert not leader_evolution_status(no_bloodline, "a")["can_use"]


def test_leader_evolution_recalculates_form_and_keeps_runtime_state():
    state = _state(_make_pokemon("火神"))
    p = state.team_a[0]
    p.current_hp = p.hp // 2
    p.energy = 3
    p.atk_up = 0.2
    p.poison_stacks = 2
    old_skills = [s.name for s in p.skills]

    ok, reason = execute_leader_evolution(state, "a")

    assert ok, reason
    assert p.name == "烈火战神"
    assert p.evo_stage == "首领进化"
    assert p.is_leader_evolved
    assert p.ability.startswith("爆燃")
    assert [s.name for s in p.skills] == old_skills
    assert p.energy == 3
    assert p.atk_up == 0.2
    assert p.poison_stacks == 2
    assert p.current_hp / p.hp == 0.5
    assert leader_evolution_status(state, "a")["can_use"] is False
