# 技能实现总表

> 自动汇总自 `data/nrc.db`、`src/effect_data.py` 与 `src/skill_effects_generated.py`。
> 对战加载优先级与 `src/skill_db.py` 保持一致：手写实现覆盖生成实现；没有实现的技能在“实现”小节留空。

## 汇总

- 技能总数：469
- 手写实现：127
- 生成实现：342
- 其他运行时实现：0
- 空实现：0

## 技能列表

### 001. 冰锋横扫

- 数据库 ID：1
- 系别：冰
- 类型：魔攻
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，本技能威力等于敌方精灵技能总能耗的10倍。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "enemy_total_cost",
          "multiplier": 10
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 002. 抓挠

- 数据库 ID：2
- 系别：普通
- 类型：物攻
- 能耗：0
- 威力：35
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，自己回复1能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 003. 猛烈撞击

- 数据库 ID：3
- 系别：普通
- 类型：物攻
- 能耗：1
- 威力：65
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 004. 飞踢

- 数据库 ID：4
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：110
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 005. 扫尾

- 数据库 ID：5
- 系别：普通
- 类型：物攻
- 能耗：2
- 威力：90
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 006. 迫近攻击

- 数据库 ID：6
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：90
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤。每次使用后，本技能威力永久+45。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 45,
          "trigger": "per_use"
        }
      }
    ]
  }
]
```

### 007. 音爆

- 数据库 ID：7
- 系别：普通
- 类型：魔攻
- 能耗：4
- 威力：130
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 008. 冲撞

- 数据库 ID：8
- 系别：普通
- 类型：物攻
- 能耗：7
- 威力：135
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，回合结束时，本技能能耗永久-1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "cost",
          "delta": -1,
          "trigger": "per_use"
        }
      }
    ]
  }
]
```

### 009. 见招拆招

- 数据库 ID：9
- 系别：普通
- 类型：物攻
- 能耗：2
- 威力：65
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，若上回合使用状态技能，本次技能威力+55。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "IF",
    "filter": {
      "prev_status": true
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "prev_status",
          "bonus": 55
        }
      }
    ]
  }
]
```

### 010. 触底强击

- 数据库 ID：10
- 系别：普通
- 类型：魔攻
- 能耗：3
- 威力：65
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，使用后若能量耗尽，本次技能威力+110。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 011. 突袭

- 数据库 ID：11
- 系别：普通
- 类型：魔攻
- 能耗：2
- 威力：70
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，应对状态：本次技能威力变为3倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "counter",
          "multiplier": 3.0
        }
      }
    ]
  }
]
```

### 012. 连续爪击

- 数据库 ID：12
- 系别：普通
- 类型：物攻
- 能耗：2
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，2连击，应对状态：本次技能连击数翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "current_hit_count_mult",
          "value": 2.0
        }
      }
    ]
  }
]
```

### 013. 追打

- 数据库 ID：13
- 系别：普通
- 类型：魔攻
- 能耗：3
- 威力：75
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，1连击，应对状态：本技能变为3连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 014. 旋转突击

- 数据库 ID：14
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：35
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，3连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 015. 偷袭

- 数据库 ID：15
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：85
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，应对状态：本次技能威力变为3倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "counter",
          "multiplier": 3.0
        }
      }
    ]
  }
]
```

### 016. 乱打

- 数据库 ID：16
- 系别：普通
- 类型：魔攻
- 能耗：4
- 威力：25
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，5连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 017. 乘胜追击

- 数据库 ID：17
- 系别：普通
- 类型：物攻
- 能耗：2
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，1连击，每次使用后，本技能连击数永久+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "hit_count",
          "delta": 1,
          "trigger": "per_use"
        }
      }
    ]
  }
]
```

### 018. 阻断

- 数据库 ID：18
- 系别：普通
- 类型：魔攻
- 能耗：2
- 威力：80
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，应对状态：额外打断被应对技能。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "INTERRUPT"
      }
    ]
  }
]
```

### 019. 穿膛

- 数据库 ID：19
- 系别：普通
- 类型：物攻
- 能耗：2
- 威力：65
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，若敌方能量小于等于2，造成5倍伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "enemy_energy_leq",
          "threshold": 2,
          "multiplier": 5.0
        }
      }
    ]
  }
]
```

### 020. 重击

- 数据库 ID：20
- 系别：普通
- 类型：物攻
- 能耗：2
- 威力：110
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，每次使用后，本技能能耗永久+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "cost",
          "delta": 1,
          "trigger": "per_use"
        }
      }
    ]
  }
]
```

### 021. 魔能爆

- 数据库 ID：21
- 系别：普通
- 类型：魔攻
- 能耗：0
- 威力：1
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，使用时消耗所有能量，消耗越高，伤害越高。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "ENERGY_ALL_IN",
        "params": {
          "power_per_energy": 25
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 022. 垂死反击

- 数据库 ID：22
- 系别：普通
- 类型：物攻
- 能耗：4
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，自己每失去5%生命，本次技能威力+5。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "self_missing_hp_step",
          "step_pct": 0.05,
          "bonus_per_step": 5
        }
      }
    ]
  }
]
```

### 023. 能量刃

- 数据库 ID：23
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：80
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，每应对成功1次，本技能威力永久+90。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 90,
          "trigger": "per_counter"
        }
      }
    ]
  }
]
```

### 024. 气势一击

- 数据库 ID：24
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：80
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，若上回合应对成功，本次技能威力+180。

**实现**

```json
[
  {
    "timing": "IF",
    "filter": {
      "prev_counter_success": true
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "prev_counter_success",
          "bonus": 240
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 025. 吞噬

- 数据库 ID：25
- 系别：普通
- 类型：物攻
- 能耗：6
- 威力：150
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，若使用本技能击败敌方，回复6能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_HIT",
    "filter": {
      "on_kill": true
    },
    "effects": [
      {
        "type": "HEAL_ENERGY",
        "params": {
          "amount": 6
        }
      }
    ]
  }
]
```

### 026. 蓄能轰击

- 数据库 ID：26
- 系别：普通
- 类型：魔攻
- 能耗：6
- 威力：130
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，每使用1次普通系技能，本技能能耗永久-2。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "cost",
          "delta": -2,
          "trigger": "per_ally_normal_skill"
        }
      }
    ]
  }
]
```

### 027. 力量增效

- 数据库 ID：27
- 系别：普通
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得物攻+100%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 1.0
        }
      }
    ]
  }
]
```

### 028. 魔法增效

- 数据库 ID：28
- 系别：普通
- 类型：状态
- 能耗：0
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得魔攻+70%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "spatk": 0.7
        }
      }
    ]
  }
]
```

### 029. 休息回复

- 数据库 ID：29
- 系别：普通
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己回复30%生命。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "timing": "ON_USE",
        "effects": [
          {
            "type": "HEAL_HP",
            "params": {
              "pct": 0.3
            }
          }
        ]
      }
    ]
  }
]
```

### 030. 聒噪

- 数据库 ID：30
- 系别：普通
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得全攻击技能能耗+3，持续3回合。

**实现**

```json
[
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "ENEMY_ENERGY_COST_UP",
        "params": {
          "amount": 3,
          "duration": 3,
          "filter": "attack"
        }
      }
    ]
  }
]
```

### 031. 激怒

- 数据库 ID：31
- 系别：普通
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方除本回合使用的技能，其他技能能耗+3，持续3回合。

**实现**

```json
[
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "ENEMY_ENERGY_COST_UP",
        "params": {
          "amount": 3,
          "duration": 3,
          "filter": "other_skills"
        }
      }
    ]
  }
]
```

### 032. 咆哮

- 数据库 ID：32
- 系别：普通
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得物攻-130%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "atk": 1.3
        }
      }
    ]
  }
]
```

### 033. 锐利眼神

- 数据库 ID：33
- 系别：普通
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：敌方获得物防和魔防-120%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "def": 1.2,
          "spdef": 1.2
        }
      }
    ]
  }
]
```

### 034. 快速移动

- 数据库 ID：34
- 系别：普通
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得速度+80，应对防御：改为速度+160。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "speed": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "speed": 0.8
        }
      }
    ]
  }
]
```

### 035. 伺机而动

- 数据库 ID：35
- 系别：普通
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：下一次攻击时，技能威力+70。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "NEXT_ATTACK_MOD",
        "params": {
          "power_bonus": 70
        }
      }
    ]
  }
]
```

### 036. 主场优势

- 数据库 ID：36
- 系别：普通
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得1层攻击印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ATTACK_MARK",
        "params": {
          "stacks": 1,
          "target": "self"
        }
      }
    ]
  }
]
```

### 037. 操控

- 数据库 ID：37
- 系别：普通
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方本回合使用的技能能耗+7，持续3回合。

**实现**

```json
[
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "ENEMY_ENERGY_COST_UP",
        "params": {
          "amount": 7,
          "duration": 3,
          "filter": "used_skill"
        }
      }
    ]
  }
]
```

### 038. 应激反应

- 数据库 ID：38
- 系别：普通
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己回复25%生命，应对防御：改为回复50%生命。

**实现**

```json
[
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": []
  }
]
```

### 039. 棘刺

- 数据库 ID：39
- 系别：普通
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：敌方获得1层棘刺印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "THORN_MARK",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 040. 精神扰乱

- 数据库 ID：40
- 系别：普通
- 类型：状态
- 能耗：0
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得全技能能耗+1，应对防御：改为能耗+3。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "enemy",
          "stat": "cost",
          "value": 1
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "ENEMY_ENERGY_COST_UP",
        "params": {
          "amount": 2,
          "filter": "all"
        }
      }
    ]
  }
]
```

### 041. 退化

- 数据库 ID：41
- 系别：普通
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：敌方获得1层萌化。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "CUTE_ENEMY_GAIN",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 042. 防御

- 数据库 ID：42
- 系别：普通
- 类型：防御
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤70%，应对攻击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 043. 防反

- 数据库 ID：43
- 系别：普通
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤60%，应对攻击：自己获得物攻和魔攻+40%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.6
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 0.4,
          "spatk": 0.4
        }
      }
    ]
  }
]
```

### 044. 血气

- 数据库 ID：44
- 系别：普通
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤60%，应对攻击：本回合受到致命伤害时，保留1生命值。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.6
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 045. 无畏之心

- 数据库 ID：45
- 系别：普通
- 类型：防御
- 能耗：5
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤100%，应对攻击：减免的伤害变为回复自己生命，且本技能能耗永久+2。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 1.0
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "HEAL_HP",
        "params": {
          "pct": 0.3
        }
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "cost",
          "delta": 2
        }
      }
    ]
  }
]
```

### 046. 借用

- 数据库 ID：46
- 系别：普通
- 类型：状态
- 能耗：0
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：每回合随机变成己方队伍中其他精灵的技能。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "borrow_ally_skill"
        }
      }
    ]
  }
]
```

### 047. 取念

- 数据库 ID：47
- 系别：普通
- 类型：状态
- 能耗：0
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：每回合随机变成敌方任意精灵的技能，且该技能能耗-2。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "copy_enemy_skill",
          "cost_reduce": 2
        }
      }
    ]
  }
]
```

### 048. 复写

- 数据库 ID：48
- 系别：普通
- 类型：状态
- 能耗：0
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：每回合随机变成自己未携带的技能，且该技能能耗-2。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "copy_random_skill",
          "cost_reduce": 2
        }
      }
    ]
  }
]
```

### 049. 落星

- 数据库 ID：49
- 系别：普通
- 类型：物攻
- 能耗：0
- 威力：45
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 050. 拍击

- 数据库 ID：50
- 系别：普通
- 类型：魔攻
- 能耗：1
- 威力：65
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 051. 音波弹

- 数据库 ID：51
- 系别：普通
- 类型：魔攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，1连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 052. 许愿星

- 数据库 ID：52
- 系别：普通
- 类型：魔攻
- 能耗：3
- 威力：110
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 053. 星星撞击

- 数据库 ID：53
- 系别：普通
- 类型：魔攻
- 能耗：2
- 威力：90
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 054. 能量炮

- 数据库 ID：54
- 系别：普通
- 类型：魔攻
- 能耗：3
- 威力：50
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，2连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 055. 压扁

- 数据库 ID：55
- 系别：普通
- 类型：物攻
- 能耗：5
- 威力：155
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 056. 践踏

- 数据库 ID：56
- 系别：普通
- 类型：物攻
- 能耗：4
- 威力：130
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 057. 湮灭

- 数据库 ID：57
- 系别：普通
- 类型：魔攻
- 能耗：5
- 威力：155
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 058. 打鼾

- 数据库 ID：58
- 系别：普通
- 类型：魔攻
- 能耗：6
- 威力：165
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 059. 先发制人

- 数据库 ID：59
- 系别：普通
- 类型：物攻
- 能耗：2
- 威力：55
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物理伤害，先手+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 060. 天旋地转

- 数据库 ID：60
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：60
- 标记：迸发
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物理伤害，先手+1，迸发：本次技能威力+30。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 061. 吨位压制

- 数据库 ID：61
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，敌方体重越低，威力越高。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 062. 以重制重

- 数据库 ID：62
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，敌方体重越高，本次技能威力越高。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 063. 当头棒喝

- 数据库 ID：63
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，若敌方本回合更换精灵，本次技能威力+100。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 064. 后发制人

- 数据库 ID：64
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：155
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物理伤害，先手-1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 065. 加固

- 数据库 ID：65
- 系别：普通
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得物防+140%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "def": 1.4
        }
      }
    ]
  }
]
```

### 066. 鼓劲

- 数据库 ID：66
- 系别：普通
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得魔防+170%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "spdef": 1.7
        }
      }
    ]
  }
]
```

### 067. 耀眼

- 数据库 ID：67
- 系别：普通
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得连击数-4。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "enemy",
          "stat": "hit_count",
          "value": -4
        }
      }
    ]
  }
]
```

### 068. 彗星

- 数据库 ID：68
- 系别：普通
- 类型：魔攻
- 能耗：0
- 威力：240
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，每失去5%生命，本次技能威力-10，使用后消耗全部生命。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "self_missing_hp_step",
          "step_pct": 0.05,
          "bonus_per_step": -10
        }
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "SELF_KO"
      }
    ]
  }
]
```

### 069. 消毒法

- 数据库 ID：69
- 系别：普通
- 类型：魔攻
- 能耗：4
- 威力：115
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，驱散敌方5层增益。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 070. 三连破

- 数据库 ID：70
- 系别：普通
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得物攻+30%，3连击。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 0.3
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "hit_count",
          "value": 3
        }
      }
    ]
  }
]
```

### 071. 热身运动

- 数据库 ID：71
- 系别：普通
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得连击数+3。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "hit_count",
          "value": 3
        }
      }
    ]
  }
]
```

### 072. 晒太阳

- 数据库 ID：72
- 系别：普通
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：驱散敌方所有增益。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "CLEANSE",
        "params": {
          "target": "enemy",
          "mode": "buffs"
        }
      }
    ]
  }
]
```

### 073. 有效预防

- 数据库 ID：73
- 系别：普通
- 类型：防御
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤50%，应对攻击：下一次行动获得先手+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.5
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 074. 嗜痛

- 数据库 ID：74
- 系别：普通
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：期间自己每次受到伤害，获得双攻+40%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 0.4,
          "spatk": 0.4
        }
      }
    ]
  }
]
```

### 075. 吓退

- 数据库 ID：75
- 系别：普通
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤60%，应对攻击：敌方脱离。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "FORCE_ENEMY_SWITCH"
      }
    ]
  }
]
```

### 076. 埋伏

- 数据库 ID：76
- 系别：普通
- 类型：魔攻
- 能耗：4
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，3连击，若敌方本回合更换精灵，本次技能连击数+3。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 077. 逆袭

- 数据库 ID：77
- 系别：普通
- 类型：物攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，本技能能耗每+1，威力+50。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "energy_cost_above_base",
          "base_cost": 3,
          "bonus_per_step": 50
        }
      }
    ]
  }
]
```

### 078. 摇篮曲

- 数据库 ID：78
- 系别：普通
- 类型：状态
- 能耗：5
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得全技能能耗+3，应对防御：额外造成打断，且敌方下回合获得眩晕。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "enemy",
          "stat": "cost",
          "value": 3
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "INTERRUPT"
      }
    ]
  }
]
```

### 079. 倾泻

- 数据库 ID：79
- 系别：普通
- 类型：魔攻
- 能耗：3
- 威力：70
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，若本次攻击未被防御技能应对，则驱散双方所有印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "DISPEL_MARKS",
        "params": {
          "condition": "not_blocked"
        }
      }
    ]
  }
]
```

### 080. 种子弹

- 数据库 ID：80
- 系别：草
- 类型：物攻
- 能耗：0
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，自己回复1能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 081. 荆棘爪

- 数据库 ID：81
- 系别：草
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 082. 仙人掌刺击

- 数据库 ID：82
- 系别：草
- 类型：物攻
- 能耗：6
- 威力：150
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 083. 刺藤

- 数据库 ID：83
- 系别：草
- 类型：物攻
- 能耗：3
- 威力：45
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，2连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 084. 藤绞

- 数据库 ID：84
- 系别：草
- 类型：物攻
- 能耗：4
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，自己回复5能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 085. 光能聚集

- 数据库 ID：85
- 系别：草
- 类型：魔攻
- 能耗：7
- 威力：100
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，每次使用其他草系技能后，本技能威力永久+60。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 60,
          "trigger": "per_ally_grass_skill"
        }
      }
    ]
  }
]
```

### 086. 徒长

- 数据库 ID：86
- 系别：草
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己回复10能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "timing": "ON_USE",
        "effects": [
          {
            "type": "HEAL_ENERGY",
            "params": {
              "amount": 10
            }
          }
        ]
      }
    ]
  }
]
```

### 087. 盛开

- 数据库 ID：87
- 系别：草
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得全技能威力+30，应对防御：改为威力+60。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "power_pct",
          "value": 0.3
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": []
  }
]
```

### 088. 根吸收

- 数据库 ID：88
- 系别：草
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己回复15%生命和4能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "timing": "ON_USE",
        "effects": [
          {
            "type": "HEAL_HP",
            "params": {
              "pct": 0.15
            }
          }
        ]
      }
    ]
  }
]
```

### 089. 氧输送

- 数据库 ID：89
- 系别：草
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己回复4能量，并获得魔攻+70%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "spatk": 0.7
        }
      }
    ]
  }
]
```

### 090. 孢子

- 数据库 ID：90
- 系别：草
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得1层寄生。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "LEECH",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 091. 芳香诱引

- 数据库 ID：91
- 系别：草
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得连击数+3，应对防御：额外造成打断，且敌方下回合获得眩晕。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "hit_count",
          "value": 3
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "INTERRUPT"
      }
    ]
  }
]
```

### 092. 丰饶

- 数据库 ID：92
- 系别：草
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得物攻和魔攻+140%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 1.3,
          "spatk": 1.3
        }
      }
    ]
  }
]
```

### 093. 移花接木

- 数据库 ID：93
- 系别：草
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己回复15%生命，随后脱离。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "FORCE_SWITCH"
      }
    ]
  }
]
```

### 094. 光合作用

- 数据库 ID：94
- 系别：草
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得1层光合印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SOLAR_MARK",
        "params": {
          "stacks": 1,
          "target": "self"
        }
      }
    ]
  }
]
```

### 095. 酶浓度调整

- 数据库 ID：95
- 系别：草
- 类型：防御
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：自己回复20%生命。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 096. 蜡质膜

- 数据库 ID：96
- 系别：草
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：回复3能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 097. 汲取

- 数据库 ID：97
- 系别：草
- 类型：魔攻
- 能耗：1
- 威力：30
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，并吸血100%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "LIFE_DRAIN",
        "params": {
          "pct": 1.0
        }
      }
    ]
  }
]
```

### 098. 飞叶

- 数据库 ID：98
- 系别：草
- 类型：物攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 099. 种皮爆裂

- 数据库 ID：99
- 系别：草
- 类型：物攻
- 能耗：1
- 威力：25
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，2连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 100. 花香

- 数据库 ID：100
- 系别：草
- 类型：魔攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 101. 棘突

- 数据库 ID：101
- 系别：草
- 类型：魔攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 102. 孢子爆散

- 数据库 ID：102
- 系别：草
- 类型：物攻
- 能耗：3
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，1连击，每次使用后，本技能连击数永久+2。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "hit_count",
          "delta": 2,
          "trigger": "per_use"
        }
      }
    ]
  }
]
```

### 103. 叶绿光束

- 数据库 ID：103
- 系别：草
- 类型：魔攻
- 能耗：4
- 威力：120
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 104. 顶端优势

- 数据库 ID：104
- 系别：草
- 类型：物攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 105. 筛管奔流

- 数据库 ID：105
- 系别：草
- 类型：物攻
- 能耗：3
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，自己生命大于80%时，本次技能威力+75。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 106. 花炮

- 数据库 ID：106
- 系别：草
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：2连击，每次连击自己获得魔攻+60%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "spatk": 0.6
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "hit_count",
          "value": 2
        }
      }
    ]
  }
]
```

### 107. 聚盐

- 数据库 ID：107
- 系别：草
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：2连击，每次连击自己回复5%生命和1能量，使用后本技能连击数永久+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "HEAL_HP",
        "params": {
          "pct": 0.05
        }
      },
      {
        "type": "HEAL_ENERGY",
        "params": {
          "amount": 1
        }
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "hit_count",
          "delta": 1
        }
      }
    ]
  }
]
```

### 108. 富养化

- 数据库 ID：108
- 系别：草
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：为场下每个精灵回复3能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "timing": "ON_USE",
        "effects": [
          {
            "type": "HEAL_ENERGY",
            "params": {
              "amount": 3
            }
          }
        ]
      }
    ]
  }
]
```

### 109. 纤维化

- 数据库 ID：109
- 系别：草
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：自己获得物防+70%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "def": 0.7
        }
      }
    ]
  }
]
```

### 110. 抽枝

- 数据库 ID：110
- 系别：草
- 类型：物攻
- 能耗：4
- 威力：90
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，应对状态：自己回复50%生命和5能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "HEAL_HP",
        "params": {
          "pct": 0.5
        }
      },
      {
        "type": "HEAL_ENERGY",
        "params": {
          "amount": 5
        }
      }
    ]
  }
]
```

### 111. 针刺射击

- 数据库 ID：111
- 系别：草
- 类型：物攻
- 能耗：3
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，若敌方本回合更换精灵，自己回复7点能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 112. 火焰冲锋

- 数据库 ID：112
- 系别：火
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 113. 炎枪

- 数据库 ID：113
- 系别：火
- 类型：魔攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 114. 火苗

- 数据库 ID：114
- 系别：火
- 类型：物攻
- 能耗：0
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，自己回复1能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 115. 闪燃

- 数据库 ID：115
- 系别：火
- 类型：物攻
- 能耗：1
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，应对状态：本次技能威力变为4倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "counter",
          "multiplier": 4.0
        }
      }
    ]
  }
]
```

### 116. 双响炮

- 数据库 ID：116
- 系别：火
- 类型：物攻
- 能耗：1
- 威力：25
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，2连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 117. 吹火

- 数据库 ID：117
- 系别：火
- 类型：物攻
- 能耗：1
- 威力：50
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，每次使用后，本技能威力永久+20。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 20,
          "trigger": "per_use"
        }
      }
    ]
  }
]
```

### 118. 流星火雨

- 数据库 ID：118
- 系别：火
- 类型：物攻
- 能耗：3
- 威力：75
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，每次击败敌方，本技能威力永久+75。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 75,
          "trigger": "per_kill"
        }
      }
    ]
  }
]
```

### 119. 持续高温

- 数据库 ID：119
- 系别：火
- 类型：魔攻
- 能耗：2
- 威力：70
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，应对状态：下次攻击技能威力翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 120. 易燃物质

- 数据库 ID：120
- 系别：火
- 类型：魔攻
- 能耗：3
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，2连击，每次连击使敌方获得2层灼烧。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "BURN",
        "params": {
          "stacks": 2
        }
      }
    ]
  }
]
```

### 121. 高温回火

- 数据库 ID：121
- 系别：火
- 类型：魔攻
- 能耗：2
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，自己脱离。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "FORCE_SWITCH"
      }
    ]
  }
]
```

### 122. 山火

- 数据库 ID：122
- 系别：火
- 类型：物攻
- 能耗：3
- 威力：15
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，每使用1次其他火系技能，本技能威力永久翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 15,
          "trigger": "per_ally_fire_skill"
        }
      }
    ]
  }
]
```

### 123. 引燃

- 数据库 ID：123
- 系别：火
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：敌方获得10层灼烧。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "BURN",
        "params": {
          "stacks": 10
        }
      }
    ]
  }
]
```

### 124. 热身

- 数据库 ID：124
- 系别：火
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：下一次攻击时，技能威力翻倍，应对防御：改为威力变为4倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "NEXT_ATTACK_MOD",
        "params": {
          "power_pct": 1.0
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": []
  }
]
```

### 125. 充分燃烧

- 数据库 ID：125
- 系别：火
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：使敌方身上的灼烧翻倍，并触发1次灼烧伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "double_enemy_burn_and_tick"
        }
      }
    ]
  }
]
```

### 126. 天火

- 数据库 ID：126
- 系别：火
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得10层灼烧，应对防御：改为获得30层。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "BURN",
        "params": {
          "stacks": 10
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": []
  }
]
```

### 127. 火焰护盾

- 数据库 ID：127
- 系别：火
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤70%，应对攻击：敌方获得6层灼烧。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "BURN",
        "params": {
          "stacks": 4
        }
      }
    ]
  }
]
```

### 128. 火云车

- 数据库 ID：128
- 系别：火
- 类型：物攻
- 能耗：5
- 威力：140
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 129. 爆裂飞弹

- 数据库 ID：129
- 系别：火
- 类型：魔攻
- 能耗：7
- 威力：160
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 130. 热气

- 数据库 ID：130
- 系别：火
- 类型：魔攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 131. 流火

- 数据库 ID：131
- 系别：火
- 类型：魔攻
- 能耗：1
- 威力：15
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，3连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 132. 火爪

- 数据库 ID：132
- 系别：火
- 类型：魔攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 133. 火焰箭

- 数据库 ID：133
- 系别：火
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 134. 炙热波动

- 数据库 ID：134
- 系别：火
- 类型：魔攻
- 能耗：3
- 威力：55
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，敌方获得4层灼烧，应对状态：本次技能威力和赋予灼烧翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "BURN",
        "params": {
          "stacks": 4
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 135. 火焰切割

- 数据库 ID：135
- 系别：火
- 类型：物攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 136. 烈焰风暴

- 数据库 ID：136
- 系别：火
- 类型：魔攻
- 能耗：4
- 威力：75
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，敌方获得6层灼烧。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "BURN",
        "params": {
          "stacks": 6
        }
      }
    ]
  }
]
```

### 137. 炎息

- 数据库 ID：137
- 系别：火
- 类型：物攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 138. 灼伤

- 数据库 ID：138
- 系别：火
- 类型：物攻
- 能耗：4
- 威力：120
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 139. 炎打

- 数据库 ID：139
- 系别：火
- 类型：魔攻
- 能耗：2
- 威力：95
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成高额魔法伤害，自己获得物防-40%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 140. 怒火

- 数据库 ID：140
- 系别：火
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得双攻+120%和双防-40%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 1.2,
          "spatk": 1.2
        }
      }
    ]
  }
]
```

### 141. 淬火

- 数据库 ID：141
- 系别：火
- 类型：防御
- 能耗：4
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：下次攻击技能威力翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 142. 燃尽

- 数据库 ID：142
- 系别：火
- 类型：魔攻
- 能耗：4
- 威力：155
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，敌方每失去5%生命，本次技能威力-5。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "self_missing_hp_step",
          "step_pct": 0.05,
          "bonus_per_step": -5
        }
      }
    ]
  }
]
```

### 143. 焚毁

- 数据库 ID：143
- 系别：火
- 类型：魔攻
- 能耗：2
- 威力：60
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，驱散敌方所有印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "DISPEL_ENEMY_MARKS"
      }
    ]
  }
]
```

### 144. 焚烧烙印

- 数据库 ID：144
- 系别：火
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：驱散双方所有印记，每驱散1层，敌方获得5层灼烧。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DISPEL_MARKS_TO_BURN",
        "params": {
          "burn_per_mark": 5
        }
      }
    ]
  }
]
```

### 145. 除厄

- 数据库 ID：145
- 系别：火
- 类型：魔攻
- 能耗：2
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，驱散自己的减益。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "CLEANSE",
        "params": {
          "target": "self",
          "mode": "debuffs"
        }
      }
    ]
  }
]
```

### 146. 阳火增辉

- 数据库 ID：146
- 系别：火
- 类型：魔攻
- 能耗：3
- 威力：75
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，每次击败敌方，本技能威力永久翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_HIT",
    "filter": {
      "on_kill": true
    },
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power_double",
          "delta": 1
        }
      }
    ]
  }
]
```

### 147. 甩水

- 数据库 ID：147
- 系别：水
- 类型：魔攻
- 能耗：0
- 威力：30
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，自己回复1能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "HEAL_ENERGY",
        "params": {
          "amount": 1
        }
      }
    ]
  }
]
```

### 148. 水弹枪

- 数据库 ID：148
- 系别：水
- 类型：魔攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 149. 气泡

- 数据库 ID：149
- 系别：水
- 类型：魔攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 150. 水炮

- 数据库 ID：150
- 系别：水
- 类型：魔攻
- 能耗：5
- 威力：110
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，每次使用后，本技能能耗永久-1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "cost",
          "delta": -1,
          "trigger": "per_use"
        }
      }
    ]
  }
]
```

### 151. 水刃

- 数据库 ID：151
- 系别：水
- 类型：物攻
- 能耗：4
- 威力：115
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，应对状态：本技能能耗永久-4。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "cost",
          "delta": -4
        }
      }
    ]
  }
]
```

### 152. 天洪

- 数据库 ID：152
- 系别：水
- 类型：魔攻
- 能耗：7
- 威力：150
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，应对状态：本技能能耗永久-6。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "cost",
          "delta": -6
        }
      }
    ]
  }
]
```

### 153. 润泽

- 数据库 ID：153
- 系别：水
- 类型：状态
- 能耗：7
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得魔攻+190%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "spatk": 1.9
        }
      }
    ]
  }
]
```

### 154. 蓄水

- 数据库 ID：154
- 系别：水
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：下次使用的技能能耗-6。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "NEXT_ATTACK_MOD",
        "params": {
          "cost_reduce": 6
        }
      }
    ]
  }
]
```

### 155. 打湿

- 数据库 ID：155
- 系别：水
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得1层湿润印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "MOISTURE_MARK",
        "params": {
          "stacks": 1,
          "target": "self"
        }
      }
    ]
  }
]
```

### 156. 落雨

- 数据库 ID：156
- 系别：水
- 类型：状态
- 能耗：5
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：将天气改为雨天，持续8回合。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "WEATHER",
        "params": {
          "turns": 8,
          "type": "rain"
        }
      }
    ]
  }
]
```

### 157. 泡沫幻影

- 数据库 ID：157
- 系别：水
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤80%，应对攻击：自己脱离。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "FORCE_SWITCH"
      }
    ]
  }
]
```

### 158. 水泡盾

- 数据库 ID：158
- 系别：水
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：自己获得魔攻+70%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "spatk": 0.7
        }
      }
    ]
  }
]
```

### 159. 水环

- 数据库 ID：159
- 系别：水
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤60%，应对攻击：自己获得全技能能耗-2。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "PASSIVE_ENERGY_REDUCE",
        "params": {
          "reduce": 2,
          "range": "all"
        }
      }
    ]
  }
]
```

### 160. 水光冲击

- 数据库 ID：160
- 系别：水
- 类型：魔攻
- 能耗：5
- 威力：140
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 161. 水波术

- 数据库 ID：161
- 系别：水
- 类型：魔攻
- 能耗：6
- 威力：90
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，回合结束时，本技能威力永久+20。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 20,
          "trigger": "per_turn_end"
        }
      }
    ]
  }
]
```

### 162. 水弹

- 数据库 ID：162
- 系别：水
- 类型：魔攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 163. 泡沫

- 数据库 ID：163
- 系别：水
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 164. 肥皂泡

- 数据库 ID：164
- 系别：水
- 类型：魔攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 165. 水花四溅

- 数据库 ID：165
- 系别：水
- 类型：魔攻
- 能耗：3
- 威力：20
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，4连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 166. 潮涌

- 数据库 ID：166
- 系别：水
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 167. 水幕冲击

- 数据库 ID：167
- 系别：水
- 类型：物攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 168. 激流

- 数据库 ID：168
- 系别：水
- 类型：魔攻
- 能耗：4
- 威力：120
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 169. 涌泉

- 数据库 ID：169
- 系别：水
- 类型：魔攻
- 能耗：6
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，本技能能耗每-1，威力+10。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 170. 洗礼

- 数据库 ID：170
- 系别：水
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：驱散自己的减益，并获得全技能能耗-1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "cost",
          "value": -1
        }
      },
      {
        "type": "CLEANSE",
        "params": {
          "target": "self",
          "mode": "debuffs"
        }
      }
    ]
  }
]
```

### 171. 盐水浴

- 数据库 ID：171
- 系别：水
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得全技能能耗-2，应对防御：改为技能能耗-3。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "PASSIVE_ENERGY_REDUCE",
        "params": {
          "reduce": 2,
          "range": "all"
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "PASSIVE_ENERGY_REDUCE",
        "params": {
          "reduce": 1,
          "range": "all"
        }
      }
    ]
  }
]
```

### 172. 潮汐

- 数据库 ID：172
- 系别：水
- 类型：防御
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤60%，应对攻击：自己获得1层湿润印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.6
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "MOISTURE_MARK",
        "params": {
          "stacks": 1,
          "target": "self"
        }
      }
    ]
  }
]
```

### 173. 闪光

- 数据库 ID：173
- 系别：光
- 类型：魔攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 174. 闪光冲击

- 数据库 ID：174
- 系别：光
- 类型：物攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 175. 过曝

- 数据库 ID：175
- 系别：光
- 类型：魔攻
- 能耗：3
- 威力：60
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，每使用过1个其他系别技能，本技能威力永久+30。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 30,
          "trigger": "per_unique_element"
        }
      }
    ]
  }
]
```

### 176. 折射

- 数据库 ID：176
- 系别：光
- 类型：魔攻
- 能耗：4
- 威力：50
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，携带其他系别技能会给本技能带来不同效果。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 177. 漫反射

- 数据库 ID：177
- 系别：光
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：每种系别中的至多1个技能，威力+35。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "modify_matching_skills",
          "power_bonus": 35,
          "per_element_one": true
        }
      }
    ]
  }
]
```

### 178. 镜像反射

- 数据库 ID：178
- 系别：光
- 类型：防御
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤70%，应对攻击：本技能变为被应对的技能。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 179. 光球

- 数据库 ID：179
- 系别：光
- 类型：魔攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 180. 光之矛

- 数据库 ID：180
- 系别：光
- 类型：物攻
- 能耗：3
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，3连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 181. 光刃

- 数据库 ID：181
- 系别：光
- 类型：物攻
- 能耗：4
- 威力：120
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 182. 脉冲光线

- 数据库 ID：182
- 系别：光
- 类型：魔攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 183. 虹光冲击

- 数据库 ID：183
- 系别：光
- 类型：魔攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 184. 折线冲击

- 数据库 ID：184
- 系别：光
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 185. 天光

- 数据库 ID：185
- 系别：光
- 类型：魔攻
- 能耗：3
- 威力：95
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，本技能系别和天气系别相同。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 186. 透射

- 数据库 ID：186
- 系别：光
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 187. 放晴

- 数据库 ID：187
- 系别：光
- 类型：状态
- 能耗：0
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：光系技能威力永久+50%，应对防御：改为永久+100%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "modify_matching_skills",
          "power_pct": 0.4,
          "element": [
            "光"
          ]
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "modify_matching_skills",
          "power_pct": 0.4,
          "element": [
            "光"
          ]
        }
      }
    ]
  }
]
```

### 188. 械斗

- 数据库 ID：188
- 系别：机械
- 类型：物攻
- 能耗：1
- 威力：45
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，本技能位于1号位时威力+60，传动1。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "POSITION_BUFF",
        "params": {
          "positions": [
            0
          ],
          "buff": {
            "power": 60
          }
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "DRIVE",
        "params": {
          "value": 1
        }
      }
    ]
  }
]
```

### 189. 齿轮扭矩

- 数据库 ID：189
- 系别：机械
- 类型：物攻
- 能耗：3
- 威力：80
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，每回合位置发生变化时，本技能威力永久+20。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 20,
          "trigger": "per_position_change"
        }
      }
    ]
  }
]
```

### 190. 钢钻

- 数据库 ID：190
- 系别：机械
- 类型：物攻
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，技能威力为两侧技能威力和的三分之一，传动1。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "adjacent_power_sum",
          "divisor": 3
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "DRIVE",
        "params": {
          "value": 1
        }
      }
    ]
  }
]
```

### 191. 钢铁洪流

- 数据库 ID：191
- 系别：机械
- 类型：物攻
- 能耗：3
- 威力：70
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，本技能位于1号位时威力+90，传动2。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "POSITION_BUFF",
        "params": {
          "positions": [
            0
          ],
          "buff": {
            "power": 90
          }
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "DRIVE",
        "params": {
          "value": 2
        }
      }
    ]
  }
]
```

### 192. 杠杆置换

- 数据库 ID：192
- 系别：机械
- 类型：状态
- 能耗：0
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己回复2能量，交换两侧技能位置。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "timing": "ON_USE",
        "effects": [
          {
            "type": "HEAL_ENERGY",
            "params": {
              "amount": 2
            }
          }
        ]
      }
    ]
  }
]
```

### 193. 轴承支撑

- 数据库 ID：193
- 系别：机械
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：主动：本技能被动额外-1能耗，被动：两侧技能能耗-1，传动1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "PASSIVE_ENERGY_REDUCE",
        "params": {
          "reduce": 1,
          "range": "self"
        }
      },
      {
        "type": "PASSIVE_ENERGY_REDUCE",
        "params": {
          "reduce": 1,
          "range": "adjacent"
        }
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "DRIVE",
        "params": {
          "value": 1
        }
      }
    ]
  }
]
```

### 194. 联动装置

- 数据库 ID：194
- 系别：机械
- 类型：状态
- 能耗：0
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：使用后两侧技能的威力永久+20，应对防御：变为威力永久+30。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 20,
          "range": "adjacent"
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 10,
          "range": "adjacent"
        }
      }
    ]
  }
]
```

### 195. 能量守恒

- 数据库 ID：195
- 系别：机械
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤80%，应对攻击：两侧技能能耗永久-1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "PASSIVE_ENERGY_REDUCE",
        "params": {
          "reduce": 1,
          "range": "adjacent"
        }
      }
    ]
  }
]
```

### 196. 拆卸

- 数据库 ID：196
- 系别：机械
- 类型：物攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 197. 离子震荡

- 数据库 ID：197
- 系别：机械
- 类型：魔攻
- 能耗：3
- 威力：90
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，本技能位于3号位时威力+40，传动1。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "POSITION_BUFF",
        "params": {
          "positions": [
            2
          ],
          "buff": {
            "power": 40
          }
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "DRIVE",
        "params": {
          "value": 1
        }
      }
    ]
  }
]
```

### 198. 传感器

- 数据库 ID：198
- 系别：机械
- 类型：物攻
- 能耗：1
- 威力：20
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，2连击，本技能位于1号或3号位时连击+1，传动1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "POSITION_BUFF",
        "params": {
          "positions": [
            0,
            2
          ],
          "buff": {
            "hit_count": 1
          }
        }
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "DRIVE",
        "params": {
          "value": 1
        }
      }
    ]
  }
]
```

### 199. 金属噪音

- 数据库 ID：199
- 系别：机械
- 类型：魔攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 200. 磁暴

- 数据库 ID：200
- 系别：机械
- 类型：魔攻
- 能耗：2
- 威力：70
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，本技能位于1号或3号位时威力+30，传动1。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "POSITION_BUFF",
        "params": {
          "positions": [
            0,
            2
          ],
          "buff": {
            "power": 30
          }
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "DRIVE",
        "params": {
          "value": 1
        }
      }
    ]
  }
]
```

### 201. 齿轮切开

- 数据库 ID：201
- 系别：机械
- 类型：物攻
- 能耗：5
- 威力：130
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，本技能位于1号或3号位时能耗-2，传动1。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "POSITION_BUFF",
        "params": {
          "positions": [
            0,
            2
          ],
          "buff": {
            "cost_reduce": 2
          }
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "DRIVE",
        "params": {
          "value": 1
        }
      }
    ]
  }
]
```

### 202. 主轴

- 数据库 ID：202
- 系别：机械
- 类型：物攻
- 能耗：2
- 威力：75
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，此技能位置不会改变。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 203. 啮合传递

- 数据库 ID：203
- 系别：机械
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得速度+80，本技能位于1号或3号位时额外获得物攻+60%，传动1。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "speed": 0.8
        }
      },
      {
        "type": "POSITION_BUFF",
        "params": {
          "positions": [
            0,
            2
          ],
          "buff": {
            "atk": 1.0
          }
        }
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "DRIVE",
        "params": {
          "value": 1
        }
      }
    ]
  }
]
```

### 204. 扬沙

- 数据库 ID：204
- 系别：地
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 205. 跺地

- 数据库 ID：205
- 系别：地
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 206. 地刺

- 数据库 ID：206
- 系别：地
- 类型：物攻
- 能耗：3
- 威力：95
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，应对状态：额外打断被应对技能。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "INTERRUPT"
      }
    ]
  }
]
```

### 207. 岩土暴击

- 数据库 ID：207
- 系别：地
- 类型：物攻
- 能耗：8
- 威力：140
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，每被攻击1次。本技能能耗永久-1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 208. 石锁

- 数据库 ID：208
- 系别：地
- 类型：物攻
- 能耗：3
- 威力：50
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，敌方3回合无法更换精灵。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 209. 裂石

- 数据库 ID：209
- 系别：地
- 类型：物攻
- 能耗：3
- 威力：95
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，应对状态：敌方获得物防-80%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "def": 0.8
        }
      }
    ]
  }
]
```

### 210. 抛石

- 数据库 ID：210
- 系别：地
- 类型：物攻
- 能耗：30
- 威力：140
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，回合结束时，本技能能耗永久-5。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "cost",
          "delta": -5,
          "trigger": "per_use"
        }
      }
    ]
  }
]
```

### 211. 地震

- 数据库 ID：211
- 系别：地
- 类型：物攻
- 能耗：10
- 威力：190
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 212. 流沙

- 数据库 ID：212
- 系别：地
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方3回合无法更换精灵，应对防御：敌方获得双防-60%。

**实现**

```json
[
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "spdef": 0.6,
          "def": 0.6
        }
      }
    ]
  }
]
```

### 213. 泥浆铠甲

- 数据库 ID：213
- 系别：地
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得物攻和物防+60%，应对防御：额外使自己的增益翻倍。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 0.6,
          "def": 0.6
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": []
  }
]
```

### 214. 沙涌

- 数据库 ID：214
- 系别：地
- 类型：状态
- 能耗：7
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：将天气改为沙暴，持续8回合。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "WEATHER",
        "params": {
          "type": "sandstorm",
          "turns": 5
        }
      }
    ]
  }
]
```

### 215. 刺盾

- 数据库 ID：215
- 系别：地
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤70%，应对攻击：敌方获得物攻-70%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "atk": 0.7
        }
      }
    ]
  }
]
```

### 216. 硬化

- 数据库 ID：216
- 系别：地
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤90%，若上次使用攻击技则本技能能耗-2，应对攻击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.9
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 217. 壁垒

- 数据库 ID：217
- 系别：地
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤90%，应对攻击：防御技能冷却-1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.9
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 218. 遁地

- 数据库 ID：218
- 系别：地
- 类型：防御
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤50%并脱离，应对攻击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.5
        }
      },
      {
        "type": "FORCE_SWITCH"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 219. 泥浆

- 数据库 ID：219
- 系别：地
- 类型：魔攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 220. 泥巴喷射

- 数据库 ID：220
- 系别：地
- 类型：魔攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 221. 落石

- 数据库 ID：221
- 系别：地
- 类型：物攻
- 能耗：1
- 威力：55
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，1连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 222. 热砂

- 数据库 ID：222
- 系别：地
- 类型：魔攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 223. 陨石

- 数据库 ID：223
- 系别：地
- 类型：魔攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 224. 鸣沙陷阱

- 数据库 ID：224
- 系别：地
- 类型：物攻
- 能耗：4
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，物防比敌方越高，本次技能威力越高。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 225. 地陷

- 数据库 ID：225
- 系别：地
- 类型：物攻
- 能耗：5
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，自己获得物防+70%，应对状态：本次技能威力翻倍，且物防额外+70%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "def": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "counter",
          "multiplier": 2.0
        }
      }
    ]
  }
]
```

### 226. 岩脉崩毁

- 数据库 ID：226
- 系别：地
- 类型：物攻
- 能耗：4
- 威力：120
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，本技能能耗固定为4。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 227. 震击

- 数据库 ID：227
- 系别：地
- 类型：物攻
- 能耗：3
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成伤害，敌方获得连击数-3。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "enemy",
          "stat": "hit_count",
          "value": -3
        }
      }
    ]
  }
]
```

### 228. 石肤术

- 数据库 ID：228
- 系别：地
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得物防+160%和魔防-60%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "def": 1.6
        }
      }
    ]
  }
]
```

### 229. 钧势

- 数据库 ID：229
- 系别：地
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得物防+140%和速度-30。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "def": 1.4
        }
      }
    ]
  }
]
```

### 230. 蓄势待发

- 数据库 ID：230
- 系别：地
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得1层蓄势印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "MOMENTUM_MARK",
        "params": {
          "stacks": 1,
          "target": "self"
        }
      }
    ]
  }
]
```

### 231. 淤泥表皮

- 数据库 ID：231
- 系别：地
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：敌方获得连击数-3。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 232. 不动如山

- 数据库 ID：232
- 系别：地
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤90%，应对攻击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.9
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 233. 砂石冲撞

- 数据库 ID：233
- 系别：地
- 类型：物攻
- 能耗：3
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，若敌方本回合更换精灵，自己获得物防+100%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "def": 1.0
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 234. 风吹雪

- 数据库 ID：234
- 系别：冰
- 类型：魔攻
- 能耗：0
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，自己回复1能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 235. 暴风雪

- 数据库 ID：235
- 系别：冰
- 类型：物攻
- 能耗：3
- 威力：85
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，敌方获得1层冻结。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "FREEZE",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 236. 冰晶坠

- 数据库 ID：236
- 系别：冰
- 类型：物攻
- 能耗：4
- 威力：90
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，敌方获得全技能能耗+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "enemy",
          "stat": "cost",
          "value": 1
        }
      }
    ]
  }
]
```

### 237. 冰雹

- 数据库 ID：237
- 系别：冰
- 类型：物攻
- 能耗：4
- 威力：105
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，应对状态：额外使敌方获得全技能能耗+3。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "enemy",
          "stat": "cost",
          "value": 3
        }
      },
      {
        "type": "ENEMY_ENERGY_COST_UP",
        "params": {
          "amount": 3,
          "filter": "all"
        }
      }
    ]
  }
]
```

### 238. 极寒领域

- 数据库 ID：238
- 系别：冰
- 类型：魔攻
- 能耗：6
- 威力：105
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，若敌方有冻结，本次技能威力+60，应对状态：使冻结翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 239. 冰冻光线

- 数据库 ID：239
- 系别：冰
- 类型：魔攻
- 能耗：7
- 威力：90
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，敌方获得全技能能耗+2。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "enemy",
          "stat": "cost",
          "value": 2
        }
      }
    ]
  }
]
```

### 240. 霜降

- 数据库 ID：240
- 系别：冰
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得4层冻结。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "FREEZE",
        "params": {
          "stacks": 4
        }
      }
    ]
  }
]
```

### 241. 瞬间零度

- 数据库 ID：241
- 系别：冰
- 类型：状态
- 能耗：0
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：本回合敌方使用的技能能耗+3，应对防御：改为全技能能耗+3。

**实现**

```json
[
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "ENEMY_ENERGY_COST_UP",
        "params": {
          "amount": 3,
          "filter": "all"
        }
      }
    ]
  }
]
```

### 242. 雾气环绕

- 数据库 ID：242
- 系别：冰
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：回复能量，回复值等于敌方技能总能耗的一半。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "HEAL_ENERGY",
        "params": {
          "amount": 0,
          "per": "enemy_total_cost_half"
        }
      }
    ]
  }
]
```

### 243. 霜天

- 数据库 ID：243
- 系别：冰
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得1层冻结，且每有1层冻结获得全技能能耗+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "FREEZE",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 244. 冰天雪地

- 数据库 ID：244
- 系别：冰
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：被应对技能能耗+3。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 245. 冰墙

- 数据库 ID：245
- 系别：冰
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：敌方获得2层冻结。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 246. 冰锥

- 数据库 ID：246
- 系别：冰
- 类型：物攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 247. 冷风

- 数据库 ID：247
- 系别：冰
- 类型：魔攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 248. 冰爪

- 数据库 ID：248
- 系别：冰
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 249. 打雪仗

- 数据库 ID：249
- 系别：冰
- 类型：魔攻
- 能耗：3
- 威力：45
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，2连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 250. 滚雪球

- 数据库 ID：250
- 系别：冰
- 类型：物攻
- 能耗：3
- 威力：55
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，敌方获得2层冻结，应对状态：额外获得2层，本次技能威力翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "FREEZE",
        "params": {
          "stacks": 2
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "counter",
          "multiplier": 2.0
        }
      }
    ]
  }
]
```

### 251. 丢冰块

- 数据库 ID：251
- 系别：冰
- 类型：物攻
- 能耗：3
- 威力：90
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，敌方获得速度-30。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 252. 寒风吹

- 数据库 ID：252
- 系别：冰
- 类型：魔攻
- 能耗：3
- 威力：70
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，敌方获得魔防-50%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "spdef": 0.5
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 253. 雪球

- 数据库 ID：253
- 系别：冰
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得速度-90。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "timing": "ON_USE",
        "effects": [
          {
            "type": "SELF_BUFF",
            "params": {
              "speed": -0.9
            }
          }
        ]
      }
    ]
  }
]
```

### 254. 碎冰冰

- 数据库 ID：254
- 系别：冰
- 类型：魔攻
- 能耗：3
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，敌方每有1层冻结，本次技能威力+20。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "FREEZE",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 255. 冰捆缚

- 数据库 ID：255
- 系别：冰
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：2连击，每次连击敌方获得全技能能耗+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "enemy",
          "stat": "cost",
          "value": 1
        }
      },
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "hit_count",
          "value": 2
        }
      }
    ]
  }
]
```

### 256. 速冻

- 数据库 ID：256
- 系别：冰
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：敌方获得2层减速印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SLOW_MARK",
        "params": {
          "stacks": 2
        }
      }
    ]
  }
]
```

### 257. 冰蛋壳

- 数据库 ID：257
- 系别：冰
- 类型：防御
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤60%，应对攻击：敌方获得2层减速印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.6
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "SLOW_MARK",
        "params": {
          "stacks": 2
        }
      }
    ]
  }
]
```

### 258. 雪替身

- 数据库 ID：258
- 系别：冰
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤70%，应对攻击：回复能量，回复值等于被应对技能能耗的2倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 259. 冬至

- 数据库 ID：259
- 系别：冰
- 类型：状态
- 能耗：7
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：将天气改为暴风雪，持续8回合。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "WEATHER",
        "params": {
          "turns": 8,
          "type": "snow"
        }
      }
    ]
  }
]
```

### 260. 霜冻

- 数据库 ID：260
- 系别：冰
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得魔防-100%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "spdef": 1.0
        }
      }
    ]
  }
]
```

### 261. 冰点

- 数据库 ID：261
- 系别：冰
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得5层冻结，应对防御：额外获得5层。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "FREEZE",
        "params": {
          "stacks": 5
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": []
  }
]
```

### 262. 龙吼

- 数据库 ID：262
- 系别：龙
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 263. 吹炎

- 数据库 ID：263
- 系别：龙
- 类型：物攻
- 能耗：3
- 威力：170
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：蓄力，造成物伤，应对状态：本次技能威力翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "counter",
          "multiplier": 2.0
        }
      }
    ]
  }
]
```

### 264. 怨力打击

- 数据库 ID：264
- 系别：龙
- 类型：魔攻
- 能耗：3
- 威力：1
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：蓄力，造成魔伤，若蓄力期间受到攻击，本技能威力变为敌方技能威力的3倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 265. 升龙咆哮

- 数据库 ID：265
- 系别：龙
- 类型：魔攻
- 能耗：3
- 威力：200
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：蓄力，对敌方造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 266. 龙之利爪

- 数据库 ID：266
- 系别：龙
- 类型：物攻
- 能耗：3
- 威力：130
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：蓄力，造成物伤并吸血50%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_HIT",
    "effects": [
      {
        "type": "LIFE_DRAIN",
        "params": {
          "pct": 0.5
        }
      }
    ]
  }
]
```

### 267. 龙吟

- 数据库 ID：267
- 系别：龙
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：蓄力，自己获得双攻+100%和速度+60。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 1.0,
          "spatk": 1.0,
          "speed": 0.6
        }
      }
    ]
  }
]
```

### 268. 架势

- 数据库 ID：268
- 系别：龙
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己回复20%生命，下次技能无需蓄力。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "timing": "ON_USE",
        "effects": [
          {
            "type": "HEAL_HP",
            "params": {
              "pct": 0.2
            }
          }
        ]
      }
    ]
  }
]
```

### 269. 龙爪

- 数据库 ID：269
- 系别：龙
- 类型：物攻
- 能耗：4
- 威力：120
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 270. 龙息环爆

- 数据库 ID：270
- 系别：龙
- 类型：魔攻
- 能耗：1
- 威力：55
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，应对状态：下次技能无需蓄力。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 271. 角击

- 数据库 ID：271
- 系别：龙
- 类型：魔攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 272. 龙炮

- 数据库 ID：272
- 系别：龙
- 类型：物攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 273. 隼鳞

- 数据库 ID：273
- 系别：龙
- 类型：物攻
- 能耗：5
- 威力：140
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 274. 龙威

- 数据库 ID：274
- 系别：龙
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得1层龙噬印记 。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DRAGON_MARK",
        "params": {
          "stacks": 1,
          "target": "self"
        }
      }
    ]
  }
]
```

### 275. 龙血

- 数据库 ID：275
- 系别：龙
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤70%，本技能可以在蓄力状态下使用，应对攻击：下次技能无需蓄力。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 276. 绵里藏针

- 数据库 ID：276
- 系别：龙
- 类型：魔攻
- 能耗：2
- 威力：50
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，若敌方上回合没受到技能伤害，本技能威力永久+30。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 30,
          "trigger": "per_enemy_no_damage_last_turn"
        }
      }
    ]
  }
]
```

### 277. 导电撞击

- 数据库 ID：277
- 系别：电
- 类型：物攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 278. 电弧

- 数据库 ID：278
- 系别：电
- 类型：物攻
- 能耗：3
- 威力：80
- 标记：迸发
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，迸发：本次技能威力+40。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 279. 触电

- 数据库 ID：279
- 系别：电
- 类型：魔攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 280. 超导

- 数据库 ID：280
- 系别：电
- 类型：魔攻
- 能耗：3
- 威力：95
- 标记：迸发
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，迸发：本技能能耗-1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 281. 引雷

- 数据库 ID：281
- 系别：电
- 类型：魔攻
- 能耗：3
- 威力：35
- 标记：迸发
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，2连击，迸发：本次技能威力+20。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 282. 闪击折返

- 数据库 ID：282
- 系别：电
- 类型：物攻
- 能耗：5
- 威力：45
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，2连击，自己脱离。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "FORCE_SWITCH"
      }
    ]
  }
]
```

### 283. 落雷

- 数据库 ID：283
- 系别：电
- 类型：魔攻
- 能耗：4
- 威力：100
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，每次入场，本技能威力永久+20。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "power",
          "delta": 20,
          "trigger": "per_entry"
        }
      }
    ]
  }
]
```

### 284. 雷暴

- 数据库 ID：284
- 系别：电
- 类型：魔攻
- 能耗：1
- 威力：55
- 标记：迸发
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，迸发：本技能获得所有生效过的迸发，每获得1种，本技能能耗+1，威力+10。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 285. 麻痹

- 数据库 ID：285
- 系别：电
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方先手-1，应对防御：额外使敌方获得双攻-70%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "enemy",
          "stat": "priority",
          "value": -1
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "atk": 0.7,
          "spatk": 0.7
        }
      }
    ]
  }
]
```

### 286. 增程电池

- 数据库 ID：286
- 系别：电
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得1层蓄电印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "CHARGE_MARK",
        "params": {
          "stacks": 1,
          "target": "self"
        }
      }
    ]
  }
]
```

### 287. 加大功率

- 数据库 ID：287
- 系别：电
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己脱离，替换入场的精灵回复8能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "FORCE_SWITCH"
      }
    ]
  }
]
```

### 288. 集中

- 数据库 ID：288
- 系别：电
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：自己回合结束返场。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 289. 电流

- 数据库 ID：289
- 系别：电
- 类型：魔攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 290. 球状闪电

- 数据库 ID：290
- 系别：电
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 291. 磁干扰

- 数据库 ID：291
- 系别：电
- 类型：魔攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 292. 离子火花

- 数据库 ID：292
- 系别：电
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 293. 交叉闪电

- 数据库 ID：293
- 系别：电
- 类型：物攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 294. 超导加速

- 数据库 ID：294
- 系别：电
- 类型：魔攻
- 能耗：2
- 威力：70
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，自己获得速度+30。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "speed": 0.3
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 295. 双联脉冲

- 数据库 ID：295
- 系别：电
- 类型：魔攻
- 能耗：4
- 威力：50
- 标记：迸发
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，迸发：本技能使用次数+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 296. 过载回路

- 数据库 ID：296
- 系别：电
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：回合结束自己返场，下回合所选技能使用次数+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "FORCE_SWITCH"
      }
    ]
  }
]
```

### 297. 远程访问

- 数据库 ID：297
- 系别：电
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：使敌方精灵返场。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "FORCE_ENEMY_SWITCH"
      }
    ]
  }
]
```

### 298. 感电

- 数据库 ID：298
- 系别：电
- 类型：魔攻
- 能耗：2
- 威力：60
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，每离场1次，本技能使用次数永久+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 299. 强制重启

- 数据库 ID：299
- 系别：电
- 类型：魔攻
- 能耗：3
- 威力：90
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，应对状态：回合结束时使敌方精灵返场。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 300. 电离爆破

- 数据库 ID：300
- 系别：电
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得速度-40，3连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "hit_count",
          "value": 3
        }
      }
    ]
  }
]
```

### 301. 电磁偏转

- 数据库 ID：301
- 系别：电
- 类型：防御
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤70%，应对攻击：下回合所选技能使用次数+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 302. 毒针

- 数据库 ID：302
- 系别：毒
- 类型：物攻
- 能耗：0
- 威力：20
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，敌方获得1层中毒。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "POISON",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 303. 腐蚀酸液

- 数据库 ID：303
- 系别：毒
- 类型：魔攻
- 能耗：2
- 威力：35
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，敌方获得2层中毒。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "POISON",
        "params": {
          "stacks": 2
        }
      }
    ]
  }
]
```

### 304. 连续毒针

- 数据库 ID：304
- 系别：毒
- 类型：物攻
- 能耗：2
- 威力：15
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，2连击，每次连击使敌方获得1层中毒。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "POISON",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 305. 毒囊

- 数据库 ID：305
- 系别：毒
- 类型：物攻
- 能耗：2
- 威力：25
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，敌方获得2层中毒，应对状态：改为获得6层。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "POISON",
        "params": {
          "stacks": 2
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "COUNTER_OVERRIDE",
        "params": {
          "replace": "poison",
          "from": 2,
          "to": 6
        }
      }
    ]
  }
]
```

### 306. 毒液渗透

- 数据库 ID：306
- 系别：毒
- 类型：魔攻
- 能耗：5
- 威力：120
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，敌方每有1层中毒效果，本技能能耗-1，敌方获得1层中毒。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "ENERGY_COST_DYNAMIC",
        "params": {
          "per": "enemy_poison",
          "reduce": 1
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "POISON",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 307. 感染病

- 数据库 ID：307
- 系别：毒
- 类型：魔攻
- 能耗：4
- 威力：85
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，若击败敌方则将中毒转化为中毒印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_HIT",
    "filter": {
      "on_kill": true
    },
    "effects": [
      {
        "type": "CONVERT_POISON_TO_MARK",
        "params": {
          "on": "kill"
        }
      }
    ]
  }
]
```

### 308. 毒孢子

- 数据库 ID：308
- 系别：毒
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得5层中毒。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "POISON",
        "params": {
          "stacks": 5
        }
      }
    ]
  }
]
```

### 309. 毒雾

- 数据库 ID：309
- 系别：毒
- 类型：状态
- 能耗：7
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：将敌方所有增益，转化成中毒。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "CONVERT_BUFF_TO_POISON"
      }
    ]
  }
]
```

### 310. 剧毒

- 数据库 ID：310
- 系别：毒
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得3层中毒，应对防御：改为获得8层。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "POISON",
        "params": {
          "stacks": 3
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": []
  }
]
```

### 311. 以毒攻毒

- 数据库 ID：311
- 系别：毒
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：敌方每有1层中毒效果，自己获得魔攻+30%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "CONDITIONAL_BUFF",
        "params": {
          "condition": "per_enemy_poison",
          "buff": {
            "spatk": 0.3
          }
        }
      }
    ]
  }
]
```

### 312. 落井下毒

- 数据库 ID：312
- 系别：毒
- 类型：状态
- 能耗：6
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：使敌方精灵减益的层数翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "double_enemy_debuffs"
        }
      }
    ]
  }
]
```

### 313. 毒泡泡

- 数据库 ID：313
- 系别：毒
- 类型：魔攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 314. 溃烂触碰

- 数据库 ID：314
- 系别：毒
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 315. 毒沼

- 数据库 ID：315
- 系别：毒
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 316. 瘴气喷射

- 数据库 ID：316
- 系别：毒
- 类型：魔攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 317. 鸩毒

- 数据库 ID：317
- 系别：毒
- 类型：魔攻
- 能耗：3
- 威力：75
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，敌方每有1层中毒效果，本次技能威力+10，应对状态：改为本次威力+20。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "POISON",
        "params": {
          "stacks": 1
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 318. 腐化

- 数据库 ID：318
- 系别：毒
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方每有1层中毒效果，敌方获得双攻-30%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "atk": 0.3,
          "spatk": 0.3
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "POISON",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 319. 疫病吐息

- 数据库 ID：319
- 系别：毒
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：敌方获得1层中毒印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "POISON_MARK",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 320. 不可接触

- 数据库 ID：320
- 系别：毒
- 类型：防御
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤50%，敌方每有1层中毒效果，本技能减伤+10%，应对攻击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.5
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 321. 啃咬

- 数据库 ID：321
- 系别：虫
- 类型：物攻
- 能耗：0
- 威力：40
- 标记：受奉献影响
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，1连击，本技能会受奉献影响，每被影响1次，能耗永久+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 322. 飞断

- 数据库 ID：322
- 系别：虫
- 类型：物攻
- 能耗：1
- 威力：20
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，己方队伍获得1次奉献：威力+20。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "DEVOTION_GRANT",
        "params": {
          "type": "飞断"
        }
      }
    ]
  }
]
```

### 323. 虫群过境

- 数据库 ID：323
- 系别：虫
- 类型：物攻
- 能耗：5
- 威力：45
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，2连击。己方队伍获得1次奉献：获得连击数+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "DEVOTION_GRANT",
        "params": {
          "type": "虫群过境"
        }
      }
    ]
  }
]
```

### 324. 虫群

- 数据库 ID：324
- 系别：虫
- 类型：物攻
- 能耗：7
- 威力：20
- 标记：受奉献影响
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，1连击，本技能会受奉献影响。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 325. 虫网

- 数据库 ID：325
- 系别：虫
- 类型：魔攻
- 能耗：0
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，自己回复1能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 326. 虫击

- 数据库 ID：326
- 系别：虫
- 类型：物攻
- 能耗：3
- 威力：90
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，应对状态：本次技能威力变为2倍，无视敌方系别抵抗。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "counter",
          "multiplier": 2.0
        }
      }
    ]
  }
]
```

### 327. 虫鸣

- 数据库 ID：327
- 系别：虫
- 类型：魔攻
- 能耗：2
- 威力：15
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，队伍中的精灵每携带1个虫鸣，本次技能连击数+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 328. 捆缚

- 数据库 ID：328
- 系别：虫
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：敌方获得2层中毒，获得1次奉献：敌方获得2层中毒。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "POISON",
        "params": {
          "stacks": 2
        }
      },
      {
        "type": "DEVOTION_GRANT",
        "params": {
          "type": "捆缚"
        }
      }
    ]
  }
]
```

### 329. 假寐

- 数据库 ID：329
- 系别：虫
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己回复2能量，己方队伍获得1次奉献：能耗-2。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "HEAL_ENERGY",
        "params": {
          "amount": 2
        }
      },
      {
        "type": "DEVOTION_GRANT",
        "params": {
          "type": "假寐"
        }
      }
    ]
  }
]
```

### 330. 虫茧

- 数据库 ID：330
- 系别：虫
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己回复20%生命，己方队伍获得1次奉献：获得10%吸血。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "HEAL_HP",
        "params": {
          "pct": 0.2
        }
      },
      {
        "type": "DEVOTION_GRANT",
        "params": {
          "type": "虫茧"
        }
      }
    ]
  }
]
```

### 331. 虫群智慧

- 数据库 ID：331
- 系别：虫
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：己方队伍获得2次随机奉献。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "grant_random_devotion",
          "count": 2
        }
      }
    ]
  }
]
```

### 332. 贮藏

- 数据库 ID：332
- 系别：虫
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得双攻+50%，每携带1个0能耗技能，额外+50%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 0.5,
          "spatk": 0.5
        }
      }
    ]
  }
]
```

### 333. 掩护

- 数据库 ID：333
- 系别：虫
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤70%，紧急脱离，应对攻击：下个入场精灵获得减伤。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      },
      {
        "type": "FORCE_SWITCH"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 334. 蛰针

- 数据库 ID：334
- 系别：虫
- 类型：物攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 335. 虫刺

- 数据库 ID：335
- 系别：虫
- 类型：魔攻
- 能耗：1
- 威力：15
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，3连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 336. 噬心

- 数据库 ID：336
- 系别：虫
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 337. 尾后针

- 数据库 ID：337
- 系别：虫
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 338. 虫蛊

- 数据库 ID：338
- 系别：虫
- 类型：魔攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 339. 翅刃

- 数据库 ID：339
- 系别：虫
- 类型：物攻
- 能耗：4
- 威力：95
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，驱散敌方所有印记，应对状态：改为偷取印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "DISPEL_ENEMY_MARKS"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "STEAL_MARKS"
      }
    ]
  }
]
```

### 340. 网缚

- 数据库 ID：340
- 系别：虫
- 类型：物攻
- 能耗：2
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，敌方获得物防-30%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "def": 0.3
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 341. 食腐

- 数据库 ID：341
- 系别：虫
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：驱散敌方印记，每层印记回复自己10%生命。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "CONSUME_MARKS_HEAL",
        "params": {
          "heal_pct_per_mark": 0.1
        }
      }
    ]
  }
]
```

### 342. 虫结阵

- 数据库 ID：342
- 系别：虫
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：己方队伍获得1次随机奉献。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 343. 草虫冲击

- 数据库 ID：343
- 系别：虫
- 类型：物攻
- 能耗：3
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，若敌方本回合更换精灵，本次威力+50且无视敌方系别抵抗。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 344. 寸拳

- 数据库 ID：344
- 系别：武
- 类型：物攻
- 能耗：0
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，自己回复1能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 345. 崩拳

- 数据库 ID：345
- 系别：武
- 类型：物攻
- 能耗：2
- 威力：65
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，应对状态：自己获得物攻+100%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 1.0
        }
      }
    ]
  }
]
```

### 346. 散手

- 数据库 ID：346
- 系别：武
- 类型：物攻
- 能耗：3
- 威力：35
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，2连击，应对状态：本技能改为6连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 347. 无影脚

- 数据库 ID：347
- 系别：武
- 类型：物攻
- 能耗：3
- 威力：85
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，应对状态：本次技能威力变为2倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "counter",
          "multiplier": 2.0
        }
      }
    ]
  }
]
```

### 348. 斩断

- 数据库 ID：348
- 系别：武
- 类型：物攻
- 能耗：2
- 威力：75
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，应对状态：额外打断被应对技能。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "INTERRUPT"
      }
    ]
  }
]
```

### 349. 反击拳

- 数据库 ID：349
- 系别：武
- 类型：物攻
- 能耗：2
- 威力：25
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，2连击，若后手攻击，改为3连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 350. 技巧打击

- 数据库 ID：350
- 系别：武
- 类型：物攻
- 能耗：2
- 威力：35
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，应对状态：本次技能威力变为10倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "counter",
          "multiplier": 10.0
        }
      }
    ]
  }
]
```

### 351. 截拳

- 数据库 ID：351
- 系别：武
- 类型：物攻
- 能耗：3
- 威力：90
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，应对状态：额外造成打断，回复该技能能耗的能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "INTERRUPT"
      }
    ]
  }
]
```

### 352. 化劲

- 数据库 ID：352
- 系别：武
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得全技能威力+40。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "power_pct",
          "value": 0.4
        }
      }
    ]
  }
]
```

### 353. 破绽

- 数据库 ID：353
- 系别：武
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得双防-70%，应对防御：自己额外获得物攻+70%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "spdef": 0.7,
          "def": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 0.7
        }
      }
    ]
  }
]
```

### 354. 破防

- 数据库 ID：354
- 系别：武
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得双防-130%，应对防御：额外使被应对技能冷却2回合。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "spdef": 1.3,
          "def": 1.3
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": []
  }
]
```

### 355. 气沉丹田

- 数据库 ID：355
- 系别：武
- 类型：状态
- 能耗：10
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己回复60%生命，获得物攻+130%，每次应对后本技能能耗-3，使用后能耗重置。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "HEAL_HP",
        "params": {
          "pct": 0.6
        }
      },
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 1.3
        }
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "RESET_SKILL_COST"
      }
    ]
  }
]
```

### 356. 硬门

- 数据库 ID：356
- 系别：武
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：应对攻击：打断被应对技能，并造成90威力物伤。

**实现**

```json
[
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "INTERRUPT"
      }
    ]
  }
]
```

### 357. 听桥

- 数据库 ID：357
- 系别：武
- 类型：防御
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤60%，应对攻击：对敌方造成物理伤害，威力与被应对技能相等。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.6
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "MIRROR_DAMAGE",
        "params": {
          "source": "countered_skill"
        }
      }
    ]
  }
]
```

### 358. 气波

- 数据库 ID：358
- 系别：武
- 类型：魔攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 359. 爆冲

- 数据库 ID：359
- 系别：武
- 类型：物攻
- 能耗：3
- 威力：65
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，应对状态：本次技能威力变为5倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "counter",
          "multiplier": 5.0
        }
      }
    ]
  }
]
```

### 360. 缠丝劲

- 数据库 ID：360
- 系别：武
- 类型：物攻
- 能耗：1
- 威力：25
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，2连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 361. 贯手

- 数据库 ID：361
- 系别：武
- 类型：魔攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 362. 影袭

- 数据库 ID：362
- 系别：武
- 类型：物攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 363. 一拳

- 数据库 ID：363
- 系别：武
- 类型：物攻
- 能耗：5
- 威力：140
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 364. 叠势

- 数据库 ID：364
- 系别：武
- 类型：魔攻
- 能耗：3
- 威力：25
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，2连击，每成功应对1次，本技能连击数永久+2。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "hit_count",
          "delta": 2,
          "trigger": "per_counter"
        }
      }
    ]
  }
]
```

### 365. 提气

- 数据库 ID：365
- 系别：武
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得全技能威力+40，若敌方本回合更换精灵，额外获得威力+50。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "power_pct",
          "value": 0.4
        }
      }
    ]
  }
]
```

### 366. 预备势

- 数据库 ID：366
- 系别：武
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得物攻+80%，应对防御：额外使敌方获得物防-80%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "ENEMY_DEBUFF",
        "params": {
          "def": 0.8
        }
      }
    ]
  }
]
```

### 367. 防御反击

- 数据库 ID：367
- 系别：武
- 类型：防御
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：自己获得全技能威力+40。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "power_pct",
          "value": 0.4
        }
      }
    ]
  }
]
```

### 368. 回旋踢

- 数据库 ID：368
- 系别：武
- 类型：物攻
- 能耗：3
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，若敌方本回合更换精灵，本次技能威力翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 369. 啄击

- 数据库 ID：369
- 系别：翼
- 类型：物攻
- 能耗：0
- 威力：15
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，2连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 370. 扇风

- 数据库 ID：370
- 系别：翼
- 类型：物攻
- 能耗：3
- 威力：75
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，若先于敌方攻击，本次技能威力+50%。

**实现**

```json
[
  {
    "timing": "IF",
    "filter": {
      "first_strike": true
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "first_strike",
          "bonus_pct": 0.5
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 371. 翼击

- 数据库 ID：371
- 系别：翼
- 类型：魔攻
- 能耗：3
- 威力：50
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，迅捷。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "AGILITY"
      },
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 372. 疾风刺

- 数据库 ID：372
- 系别：翼
- 类型：物攻
- 能耗：2
- 威力：25
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，1连击，若先于敌方攻击，改为3连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 373. 龙卷风

- 数据库 ID：373
- 系别：翼
- 类型：物攻
- 能耗：5
- 威力：70
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，迅捷，应对状态：本次技能威力变为1.5倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "AGILITY"
      },
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 374. 乘风

- 数据库 ID：374
- 系别：翼
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得速度+120。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "speed": 1.2
        }
      }
    ]
  }
]
```

### 375. 风起

- 数据库 ID：375
- 系别：翼
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得1层风起印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "WIND_MARK",
        "params": {
          "stacks": 1,
          "target": "self"
        }
      }
    ]
  }
]
```

### 376. 暴风眼

- 数据库 ID：376
- 系别：翼
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：行动时连击数+100%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "hit_count_double",
          "value": 1
        }
      }
    ]
  }
]
```

### 377. 风墙

- 数据库 ID：377
- 系别：翼
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤50%，迅捷，应对攻击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.5
        }
      },
      {
        "type": "AGILITY"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 378. 鸣叫

- 数据库 ID：378
- 系别：翼
- 类型：魔攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 379. 鹰爪

- 数据库 ID：379
- 系别：翼
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 380. 羽刃

- 数据库 ID：380
- 系别：翼
- 类型：物攻
- 能耗：2
- 威力：75
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，应对状态：回合结束使敌方紧急脱离。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "FORCE_ENEMY_SWITCH"
      }
    ]
  }
]
```

### 381. 风矢

- 数据库 ID：381
- 系别：翼
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 382. 回旋风暴

- 数据库 ID：382
- 系别：翼
- 类型：魔攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 383. 俯冲猛击

- 数据库 ID：383
- 系别：翼
- 类型：物攻
- 能耗：5
- 威力：140
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 384. 闪击

- 数据库 ID：384
- 系别：翼
- 类型：物攻
- 能耗：4
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，速度比敌方越高，本次技能威力越高。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 385. 飞羽

- 数据库 ID：385
- 系别：翼
- 类型：状态
- 能耗：0
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：迅捷，驱散敌方1种增益。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "AGILITY"
      }
    ]
  }
]
```

### 386. 风隐

- 数据库 ID：386
- 系别：翼
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方和自己均脱离，先手-1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "timing": "ON_USE",
        "effects": [
          {
            "type": "FORCE_SWITCH"
          }
        ]
      }
    ]
  }
]
```

### 387. 羽化加速

- 数据库 ID：387
- 系别：翼
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得全技能威力+20，迅捷。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "AGILITY"
      },
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "power_pct",
          "value": 0.2
        }
      }
    ]
  }
]
```

### 388. 羽翼庇护

- 数据库 ID：388
- 系别：翼
- 类型：防御
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤70%，应对攻击：自己获得连击数+3。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 389. 疾风连袭

- 数据库 ID：389
- 系别：翼
- 类型：状态
- 能耗：0
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：释放自己释放过的迅捷技能，其能耗之和的二分之一加至本技能能耗，每次使用后能耗+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "REPLAY_AGILITY"
      },
      {
        "type": "AGILITY_COST_SHARE",
        "params": {
          "divisor": 2
        }
      }
    ]
  },
  {
    "timing": "POST_USE",
    "effects": [
      {
        "type": "ENERGY_COST_ACCUMULATE",
        "params": {
          "delta": 1
        }
      }
    ]
  }
]
```

### 390. 飞吻

- 数据库 ID：390
- 系别：萌
- 类型：魔攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 391. 超级糖果

- 数据库 ID：391
- 系别：萌
- 类型：物攻
- 能耗：3
- 威力：100
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，自己获得萌化：本次技能威力+60。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "CUTE_IF_POWER_BONUS",
        "params": {
          "bonus": 60
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "CUTE_GAIN",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 392. 砂糖弹球

- 数据库 ID：392
- 系别：萌
- 类型：物攻
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，双方体重差越大，本次技能威力越高。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 393. 生日蛋糕

- 数据库 ID：393
- 系别：萌
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：驱散自己的减益，自己的增益翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "CUTE_ON_GAIN_COST_REDUCE",
        "params": {
          "stacks": 1,
          "reduce": 4
        }
      }
    ]
  }
]
```

### 394. 示弱

- 数据库 ID：394
- 系别：萌
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得萌化：速度永久+150。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "CUTE_ON_GAIN_SPEED_PERM",
        "params": {
          "stacks": 1,
          "speed": 150
        }
      }
    ]
  }
]
```

### 395. 赤子之心

- 数据库 ID：395
- 系别：萌
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得萌化：全技能能耗永久-3。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "CUTE_ALL_BENCH",
        "params": {
          "stacks": 1
        }
      },
      {
        "type": "HEAL_HP",
        "params": {
          "pct": 0.4
        }
      },
      {
        "type": "HEAL_ENERGY",
        "params": {
          "amount": 4
        }
      }
    ]
  }
]
```

### 396. 反弹

- 数据库 ID：396
- 系别：萌
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：将自己的萌化转移给敌方。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "CUTE_TRANSFER"
      }
    ]
  }
]
```

### 397. 甜心续航

- 数据库 ID：397
- 系别：萌
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己和敌方获得萌化：回复40%生命和4能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "CUTE_BOTH",
        "params": {
          "stacks": 1
        }
      },
      {
        "type": "HEAL_HP",
        "params": {
          "pct": 0.4
        }
      },
      {
        "type": "HEAL_ENERGY",
        "params": {
          "amount": 4
        }
      }
    ]
  }
]
```

### 398. 破罐破摔

- 数据库 ID：398
- 系别：萌
- 类型：魔攻
- 能耗：3
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，自己有减益时，本次技能威力+60。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 399. 鞭打

- 数据库 ID：399
- 系别：萌
- 类型：物攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 400. 魅惑

- 数据库 ID：400
- 系别：萌
- 类型：魔攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 401. 碰爪

- 数据库 ID：401
- 系别：萌
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 402. 撒娇

- 数据库 ID：402
- 系别：萌
- 类型：魔攻
- 能耗：3
- 威力：30
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，3连击。自己获得萌化：威力永久+20。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "CUTE_ON_GAIN_POWER_PERM",
        "params": {
          "stacks": 1,
          "delta": 20
        }
      }
    ]
  }
]
```

### 403. 爆米花爆破

- 数据库 ID：403
- 系别：萌
- 类型：物攻
- 能耗：5
- 威力：140
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 404. 击鼓传花

- 数据库 ID：404
- 系别：萌
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己脱离，下个入场精灵继承自己增益。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "FORCE_SWITCH"
      }
    ]
  }
]
```

### 405. 月光合奏

- 数据库 ID：405
- 系别：萌
- 类型：物攻
- 能耗：3
- 威力：30
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，1连击，双方携带的所有精灵每有1层萌化，本次技能连击数+1。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "CUTE_TEAM_POWER"
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 406. 捧杀

- 数据库 ID：406
- 系别：萌
- 类型：防御
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤90%，应对攻击：敌方获得1层萌化。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.9
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "CUTE_ENEMY_GAIN",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 407. 鬼火

- 数据库 ID：407
- 系别：幽
- 类型：魔攻
- 能耗：0
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，自己回复1能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 408. 惊吓盒子

- 数据库 ID：408
- 系别：幽
- 类型：物攻
- 能耗：3
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，应对状态：使敌方失去6能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 409. 背袭

- 数据库 ID：409
- 系别：幽
- 类型：魔攻
- 能耗：2
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，若敌方能量等于0，造成20倍伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 410. 坟场搏击

- 数据库 ID：410
- 系别：幽
- 类型：物攻
- 能耗：4
- 威力：180
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，敌方每有1能量，本次技能威力-10%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 411. 恶作剧

- 数据库 ID：411
- 系别：幽
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方失去3能量，应对防御：改为敌方失去6能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ENEMY_LOSE_ENERGY",
        "params": {
          "amount": 3
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": []
  }
]
```

### 412. 降灵

- 数据库 ID：412
- 系别：幽
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：敌方获得1层降灵印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SPIRIT_MARK",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 413. 报复

- 数据库 ID：413
- 系别：幽
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤70%，应对攻击：敌方失去3能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 414. 恐吓

- 数据库 ID：414
- 系别：幽
- 类型：魔攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 415. 幽灵爆发

- 数据库 ID：415
- 系别：幽
- 类型：魔攻
- 能耗：5
- 威力：140
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 416. 诡刺

- 数据库 ID：416
- 系别：幽
- 类型：物攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 417. 幻象

- 数据库 ID：417
- 系别：幽
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 418. 午夜噪音

- 数据库 ID：418
- 系别：幽
- 类型：魔攻
- 能耗：4
- 威力：20
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，5连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 419. 灵媒

- 数据库 ID：419
- 系别：幽
- 类型：魔攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 420. 灵光

- 数据库 ID：420
- 系别：幽
- 类型：魔攻
- 能耗：3
- 威力：25
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，3连击，若敌方本回合更换精灵，本次技能连击数翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 421. 嘲弄

- 数据库 ID：421
- 系别：幽
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：自己获得魔攻+90%，若敌方本回合更换精灵，自己获得速度+70。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "spatk": 0.7
        }
      }
    ]
  },
  {
    "timing": "IF",
    "filter": {
      "enemy_switch": true
    },
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "speed": 0.7
        }
      }
    ]
  }
]
```

### 422. 勾魂

- 数据库 ID：422
- 系别：幽
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：偷取敌方3能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "STEAL_ENERGY",
        "params": {
          "amount": 3
        }
      }
    ]
  }
]
```

### 423. 虚化

- 数据库 ID：423
- 系别：幽
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：自己获得魔防+70%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "spdef": 0.7
        }
      }
    ]
  }
]
```

### 424. 魔爪

- 数据库 ID：424
- 系别：恶
- 类型：物攻
- 能耗：0
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，自己回复1能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 425. 恶能量

- 数据库 ID：425
- 系别：恶
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 426. 蝙蝠

- 数据库 ID：426
- 系别：恶
- 类型：物攻
- 能耗：2
- 威力：65
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，并吸血100%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "LIFE_DRAIN",
        "params": {
          "pct": 1.0
        }
      }
    ]
  }
]
```

### 427. 撕裂

- 数据库 ID：427
- 系别：恶
- 类型：物攻
- 能耗：3
- 威力：85
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，应对状态：本次攻击吸血100%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "LIFE_DRAIN",
        "params": {
          "pct": 1.0
        }
      }
    ]
  }
]
```

### 428. 撕咬

- 数据库 ID：428
- 系别：恶
- 类型：物攻
- 能耗：3
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，3连击，若自己的生命低于50%，本次技能连击数+2。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "IF",
    "filter": {
      "self_hp_below": 0.5
    },
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "current_hit_count",
          "value": 2,
          "condition": "self_hp_below",
          "threshold": 0.5
        }
      }
    ]
  }
]
```

### 429. 暗突袭

- 数据库 ID：429
- 系别：恶
- 类型：物攻
- 能耗：4
- 威力：70
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，吸血50%，应对状态：本次技能威力翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_HIT",
    "effects": [
      {
        "type": "LIFE_DRAIN",
        "params": {
          "pct": 0.5
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "POWER_DYNAMIC",
        "params": {
          "condition": "counter",
          "multiplier": 2.0
        }
      }
    ]
  }
]
```

### 430. 极限撕裂

- 数据库 ID：430
- 系别：恶
- 类型：物攻
- 能耗：4
- 威力：135
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，若生命高于50%，使用后自己获得双攻-50%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "POST_USE",
    "filter": {
      "self_hp_gt": 0.5
    },
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": -0.5,
          "spatk": -0.5
        }
      }
    ]
  }
]
```

### 431. 灾厄

- 数据库 ID：431
- 系别：恶
- 类型：物攻
- 能耗：1
- 威力：150
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对自己造成物伤，应对状态：改为对敌方造成物伤。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 432. 彼岸之手

- 数据库 ID：432
- 系别：恶
- 类型：物攻
- 能耗：10
- 威力：150
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，自己每失去10%生命，本技能能耗-1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 433. 贪婪

- 数据库 ID：433
- 系别：恶
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得100%吸血。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "GRANT_LIFE_DRAIN",
        "params": {
          "pct": 1.0
        }
      }
    ]
  }
]
```

### 434. 力量吞噬

- 数据库 ID：434
- 系别：恶
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得全技能威力-20，自己获得全技能威力+20。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "power_pct",
          "value": 0.2
        }
      },
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "enemy",
          "stat": "power_pct",
          "value": -0.2
        }
      }
    ]
  }
]
```

### 435. 欺诈契约

- 数据库 ID：435
- 系别：恶
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：与敌方交换增益和减益。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "swap_buffs"
        }
      }
    ]
  }
]
```

### 436. 恶意逃离

- 数据库 ID：436
- 系别：恶
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：脱离，应对防御：额外使敌方攻击技能能耗+4。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "FORCE_SWITCH"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": [
      {
        "type": "ENEMY_ENERGY_COST_UP",
        "params": {
          "amount": 6,
          "filter": "attack"
        }
      }
    ]
  }
]
```

### 437. 隐藏条款

- 数据库 ID：437
- 系别：恶
- 类型：状态
- 能耗：8
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：与敌方交换携带的技能。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "swap_skills"
        }
      }
    ]
  }
]
```

### 438. 等价交换

- 数据库 ID：438
- 系别：恶
- 类型：防御
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤90%，应对攻击：自己获得50%吸血。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.9
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": [
      {
        "type": "GRANT_LIFE_DRAIN",
        "params": {
          "pct": 0.5
        }
      }
    ]
  }
]
```

### 439. 恶念交换

- 数据库 ID：439
- 系别：恶
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：与敌方交换生命比例。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "swap_hp_ratio"
        }
      }
    ]
  }
]
```

### 440. 迫害

- 数据库 ID：440
- 系别：恶
- 类型：物攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 441. 掠夺

- 数据库 ID：441
- 系别：恶
- 类型：魔攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 442. 黑手

- 数据库 ID：442
- 系别：恶
- 类型：魔攻
- 能耗：3
- 威力：45
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，2连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 443. 诋毁

- 数据库 ID：443
- 系别：恶
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 444. 栽赃

- 数据库 ID：444
- 系别：恶
- 类型：魔攻
- 能耗：6
- 威力：150
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 445. 跌落

- 数据库 ID：445
- 系别：恶
- 类型：物攻
- 能耗：3
- 威力：120
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成大量物伤，自己获得物攻-50%，应对状态：改为获得物攻+50%。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "atk": 0.5
        }
      }
    ]
  }
]
```

### 446. 牵连

- 数据库 ID：446
- 系别：恶
- 类型：魔攻
- 能耗：4
- 威力：85
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，敌方每有1只力竭精灵，本次技能威力+30。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 447. 暗箱操作

- 数据库 ID：447
- 系别：恶
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：自己获得双攻和双防-100%，应对防御：改为敌方获得双攻和双防-100%。

**实现**

```json
[
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": []
  }
]
```

### 448. 虚假破产

- 数据库 ID：448
- 系别：恶
- 类型：防御
- 能耗：2
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：减伤80%，能量不足时，消耗5%生命代替1能量，应对攻击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```

### 449. 趁火打劫

- 数据库 ID：449
- 系别：恶
- 类型：物攻
- 能耗：3
- 威力：35
- 实现来源：手写实现：src/effect_data.py
- 描述：造成物伤，2连击，若击败敌方，本技能连击数永久+2。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_HIT",
    "filter": {
      "on_kill": true
    },
    "effects": [
      {
        "type": "PERMANENT_MOD",
        "params": {
          "target": "hit_count",
          "delta": 2
        }
      }
    ]
  }
]
```

### 450. 伪造账单

- 数据库 ID：450
- 系别：恶
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：若敌方本回合回复生命，改为失去2倍。先手+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "ABILITY_COMPUTE",
        "params": {
          "action": "anti_heal",
          "multiplier": 2
        }
      }
    ]
  }
]
```

### 451. 念力膨胀

- 数据库 ID：451
- 系别：幻
- 类型：物攻
- 能耗：2
- 威力：80
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 452. 空间压迫

- 数据库 ID：452
- 系别：幻
- 类型：物攻
- 能耗：3
- 威力：70
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，敌方获得1层星陨印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "METEOR",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 453. 坍缩

- 数据库 ID：453
- 系别：幻
- 类型：魔攻
- 能耗：3
- 威力：85
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，若击败敌方，自己获得魔攻+70%。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "SELF_BUFF",
        "params": {
          "spatk": 0.7
        }
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 454. 四维降解

- 数据库 ID：454
- 系别：幻
- 类型：魔攻
- 能耗：7
- 威力：100
- 实现来源：手写实现：src/effect_data.py
- 描述：造成魔伤，敌方每有1层印记，本技能能耗-1。

**实现**

```json
[
  {
    "timing": "PRE_USE",
    "effects": [
      {
        "type": "ENERGY_COST_PER_ENEMY_MARK"
      }
    ]
  },
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 455. 偷师

- 数据库 ID：455
- 系别：幻
- 类型：物攻
- 能耗：0
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成物伤，自己回复1能量。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 456. 多维击打

- 数据库 ID：456
- 系别：幻
- 类型：魔攻
- 能耗：4
- 威力：15
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，1连击，敌方每有1层星陨印记，本次技能连击数+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      },
      {
        "type": "METEOR",
        "params": {
          "stacks": 1
        }
      }
    ]
  }
]
```

### 457. 错乱

- 数据库 ID：457
- 系别：幻
- 类型：魔攻
- 能耗：2
- 威力：65
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，应对状态：敌方获得3层星陨印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "status"
    },
    "effects": []
  }
]
```

### 458. 超维投射

- 数据库 ID：458
- 系别：幻
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得4层星陨印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "METEOR",
        "params": {
          "stacks": 4
        }
      }
    ]
  }
]
```

### 459. 星轨裂变

- 数据库 ID：459
- 系别：幻
- 类型：状态
- 能耗：1
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得2层星陨印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "METEOR",
        "params": {
          "stacks": 2
        }
      }
    ]
  }
]
```

### 460. 星链

- 数据库 ID：460
- 系别：幻
- 类型：状态
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：2连击，每次连击使敌方获得1层星陨印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "METEOR",
        "params": {
          "stacks": 1
        }
      },
      {
        "type": "SKILL_MOD",
        "params": {
          "target": "self",
          "stat": "hit_count",
          "value": 2
        }
      }
    ]
  }
]
```

### 461. 超新星馈赠

- 数据库 ID：461
- 系别：幻
- 类型：状态
- 能耗：2
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得2层星陨印记，每使用1次，赋予的星陨印记层数+1。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "METEOR",
        "params": {
          "stacks": 2
        }
      }
    ]
  }
]
```

### 462. 心灵洞悉

- 数据库 ID：462
- 系别：幻
- 类型：状态
- 能耗：7
- 威力：0
- 实现来源：手写实现：src/effect_data.py
- 描述：敌方获得星陨印记，获得层数等于敌方印记层数。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "MARKS_TO_METEOR"
      }
    ]
  }
]
```

### 463. 二律背反

- 数据库 ID：463
- 系别：幻
- 类型：状态
- 能耗：4
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：敌方获得3层星陨印记，应对防御：额外使敌方星陨印记层数翻倍。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "METEOR",
        "params": {
          "stacks": 3
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "defense"
    },
    "effects": []
  }
]
```

### 464. 粒子对撞

- 数据库 ID：464
- 系别：幻
- 类型：物攻
- 能耗：0
- 威力：40
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 465. 星云漩涡

- 数据库 ID：465
- 系别：幻
- 类型：物攻
- 能耗：1
- 威力：60
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 466. 双星

- 数据库 ID：466
- 系别：幻
- 类型：物攻
- 能耗：3
- 威力：100
- 实现来源：手写实现：src/effect_data.py
- 描述：对敌方精灵造成物理伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 467. 针状物

- 数据库 ID：467
- 系别：幻
- 类型：魔攻
- 能耗：3
- 威力：30
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：造成魔伤，3连击。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 468. 大爆炸

- 数据库 ID：468
- 系别：幻
- 类型：魔攻
- 能耗：3
- 威力：100
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：对敌方精灵造成魔法伤害。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE"
      }
    ]
  }
]
```

### 469. 冥想

- 数据库 ID：469
- 系别：幻
- 类型：防御
- 能耗：3
- 威力：0
- 实现来源：生成实现：src/skill_effects_generated.py
- 描述：减伤80%，应对攻击：敌方获得2层星陨印记。

**实现**

```json
[
  {
    "timing": "ON_USE",
    "effects": [
      {
        "type": "DAMAGE_REDUCTION",
        "params": {
          "pct": 0.8
        }
      }
    ]
  },
  {
    "timing": "ON_COUNTER",
    "filter": {
      "category": "attack"
    },
    "effects": []
  }
]
```
