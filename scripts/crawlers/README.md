# 爬虫入口整理

这个目录集中放置项目的数据爬虫，每个 Python 文件对应一种数据来源或资源类型。

- `ability_icons.py`：BiliGame 精灵详情页特性图标，输出 `data/ability_icons/`。
- `spirit_icons.py`：BiliGame 精灵图鉴、形态立绘和进化信息。
- `skills_biligame.py`：BiliGame 技能图鉴、技能图标、系别/分类/耗能图标。
- `pokemon_skills.py`：BiliGame 精灵详情页可学习技能和学习来源。
- `mechanics_rocomaster.py`：RocoMaster 机制百科文本。
- `skills_rocoworld.py`：旧版 RocoWorld Wiki 技能数据爬虫。

根目录 `scripts/` 下的旧脚本仍可作为兼容入口使用；后续新增爬虫优先放在本目录。
