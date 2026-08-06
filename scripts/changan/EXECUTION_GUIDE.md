# Tang Chang'an — 分阶段执行指南

本目录已经包含 58 个细粒度建筑模块，最终 dry-run 总计 **90,262** 条 `/fill` 命令。
直接在游戏中一次性执行 4 万多条命令很容易超时或造成长时间卡顿，因此建议按**平铺层 → 地标层 → 细节层 → 事件层**的顺序分批建造。

> **现有长安世界安全提示**：当前世界已经完成外城、宫殿、雁塔、坊院和 v5 立体屋顶施工。
> 不要在当前世界重新执行 Phase 0、`--phase tiling`、完整 `--phase landmarks` 或
> `--phase all`，否则旧模块会覆盖现有结构。当前世界应使用 `--include` 精确选择增量模块。

---

## 1. 整体建造思路

长安城建议按以下 4 层叠加：

1. **基础地形层**（项目根目录脚本）
   - `foundation_changan_city_v2.py` — 6000×6000 平地基础板
   - `generate_changan_city_v1.py` — 城墙、城门、主干道、坊区骨架
   - `detail_changan_city_v2.py` — 宫殿屋顶、市场摊位、路灯等初版细节

2. **平铺填充层**（`scripts/changan/` 可大面积平铺的模块）
   - 住宅区、商业区、农田、道路、街道设施
   - 这一层负责把 6000×6000 地图迅速填满

3. **地标建筑层**（单点精细模块）
   - 大明宫、太极宫、兴庆宫、各城门、大小雁塔、寺庙等
   - 在平铺层之上覆盖，提升视觉焦点

4. **细节层叠层**
   - 门窗格栅、屋脊兽、街景道具、排水沟、卫兵岗哨等

5. **事件/氛围层**
   - 夜市灯笼、上元节灯会、烟花等（可按季节或活动单独开启）

---

## 2. 推荐执行顺序与命令

### Phase 0 — 项目根目录基础层（仅限全新/空白世界）

```bash
# 1. 地形基础板
.venv/bin/python scripts/foundation_changan_city_v2.py --execute --limit 500

# 2. 生成城墙、城门、主干道、坊区骨架命令文件
.venv/bin/python scripts/generate_changan_city_v1.py

# 3. 将生成的骨架命令分批施工进世界
.venv/bin/python scripts/build_changan_city_vanilla_fill.py --execute --limit 500

# 4. 初版细节（宫殿屋顶、市场摊位、路灯）
.venv/bin/python scripts/detail_changan_city_v2.py --execute --limit 500
```

> `generate_changan_city_v1.py` 只生成命令文件，不直接施工；实际施工由
> `build_changan_city_vanilla_fill.py` 完成。Phase 0 会清空和平整城市区域，禁止在现有世界重跑。

### Phase 0.5 — 龙首原地形（建筑之前）

```bash
.venv/bin/python scripts/changan/run_all_phases.py --phase terrain
.venv/bin/python scripts/changan/run_all_phases.py --phase terrain --execute --limit 500
```

### Phase 1 — 平铺填充层（快速占满地图）

```bash
# 1. 108 坊住宅区（260×260 自动平铺，已跳过皇城和东西市）
.venv/bin/python scripts/changan/ward_block.py --execute --limit 500

# 2. 东西市商铺街区（120×120 自动平铺）
.venv/bin/python scripts/changan/market_block.py --execute --limit 500

# 3. 城外农田与村落（城墙外四郊自动平铺）
.venv/bin/python scripts/changan/suburb_farms.py --execute --limit 500

# 4. 道路分级铺装
.venv/bin/python scripts/changan/road_paving.py --execute --limit 300

# 5. 街道设施：路灯、行道树、牌坊
.venv/bin/python scripts/changan/street_facilities.py --execute --limit 500
```

### Phase 2 — 商业沿街与花园

```bash
# 东西市沿街酒楼
.venv/bin/python scripts/changan/tavern.py --execute --limit 300

# 市场晾晒布匹、酒旗、幌子和招牌
.venv/bin/python scripts/changan/market_details.py --execute --limit 200
```

### Phase 3 — 地标建筑（单点覆盖）

```bash
# 宫殿群
.venv/bin/python scripts/changan/palace_hanyuan_dian.py --execute --limit 300
.venv/bin/python scripts/changan/palace_xuanzheng_dian.py --execute --limit 300
.venv/bin/python scripts/changan/palace_zichen_dian.py --execute --limit 300
.venv/bin/python scripts/changan/palace_xingqing.py --execute --limit 300
.venv/bin/python scripts/changan/imperial_taiji_palace.py --execute --limit 300
.venv/bin/python scripts/changan/imperial_daming_palace.py --execute --limit 300
.venv/bin/python scripts/changan/palace_interior.py --execute --limit 300

# 城门与城墙
.venv/bin/python scripts/changan/gate_zhuque_men.py --execute --limit 200
.venv/bin/python scripts/changan/gate_mingde_men.py --execute --limit 200
.venv/bin/python scripts/changan/gates_all.py --execute --limit 300
.venv/bin/python scripts/changan/wall_corner_tower.py --execute --limit 200
.venv/bin/python scripts/changan/wall_battlement_moat.py --execute --limit 500

# 塔与寺庙
.venv/bin/python scripts/changan/pagoda_giant.py --execute --limit 200
.venv/bin/python scripts/changan/pagoda_small.py --execute --limit 200
.venv/bin/python scripts/changan/temple_qinglong.py --execute --limit 200
.venv/bin/python scripts/changan/temple_daxingshan.py --execute --limit 200
.venv/bin/python scripts/changan/temple_dayan.py --execute --limit 200
.venv/bin/python scripts/changan/temple_xuandu.py --execute --limit 200
.venv/bin/python scripts/changan/temple_daci.py --execute --limit 200
.venv/bin/python scripts/changan/temple_jianfu.py --execute --limit 200
.venv/bin/python scripts/changan/foreign_temples.py --execute --limit 100

# 官署、娱乐、钟鼓楼
.venv/bin/python scripts/changan/government_offices.py --execute --limit 200
.venv/bin/python scripts/changan/entertainment_venues.py --execute --limit 200
.venv/bin/python scripts/changan/bell_drum_towers.py --execute --limit 100

# 桥梁与水系
.venv/bin/python scripts/changan/bridge_stone_arch.py --execute --limit 200
.venv/bin/python scripts/changan/canal_waterway.py --execute --limit 200
.venv/bin/python scripts/changan/water_gates.py --execute --limit 100
```

### Phase 4 — 细节层叠

```bash
# 门窗格栅
.venv/bin/python scripts/changan/window_lattice.py --execute --limit 500

# 屋脊兽、鸱吻、瓦当
.venv/bin/python scripts/changan/roof_ornaments.py --execute --limit 100

# 街景道具：马车、轿子、货摊
.venv/bin/python scripts/changan/street_props.py --execute --limit 200

# 市场晾晒布匹、酒旗、幌子
.venv/bin/python scripts/changan/market_details.py --execute --limit 200

# 排水沟、下水道井盖
.venv/bin/python scripts/changan/drainage_ditches.py --execute --limit 100

# 卫兵岗哨
.venv/bin/python scripts/changan/city_guards.py --execute --limit 300

# 屋顶/窗棂等其它装饰
.venv/bin/python scripts/changan/garden_rockery.py --execute --limit 100
.venv/bin/python scripts/changan/official_residence.py --execute --limit 200

# 宫殿/寺庙/官署花园
.venv/bin/python scripts/changan/flowers_gardens.py --execute --limit 300
```

### Phase 5 — 事件/氛围层（可选）

```bash
# 上元节灯会
.venv/bin/python scripts/changan/lantern_festival.py --execute --limit 300

# 夜市灯笼
.venv/bin/python scripts/changan/night_market.py --execute --limit 200
```

---

## 3. 分批执行技巧

所有 `scripts/changan/*.py` 模块都支持统一的执行参数：

```text
--execute          真正发送命令到服务器（默认 dry-run）
--start N          跳过前 N 条 fill 命令
--limit N          本次只执行 N 条命令
--delay-ms MS      每条命令之间的延迟（默认 60ms）
--report-every N   每 N 条命令打印一次进度
--timeout S        rcon 超时秒数
--no-forceload     如果区块已加载，可跳过 forceload
```

### 推荐分批策略

每次 `--limit 500` 左右，执行完再继续：

```bash
# 第一批次
.venv/bin/python scripts/changan/ward_block.py --execute --limit 500

# 第二批次（接上一批末尾）
.venv/bin/python scripts/changan/ward_block.py --execute --start 500 --limit 500

# 第三批次
.venv/bin/python scripts/changan/ward_block.py --execute --start 1000 --limit 500
```

每个模块 dry-run 时会输出总命令数，据此决定需要分多少批：

```bash
.venv/bin/python scripts/changan/ward_block.py
# 输出类似："total_fills": 10788
```

---

## 4. 平铺 vs 层叠原则

| 类型 | 代表模块 | 作用 |
|---|---|---|
| **平铺** | `ward_block`, `market_block`, `suburb_farms`, `road_paving`, `street_facilities` | 用重复单元快速覆盖大面积 |
| **单点地标** | `palace_*`, `gate_*`, `pagoda_*`, `temple_*` | 覆盖在平铺层上，形成视觉焦点 |
| **层叠细节** | `window_lattice`, `roof_ornaments`, `street_props`, `market_details` | 不破坏主体，只增加表面细节 |
| **氛围事件** | `lantern_festival`, `night_market` | 可反复开关的节日/夜间效果 |

---

## 5. 注意事项

1. **执行前务必 dry-run 一次**：先不带 `--execute` 跑一遍，确认坐标和命令数无误。
2. **备份存档**：执行前备份 `server/world`，防止意外覆盖。
3. **服务器需要在线且 rcon 可用**：脚本通过 `docker exec mc-ai-paper rcon-cli` 发送命令，确保容器名与 `lib.py` 中 `DOCKER_CONTAINER` 一致。
4. **区块加载**：默认会自动 forceload 每个 fill 命令涉及的区块；如果区域已经预生成并加载过，可以加 `--no-forceload` 提速。
5. **y 轴层叠关系**：
   - 基础板通常在 y=0~1
   - 道路/街道设施在 y=2~3
   - 坊区建筑从 y=1 开始
   - 地标建筑从 y=1 或更高开始
   后执行的模块会覆盖同一位置的旧方块，因此顺序很重要。
6. **完整区块加载**：公共执行器会把长条 fill 切到 128×128 加载区后执行，单次最多强加载 64 个区块，不要自行绕过。
7. **当前世界增量施工**：优先使用 `--include`，不要依赖 `--phase all`。

---

## 6. 一键总控脚本

如果希望一次性按阶段调度，可以使用本目录下的：

```bash
# Dry-run 全部模块
.venv/bin/python scripts/changan/build_all.py

# 查看一个阶段内指定模块
.venv/bin/python scripts/changan/run_all_phases.py --phase details \
  --include roof_ornaments,street_props,city_guards

# 排除会覆盖现有结构的模块
.venv/bin/python scripts/changan/run_all_phases.py --phase landmarks \
  --exclude palace_hanyuan_dian,palace_xuanzheng_dian,imperial_taiji_palace,pagoda_giant,pagoda_small
```

> `build_all.py` 适合查看总数或少量 `--include` 模块；实际大规模建造建议使用
> `run_all_phases.py` 分阶段、分模块和分批次执行。
