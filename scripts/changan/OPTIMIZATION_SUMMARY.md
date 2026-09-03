# Chang'an 模块优化汇总（2026-07 更新）

本次优化已于 **2026-07-19** 完成审查、修复和当前世界增量施工：

1. **大规模扩展现有模块**的覆盖密度
2. **新增 10 个独立细节模块**
3. **新增材质语义文档**（`MATERIALS.md`）
4. **接入总编排脚本**（`build_all.py`、`run_all_phases.py`）

> 所有脚本均已通过 `py_compile` 和全量 dry-run；当前世界的优化增量已执行并抽样验证。

---

## 一、扩展后的模块（密度提升）

| 模块 | 改动前 | 改动后 | 变化 | 说明 |
|---|---|---:|---:|---|
| `suburb_farms.py` | 4,057 | **17,112** | +13,055 | 四郊农田延伸到约 1,000 格，水渠限制在城外，新增村落、风车、稻草堆 |
| `market_details.py` | 56 | **940** | +884 | 东西市每个象限密集布置酒旗、布架、招牌、货郎担、灯笼串 |
| `drainage_ditches.py` | 96 | **840** | +744 | 主干道排水沟 + 每个坊巷交叉口的雨水井/暗沟 |
| `window_lattice.py` | 5,539 | **12,534** | +6,995 | 对齐丹凤门、蓬莱阁、太极宫、兴庆宫、所有城门、钟鼓楼、官署和六座寺庙真实墙面 |
| `palace_interior.py` | 288 | **1,157** | +869 | 覆盖含元殿、宣政殿、紫宸殿、太极殿、两仪殿、花萼相辉楼，新增官员案几 |
| `flowers_gardens.py` | 1,118 | **1,838** | +720 | 定点花园 + 每个住宅坊的安全空隙花圃，避开宅院和宫殿主体 |
| `street_props.py` | 112 | **1,483** | +1,371 | 主干道交叉口、东西市、坊内街巷、宫城仪仗路全面加马车/轿子/货摊/水桶/石凳 |
| `roof_ornaments.py` | 22 | **3,195** | +3,173 | 屋脊高度和中心线按主体屋顶重新计算，覆盖宫殿、城门、钟鼓楼、寺庙和塔刹 |

---

## 二、新增模块

| 新模块 | fills | 用途 |
|---|---:|---|
| `rampart_horse_way.py` | 576 | 城墙登城马道（8 处逐级斜坡+随坡抬升护栏） |
| `moat_bridge_railings.py` | 204 | 城门外护城河桥：栏杆、桥墩、桥头石狮 |
| `temple_incense_banners.py` | 212 | 各大寺庙/道观香炉、幡旗、石碑、圣树 |
| `palace_plaques_murals.py` | 52 | 宫殿匾额、墙面壁画；移除与主体重复或错位的城门匾额/屏风 |
| `tomb_spirit_way.py` | 73 | 城郊皇陵：神道、石像生、献殿、封土 |
| `farm_irrigation.py` | 308 | 郊区灌溉渠、水车、立体双柱水闸，衔接龙首渠/清明渠 |
| `street_wells_millstones.py` | 1,275 | 坊巷/市场公共水井、石磨、柴堆 |
| `entertainment_spectators.py` | 93 | 马球场、乐游园看台、入口、旗杆 |
| `leyouyuan_stele.py` | 44 | 乐游园诗碑、亭台题字、石凳 |
| `seasonal_vegetation.py` | 2,216 | 四季点状植被切换，不再整片覆盖地面（`--season spring/summer/autumn/winter`） |

---

## 三、新增文档

| 文档 | 说明 |
|---|---|
| `MATERIALS.md` | `Materials` 调色板每个材质对应的唐代构件/使用场景/风格原则 |
| `OPTIMIZATION_SUMMARY.md` | 本文件 |

---

## 四、当前总命令数

截至本次优化，全模块独立 dry-run 汇总：

- **总 fills：90,262**
- `build_all.py` dry-run：90,262
- validation：0 oversized / 0 invalid_height

阶段总数：tiling 47,782 / commercial 2,348 / landmarks 15,142 / details 21,696 / events 2,869。
新增模块均已按依赖关系接入 `run_all_phases.py`。

---

## 五、建议的使用方式

当前世界禁止重跑基础层和完整地标层；应使用 `--include` 精确执行增量模块。下面的根目录基础命令仅适用于全新空白世界：

```bash
# 1. 先跑原有的基础/骨架/细节层（项目根目录脚本）
.venv/bin/python scripts/foundation_changan_city_v2.py --execute --limit 500
.venv/bin/python scripts/generate_changan_city_v1.py --execute --limit 500
.venv/bin/python scripts/detail_changan_city_v2.py --execute --limit 500

# 2. 平铺骨架
.venv/bin/python scripts/changan/ward_block.py --execute --limit 500
.venv/bin/python scripts/changan/market_block.py --execute --limit 500

# 3. 扩展后的细节层（可按需选择）
.venv/bin/python scripts/changan/suburb_farms.py --execute --limit 500
.venv/bin/python scripts/changan/market_details.py --execute --limit 300
.venv/bin/python scripts/changan/window_lattice.py --execute --limit 500
.venv/bin/python scripts/changan/palace_interior.py --execute --limit 300
.venv/bin/python scripts/changan/roof_ornaments.py --execute --limit 300
.venv/bin/python scripts/changan/street_props.py --execute --limit 300
.venv/bin/python scripts/changan/drainage_ditches.py --execute --limit 300

# 4. 新增模块（可按需选择）
.venv/bin/python scripts/changan/rampart_horse_way.py --execute --limit 200
.venv/bin/python scripts/changan/moat_bridge_railings.py --execute --limit 200
.venv/bin/python scripts/changan/temple_incense_banners.py --execute --limit 200
.venv/bin/python scripts/changan/palace_plaques_murals.py --execute --limit 100
.venv/bin/python scripts/changan/street_wells_millstones.py --execute --limit 300
.venv/bin/python scripts/changan/farm_irrigation.py --execute --limit 200
.venv/bin/python scripts/changan/entertainment_spectators.py --execute --limit 100
.venv/bin/python scripts/changan/leyouyuan_stele.py --execute --limit 50
.venv/bin/python scripts/changan/tomb_spirit_way.py --execute --limit 100

# 5. 季节性植被（可反复切换）
.venv/bin/python scripts/changan/seasonal_vegetation.py --season spring --execute --limit 500
.venv/bin/python scripts/changan/seasonal_vegetation.py --season winter --execute --limit 500
```

---

## 六、审查修复与施工记录

审查中修复的高风险问题：

- 北郊/东郊 `range` 方向错误导致零生成
- 郊区水渠横穿 6000×6000 城区
- 马道护栏为整块高墙，没有随坡抬升
- 太极殿、两仪殿、紫宸殿及六座寺庙的室内/窗棂/匾额坐标错位
- 多组屋脊兽沿用旧屋顶高度或错误中心点
- 坊内花园和季节花圃覆盖宅院，宫苑花圃覆盖紫宸殿/国子监
- 新增模块没有接入 `build_all.py` 和 `run_all_phases.py`
- 强加载窗口过大导致 TPS 低于 10，现改为 128×128（最多 64 区块）

当前世界增量施工日志：

- `logs/optimization_tiling_20260719.log`
- `logs/optimization_commercial_20260719.log`
- `logs/optimization_landmarks_20260719.log`
- `logs/optimization_details_20260719.log`
- `logs/optimization_events_20260719.log`
- `logs/optimization_seasonal_summer_20260719.log`

施工前/后备份：

- `backups/world_backup_20260719_pre_optimization`
- `backups/world_backup_20260719_post_optimization`

## 七、3D 深化模块（新增）

发挥 Minecraft 三维空间优势的强化模块，与基础模块并存（命名 `*_3d.py`），
在基础模块之后运行以叠加立体细节：

- `lib.py` 新增 6 个 3D 原语：`add_staircase`（直线阶梯）、
  `add_spiral_stair`（塔内螺旋梯）、`add_cantilevered_floor`（悬挑楼板/平座）、
  `add_arch_bridge`（多拱桥）、`add_underground_room`（地下空间）、
  `add_dougong_cluster`（斗拱层）。
- `palace_hanyuan_3d.py`（544 fills）：转折龙尾道阶梯、飞廊悬挑、
  檐下斗拱层、三层阁楼、殿底地下宝库。
- `pagoda_giant_3d.py`（281 fills）：塔下地宫与舍利金塔、下行台阶、
  每层内部螺旋梯、平座回廊与栏杆、檐角斗拱与风铃、分节塔刹（覆钵/相轮/宝珠）、
  院碑亭与参道灯柱。
- `qujiang_pool_3d.py`（360 fills）：曲江池多层跌水、湖心岛画舫、
  悬挑水榭、曲桥、水下石阶、环湖栈道。

三个模块均已接入 `build_all.py` 与 `run_all_phases.py`（landmarks 阶段），
组合总量由 90,262 提升至 91,447 fills。地下部分使用负 y 坐标，
不与地面建筑冲突。

第二批宏伟 3D 建筑（总量 91,447 → 95,704 fills）：

- `palace_linde_3d.py`（1874 fills）：麟德殿——唐代最大宴会殿，
  三层台基上前/中/后三殿串联抬升，殿间双层复道（下通行、上观景），
  东西亭双层楼阁以飞廊连接中殿，配宴会露台与香炉。
- `mingtang_altar_3d.py`（1016 fills）：圜丘——明德门外祭天坛，
  扫描线圆盘算法构建真圆形三层坛（非方块阶梯近似），四向登坛阶梯、
  双重壝墙与四座棂星门、燔柴炉、环坛灯柱；自带地基平台找平郊野地形。
- `observatory_3d.py`（136 fills）：司天台——四收分高台至 y=48，
  外挂四段螺旋梯，台顶浑天仪由三个正交金环+玻璃天球构成，
  台下为海晶灯星座地下星图室。三个空间方向（地下/塔身/悬空仪器）全部利用。
- `polo_stadium_3d.py`（1231 fills）：马球场——南北六层阶梯看台
  （石基木凳+顶棚廊柱+走道阶梯），西侧彩楼以立柱架空并悬挑观礼台，
  南看台下方设地下马厩（隔间、马槽、双端坡道），配球门与夜赛灯环。

第三批 3D 模块（总量 95,704 → 96,941 fills）：

- `fudao_jiacheng_3d.py`（471 fills）：夹城复道——玄宗式双层架空长廊，
  石墩承重跨越东部坊区，大明宫东墙(4200,4700) → 东至 x=5900 → 南至曲江，
  下层封闭暗道（窗缝采光）、上层开敞观景廊，转角平台+三座登道楼。
- `grotto_buddha_3d.py`（248 fills）：崖壁佛龛——终南山麓岩体三层十五窟，
  每窟坐佛配金背光，二层悬挑木栈道（下置斜撑），两条石阶串联三层，
  顶部护窟瓦檐，前设供养庭院与香炉。
- `waterwheel_mill_3d.py`（166 fills）：永安渠水磨坊两座——立式水轮用
  垂直面扫描线圆环（真圆形，轮辐+八轮叶），轮轴穿入磨坊驱动磨盘，
  下设引水渠，岸边码头配缆桩灯笼。
- `wall_dilou_3d.py`（352 fills）：城墙双层敌楼四座（插在既有敌楼之间），
  外侧悬楼挑台留射孔与魔鬼洞，内部阶梯连通马道-双层-屋顶，
  斗拱琉璃屋顶上设烽火台。

第四批 3D 模块（总量 96,941 → 98,392 fills）：

- `penglai_island_3d.py`（493 fills）：太液池蓬莱仙岛——扫描线圆盘
  三层台地仙岛，三层楼阁逐层收分带悬挑回廊与斗拱，内部螺旋梯贯通，
  多拱石桥接北岸，方丈/瀛洲双陪岛，南侧船坞码头。
- `underground_drain_3d.py`（285 fills）：朱雀大街地下暗渠——砖拱
  主干渠（负 y 层，可进入），沿线五座沉淀井室配积水坑与灯龛，
  检修井直通街面铁箅，z=2500 十字口东西支渠与维护台阶，
  与地面排水沟网（drainage_ditches）上下呼应。
- `zhaigong_3d.py`（323 fills）：圜丘东侧斋宫——坛庙配套建筑群，
  双层斋戒殿（上层为斋戒静室）、铜人亭立铜人持斋戒牌、
  东西侧殿以有顶连廊接主殿台基，井亭、园池、参道灯柱俱全。
- `bell_drum_3d.py`（350 fills）：大明宫钟鼓楼重建——三层檐塔楼，
  钟楼内置木构吊钟架、青铜钟与撞木杠杆，鼓楼环形布置十二面更鼓
  加中央大鼓，内部四跑转折梯自台基直达顶层。

第五批 3D 模块（总量 98,392 → 101,040 fills）：

- `lib.py` 新增 2 个屋顶原语：`add_hip_roof`（庑殿顶——四面楼梯坡
  逐层内收，四角自然成垂脊，顶部正脊+鸱吻+挑檐翘角）与
  `add_pyramid_roof`（攒尖顶——四面坡收至一点+金色宝顶），
  本批新模块全部采用。
- `lingyan_ge_3d.py`（408 fills）：太极宫凌烟阁——三层石台基上
  三层木阁逐层收分，每层悬挑平座回廊+内部螺旋梯，墙面十八面
  「二十四功臣」彩绘壁画板，顶层庑殿顶，阁前碑亭攒尖顶+参道灯柱。
- `hanliang_ziyu_3d.py`（339 fills）：太液池西岸含凉殿·自雨亭——
  殿顶石砌蓄水箱溢流形成檐口雨帘，落入石槽排回池中；自雨亭攒尖顶
  四柱间水帘，旁设立式扫描线圆环提水轮；殿底地下冰窖储冰。
- `xishi_qiting_3d.py`（520 fills）：西市中心旗亭（三层市楼、
  庑殿顶、楼顶彩旗、二层鼓楼悬鼓）与胡商酒肆（扫描线球壳穹顶+
  金色圆窗、拱形门洞、环形吧台、葡萄美酒瓮、地下酒窖、波斯毯庭院）。
- `wanglou_network_3d.py`（600 fills）：朱雀大街两侧六座望楼——
  井字木构高塔（约 38 格），转折梯+爬梯两级登台，中部悬挑瞭望台，
  顶层朱漆大鼓+信号灯+攒尖顶，塔底小院岗亭拴马石。
- `gates_south_3d.py`（385 fills）：朱雀门/明德门 3D 深化——门洞
  阶梯拱顶内壁与门轴石、半降千斤闸（铁栅+绞盘室）、城楼双层内部
  与登城梯接马道、瓮城校场（旗杆/箭靶/兵器架）、护城河吊桥铁链。
- `xingqing_palace_3d.py`（396 fills）：兴庆宫龙庆池——花萼相辉楼
  双层楼阁立水上石桩平台，重檐（下檐+庑殿顶）+跨水飞廊；沉香亭
  攒尖顶水上亭+四柱牡丹花坛+曲桥；池北岸倒影柱廊。

第六批 3D 模块（总量 101,040 → 104,933 fills）：

- `fuyong_yuan_3d.py`（1315 fills）：曲江南岸芙蓉园——紫云楼石桩
  双层彩楼临水而立，悬挑观景水台探入池面，重檐+庑殿顶；荷花池
  睡莲浮叶+三座花岛+五段折角九曲桥；百官幕次红黄羊毛帐篷廊；
  白墙月洞门封禁苑，水岸灯柱夜宴。
- `xingyuan_3d.py`（351 fills）：曲江西岸杏园——cherry_leaves 杏林
  花毯，蛇形「曲水流觞」水道自流杯亭蜿蜒而下、粉色酒觞浮杯其间；
  三层探花宴高台+宴会厅（长案酒瓮）；北墙进士题名碑廊八通。
- `baliu_3d.py`（780 fills）：东郊灞桥——整平河滩后开挖灞水（沙床
  石岸），五孔石拱桥带分水尖+踏步引桥+桥头华表；两岸垂柳成行
  （双层垂枝树冠）；灞亭饯别（酒案酒瓮）、驿道里程碑+歇脚棚、
  河湾折柳台。
- `guangyun_dock_3d.py`（455 fills）：东郊广运潭——引水漕渠接
  铁栅双门船闸（闸室四塔楼绞盘梁）；东北岸石嘴望春楼双层楼阁
  面水而立；潭中三艘漕船（挖空船壳、干草粮堆、羊毛帆桅）；南岸
  木栈桥码头系船桩+吊臂吊货。
- `liyuan_3d.py`（494 fills）：大明宫北禁苑梨园——乐舞大堂内置
  悬鼓架三组+编钟架（金钟由大到小）+演出台；桩基戏台三圈环形
  看台；乐器库 note_block/木箱/爬梯；白花梨树林+牡丹圃；弟子院
  五舍围合水井。
- `tai_cang_3d.py`（498 fills）：东郊太仓——仓城墙垣南门楼匾额；
  地面三座仓廪（通风格栅+粮堆）；核心为 3×2 地下仓窖矩阵
  （负 y 层，木板封盖+联络隧道+壕梯下行），每窖正上 2x2 通风
  烟囱直透地表；计量台天平粮袋、东北角卫楼、西墙外漕渠码头
  与广运潭相望。

执行备份：`backups/world_backup_20260903_165552`；
施工日志：`logs/batch6_3d_20260904_rerun.log`。

## 八、后续可选的优化（未实施）

以下项因改动面较大，本次**未做**，如需可继续：

- 城门/寺庙模块抽象复用（`add_city_gate_complex`、`build_temple_complex`）
- 所有模块统一 `--single` 参数
- 执行日志持久化（`--log PATH`）
- 统一 dry-run 测试脚本（`tests/test_all_modules.py`）

如需要这些，告诉我即可继续。
