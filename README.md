# Minecraft LLM Builder

这是一个本地运行的 Minecraft AI 建筑生成实验项目。目标是把「图片 / 文字 / 多轮对话」转换成 Minecraft 建筑蓝图，支持网页预览、材料统计，并自动粘贴到 Paper 服务器里。

当前已经跑通的链路：

```text
上传图片或输入文字
  -> 图片分析 / 对话上下文
  -> Codex CLI 生成 Minecraft BuildPlan JSON DSL
  -> DSL 渲染成统一 BlockList
  -> 导出 preview.json / materials.json / .schem
  -> Mineflayer Bot 调用 FAWE 粘贴到 Paper 服务器
```

## 项目思路

一开始如果让 LLM 直接「看图 -> 生成建筑」，很容易生成泛化建筑：有屋顶、有墙、有窗，但不像目标建筑。这个项目把问题拆成几层：

1. **LLM 不直接操作 Minecraft**  
   LLM 只负责生成结构化 DSL，也就是 `BuildPlan JSON`。这样输出可校验、可重试、可编辑。

2. **DSL 不直接写 schematic**  
   DSL 先渲染成统一的 `BlockList`，再由 `BlockList` 同时导出 `.schem`、网页预览和材料统计。

3. **网页先预览，再粘贴进游戏**  
   用户可以在浏览器里看到体量、材料、方块数和坐标，再决定是否粘贴。

4. **先做建筑设计规约，再生成 Minecraft 施工代码**
   复杂建筑不再只靠“看图识别后直接堆方块”。Planner 会先在 `analysis.design_spec` 里确定建筑类型、比例、轴网、模块 bounding box、接口面、材料表和质量检查，再把这份设计规约翻译成 DSL parts。

5. **多轮对话持续修改同一个项目**
   每个项目都有自己的 `state.json`、`plan.json`、`preview.json` 和对话记录，后续可以继续要求“更高一点”“飞檐更明显”“换材质”“不要覆盖旧建筑”。

6. **坐标自动分配，避免多个建筑互相覆盖**
   后端会根据已有项目 bounds 分配新的粘贴位置，并把出生点放在建筑外侧。

核心中间层是：

```text
DSL -> BlockList -> .schem
DSL -> BlockList -> preview.json
DSL -> BlockList -> materials.json
```

这个设计后面也能继续扩展到：

```text
.litematic / .schem 导入 -> BlockList -> 网页预览 -> 转换/粘贴
```

## 当前功能

- Vue 3 网页工作台
- 首页项目列表
- 创建新项目
- 上传图片和输入提示词
- 多轮对话继续修改老项目
- Three.js 3D 预览
- WebGL 不可用时自动降级 Canvas 2D 预览
- 下载 `.schem`
- 查看材料统计
- 设置粘贴点和出生点
- 自动分配不重叠坐标
- 一键粘贴到 Minecraft
- Paper + FAWE 服务端
- Mineflayer Bot 执行 `/schem load` 和 `//paste -a`
- RCON 设置世界出生点

## 技术栈

```text
前端：Vue 3 + Three.js
后端：FastAPI
LLM 规划：Codex CLI
DSL 校验：Pydantic
Schematic 生成：mcschematic
Minecraft 服务端：Paper 1.21.4
世界编辑：FastAsyncWorldEdit
Bot：Mineflayer
通信：HTTP + RCON + 游戏内命令
```

## 目录结构

```text
Minecraft-llm/
├── backend/
│   ├── main.py                       # FastAPI 路由、项目状态、粘贴、坐标分配
│   ├── ai/
│   │   ├── planner.py                 # Codex CLI 规划器
│   │   └── vision.py                  # 图片分析占位模块
│   ├── blocks/
│   │   └── block_list.py              # 统一方块中间层
│   ├── dsl/
│   │   └── schema.py                  # BuildPlan DSL schema
│   ├── schematic/
│   │   └── generator.py               # DSL 渲染、schem/preview/materials 输出
│   ├── minecraft/
│   │   ├── bot_client.py
│   │   ├── fawe.py
│   │   └── rcon.py
│   └── projects/                      # 项目状态和生成文件
├── bot/
│   └── bot.js                         # Mineflayer HTTP Bot
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── style.css
├── scripts/
│   ├── generate_tianning_octagonal_v3.py
│   └── ...                            # 示例建筑生成脚本
├── server/                            # Paper 服务端数据，默认不提交
├── docker-compose.yml
└── README.md
```

## 快速启动

需要先安装 Docker 和 Docker Compose。

```bash
docker compose up --build
```

打开网页：

```text
http://localhost:8000
```

Java 版 Minecraft 加入服务器：

```text
localhost:25565
```

默认端口：

```text
8000   FastAPI + Vue 网页
25565  Minecraft Java 服务器
25575  RCON
3001   Mineflayer Bot HTTP API
19132  Bedrock/Geyser UDP 端口，如果服务端已安装相关插件
```

注意：不要把 RCON、Bot API、后端 API 直接暴露到公网。

## 本地开发模式

如果本机已经登录了 Codex CLI，推荐让 Minecraft 和 Bot 继续跑在 Docker 里，后端直接跑在宿主机。这样 FastAPI 可以直接调用本机 Codex。

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
./scripts/run_backend_codex_local.sh
```

常用环境变量：

```text
PLANNER_MODE=codex
CODEX_COMMAND=codex
CODEX_MODEL=
CODEX_TIMEOUT_SECONDS=420

RCON_HOST=localhost
RCON_PORT=25575
RCON_PASSWORD=minecraft-ai-builder
BOT_URL=http://localhost:3001

PASTE_ENABLED=true
```

如果没有 Codex CLI，可以用静态 fallback：

```text
PLANNER_MODE=static
```

## 使用流程

1. 打开 `http://localhost:8000/#/`
2. 首页会显示项目列表
3. 点击 `创建新项目`
4. 上传图片或输入文字描述
5. 等待 Codex 生成 DSL 和 schematic
6. 在网页中查看预览
7. 继续对话修改建筑
8. 检查粘贴点和出生点
9. 点击 `粘贴到 Minecraft`
10. 进入游戏查看建筑

项目页支持：

```text
预览建筑
下载 .schem
查看 DSL
查看图片分析
查看生成诊断
查看 RCON 返回
修改粘贴坐标
修改出生坐标
继续多轮对话
重新生成并粘贴
```

## API

主要接口：

```text
GET  /api/health
GET  /api/projects
POST /api/projects
GET  /api/projects/{project_id}
POST /api/projects/{project_id}/chat
POST /api/projects/{project_id}/paste
POST /api/projects/{project_id}/placement
GET  /api/projects/{project_id}/preview
GET  /api/projects/{project_id}/materials
GET  /api/projects/{project_id}/analysis-report
GET  /api/projects/{project_id}/schematic
GET  /api/library
```

旧版单任务接口仍保留：

```text
POST /api/builds
GET  /api/builds/{task_id}
GET  /api/builds/{task_id}/preview
GET  /api/builds/{task_id}/schematic
```

## BuildPlan DSL

LLM 最终生成的是一个 JSON DSL：

```json
{
  "name": "project_example",
  "size": [48, 28, 40],
  "origin": [0, 64, 0],
  "palette": {
    "wall": "smooth_quartz",
    "roof": "oxidized_cut_copper"
  },
  "analysis": {
    "selected_template": "pagoda_stack",
    "design_spec": {
      "building_type": "pagoda",
      "scale_intent": "96 x 202 x 96 landmark tower",
      "grid": ["13 tiers", "tier_height=12", "octagonal symmetry"],
      "modules": [
        {
          "name": "main_tower",
          "role": "mass",
          "bbox": [[12, 12, 12], [84, 176, 84]]
        }
      ],
      "material_schedule": ["body=smooth_quartz", "roof=oxidized_cut_copper"],
      "quality_checks": ["八角轮廓清晰", "每层都有飞檐"]
    },
    "intent": ["简短结构化设计说明"]
  },
  "parts": []
}
```

支持的部件类型：

```text
box
roof_gable
window_grid
window
door
stairs
slab
cylinder
blocks
octagonal_tower
octagonal_roof
octagonal_eave
vajra_spire
mini_pagoda_ring
facade_panel_ring
component
```

为了生成更像宝塔的建筑，项目新增了几个偏建筑语义的部件：

```text
octagonal_tower      八角塔身
octagonal_eave       八角飞檐，带外挑和翘角
facade_panel_ring    八面重复窗格/匾额
mini_pagoda_ring     塔基周围小白塔
vajra_spire          金刚宝座式金色塔刹
```

## 材料库和组件库

项目现在支持数据驱动的材料库、组件库、模板库和设计规约：

```text
backend/library/materials.json
backend/library/components.json
backend/library/templates.json
backend/library/design_contract.json
```

材料库用于描述一组建筑风格常用方块，例如：

```text
tianning_pagoda      白玉塔身、青铜飞檐、金色塔刹
jiangnan_wood        江南白墙、深色木构、灰瓦
modern_concrete      现浇混凝土、玻璃、外露结构
stone_arch_bridge    石拱桥
suspension_bridge    悬索桥
modern_glass_office  现代玻璃办公楼
ancient_temple       中式寺庙/殿堂
water_town           江南水乡
industrial_steel     工业钢结构
```

模板库用于先选建筑范式，避免把某次成功的组件乱套到不适合的建筑上。例如：

```text
pagoda_stack          宝塔/寺庙塔
temple_hall           中式殿堂/牌楼
jiangnan_water_town   江南水乡街区
modern_glass_gate     现代门形地标/大裤衩类建筑
office_tower          普通现代办公楼
stone_arch_bridge     石拱桥
suspension_bridge     悬索桥/斜拉桥
```

组件库用于把常见结构拆成可复用的小组件。每个组件现在带有 category、styles、building_types、stages、scale_range、parameter_ranges、applicability 和 avoid_when。LLM 可以引用这些组件，放大、缩小、平移、改参数、换材料，再叠加成完整建筑。

当前组件示例：

```text
pagoda_tier                 单层八角宝塔组件
mini_pagoda_cluster         塔基小白塔环绕
stone_arch_bridge           石拱桥
concrete_podium             现浇混凝土基座/裙房
suspension_bridge_segment   悬索桥片段
```

DSL 中使用组件：

```json
{
  "type": "component",
  "name": "pagoda_tier",
  "at": [0, 24, 0],
  "scale": 1.25,
  "parameters": {
    "radius": 18,
    "height": 8,
    "eave_overhang": 6
  },
  "materials": {
    "body": "smooth_quartz",
    "roof": "oxidized_cut_copper",
    "trim": "cut_copper"
  }
}
```

这意味着以后可以让 LLM 组合：

```text
3 个 pagoda_tier 叠成塔身
1 个 mini_pagoda_cluster 做塔基
1 个 stone_arch_bridge 做入口桥
1 个 concrete_podium 做现代混凝土平台
若干 box/window/slab 做自定义细节
```

## 设计规约工作流

更合理的生成链路应该接近现实建筑流程：

```text
图片/文字
  -> 识别建筑类型、风格、比例、关键轮廓
  -> 选择模板
  -> 生成 design_spec
  -> 检查尺寸、轴网、模块接口、材料表
  -> 翻译成 BuildPlan parts
  -> 渲染 preview / materials / analysis_report / schem
```

`design_spec` 是中间的“设计图/施工图”：

```text
building_type       建筑类型
selected_template   模板
scale_intent        目标比例和尺寸
grid                轴网、层高、开间、跨度
modules             地基、主体、空洞、立面、屋顶、室内、灯光等模块
interfaces          模块之间的接口面
material_schedule   材料表
quality_checks      生成后要检查的要点
```

如果单次 LLM 输出太大，后续可以按模块分部调用：

```text
先生成全局 design_spec
  -> 地基模块
  -> 主体模块
  -> void/air 清空模块
  -> 立面模块
  -> 屋顶模块
  -> 室内模块
  -> 灯光和细节模块
  -> 合并 BlockList
```

关键是所有模块必须使用同一个本地坐标系，并且每个模块都有明确 bbox 和 interface。这样切口长度、楼层高度、桥梁接口、屋顶边界才能对齐，不会出现拼接错位。

## 生成诊断

每次生成时后端会额外输出：

```text
project_xxx.analysis.json
```

网页右侧会显示摘要，包括：

```text
模板猜测
parts 数量
design_spec 模块数量
玻璃比例
灯光比例
组件类别
警告列表
```

例如古建玻璃比例过高、现代高层灯光太少、宝塔没有使用八角层组件、大型建筑缺少模块化设计规约，都会在诊断里提示。

验证组件库：

```bash
.venv/bin/python scripts/test_component_library.py
```

## Schematic 粘贴流程

`.schem` 会写到：

```text
server/plugins/FastAsyncWorldEdit/schematics
```

后端调用 Mineflayer Bot 执行：

```text
/tp BuilderBot <x> <y> <z>
/schem load <schematic_name>
//paste -a
```

随后通过 RCON 设置出生点：

```text
/setworldspawn <spawn_x> <spawn_y> <spawn_z>
```

坐标分配逻辑会读取已有项目的 bounds，自动寻找一个不重叠的位置，并留出 margin。

## 示例：常州天宁宝塔 V3

生成脚本：

```bash
.venv/bin/python scripts/generate_tianning_octagonal_v3.py
```

当前 V3 示例：

```text
project_id: tianning_oct_v3
尺寸: 96 x 202 x 96
总方块: 183554
预览方块: 183554
是否抽样: false

preview:
backend/projects/tianning_oct_v3/project_tianning_oct_v3.preview.json

materials:
backend/projects/tianning_oct_v3/project_tianning_oct_v3.materials.json

schem:
server/plugins/FastAsyncWorldEdit/schematics/project_tianning_oct_v3.schem
```

V3 的目标是更像常州天宁宝塔：

```text
更高更瘦的十三层八角塔身
每层都有外挑青铜飞檐
白色石材/玉石感塔身
顶部金刚宝座式金色塔刹
塔基周围一圈小白塔
八面重复窗格和牌匾
```

主要材料：

```text
smooth_quartz
oxidized_cut_copper
stone_bricks
exposed_cut_copper
quartz_bricks
cut_copper
gold_block
cyan_stained_glass_pane
```

## 外部蓝图导入

目前项目可以下载外部蓝图做检查，但还没有完整实现导入转换。有些站点返回的是 `.litematic`，不是 FAWE 可直接粘贴的 `.schem`。

后续计划：

```text
.litematic / .schem 读取
  -> BlockList
  -> 网页预览
  -> 材料统计
  -> 转换为 FAWE 可用 .schem
```

这个方向借鉴了 McSTools 的统一结构数据思路，但当前实现没有复制其代码。

## 验证命令

后端和脚本编译检查：

```bash
python3 -m compileall backend scripts
```

前端 JS 语法检查：

```bash
node --check frontend/app.js
```

生成天宁宝塔 V3：

```bash
.venv/bin/python scripts/generate_tianning_octagonal_v3.py
```

检查后端：

```bash
curl http://127.0.0.1:8000/api/health
```

检查项目列表：

```bash
curl http://127.0.0.1:8000/api/projects
```

## 已知限制

- `backend/ai/vision.py` 目前还是占位实现，图片理解能力有限。
- 当前效果更多依赖 Codex CLI 的图片输入和用户文字描述。
- 网页预览不是完整 Minecraft 渲染器，只是方块体量和颜色预览。
- 云桌面或显卡受限环境可能无法创建 WebGL，上线了 Canvas fallback。
- 大型 schematic 粘贴需要等待 FAWE 执行完成。
- Paper 当前使用 `ONLINE_MODE=false` 方便 Bot 登录，只适合本地/内网实验。
- 不建议把 RCON、Bot API、后端 API 暴露到公网。

## Git 提交建议

不要提交这些本地运行数据：

```text
.env
.venv/
backend/uploads/
backend/generated_plans/
backend/projects/
server/
downloads/
McSTools/
```

`server/` 里包含 Minecraft 世界、插件和运行数据，体积大且包含本地状态。  
`backend/projects/` 里包含生成结果和预览 JSON，适合本地留存，不适合作为源码提交。

## 下一步计划

- 接入真正的视觉模型，例如 GPT-4o / Qwen-VL。
- 实现 `.litematic` / `.schem` 导入到 `BlockList`。
- 继续扩充组件库，例如廊桥、拱券、斗拱、悬索桥塔、混凝土框架、幕墙单元。
- 预览支持分层、材料过滤、LOD 和点击查看方块。
- 增加任务队列，支持多个大项目并行排队。
- 增加材质包映射，让建筑能针对不同材质包优化。
- 粘贴前自动清理区域、铺平台、加照明和路径。
