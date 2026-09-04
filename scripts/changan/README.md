# Tang Chang'an Fine-Grained Building Modules

This directory contains per-building Python scripts that generate vanilla
Minecraft `/fill` commands for a detailed Tang Chang'an reconstruction.

All coordinates are **local** to the city origin `(9000, 64, 9000)` defined in
`lib.py`.  Each script converts them to world coordinates and splits large
volumes into safe 32768-block `/fill` chunks.

## Quick start

```bash
# See how many commands a module generates (dry run)
.venv/bin/python scripts/changan/palace_hanyuan_dian.py

# Execute one module in small batches
.venv/bin/python scripts/changan/palace_hanyuan_dian.py --execute --limit 300

# Continue the next batch
.venv/bin/python scripts/changan/palace_hanyuan_dian.py --execute --start 300 --limit 300
```

## Available modules

| Script | What it builds | Dry-run fills |
|--------|----------------|--------------:|
| `palace_hanyuan_dian.py` | 大明宫含元殿：三层台基、龙尾道、柱廊、重檐屋顶、东西阙楼 | 1370 |
| `palace_xuanzheng_dian.py` | 大明宫宣政殿：中朝殿堂、两侧中书/门下省 | 836 |
| `palace_zichen_dian.py` | 大明宫紫宸殿：内朝、后花园池塘、侧亭 | 401 |
| `palace_xingqing.py` | 兴庆宫：宫墙、龙庆池、沉香亭、花萼相辉楼 | 110 |
| `imperial_taiji_palace.py` | 太极宫：承天门、太极殿、两仪殿、官署 | 439 |
| `gate_zhuque_men.py` | 朱雀门：城楼、五门道、箭楼、瓮城 | 165 |
| `gate_mingde_men.py` | 明德门：南正门、五门道、阙楼、瓮城 | 253 |
| `wall_corner_tower.py` | 外郭城四角角楼 | 148 |
| `pagoda_giant.py` | 大慈恩寺大雁塔：七层方形楼阁式塔、寺院 | 322 |
| `pagoda_small.py` | 荐福寺小雁塔：十三层密檐式塔、寺院 | 347 |
| `temple_qinglong.py` | 青龙寺：山门、大雄宝殿、佛塔、藏经阁 | 199 |
| `temple_daxingshan.py` | 大兴善寺：山门、天王殿、大雄殿、译经阁 | 268 |
| `market_block.py` | 东西市可平铺 120×120 商铺街区 | 10752 |
| `ward_block.py` | 108坊可平铺 260×260 住宅坊区 | 15345 |
| `tavern.py` | 市场沿街可平铺酒楼 | 1408 |
| `street_facilities.py` | 朱雀大街中分带、路灯、行道树、牌坊 | 3897 |
| `imperial_daming_palace.py` | 大明宫整体：宫墙、丹凤门、太液池、蓬莱阁 | 781 |
| `bridge_stone_arch.py` | 石拱桥（朱雀桥、太液桥等） | 148 |
| `canal_waterway.py` | 龙首渠、清明渠、永安渠及两岸柳树 | 230 |
| `garden_rockery.py` | 御花园假山、池塘、山顶亭 | 78 |
| `official_residence.py` | 王府/官邸大院（秦王府、齐王府等） | 336 |
| `gates_all.py` | 其余 10 座外郭城门（安化、启夏、玄武、春明、金光等） | 968 |
| `temple_dayan.py` | 大庄严寺（大严塔、大雄殿、译经阁） | 350 |
| `temple_xuandu.py` | 玄都观（三清殿、桃花林、reflecting pond） | 114 |
| `wall_battlement_moat.py` | 城墙垛口、敌楼、护城河石岸与荷叶 | 2772 |
| `palace_interior.py` | 宫殿室内地板、龙椅、顶灯、壁灯 | 288 |
| `night_market.py` | 东西市夜市灯笼串、红毯、门楼灯 | 156 |
| `entertainment_venues.py` | 马球场、乐游园（清秋阁、亭台石凳） | 171 |
| `roof_ornaments.py` | 屋脊兽、鸱吻、瓦当装饰 | 2726 |
| `window_lattice.py` | 宫殿寺庙门窗木格栅 | 5539 |
| `bell_drum_towers.py` | 钟楼、鼓楼（大明宫、太极宫各一组） | 156 |
| `government_offices.py` | 尚书省、御史台、大理寺、鸿胪寺 | 352 |
| `lantern_festival.py` | 上元节灯会：朱雀大街灯棚、城门灯、市场灯弧 | 497 |
| `ancestral_temple_altar.py` | 太庙、社稷坛 | 162 |
| `academy_guozijian.py` | 国子监、太学、辟雍、碑亭 | 192 |
| `suburb_farms.py` | 城外农田、村落民居 | 4057 |
| `road_paving.py` | 道路分级铺装：御道、主干道、坊巷 | 368 |
| `drainage_ditches.py` | 主街排水沟、下水道井盖 | 96 |
| `water_gates.py` | 城墙水关（龙首渠、清明渠、永安渠穿墙处） | 54 |
| `foreign_temples.py` | 西市外籍宗教区：波斯寺、祆祠、景教寺 | 68 |
| `temple_daci.py` | 大慈恩寺完整寺院（ complement 大雁塔） | 149 |
| `temple_jianfu.py` | 荐福寺完整寺院（ complement 小雁塔） | 104 |
| `street_props.py` | 马车、轿子、货摊、推车 | 1483 |
| `city_guards.py` | 宫殿/城门卫兵、岗哨 | 267 |
| `market_details.py` | 晾晒布匹、酒旗、幌子、招牌 | 56 |
| `mountain_zhongnan.py` | 终南山远景山脉 | 952 |
| `terrain_longshou.py` | 龙首原地形抬升（大明宫、太极宫高地） | 425 |
| `flowers_gardens.py` | 牡丹、荷花、菊花、梅花等花园 | 4187 |
| `palace_hanyuan_3d.py` | 含元殿 3D 强化：转折龙尾道阶梯、飞廊悬挑、斗拱层、三层阁楼、地下宝库 | 544 |
| `pagoda_giant_3d.py` | 大雁塔 3D 强化：地宫舍利塔、层内螺旋梯、平座回廊、斗拱、分节塔刹、碑亭 | 281 |
| `qujiang_pool_3d.py` | 曲江池 3D 景区：多层跌水、湖心岛画舫、悬挑水榭、曲桥、环湖栈道 | 360 |
| `palace_linde_3d.py` | 麟德殿：三殿串联、三层台基、东西亭双层楼阁、飞廊复道、宴会露台 | 1874 |
| `mingtang_altar_3d.py` | 圜丘天坛：三层圆形坛（扫描线圆盘）、四向登坛阶梯、双重壝墙棂星门、燔柴炉 | 1016 |
| `observatory_3d.py` | 司天台：四收分高台、外挂螺旋梯、浑天仪三环、地下星图室 | 136 |
| `polo_stadium_3d.py` | 马球场：六层阶梯看台、彩楼悬挑观礼台、台下地下马厩、球门灯柱 | 1231 |
| `fudao_jiacheng_3d.py` | 夹城复道：大明宫至曲江双层架空长廊（下层封闭、上层观景）、转角平台、登道楼 | 471 |
| `grotto_buddha_3d.py` | 崖壁佛龛：三层十五窟、坐佛金背光、悬挑木栈道、石阶连通、供养庭院 | 248 |
| `waterwheel_mill_3d.py` | 永安渠水磨坊：立式扫描线圆环水轮、轮叶轮辐、磨坊二层、引水渠码头 | 166 |
| `wall_dilou_3d.py` | 城墙双层敌楼：悬楼挑台、射孔、内部阶梯、斗拱屋顶、烽火台 | 352 |
| `penglai_island_3d.py` | 太液池蓬莱仙岛：三层台地仙岛、三层楼阁悬廊、螺旋梯、多拱桥、方丈瀛洲双岛 | 493 |
| `underground_drain_3d.py` | 朱雀大街地下暗渠：砖拱主干渠、沉淀井室、检修井、支渠、下行台阶 | 285 |
| `zhaigong_3d.py` | 圜丘斋宫：双层斋戒殿、铜人亭、侧殿连廊、井亭花园、参道灯柱 | 323 |
| `bell_drum_3d.py` | 钟鼓楼重建：三层檐塔、吊钟木架撞木、十二面更鼓、内部转折梯 | 350 |
| `lingyan_ge_3d.py` | 凌烟阁：三层木阁、悬挑平座、二十四功臣壁画墙、庑殿顶、碑亭 | 408 |
| `hanliang_ziyu_3d.py` | 含凉殿·自雨亭：屋顶水箱雨帘、提水轮、攒尖顶水亭、地下冰窖 | 339 |
| `xishi_qiting_3d.py` | 西市旗亭+胡商酒肆：三层市楼庑殿顶、扫描线球壳穹顶酒肆、地下酒窖 | 520 |
| `wanglou_network_3d.py` | 望楼系统：朱雀大街六座鼓号木塔、悬挑瞭望台、攒尖顶鼓台 | 600 |
| `gates_south_3d.py` | 朱雀门/明德门 3D 深化：门洞拱顶、千斤闸、城楼内部、瓮城校场、吊桥 | 385 |
| `xingqing_palace_3d.py` | 兴庆宫花萼相辉楼+沉香亭：双层楼阁跨水飞廊、攒尖顶水上亭、牡丹坛 | 396 |
| `fuyong_yuan_3d.py` | 芙蓉园紫云楼：临水双层彩楼、悬挑观景水台、荷花池九曲桥、百官幕次、月洞门 | 1315 |
| `xingyuan_3d.py` | 杏园·曲水流觞：杏林花毯、蜿蜒流杯水道、探花宴高台、进士题名碑廊 | 351 |
| `baliu_3d.py` | 灞桥·折柳送别：灞水河渠、五孔石拱桥分水尖、垂柳两岸、灞亭饯别、驿道里程碑 | 780 |
| `guangyun_dock_3d.py` | 广运潭漕运：引水漕渠、铁栅船闸、望春楼、三艘漕船粮帆、码头吊臂 | 455 |
| `liyuan_3d.py` | 梨园法曲：乐舞大堂悬鼓编钟、桩基戏台环形看台、乐器库、梨树林、弟子院 | 494 |
| `tai_cang_3d.py` | 太仓地下仓窖：仓城墙门楼、地面三仓、3×2 地下仓窖矩阵、通风烟囱、计量台 | 498 |
| `weishui_ferry_3d.py` | 渭水咸阳古渡：横贯大河、石阶码头栈桥、双帆渡船、古渡牌坊石碑、河神祠、纤道 | 546 |
| `kunming_pool_3d.py` | 昆明池水军操练湖：湖心石鲸、牵牛织女石像隔岸、豫章台、汉式楼船两艘 | 525 |
| `huaqing_palace_3d.py` | 华清宫温泉：九龙湖九曲桥、海棠汤莲花汤、温泉泉眼引水暗渠、飞霜殿 | 549 |
| `beilin_3d.py` | 碑林开成石经：重檐碑亭丰碑、石经长廊卅六碑、墓志碑阵、拓印书肆、墨池 | 538 |
| `silk_caravan_3d.py` | 丝路驼队波斯邸：五驼商队卧驼、波斯穹顶货栈、香料市集、望乡灯塔 | 549 |
| `hanlin_academy_3d.py` | 翰林院学士待诏：三进值房书案、藏书小阁、画案院、月洞门曲水池 | 492 |
| `sanqing_temple_3d.py` | 三清殿道观：真八角三层八卦坛爻象、三清神台、三足焚香鼎、龟蛇石雕、丹房 | 494 |
| `qinwu_tower_3d.py` | 勤政务本楼：跨宫墙券洞城楼、南挑观乐露台金座、观乐广场看棚百戏台 | 417 |
| `douting_post_3d.py` | 都亭驿四方馆：驿务大堂舆图墙、四方客房波斯使节房、八间马厩、信鸽楼、驿站马车 | 491 |
| `tangchang_guan_3d.py` | 唐昌观玉蕊花：参天玉蕊神树、落花四径、题诗壁廊、花神小祠、扫花僧舍 | 480 |
| `xiaoyanta_3d.py` | 小雁塔雁塔晨钟：塔下地宫舍利函、密檐风铃、分节塔刹、贯通螺旋梯、悬钟钟楼 | 380 |
| `taiyiyuan_3d.py` | 太医署：针灸铜人、百子柜药房、百草药圃、晾药架、煎药处、杏林 | 471 |
| `jingjiao_bei_3d.py` | 大秦景教碑园：金十字巨碑龟趺、连珠纹照壁、传教士墓碑阵、经卷堂礼拜堂 | 328 |
| `beacon_tower_3d.py` | 骊山烽火台：峰顶找平高台、垛口烽火盆狼烟、驻守房、下山磴道 | 156 |
| `bangyuan_3d.py` | 贡院放榜：十二号舍阵、明远楼、黄金榜墙、龙门跃鱼牌坊、报喜棚、誊录所 | 483 |
| `wenyuan_3d.py` | 文人园辋川意境：竹里馆、鹿柴石鹿、辛夷坞花溪、临湖亭曲桥、邀月台 | 323 |
| `zhijinfang_3d.py` | 织锦署：六台织机大坊、八口染缸阵、晾布长架、蚕箔房、锦缎展示堂 | 492 |
| `bingjiao_3d.py` | 官冰窖：三座覆土地下冰窖存冰、运冰坡道、采冰码头、赐冰亭 | 386 |
| `jinzouyuan_3d.py` | 进奏院群：六道藩镇院落道旗、四方朝贡照壁、驿传马厩、文牍房、谯楼 | 497 |
| `build_all.py` | 组合以上所有模块 | 113530 |

## Tiling / layering strategy

The city is filled in layers:

1. **Foundation** (`foundation_changan_city_v2.py`) — flat terrain plate.
2. **Skeleton** (`generate_changan_city_v1.py`) — walls, gates, avenues, wards.
3. **Detail pass** (`detail_changan_city_v2.py`) — palace roofs, market stalls, lamps.
4. **Fine-grained modules** (this directory) — per-building refinements.

You can run modules independently and repeatedly.  New blocks overwrite old
ones in the same location, so each layer upgrades what is underneath.

## Common CLI flags

Every module accepts:

```text
--execute          Send commands to the server (default is dry-run)
--start N          Skip the first N /fill commands
--limit N          Process only N commands
--delay-ms MS      Wait MS milliseconds between commands
--report-every N   Print progress every N commands
--timeout S        rcon timeout in seconds
--no-forceload     Skip chunk forceload (use only if area is already loaded)
```

## Recommended execution order

```bash
# 1. Palaces and landmarks (visible from the spawn point)
.venv/bin/python scripts/changan/palace_hanyuan_dian.py --execute --limit 300
.venv/bin/python scripts/changan/palace_xuanzheng_dian.py --execute --limit 300
.venv/bin/python scripts/changan/palace_zichen_dian.py --execute --limit 200

# 2. City gates
.venv/bin/python scripts/changan/gate_zhuque_men.py --execute --limit 100

# 3. Religious landmarks
.venv/bin/python scripts/changan/pagoda_giant.py --execute --limit 100
.venv/bin/python scripts/changan/pagoda_small.py --execute --limit 100
.venv/bin/python scripts/changan/temple_qinglong.py --execute --limit 100
.venv/bin/python scripts/changan/palace_xingqing.py --execute --limit 100

# 4. Detail layers (overwrites large blank walls/roofs)
.venv/bin/python scripts/changan/window_lattice.py --execute --limit 500
.venv/bin/python scripts/changan/roof_ornaments.py --execute --limit 100

# 5. Atmosphere
.venv/bin/python scripts/changan/lantern_festival.py --execute --limit 300
.venv/bin/python scripts/changan/night_market.py --execute --limit 200

# 6. Dense commercial/residential tiling (do in small batches!)
.venv/bin/python scripts/changan/market_block.py --execute --limit 500
.venv/bin/python scripts/changan/ward_block.py --execute --limit 500
.venv/bin/python scripts/changan/tavern.py --execute --limit 300
```

## Adding a new module

1. Create `scripts/changan/my_building.py`.
2. Import `Fill` and helpers from `scripts.changan.lib`.
3. Define `def build_my_building(fills: list[Fill]) -> None:`.
4. Call `run_builder(build_my_building, "my_building")` in `main()`.
5. Add the module to `build_all.py`'s `MODULES` dict.

See `palace_hanyuan_dian.py` for a complete example.

For 3D work, `lib.py` also provides vertical-space primitives:
`add_staircase` (straight stair), `add_spiral_stair` (in-tower spiral),
`add_cantilevered_floor` (overhanging gallery), `add_arch_bridge`,
`add_underground_room` (crypt/basement), `add_dougong_cluster` (bracket
sets), `add_hip_roof` (wudian hip roof) and `add_pyramid_roof`
(cuanjian pavilion roof). See `palace_hanyuan_3d.py` and
`pagoda_giant_3d.py` for usage.
