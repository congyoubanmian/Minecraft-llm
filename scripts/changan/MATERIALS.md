# Tang Chang'an Material Semantics

本文件说明 `scripts/changan/lib.py` 中 `Materials` 调色板各材质在唐代长安城建筑中的语义与推荐用法，避免后续模块风格漂移。

| Constant | Minecraft Block | 对应唐代材质 / 构件 | 推荐用途 |
|---|---|---|---|
| `RED_WALL` | `red_terracotta` | 夯土/宫墙红土 | 宫殿、寺庙、官署主墙体；城门城楼主体 |
| `RED_WALL_ALT` | `red_concrete` | 朱红墙面 | 皇家建筑内墙、柱体、匾额底色 |
| `RED_GLAZED` | `red_glazed_terracotta` | 琉璃红釉瓦 | 高等级宫殿屋脊点缀 |
| `STONE` | `stone_bricks` | 青石砖 | 城墙、道路、普通官署、民间大宅墙体 |
| `MOSS_STONE` | `mossy_stone_bricks` | 苔痕古砖 | 老城墙、寺庙、古墓、神道石阶 |
| `CRACKED_STONE` | `cracked_stone_bricks` | 风化裂砖 | 废弃角楼、废墟、古墓表面 |
| `DARK` | `deepslate_tiles` | 深灰板岩 | 城墙垛口、排水沟盖板、屋顶深色装饰 |
| `DARK_BRICKS` | `deepslate_bricks` | 深灰砖 | 城墙、敌楼、水关石砌 |
| `ANDESITE` | `polished_andesite` | 磨光花岗石 | 御道、街道铺装、排水沟衬砌、井台 |
| `GRANITE` | `polished_granite` | 红花岗岩 | 王府台基、宫殿基座、道路路缘 |
| `SMOOTH` | `smooth_stone` | 青石/灰砖 | 普通道路、桥梁桥面、广场铺地 |
| `COBBLE` | `cobblestone` | 卵石 | 坊巷小路、农郊土路、排水沟底 |
| `GRAY_CONCRETE` | `gray_concrete` | 素灰/雨水井 | 雨水井盖、下水道口、现代感不强的素色块 |
| `IRON_BARS` | `iron_bars` | 铁栅/铁箅子 | 水关栅栏、卫兵长矛、井盖 |
| `GOLD` | `gold_block` | 鎏金/鎏金铜饰 | 脊兽、鸱吻、匾额、塔刹、龙椅 |
| `GOLD_ACCENT` | `gilded_blackstone` | 鎏金黑石 | 高等级宫殿檐角、塔顶、祭祀器物 |
| `YELLOW_GLAZED` | `yellow_glazed_terracotta` | 黄琉璃瓦 | 皇家专用屋顶（理论上，Minecraft 中用 prismarine 代替更美观） |
| `ROOF_GREEN` | `dark_prismarine` | 绿琉璃瓦 | 唐代宫殿、寺庙主流屋顶 |
| `ROOF_GREEN_SLAB` | `dark_prismarine_slab` | 绿瓦檐 | 屋檐边缘、瓦当 |
| `ROOF_BLUE` | `prismarine_bricks` | 蓝琉璃瓦 | 次要宫殿、楼阁、民居大宅屋顶 |
| `ROOF_BLUE_SLAB` | `prismarine_brick_slab` | 蓝瓦檐 | 次要建筑屋檐 |
| `ROOF_DARK` | `deepslate_tiles` | 黑瓦 | 北方民居、储藏室、低等级建筑 |
| `LOG` | `dark_oak_log` | 原木/柱木 | 柱、梁、斗拱、井架、灯杆 |
| `WOOD` | `dark_oak_planks` | 木板/梁架 | 门窗、梁架、地板、室内隔断 |
| `SPRUCE` | `spruce_planks` | 杉木 | 民间建筑、市场摊位、农具 |
| `BIRCH` | `birch_planks` | 桦木/白木 | 高级门窗、家具、桥梁栏杆 |
| `FENCE` | `dark_oak_fence` | 木栅栏 | 花园围栏、市场摊位、宫廷围栏 |
| `WHITE` | `white_concrete` | 白灰/白玉 | 宫殿基座、台阶、粉墙、石桥 |
| `WHITE_TERRACOTTA` | `white_terracotta` | 白陶土 | 官署、民居粉墙、磨光地面 |
| `QUARTZ` | `quartz_block` | 大理石/石英 | 高等级台阶、碑亭、神道石 |
| `GLASS` | `glass_pane` | 明瓦/窗纸 | 宫殿、寺庙、大宅窗户 |
| `RED_STAINED_GLASS` | `red_stained_glass_pane` | 红纱/朱色窗纸 | 皇家建筑、寺庙佛殿窗户 |
| `LANTERN` | `lantern` | 灯笼 | 夜市、节日灯会、寺庙香火 |
| `SEA_LANTERN` | `sea_lantern` | 宫灯/石灯 | 宫殿、寺庙、御道、灯塔 |
| `REDSTONE_LAMP` | `redstone_lamp` | 石灯/烛台 | 宫殿室内、密室照明 |
| `RED_WOOL` | `red_wool` | 红布/朱红绸 | 酒旗、灯笼、婚礼、皇家仪仗 |
| `BLUE_WOOL` | `blue_wool` | 蓝布/靛蓝绸 | 商铺招牌、布匹、僧袍 |
| `YELLOW_WOOL` | `yellow_wool` | 黄布/鎏金绸 | 皇家、佛寺、贵族仪仗 |
| `GREEN_WOOL` | `green_wool` | 绿布/荷叶 | 植物、湖水荷叶、布匹 |
| `BLACK_WOOL` | `black_wool` | 墨/玄色绸 | 匾额文字、士兵盔甲、道观 |
| `WHITE_WOOL` | `white_wool` | 白布/绢帛 | 丧仪、雪、白帆、诗纸 |
| `PINK_WOOL` | `pink_wool` | 粉彩/桃花 | 花卉、少女服饰、荷花 |
| `WATER` | `water` | 水体 | 护城河、湖泊、排水沟、水井 |
| `LEAVES` | `oak_leaves` | 树叶 | 行道树、庭院树、远景植被 |
| `TREE_LOG` | `oak_log` | 树干 | 行道树、槐树、古树 |
| `GRASS` | `grass_block` | 草地 | 花园、庭院、郊外 |
| `DIRT` | `dirt` | 泥土 | 农田、土坡、地基 |
| `AIR` | `air` | 空气 | 门洞、窗洞、雕刻镂空 |

## 使用原则

1. **皇家 vs 民间**：皇家优先 `RED_WALL` + `GOLD` + `ROOF_GREEN`；民间优先 `STONE` + `WOOD` + `ROOF_DARK`。
2. **宗教差异**：佛寺用 `RED_WALL` + `GOLD`；道观可用 `DARK` + `BLACK_WOOL`；景教/祆教可用 `WHITE` + `QUARTZ`。
3. **等级感**：越高等级建筑，`ANDESITE`/`GRANITE`/`QUARTZ` 使用越多，颜色越鲜明。
4. **替代说明**：唐代并无 prismarine，但 Minecraft 中 `dark_prismarine` 的绿釉质感最接近唐琉璃瓦，因此约定俗成使用。

## 后续新增材质

新增 `Materials` 常量时，请同步更新本文件，注明对应唐代构件与使用场景。
