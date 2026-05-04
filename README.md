# 洛克王国本地对战模拟器

本项目是一个本地化的洛克王国资料与手动对战模拟系统。当前入口为图鉴页，核心流程是查看图鉴与技能资料、配置双方队伍、进入对战页手动选择双方行动并结算。

## 快速开始

```bash
pip install fastapi uvicorn[standard] openpyxl pandas beautifulsoup4 requests
python run_web.py
```

启动后访问：

- `http://localhost:8765/dex`：精灵图鉴，也是根入口 `/`
- `http://localhost:8765/skills`：技能图鉴与技能详情
- `http://localhost:8765/mechanics`：机制百科
- `http://localhost:8765/storage`：本地精灵仓库
- `http://localhost:8765/simulator`：双方队伍配置
- `http://localhost:8765/battle`：手动对战页

## 项目结构

```text
NRC_AI/
├── src/
│   ├── models.py
│   ├── effect_models.py
│   ├── effect_data.py
│   ├── effect_engine.py
│   ├── skill_effects_generated.py
│   ├── battle.py
│   ├── skill_db.py
│   ├── pokemon_db.py
│   ├── team_builder.py
│   └── server.py
├── web/
│   ├── dex.html
│   ├── skills.html
│   ├── mechanics.html
│   ├── storage.html
│   ├── simulator.html
│   ├── battle.html
│   └── theme.css
├── data/
│   ├── nrc.db
│   ├── spirit_icons/
│   └── skill_icons/
├── scripts/
├── tests/
└── ROADMAP.md
```

## 主要功能

- 精灵图鉴：本地数据库查询、种族值、特性、可学习技能
- 技能图鉴：技能图标、属性/分类筛选、描述、效果标签、学习精灵
- 机制百科：状态、印记、回合流程、特性结算说明
- 队伍配置：双方队伍、技能、特性、性格、个体配置
- 手动对战：双方行动选择、结构化战报、动画事件、补位流程

## 当前重点

1. 完善技能图鉴与悬浮提示展示。
2. 继续补充状态、印记、特性解释来源。
3. 增强队伍库和精灵仓库，减少重复配队成本。
4. 升级对战页 UI、结构化日志和回放系统。
