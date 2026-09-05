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

第七批 3D 模块（总量 104,933 → 107,640 fills）：

- `weishui_ferry_3d.py`（546 fills）：北郊渭水——整平后开挖东西向
  大河（沙床石岸），渡口石阶码头层层下水+木栈桥系船缆绳；双帆
  渡船一泊一行（挖空舱室、船尾橹）；「咸阳古渡」牌坊石碑、河神
  祠、草棚茶摊、北岸纤夫栈道拴纤石与芦苇滩。
- `kunming_pool_3d.py`（525 fills）：西郊昆明池——大湖中苔石巨鲸
  跃出水面（分节躯干背鳍尾鳍）；两岸牵牛织女石英坐像隔湖相望，
  各配石婆石爷小庙；北岸豫章台三层高台面水；两艘汉式楼船双层
  楼舱重檐兽首；水操浮标阵与湖心岛石桥。
- `huaqing_palace_3d.py`（549 fills）：南郊山麓华清宫——九龙湖+
  九段折桥湖心晚霞亭；海棠汤（花瓣形贵妃池）与莲花汤（双层莲台
  御汤）石广场；后山温泉泉眼石槽暗渠引水入汤入湖，尾端散水白雾；
  飞霜殿重檐庑殿、东西配殿宫墙门楼。
- `beilin_3d.py`（538 fills）：务本坊碑林——重檐碑亭内 3x3x12
  石台孝经丰碑；东西石经长廊 36 通碑版；北部墓志铭斜列碑阵；
  东南拓印书肆（书架拓案墨缸晾纸架）；讲经堂、墨池、柏树甬道。
- `silk_caravan_3d.py`（549 fills）：开远门外丝路故道——五头双峰
  驼商队（站卧错落、驮货彩毯、铁栅缰绳相连）；波斯邸两层货栈
  （拱门琉璃拼花+沙岩收圆穹顶金顶珠）；香料市集棚、货场草垛、
  歇脚驿站马厩水槽、胡商望乡灯塔。

执行备份：`backups/world_backup_20260904_001635`；
施工日志：`logs/batch7_3d_20260904.log`。

第八批 3D 模块（总量 107,640 → 110,014 fills）：

- `hanlin_academy_3d.py`（492 fills）：大明宫西翰林院——三进院落
  学士值房（书架书案烛台）、待诏直院望亭棋局、两层藏书小阁回
  廊、开敞画堂宣纸颜料、月洞门曲水汀步、竹影梅枝。
- `sanqing_temple_3d.py`（494 fills）：大明宫西北三清殿——玄金
  配色道观；真八角三层八卦坛（相邻层旋转 22.5°、八方嵌两色
  羊毛卦象、中央太极）；三清神台金冠背光；三足焚香鼎青烟摇曳、
  龟蛇玄武石雕、丹房炼丹炉、幡杆牌楼。
- `qinwu_tower_3d.py`（417 fills）：兴庆宫南墙勤政务本楼——跨墙
  三券洞台基双层城楼重檐庑殿；南挑观乐大露台金座；楼下观乐
  广场百姓看棚八座、百戏台彩旗、马道登城、石狮金匾。
- `douting_post_3d.py`（491 fills）：都亭驿四方馆——驿务大堂驿程
  舆图墙（红路线金节点）、四方客房八间（含波斯使节房）、八间
  马厩拴马桩、驿站马车布幔、三层信鸽楼、井亭草料场。
- `tangchang_guan_3d.py`（480 fills）：唐昌观玉蕊花——中庭参天
  玉蕊神树（三层白花冠垂花枝）、四方落花径、题诗壁廊十二诗板
  与元白诗碑、花神小祠、扫花僧舍、放生池睡莲。

执行备份：`backups/world_backup_20260904_010324`；
施工日志：`logs/batch8_3d_20260904.log`（首跑中断于 sanqing/douting）与 `logs/batch8_3d_20260904_rerun.log`（完整重跑）。

批次内修正：`tangchang_guan_3d.py` 首版南缘（z 3600）会压到荐福寺北门（z 3496 起），已整体北移 130 格（地块调整为 x 1150..1500、z 3120..3470）后再执行，荐福寺山门完好。

第九批 3D 模块（总量 110,014 → 111,349 fills）：

- `xiaoyanta_3d.py`（380 fills）：荐福寺小雁塔深化——塔下负 y 地宫
  （石棺床+金函舍利+南磴道）、每层密檐金风铃、塔顶分节塔刹
  （覆钵+三重金相轮+仰月宝珠）、塔心竖井+螺旋梯贯通至顶、
  东南晨钟楼（悬链金钟+撞木）、雁塔晨钟碑、环形砖铺甬道。
- `taiyiyuan_3d.py`（471 fills）：皇城太医署——医术大堂（重檐庑殿）
  内针灸铜人（石英拼立像+金经络）；东厢百子柜药房（5x8 药柜
  阵+药碾药戥药炉）；南院 6x4 百草药圃+晾药架；署丞院、煎药棚、
  井亭、杏树（誉满杏林）。
- `jingjiao_bei_3d.py`（328 fills）：义宁坊大秦景教碑园——碑亭内
  3x3x11 石英巨碑（龟趺+碑首金色十字）、十字连珠纹照壁、传教
  士斜列墓碑阵（两通带金十字）、经卷堂、木桁架礼拜小堂（东向
  圆窗）、驼客歇脚处。
- `beacon_tower_3d.py`（156 fills）：终南山主峰烽火台——按山体
  公式实算峰尖 y=179，15x15 双层鼓座找平；11x11 收分实心烽燧
  （垛口+射孔+灯窗），顶面三足金盆狼烟三段摇曳；驻守房、储薪
  棚、令旗杆、下山磴道、西壁登顶踏步。

本批起执行前增加 bbox 冲突扫描步骤（新模块与全部既有地标
包围盒自动比对）。

执行备份：`backups/world_backup_20260904_142609`；
施工日志：`logs/batch9_3d_20260904.log`。

第十批 3D 模块（总量 111,349 → 113,530 fills）：

- `bangyuan_3d.py`（483 fills）：皇城贡院——东西两排十二间号舍
  （三面墙+半高板台+窄巷）、明远楼两层攒尖环廊、北面黄金榜墙
  （7 行 12 条黑字行）、龙门跃鱼牌坊、观榜棚报喜棚锣架、誊录所。
- `wenyuan_3d.py`（323 fills）：坊间文人园（辋川意境）——竹林环抱
  竹里馆（琴台诗集）、鹿柴柴门卧石鹿、辛夷坞花溪环抱花树、
  湖心临湖亭三折曲桥、邀月台、叠石曲径，无墙开放布局。
- `zhijinfang_3d.py`（492 fills）：官营织锦署——大工棚六台织机
  （经线铁栅+彩布卷）、八口彩水染缸阵、三层晾布长架 12 幅、
  蚕箔房缫丝锅蚕簇、锦缎展示堂三展台、染料库房。
- `bingjiao_3d.py`（386 fills）：官冰窖——三座覆土穹丘地下冰窖
  （负 y 窖内 packed_ice 冰阵+稻草隔热层+木板窖门）、运冰缓坡
  防滑横条、西墙外采冰渠卸冰栈台、管理房赐冰亭警示碑。
- `jinzouyuan_3d.py`（497 fills）：进奏院巷——六道藩镇院落（各具
  颜色道旗+文书堂+寝居+天井）、四方朝贡图照壁（铁栅路线汇金
  长安）、公共驿传马厩、文牍房、谯楼烽火信标。

执行备份：`backups/world_backup_20260904_152353`；
施工日志：`logs/batch10_3d_20260904.log`。

第十一批·细节深化 I（总量 113,530 → 114,837 fills）：

lib.py 新增 5 个细节原语：`add_roof_beasts`（正脊走兽队列）、
`add_eave_bells`（檐角风铃）、`add_balustrade`（望柱栏板）、
`add_door_studs`（门钉阵）、`add_pixel_mural`（像素壁画）。
执行前新增"贴附率"校验：细节方块须紧贴目标建筑（走兽基座
34/34 全部锚定正脊）。

- `palace_roof_detail_3d.py`（440 fills）：含元/麟德/宣政/紫宸四殿
  正脊走兽 22 只（每殿每脊一队）、垂兽 8 只、檐口瓦当交替点阵、
  翼角套兽+风铃、含元殿鸱吻金角加高。
- `palace_facade_detail_3d.py`（448 fills）：四殿南主立面斗拱密排
  带+四面转角三层斗拱簇、四大门 5x7 门钉金阵+铺首衔环、抱鼓
  石、含元殿龙纹御路（DARK 底金波纹云点）、匾额楹联、麟德殿
  顶层/紫宸月台望柱栏板。
- `pagoda_body_detail_3d.py`（419 fills）：大雁塔每层四面佛龛坐佛
  金背光、小雁塔 52 扇壶门（逐层错位）、两塔檐口瓦当、大雁塔刹
  链四垂、南门圣教序像素碑刻（add_pixel_mural 首秀）。

执行备份：`backups/world_backup_20260904_180309`；
施工日志：`logs/batch11_detail_20260904.log`。

第十二批·细节深化 II（总量 114,837 → 115,937 fills）：

- `gate_wall_detail_3d.py`（429 fills）：朱雀门/明德门像素石匾
  （"朱雀门""明德门"意象碑文+金印）、东市马面"长安"堡铭、八座
  敌楼礌石孔阵+挑檐、垛口旗台八座、门洞壁龛灯、四角楼风铃+栏
  板、马道登城碑。
- `mural_detail_3d.py`（418 fills）：四幅大幅像素壁画——含元殿东
  山墙敦煌飞天（24x14 青绿底飘带仙人）、青龙寺青绿山水（远山
  近水亭台）、大兴善寺说法图（金佛背光胁侍莲台）、碑林新照壁
  长安贡赋图（城楼驼队旌旗），各配碑记。
- `courtyard_life_detail_3d.py`（253 fills）：五院生活小品——日晷
  2、青铜香炉 5、承天门华表一对、檐下灯笼串 54 盏、太平缸 6、
  王府鹤纹影壁 2、拴马石上马石 4 组、水井辘轳 2。

执行备份：`backups/world_backup_20260904_183810`；
施工日志：`logs/batch12_detail_20260904.log`。

第十三批·B 方案新地标（总量 115,937 → 117,565 fills）：

- `taiye_boat_3d.py`（294 fills）：太液池东南净水域——双层画舫
  （螭首船头+朱栏平座+攒尖敞阁+橹楼宴案）、歌舞舫、水傀儡戏台
  （双层木筏+傀儡柜三小人+石槽水幕+乐师座）、彩旗浮标水道、
  岸宴帐红黄双帐；运行时断言避开蓬莱岛/石桥/陪岛/船坞。
- `jieshi_pailou_3d.py`（256 fills）：三座四柱三间跨街牌楼（西市/
  东市/朱雀街，朱雀座抬高跨御道避路缘石），冲天柱+双层额枋+
  彩绘花板+金匾+柱头彩灯、抱鼓石、市招幌子、石敢当、水沟盖板；
  对全部 88 模块 123,941 fill 做过精确碰撞扫描零冲突。
- `qujiang_night_3d.py`（278 fills）：曲江东南净水域夜宴灯船——
  主宴灯船（灯笼环 12+船头灯楼）、红黄副船、24 盏河灯环状漂
  流、水上灯架、东北实土带夜宴帐+灯谜墙+导引灯柱；首版与乐
  游园大平台（entertainment_venues 的 x≤5800,z≤5600 草台）冲突
  2033 格，已整体迁至净水域并复查归零。
- `tangsancai_kiln_3d.py`（398 fills）：西南隅唐三彩窑场——三座
  馒头窑（拱壳+火膛投柴孔+高烟囱狼烟）、晾坯场 15 件素坯、釉
  料缸阵、三彩成品棚（釉斑骆驼/马）、窑神碑、手推车。
- `baixi_chang_3d.py`（402 fills）：东市南口百戏场——红黄条纹
  大棚两座、十五格顶竿戴竿人偶、角抵擂台缠斗像、幻术黑帐、
  看棚六座、货郎担糖葫芦、五色幡门锣鼓架。

执行备份：`backups/world_backup_20260904_191103`；
施工日志：`logs/batch13_landmark_20260904.log`。

第十六批·市井生活（总量 117,565 → 118,163 fills，本批 +1,422）：

- `danfeng_plaza_3d.py`（391 fills）：丹凤门皇家广场——三层拼花
  石板+金边御道、东西阙台（三段收分+垛口，廊庑接门楼成凹字）、
  下马碑（像素碑文）、仪仗旗阵 10 杆、百官待朝廊、石狮宫灯。
- `street_traffic_3d.py`（289 fills）：朱雀大街辅路市井车马——货运
  牛车两辆（空心圆轮+驾辕牛）、青帷官轿+四轿夫、驮货驴队、独
  轮车、挑夫行人、歇脚亭路牌。
- `hanshi_qingming_3d.py`（323 fills）：东北郊寒食清明坟园——七座
  坟丘（碑铭供桌）、纸钱铺纸马、坟头插柳、高秋千、石祭台、禁
  火冷灶，与 tomb_spirit_way 神道保持 190 格缓冲。

执行备份：`backups/world_backup_20260905_020829`；
施工日志：`logs/batch16_street_20260905.log`。

补遗②：`food_street_3d` 已用 FAWE 管线重贴（42 秒，含 AIR 前后分组
修复），树干树叶 8/8 抽验落地。

第十七批·室内造像与苑寺（总量 121,051 → 124,911 fills，+3,860）：

- `palace_hall_v2_3d.py`（471 fills）：四大殿室内精装 v2——蟠龙
  金柱（金鳞螺旋+龙头 8 根）、藻井（金盘莲瓣宝珠）4 组、三联
  御屏（像素仙鹤山纹）、红帷幔 21 榀、朝服架、铜鹤灯、麟德殿
  歌台酒器。
- `temple_buddha_3d.py`（477 fills）：大兴善/慈恩/青龙三寺大雄殿
  造像群——三世佛金背光、十八罗汉持物两列、胁侍菩萨、千手观
  音像素壁（16x12）、幡杆蒲团供案。贴附率 100%。
- `ximingsi_3d.py`（531 fills）：延康坊西明寺——大雄殿三世佛、
  翻经院译场（译师坐像经案）、两层藏经阁、五层密檐塔、钟碑
  亭、双僧房院；迁坊前对全部 88 模块做过零碰撞扫描。
- `neiyuan_3d.py`（470 fills）：大明宫东北内苑——十二间御马厩
  （通风楼+驯马场）、射圃（弓道箭靶看席）、湖心水亭、玻璃花
  房、御库、鹿苑卧鹿。
- 卫国公府迁府：官邸原址（2600,3200）与西明寺地块冲突，府邸
  迁至坊内空地 (3350,3350)，fill 路径重贴 6/6 落地。

执行备份：`backups/world_backup_20260905_164330`。

补遗：`food_street_3d.py`（376 fills）——西市南门外市井饮食街。
首版选址（x 1850..2200, z 3150..3500）体素检测撞上清明渠
（z 3450..3550，3872 格）与坊门（47 格），迁移至 z 3560..3800
净空带；二次检测发现整地层铲掉秦王府墙基（1023 格），地基西
缘收回 x 2120→2100 后归零。

管线重要修复：schem 模式的 AIR 重放顺序——模块里"先清场后建
房"的 AIR fill 原本会在粘贴后统一重放，把刚贴好的树干/建筑下
半截抹掉。现按原始顺序拆分为"粘贴前清场 AIR"（replay before
paste）与"粘贴后雕刻 AIR"（replay after paste），食街 8/8 抽验
全部落地，TPS 20。

第十四批·夜景与坊门（总量 117,565 → 120,420 fills）：


- `night_lighting_3d.py`（495 fills）：全城夜景照明——朱雀大街地灯
  66 对、八大地标轮廓灯（四殿翼角+三门门楣+钟鼓楼）、太液/曲江
  湖岸矮脚灯 73 盏、东西市悬灯 40 盏、太液桥/曲江桥桥索灯 42 盏。
- `ward_gates_3d.py`（2360 fills）：51 座坊门——两柱一门悬山顶+
  白匾 5x5 像素坊名（52 字点阵字典，全真唐长安坊名：修真、金城、
  醴泉、永兴、长乐、平康、崇仁…），跳过市场区与地标坊 57 格。

第十五批·色彩规划与地形柔化（总量 120,420 → 121,018 fills）：

- `roof_color_zoning_3d.py`（274 fills）：屋顶色彩规划——宫城金脊
  垂脊标饰 12 枚、皇城官署黄脊 22 条、东西市深灰脊 12 条、坊区
  灰脊 12 条、佛寺青脊补齐 8 条、朱雀街口五行色图例壁画。
- `mountain_smooth_3d.py`（324 fills）：终南山柔化——五段鞍部
  填谷梯台坡链（每段相向 6 级坡+山肩），碎石裙、山脊小径山松、
  灌木补丁、山涧芦苇；峰顶与烽火台/佛龛区零接触（y≤100 红线）。

工程优化（本阶段同批落地）：
- FAWE 蓝图管线：`run_all_phases --schem` 每模块一次 FAWE 粘贴
  （体积分片 x-banding + 贴后探针自检 + 3 次重试自愈 + bluemap
  暂停避内存竞争），实测 2855 fills 全城模块 2m25s 完成（旧管线
  估 20-40 分钟）。AIR 雕刻仍走 /fill。
- `verify_modules.py`：bbox/体素碰撞/贴附率三合一预检工具。
- 备份轮转 `rotate_backups.sh`（保留最近 3 份+每月归档）；备份目
  录挂载宿主机（原先困在容器层，9 份 3GB）。
- BlueMap 网页地图（8100 端口）已验证可用并强制全图重渲染。

执行备份：`backups/world_backup_20260905_000017`（夜景/坊门）、
`backups/world_backup_20260905_010516`（色彩/地形）；
施工日志：`logs/batch14_light_ward_20260905.log`、
`logs/batch15_zone_terrain_20260905.log`。

## 八、后续可选的优化（未实施）

以下项因改动面较大，本次**未做**，如需可继续：

- 城门/寺庙模块抽象复用（`add_city_gate_complex`、`build_temple_complex`）
- 所有模块统一 `--single` 参数
- 执行日志持久化（`--log PATH`）
- 统一 dry-run 测试脚本（`tests/test_all_modules.py`）

如需要这些，告诉我即可继续。
