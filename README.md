# Roco Battle Simulator

一个本地运行的洛克王国资料库、配队仓库与手动对战模拟器。项目当前以图鉴页作为入口，所有常规页面都读取本地数据与本地图片资源，不依赖联网；爬虫只用于主动刷新数据与素材。

项目暂不包含 AI 自动出招或自动配队功能，核心目标是把图鉴、技能、机制、仓库、队伍和对战结算整理成一套可验证、可扩展的本地工具。

## 快速开始

建议使用 Python 3.10 或更新版本。

```bash
cd ~/Desktop/Programming/Github_Project/roco-battle-simulator
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 run_web.py
```

启动后默认打开：

```text
http://localhost:8765/dex
```

Windows 也可以直接运行：

```bat
run.bat
```

## 页面入口

| 路径 | 页面 | 用途 |
| --- | --- | --- |
| `/`、`/dex` | 图鉴 | 精灵列表、图标、编号、系别、种族值、特性描述、可学技能 |
| `/skills` | 技能 | 技能图鉴、技能详情、图标、系别/类型/能耗、可学习精灵 |
| `/mechanics` | 机制 | 印记、状态、关键词、天气等机制解释与关联技能/特性 |
| `/tools` | 工具 | 蛋组查询、孵蛋查询、克制计算器、伤害计算器 |
| `/storage` | 仓库 | 本地精灵个体、性格、个体值、血脉、配招与自定义队伍 |
| `/simulator` | 队伍 | PVP 队伍库、队伍查看、添加与删除 |
| `/battle` | 对战 | 双方手动出招、聚能、换人、首领化/愿力、结构化战报 |

## 主要功能

- 图鉴系统：左侧精灵列表，右侧详情面板；支持不同形态图标、首领形态、系别图标、特性效果、升级技能、技能石技能与血脉技能。
- 技能系统：左侧单列技能列表，右侧技能详情；展示技能图标、系别、分类、能耗、描述，并按升级、技能石、血脉分组列出可学习精灵。
- 机制百科：整理印记、增益状态、负面状态、关键词与天气，关联描述中实际出现该机制的技能和特性，并支持跳转到对应技能或精灵。
- 工具页：包含蛋组查询器、孵蛋范围查询器、克制关系图/计算器和伤害计算器。
- 仓库系统：保存用户配置好的精灵个体，可编辑名字、性格、个体值、血脉、特性和配招，并基于仓库精灵组建队伍。
- 队伍系统：展示本地 PVP 队伍库，支持带入愿力冲击或进化之力，并过滤素材缺失或非法道具队伍。
- 对战系统：手动控制双方行动，支持能量、魔力、换人、聚能、首领进化、愿力冲击、属性免疫、印记覆盖、天气与结构化日志。

## 项目结构

```text
roco-battle-simulator/
├── src/
│   ├── battle.py                  # 核心战斗流程
│   ├── damage_calculator.py       # 伤害计算器与克制计算
│   ├── effect_data.py             # 技能效果配置
│   ├── effect_engine.py           # 技能效果执行
│   ├── models.py                  # 战斗模型
│   ├── pokemon_db.py              # 精灵数据读取
│   ├── skill_db.py                # 技能数据读取
│   ├── team_builder.py            # 队伍构建
│   └── server.py                  # FastAPI 页面与接口
├── web/
│   ├── dex.html
│   ├── skills.html
│   ├── mechanics.html
│   ├── tools.html
│   ├── storage.html
│   ├── simulator.html
│   ├── battle.html
│   └── theme.css
├── data/
│   ├── nrc.db
│   ├── skill_icons/
│   ├── spirit_icons/
│   ├── ability_icons/
│   ├── mechanic_icons/
│   ├── egg_group_avatars/
│   ├── pvp_lineups.json
│   ├── egg_groups.json
│   └── egg_measurements.json
├── scripts/
│   ├── crawlers/                  # 数据与图片爬虫入口
│   ├── build_desktop.py           # PyInstaller 打包脚本
│   └── generate_skill_effects.py
├── tests/
├── docs/
├── run_web.py
├── run_desktop.py
└── requirements.txt
```

## 本地数据与爬虫

常规运行只读取 `data/`、`web/` 和 `src/` 中的本地内容。需要刷新资料或图片时，再手动运行 `scripts/crawlers/` 下的对应脚本。

爬虫入口说明见 [scripts/crawlers/README.md](/Users/hedong/Desktop/Programming/Github_Project/roco-battle-simulator/scripts/crawlers/README.md)。

当前整理出的爬虫包括：

- `skills_biligame.py`：技能图鉴、技能图标、系别/分类/能耗图标
- `spirit_icons.py`：精灵图鉴、不同形态图标与进化信息
- `ability_icons.py`：特性图标
- `pokemon_skills.py`：精灵可学习技能与学习方式
- `mechanics_rocomaster.py`：机制百科文本
- `egg_groups.py`：蛋组分类与头像缩略图
- `hatch_measurements.py`：孵蛋尺寸数据
- `pvp_lineups.py`：PVP 阵容、性格、配招、血脉与队伍描述

## 对战与技能实现文档

- 技能实现总览：[docs/SKILL_IMPLEMENTATIONS.md](/Users/hedong/Desktop/Programming/Github_Project/roco-battle-simulator/docs/SKILL_IMPLEMENTATIONS.md)
- 技能/特性配置说明：[docs/SKILLS_ABILITIES_CONFIG_GUIDE.md](/Users/hedong/Desktop/Programming/Github_Project/roco-battle-simulator/docs/SKILLS_ABILITIES_CONFIG_GUIDE.md)
- 效果逻辑整理：[docs/SKILL_EFFECT_LOGIC.md](/Users/hedong/Desktop/Programming/Github_Project/roco-battle-simulator/docs/SKILL_EFFECT_LOGIC.md)
- 覆盖情况：[docs/COVERAGE_MATRIX.md](/Users/hedong/Desktop/Programming/Github_Project/roco-battle-simulator/docs/COVERAGE_MATRIX.md)

## 常用验证

```bash
PYTHONPATH=. pytest tests/test_will_impact.py tests/test_leader_evolution.py tests/test_damage_calculator_tool.py -q
python3 -m py_compile src/models.py src/battle.py src/server.py src/damage_calculator.py
```

前端页面主要是原生 HTML/CSS/JS。修改页面后建议启动 `run_web.py`，在浏览器中检查对应页面布局和交互。

## 桌面打包

项目可以用 PyInstaller 打成桌面版，本质是启动本地 FastAPI 服务并打开本机浏览器。建议在目标系统上打包：Windows 包在 Windows 上构建，macOS 包在 macOS 上构建。

### Windows 打包

```bat
cd %USERPROFILE%\Desktop\Programming\Github_Project\roco-battle-simulator
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install pyinstaller
python scripts\build_desktop.py --windowed
```

产物默认位于：

```text
dist\洛克模拟器\洛克模拟器.exe
```

### macOS 打包

```bash
cd ~/Desktop/Programming/Github_Project/roco-battle-simulator
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller
python3 scripts/build_desktop.py --windowed
```

产物默认位于：

```text
dist/洛克模拟器.app
```

如果不加 `--windowed`，会生成普通目录包：

```bash
python3 scripts/build_desktop.py
dist/洛克模拟器/洛克模拟器
```

### GitHub Actions 自动打包

仓库内置工作流 [build-desktop.yml](/Users/hedong/Desktop/Programming/Github_Project/roco-battle-simulator/.github/workflows/build-desktop.yml)，可以在 GitHub 的 Actions 页面手动运行，也会在推送 `v*` 标签时自动运行。

工作流会分别生成：

- `roco-battle-simulator-windows.zip`
- `roco-battle-simulator-macos.zip`

详细说明见 [docs/PYINSTALLER_PACKAGING.md](/Users/hedong/Desktop/Programming/Github_Project/roco-battle-simulator/docs/PYINSTALLER_PACKAGING.md)。

## 致谢与数据来源

本项目基于 [ColinHong10/NRC_AI](https://github.com/ColinHong10/NRC_AI) 开发，原项目采用 MIT 协议。

项目中的洛克王国图鉴、技能、机制、阵容等资料主要来源于 [洛克王国 BiliGame Wiki](https://wiki.biligame.com/rocom/%E9%A6%96%E9%A1%B5)，相关内容遵循 CC BY-NC-SA 4.0 协议。
