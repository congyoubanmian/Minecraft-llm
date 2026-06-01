const { createApp } = Vue;

const BUSY_STATUSES = ["queued", "analyzing", "planning", "generating_schematic", "pasting"];
const TERMINAL_STATUSES = ["done", "failed", "cancelled"];
const PROJECT_STATUS_FILTERS = [
  "all",
  "done",
  "busy",
  "failed",
  "cancelled",
  "with_blueprint",
  "with_schematic",
  "missing_snapshots",
];
const PROJECT_SORTS = ["updated_desc", "name_asc", "blocks_desc", "volume_desc", "snapshots_desc"];

createApp({
  mixins: [window.McPreview, window.McHelpers],
  data() {
    return {
      health: "checking",
      route: "list",
      projects: [],
      projectSearch: "",
      projectStatusFilter: "all",
      projectSort: "updated_desc",
      projectListLoading: false,
      world: null,
      placements: [],
      worldLoading: false,
      worldAction: "",
      projectListAction: "",
      moduleAction: "",
      moduleLogAction: "",
      modulePlan: null,
      modulePlanLoading: false,
      library: {
        materials: {},
        components: {},
        templates: {},
      },
      file: null,
      imagePreviewUrl: "",
      initialPrompt: "",
      chatInput: "",
      submitting: false,
      project: null,
      preview: null,
      previewMode: "surface",
      selectedBlueprintModule: null,
      placementForm: {
        x: null,
        y: null,
        z: null,
        spawn_x: null,
        spawn_y: null,
        spawn_z: null,
      },
      pollTimer: null,
      ws: null,
      renderer: null,
      canvas2d: null,
      scene: null,
      camera: null,
      previewGroup: null,
      renderMode: "loading",
      resizeObserver: null,
      drag: {
        active: false,
        x: 0,
        y: 0,
      },
    };
  },
  computed: {
    busy() {
      return BUSY_STATUSES.includes(this.project?.status);
    },
    canChat() {
      return Boolean(this.project && this.chatInput.trim() && !this.busy);
    },
    messages() {
      return this.project?.messages || [];
    },
    materialEntries() {
      return Object.entries(this.library.materials || {});
    },
    componentEntries() {
      return Object.entries(this.library.components || {});
    },
    templateEntries() {
      return Object.entries(this.library.templates || {});
    },
    analysisReport() {
      return this.project?.analysis_report || null;
    },
    designBlueprint() {
      return this.analysisReport?.design_blueprint || null;
    },
    blueprintStages() {
      return this.designBlueprint?.stages || [];
    },
    blueprintModules() {
      return this.designBlueprint?.modules || [];
    },
    blueprintInterfaces() {
      return this.designBlueprint?.interfaces || [];
    },
    moduleRconEntries() {
      const operations = this.project?.module_operations || [];
      if (operations.length) {
        return operations
          .map((operation, index) => ({
            key: `${operation.created_at || index}:${operation.module}:${operation.action}`,
            name: operation.module,
            action: operation.action,
            label: this.moduleActionLabel(operation.action),
            count: operation.command_count ?? operation.commands?.length ?? 0,
            created_at: operation.created_at,
            blocks: operation.blocks,
            commands: (operation.commands || []).slice(-4),
          }))
          .reverse();
      }
      return Object.entries(this.project?.module_rcon || {})
        .map(([key, commands]) => {
          const [name, action = "paste"] = key.split(":");
          const list = Array.isArray(commands) ? commands : [];
          return {
            key,
            name,
            action,
            label: this.moduleActionLabel(action),
            count: list.length,
            commands: list.slice(-4),
          };
        })
        .reverse();
    },
    visibleProjects() {
      const query = this.projectSearch.trim().toLowerCase();
      const status = this.projectStatusFilter;
      const searched = query
        ? this.projects.filter((item) => this.projectSearchText(item).includes(query))
        : [...this.projects];
      const filtered = status === "all" ? searched : searched.filter((item) => this.projectMatchesStatusFilter(item, status));
      return filtered.sort((left, right) => this.compareProjects(left, right, this.projectSort));
    },
    previewMeta() {
      if (!this.preview) return "暂无预览";
      const size = this.preview.size?.join(" x ") || "-";
      const sampled = this.preview.sampled ? "，已抽样" : "";
      const sourceCount = this.preview.preview_source_count || this.preview.preview_count || 0;
      const previewKind = this.preview.mode === "surface" ? `外表面 ${sourceCount}` : `完整 ${this.preview.block_count || 0}`;
      const module = this.selectedBlueprintModule ? `，模块 ${this.selectedBlueprintModule.name}` : "";
      const mode = this.renderMode === "webgl" ? "WebGL 3D" : "Canvas 2D";
      return `${size}，${previewKind} 个方块，当前加载 ${this.preview.preview_count}${sampled}${module}，${mode}`;
    },
  },
  mounted() {
    this.loadProjectListPrefs();
    this.checkHealth();
    this.loadLibrary();
    window.addEventListener("hashchange", this.syncRoute);
    this.syncRoute();
  },
  beforeUnmount() {
    this.stopPolling();
    this.destroyPreviewRenderer();
    window.removeEventListener("hashchange", this.syncRoute);
  },
  methods: {
    async checkHealth() {
      try {
        const response = await fetch("/api/health");
        this.health = response.ok ? "online" : "offline";
      } catch {
        this.health = "offline";
      }
    },
    apiFetch(url, options = {}) {
      if (this.apiKey) {
        options.headers = { ...options.headers, Authorization: `Bearer ${this.apiKey}` };
      }
      return fetch(url, options);
    },
    saveApiKey() {
      if (this.apiKey) {
        localStorage.setItem("mc_builder_api_key", this.apiKey);
      } else {
        localStorage.removeItem("mc_builder_api_key");
      }
    },
    async loadLibrary() {
      try {
        const response = await this.apiFetch(`/api/library?ts=${Date.now()}`);
        if (!response.ok) throw new Error(await response.text());
        this.library = await response.json();
      } catch (error) {
        console.error(error);
        this.library = { materials: {}, components: {}, templates: {} };
      }
    },
    syncRoute() {
      const match = window.location.hash.match(/^#\/project\/([a-zA-Z0-9_-]+)$/);
      if (match) {
        this.route = "project";
        this.$nextTick(() => {
          this.ensurePreviewRenderer();
          this.fetchProject(match[1]);
        });
        return;
      }

      if (window.location.hash === "#/new") {
        this.route = "project";
        this.project = null;
        this.preview = null;
        this.previewMode = "surface";
        this.selectedBlueprintModule = null;
        this.modulePlan = null;
        this.chatInput = "";
        this.$nextTick(() => {
          this.ensurePreviewRenderer();
          this.clearPreview();
        });
        return;
      }

      this.route = "list";
      this.stopPolling();
      this.project = null;
      this.preview = null;
      this.previewMode = "surface";
      this.selectedBlueprintModule = null;
      this.modulePlan = null;
      this.clearPreview();
      this.destroyPreviewRenderer();
      this.loadProjects();
      this.loadWorldStatus();
    },
    goHome() {
      window.location.hash = "#/";
    },
    newProject() {
      this.file = null;
      if (this.imagePreviewUrl) URL.revokeObjectURL(this.imagePreviewUrl);
      this.imagePreviewUrl = "";
      this.initialPrompt = "";
      this.chatInput = "";
      window.location.hash = "#/new";
    },
    openProject(projectId) {
      window.location.hash = `#/project/${projectId}`;
    },
    async loadProjects() {
      this.projectListLoading = true;
      try {
        const response = await this.apiFetch(`/api/projects?ts=${Date.now()}`);
        if (!response.ok) throw new Error(await response.text());
        const payload = await response.json();
        this.projects = payload.projects || [];
      } catch (error) {
        this.projects = [];
        console.error(error);
      } finally {
        this.projectListLoading = false;
      }
    },
    async loadWorldStatus() {
      this.worldLoading = true;
      try {
        const [worldResponse, placementResponse] = await Promise.all([
          this.apiFetch(`/api/world/status?ts=${Date.now()}`),
          this.apiFetch(`/api/placements?ts=${Date.now()}`),
        ]);
        if (!worldResponse.ok) throw new Error(await worldResponse.text());
        if (!placementResponse.ok) throw new Error(await placementResponse.text());
        this.world = await worldResponse.json();
        const placementPayload = await placementResponse.json();
        this.placements = placementPayload.placements || [];
      } catch (error) {
        this.world = { error: error instanceof Error ? error.message : String(error) };
      } finally {
        this.worldLoading = false;
      }
    },
    async backupWorld() {
      this.worldAction = "backup";
      try {
        const response = await this.apiFetch("/api/world/backup", { method: "POST" });
        if (!response.ok) throw new Error(await response.text());
        const payload = await response.json();
        await this.loadWorldStatus();
        alert(`备份完成：${payload.backup}`);
      } catch (error) {
        alert(`备份失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.worldAction = "";
      }
    },
    async rebuildPlacements() {
      this.worldAction = "rebuild";
      try {
        const response = await this.apiFetch("/api/placements/rebuild", { method: "POST" });
        if (!response.ok) throw new Error(await response.text());
        await this.loadWorldStatus();
        alert("区域索引已从项目状态重建。");
      } catch (error) {
        alert(`重建失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.worldAction = "";
      }
    },
    async teleportLatestPlacement() {
      const latest = this.placements[0];
      if (!latest) return;
      this.worldAction = "teleport";
      try {
        const response = await this.apiFetch(`/api/placements/${latest.project_id}/teleport`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
        if (!response.ok) throw new Error(await response.text());
        await this.loadWorldStatus();
      } catch (error) {
        alert(`传送失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.worldAction = "";
      }
    },
    async archiveLatestPlacement() {
      const latest = this.placements[0];
      if (!latest || !confirm(`归档区域 ${latest.project_name || latest.project_id}？`)) return;
      this.worldAction = "archive";
      try {
        const response = await this.apiFetch(`/api/placements/${latest.project_id}/archive`, { method: "POST" });
        if (!response.ok) throw new Error(await response.text());
        await this.loadWorldStatus();
      } catch (error) {
        alert(`归档失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.worldAction = "";
      }
    },
    async clearLatestPlacement() {
      const latest = this.placements[0];
      if (!latest) return;
      const confirmation = prompt(`清空区域 ${latest.project_name || latest.project_id}。请输入 CLEAR_AREA 确认。`);
      if (confirmation !== "CLEAR_AREA") return;
      this.worldAction = "clear";
      try {
        const response = await this.apiFetch(`/api/placements/${latest.project_id}/clear`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ confirm: confirmation }),
        });
        if (!response.ok) throw new Error(await response.text());
        await this.loadWorldStatus();
        alert("区域已清空。");
      } catch (error) {
        alert(`清空失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.worldAction = "";
      }
    },
    async resetWorld() {
      const confirmation = prompt("这会备份并重置 Minecraft 世界。请输入 RESET_WORLD 确认。");
      if (confirmation !== "RESET_WORLD") return;
      this.worldAction = "reset";
      try {
        const response = await this.apiFetch("/api/world/reset", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ confirm: confirmation }),
        });
        if (!response.ok) throw new Error(await response.text());
        await this.loadWorldStatus();
        alert("世界已重置，Minecraft 正在重新生成干净世界。");
      } catch (error) {
        alert(`重置失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.worldAction = "";
      }
    },
    insertMaterialPrompt(name, material) {
      const blocks = Object.entries(material.blocks || {})
        .map(([role, block]) => `${role}=${block}`)
        .join(", ");
      this.insertPromptText(`使用材料预设 ${name}：${material.description || ""}。方块映射：${blocks}。`);
    },
    insertComponentPrompt(name, component) {
      const params = Object.entries(component.parameters || {})
        .map(([key, value]) => `${key}=${value}`)
        .join(", ");
      const materials = Object.entries(component.default_materials || {})
        .map(([role, block]) => `${role}=${block}`)
        .join(", ");
      this.insertPromptText(
        `使用组件 ${name}：${component.description || ""}。适用：${component.applicability || "按组件说明判断"}。避免：${component.avoid_when || "无"}。可调整参数：${params || "无"}。默认材料：${materials || "无"}。请按当前建筑比例放大/缩小并叠加到设计中。`,
      );
    },
    insertTemplatePrompt(name, template) {
      const palettes = (template.recommended_palettes || []).join(", ") || "按模板选择";
      const checks = (template.checks || []).join("；") || "保持模板特征";
      this.insertPromptText(
        `使用建筑模板 ${name}：${template.description || ""}。推荐材料：${palettes}。生成时检查：${checks}。如果当前目标不适合该模板，请说明并改选更合适模板。`,
      );
    },
    insertPromptText(text) {
      const target = this.project ? "chatInput" : "initialPrompt";
      const current = this[target].trim();
      this[target] = current ? `${current}\n${text}` : text;
    },
    onFileChange(event) {
      const [file] = event.target.files;
      this.file = file || null;
      if (this.imagePreviewUrl) URL.revokeObjectURL(this.imagePreviewUrl);
      this.imagePreviewUrl = file ? URL.createObjectURL(file) : "";
    },
    async createProject() {
      if (!this.file && !this.initialPrompt.trim()) return;
      this.submitting = true;
      this.project = null;
      this.preview = null;
      this.previewMode = "surface";
      this.selectedBlueprintModule = null;
      this.modulePlan = null;
      this.clearPreview();

      const form = new FormData();
      if (this.file) form.append("image", this.file);
      form.append("prompt", this.initialPrompt.trim());

      try {
        const response = await this.apiFetch("/api/projects", {
          method: "POST",
          body: form,
        });
        if (!response.ok) throw new Error(await response.text());
        const payload = await response.json();
        window.location.hash = `#/project/${payload.project_id}`;
        await this.fetchProject(payload.project_id);
        this.startPolling(payload.project_id);
      } catch (error) {
        this.project = {
          status: "failed",
          error: error instanceof Error ? error.message : String(error),
          messages: [],
        };
      } finally {
        this.submitting = false;
      }
    },
    async sendMessage(paste) {
      if (!this.canChat) return;
      const message = this.chatInput.trim();
      this.chatInput = "";

      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message, paste }),
        });
        if (!response.ok) throw new Error(await response.text());
        await this.fetchProject(this.project.id);
        this.startPolling(this.project.id);
      } catch (error) {
        this.project.error = error instanceof Error ? error.message : String(error);
      }
    },
    async pasteProject() {
      if (!this.project?.schematic_path || this.busy) return;
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/paste`, { method: "POST" });
        if (!response.ok) throw new Error(await response.text());
        await this.fetchProject(this.project.id);
      } catch (error) {
        this.project.error = error instanceof Error ? error.message : String(error);
      }
    },
    async deleteProject(projectId) {
      if (!confirm("确定删除该项目？此操作不可撤销。")) return;
      try {
        const response = await this.apiFetch(`/api/projects/${projectId}`, { method: "DELETE" });
        if (!response.ok) throw new Error(await response.text());
        this.projects = this.projects.filter((p) => p.id !== projectId);
      } catch (error) {
        alert(`删除失败：${error instanceof Error ? error.message : String(error)}`);
      }
    },
    async cleanupProjectMissingSnapshots(item) {
      const projectId = item?.id;
      const missingCount = this.projectMissingSnapshotCount(item);
      if (!projectId || !missingCount) return;
      if (!confirm(`清理项目 ${item.name || projectId} 的 ${missingCount} 条缺失快照记录？`)) return;
      this.projectListAction = `cleanup-snapshots:${projectId}`;
      try {
        const response = await this.apiFetch(`/api/projects/${projectId}/module-snapshots/cleanup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            confirm: "CLEANUP_MISSING_MODULE_SNAPSHOTS",
            module: null,
          }),
        });
        if (!response.ok) throw new Error(await response.text());
        const payload = await response.json();
        this.applyProjectSnapshotSummary(projectId, payload.snapshot_summary);
      } catch (error) {
        alert(`清理缺失快照失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.projectListAction = "";
      }
    },
    applyProjectSnapshotSummary(projectId, snapshotSummary) {
      if (!projectId || !snapshotSummary) return;
      this.projects = this.projects.map((project) =>
        project.id === projectId ? { ...project, snapshot_summary: snapshotSummary } : project,
      );
    },
    async cancelGeneration() {
      if (!this.project?.id || !this.busy) return;
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/cancel`, { method: "POST" });
        if (!response.ok) throw new Error(await response.text());
        this.stopPolling();
        await this.fetchProject(this.project.id);
      } catch (error) {
        this.project.error = error instanceof Error ? error.message : String(error);
      }
    },
    async savePlacement() {
      if (!this.project?.id || !this.project?.plan || this.busy) return;
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/placement`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.placementForm),
        });
        if (!response.ok) throw new Error(await response.text());
        await this.fetchProject(this.project.id);
      } catch (error) {
        this.project.error = error instanceof Error ? error.message : String(error);
      }
    },
    startPolling(projectId) {
      this.stopPolling();
      if (this._tryWebSocket(projectId)) return;
      this.pollTimer = window.setInterval(async () => {
        await this.fetchProject(projectId);
        if (TERMINAL_STATUSES.includes(this.project?.status)) {
          window.clearInterval(this.pollTimer);
          this.pollTimer = null;
          await this.loadPreview();
        }
      }, 1400);
    },
    _tryWebSocket(projectId) {
      try {
        const protocol = location.protocol === "https:" ? "wss:" : "ws:";
        const ws = new WebSocket(`${protocol}//${location.host}/ws/projects/${projectId}`);
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          if (data.type === "state") {
            this.project = data;
            this.syncPlacementForm();
            if (this.project?.preview_path && !this.busy) {
              this.loadPreview();
            }
            this.$nextTick(this.scrollChat);
            if (TERMINAL_STATUSES.includes(data.status)) {
              ws.close();
              this.ws = null;
              this.loadPreview();
            }
          }
        };
        ws.onclose = () => {
          if (this.ws === ws) this.ws = null;
        };
        ws.onerror = () => {
          ws.close();
          if (!this.pollTimer) this.startPolling(projectId);
        };
        this.ws = ws;
        return true;
      } catch {
        return false;
      }
    },
    stopPolling() {
      if (this.pollTimer) {
        window.clearInterval(this.pollTimer);
        this.pollTimer = null;
      }
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }
    },
    async fetchProject(projectId) {
      const response = await this.apiFetch(`/api/projects/${projectId}`);
      if (!response.ok) return;
      this.project = await response.json();
      this.syncPlacementForm();
      if (this.project?.preview_path && !this.busy) {
        await this.loadPreview();
      }
      this.$nextTick(this.scrollChat);
    },
    async setPreviewMode(mode) {
      if (this.previewMode === mode) return;
      this.previewMode = mode;
      await this.loadPreview(mode);
    },
    async loadPreview(mode = this.previewMode) {
      if (!this.project?.id || !this.project?.preview_path) return;
      const query = new URLSearchParams({ mode, ts: String(Date.now()) });
      if (this.selectedBlueprintModule?.name) query.set("module", this.selectedBlueprintModule.name);
      const response = await this.apiFetch(`/api/projects/${this.project.id}/preview?${query.toString()}`);
      if (!response.ok) return;
      this.preview = await response.json();
      this.previewMode = this.preview.mode || mode;
      this.renderPreview();
    },
    scrollChat() {
      const node = this.$refs.chatLog;
      if (node) node.scrollTop = node.scrollHeight;
    },
    syncPlacementForm() {
      const placement = this.project?.placement;
      if (!placement) return;
      this.placementForm = {
        x: placement.paste?.x ?? null,
        y: placement.paste?.y ?? null,
        z: placement.paste?.z ?? null,
        spawn_x: placement.spawn?.x ?? null,
        spawn_y: placement.spawn?.y ?? null,
        spawn_z: placement.spawn?.z ?? null,
      };
    },
    placementText(kind) {
      const value = this.project?.placement?.[kind];
      if (!value) return "-";
      return `${value.x}, ${value.y}, ${value.z}`;
    },
    placementSize(item) {
      const size = item.placement?.size;
      if (!size) return "-";
      return `${size.x} x ${size.y} x ${size.z}`;
    },
    bboxText(bbox) {
      if (!bbox) return "-";
      return `${bbox[0].join(", ")} -> ${bbox[1].join(", ")}`;
    },
    sizeText(size) {
      if (!size) return "-";
      return Array.isArray(size) ? size.join(" x ") : "-";
    },
    async selectBlueprintModule(module) {
      this.selectedBlueprintModule = module;
      await Promise.all([this.loadPreview(this.previewMode), this.loadModulePlan(module)]);
    },
    async clearBlueprintModule() {
      this.selectedBlueprintModule = null;
      this.modulePlan = null;
      await this.loadPreview(this.previewMode);
    },
    async loadModulePlan(module = this.selectedBlueprintModule) {
      if (!this.project?.id || !module?.name || !module?.bbox || !this.project?.placement) {
        this.modulePlan = null;
        return;
      }
      this.modulePlanLoading = true;
      try {
        const response = await this.apiFetch(
          `/api/projects/${this.project.id}/modules/${encodeURIComponent(module.name)}/operation-plan?ts=${Date.now()}`
        );
        if (!response.ok) throw new Error(await response.text());
        const plan = await response.json();
        if (this.selectedBlueprintModule?.name === module.name) this.modulePlan = plan;
      } catch (error) {
        console.error(error);
        if (this.selectedBlueprintModule?.name === module.name) this.modulePlan = null;
      } finally {
        this.modulePlanLoading = false;
      }
    },
    formatWorldBounds(bounds) {
      if (!bounds) return "-";
      return `${bounds.min_x}, ${bounds.min_y}, ${bounds.min_z} -> ${bounds.max_x}, ${bounds.max_y}, ${bounds.max_z}`;
    },
    formatPoint(point) {
      if (!point) return "-";
      return `${point.x}, ${point.y}, ${point.z}`;
    },
    moduleConfirmText(module, action, snapshot = null) {
      const name = module?.name || "模块";
      const plan = this.modulePlan?.module?.name === name ? this.modulePlan : null;
      if (!plan) {
        const fallback = {
          paste: `粘贴模块 ${name} 到 Minecraft？这会覆盖该模块所在区域。`,
          clear: `清空 Minecraft 中的模块区域 ${name}？`,
          replace: `替换 Minecraft 中的模块 ${name}？这会先清空该模块区域再粘贴。`,
        };
        return fallback[action] || `执行模块操作 ${name}？`;
      }
      const lines = [
        `${this.moduleActionLabel(action)}模块 ${name}？`,
        `范围：${this.formatWorldBounds(plan.world_bounds)}`,
        `影响方块：${plan.clear?.blocks ?? "-"} / ${plan.clear?.limit ?? "-"}`,
      ];
      if (action === "paste") lines.push(`粘贴点：${this.formatPoint(plan.paste)}`);
      if (action === "replace") lines.push("步骤：先清空再粘贴");
      if (action === "rollback") lines.push(`回滚快照：${this.snapshotTime(snapshot || plan.latest_snapshot)}`);
      if (plan.clear && !plan.clear.safe) lines.push("警告：该模块超过安全清空上限，后端会拒绝执行清空/替换。");
      return lines.join("\n");
    },
    latestSnapshotFor(module) {
      if (!module?.name) return null;
      if (this.modulePlan?.module?.name === module.name && this.modulePlan.latest_snapshot) {
        return this.modulePlan.latest_snapshot;
      }
      const snapshots = this.project?.module_snapshots || [];
      for (let index = snapshots.length - 1; index >= 0; index -= 1) {
        if (snapshots[index]?.module === module.name) return snapshots[index];
      }
      return null;
    },
    isSnapshotUsable(snapshot) {
      if (!snapshot) return false;
      if (snapshot.file) return Boolean(snapshot.file.exists);
      return Boolean(snapshot.path);
    },
    hasModuleSnapshot(module) {
      return this.isSnapshotUsable(this.latestSnapshotFor(module));
    },
    missingSnapshotCount(module) {
      if (!module?.name) return 0;
      return (this.project?.module_snapshots || []).filter(
        (snapshot) => snapshot?.module === module.name && snapshot?.path && snapshot.file?.exists === false,
      ).length;
    },
    snapshotTime(snapshot) {
      if (!snapshot?.created_at) return "未知时间";
      const time = snapshot.created_at.replace("T", " ").replace(/\.\d+/, "").replace("+00:00", " UTC");
      const source = this.snapshotSourceLabel(snapshot.source);
      return source ? `${time} · ${source}` : time;
    },
    snapshotSourceLabel(source) {
      const labels = {
        world: "世界区域",
        generated: "生成文件",
        failed: "快照失败",
      };
      return labels[source] || "";
    },
    snapshotFileText(snapshot) {
      if (!snapshot?.path) return "无文件";
      if (!snapshot.file?.exists) return "文件缺失";
      const size = Number(snapshot.file.size || 0);
      return size ? `${Math.ceil(size / 1024)} KB` : "空文件";
    },
    moduleSnapshotDownloadUrl(snapshot) {
      if (!this.project?.id || !snapshot?.path) return "#";
      const query = new URLSearchParams(snapshot.id ? { snapshot_id: snapshot.id } : { snapshot_path: snapshot.path });
      return `/api/projects/${this.project.id}/module-snapshots/download?${query.toString()}`;
    },
    async teleportBlueprintModule(module) {
      if (!this.project?.id || !module?.name) return;
      this.moduleAction = `teleport:${module.name}`;
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/modules/${encodeURIComponent(module.name)}/teleport`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        });
        if (!response.ok) throw new Error(await response.text());
      } catch (error) {
        alert(`模块传送失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.moduleAction = "";
      }
    },
    async pasteBlueprintModule(module) {
      if (!this.project?.id || !module?.name) return;
      if (!confirm(this.moduleConfirmText(module, "paste"))) return;
      this.moduleAction = `paste:${module.name}`;
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/modules/${encodeURIComponent(module.name)}/paste`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ confirm: "PASTE_MODULE" }),
        });
        if (!response.ok) throw new Error(await response.text());
        await response.json();
        await this.fetchProject(this.project.id);
      } catch (error) {
        alert(`模块粘贴失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.moduleAction = "";
      }
    },
    async clearBlueprintModuleArea(module) {
      if (!this.project?.id || !module?.name) return;
      if (!confirm(this.moduleConfirmText(module, "clear"))) return;
      this.moduleAction = `clear:${module.name}`;
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/modules/${encodeURIComponent(module.name)}/clear`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ confirm: "CLEAR_MODULE" }),
        });
        if (!response.ok) throw new Error(await response.text());
        await response.json();
        await this.fetchProject(this.project.id);
      } catch (error) {
        alert(`模块清空失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.moduleAction = "";
      }
    },
    async replaceBlueprintModule(module) {
      if (!this.project?.id || !module?.name) return;
      if (!confirm(this.moduleConfirmText(module, "replace"))) return;
      this.moduleAction = `replace:${module.name}`;
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/modules/${encodeURIComponent(module.name)}/replace`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ confirm: "REPLACE_MODULE" }),
        });
        if (!response.ok) throw new Error(await response.text());
        await response.json();
        await this.fetchProject(this.project.id);
      } catch (error) {
        alert(`模块替换失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.moduleAction = "";
      }
    },
    async rollbackBlueprintModule(module, snapshot = null) {
      if (!this.project?.id || !module?.name || (!snapshot && !this.hasModuleSnapshot(module))) return;
      if (snapshot && !this.isSnapshotUsable(snapshot)) return;
      if (!confirm(this.moduleConfirmText(module, "rollback", snapshot))) return;
      this.moduleAction = `rollback:${module.name}`;
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/modules/${encodeURIComponent(module.name)}/rollback`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            confirm: "ROLLBACK_MODULE",
            snapshot_id: snapshot?.id || null,
            snapshot_path: snapshot?.id ? null : snapshot?.path || null,
          }),
        });
        if (!response.ok) throw new Error(await response.text());
        await response.json();
        await this.fetchProject(this.project.id);
        await this.loadModulePlan(module);
      } catch (error) {
        alert(`模块回滚失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.moduleAction = "";
      }
    },
    async deleteModuleSnapshot(module, snapshot) {
      if (!this.project?.id || !module?.name || !snapshot?.path) return;
      if (!confirm(`删除模块 ${module.name} 的快照？\n${this.snapshotTime(snapshot)}`)) return;
      this.moduleAction = `delete-snapshot:${module.name}`;
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/module-snapshots`, {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            confirm: "DELETE_MODULE_SNAPSHOT",
            snapshot_id: snapshot.id || null,
            snapshot_path: snapshot.id ? null : snapshot.path,
          }),
        });
        if (!response.ok) throw new Error(await response.text());
        await response.json();
        await this.fetchProject(this.project.id);
        await this.loadModulePlan(module);
      } catch (error) {
        alert(`删除快照失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.moduleAction = "";
      }
    },
    async cleanupMissingModuleSnapshots(module) {
      if (!this.project?.id || !module?.name) return;
      const missingCount = this.missingSnapshotCount(module);
      if (!missingCount) return;
      if (!confirm(`清理模块 ${module.name} 的 ${missingCount} 条缺失快照记录？`)) return;
      this.moduleAction = `cleanup-snapshots:${module.name}`;
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/module-snapshots/cleanup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            confirm: "CLEANUP_MISSING_MODULE_SNAPSHOTS",
            module: module.name,
          }),
        });
        if (!response.ok) throw new Error(await response.text());
        await response.json();
        await this.fetchProject(this.project.id);
        await this.loadModulePlan(module);
      } catch (error) {
        alert(`清理缺失快照失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.moduleAction = "";
      }
    },
    async refreshModuleOperations() {
      if (!this.project?.id) return;
      this.moduleLogAction = "refresh";
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/module-operations?ts=${Date.now()}`);
        if (!response.ok) throw new Error(await response.text());
        const payload = await response.json();
        this.project.module_operations = payload.module_operations || [];
        this.project.module_rcon = payload.module_rcon || {};
      } catch (error) {
        alert(`刷新模块记录失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.moduleLogAction = "";
      }
    },
    async clearModuleOperations() {
      if (!this.project?.id || !confirm("清空当前项目的模块操作记录？")) return;
      this.moduleLogAction = "clear";
      try {
        const response = await this.apiFetch(`/api/projects/${this.project.id}/module-operations`, { method: "DELETE" });
        if (!response.ok) throw new Error(await response.text());
        await response.json();
        this.project.module_operations = [];
        this.project.module_rcon = {};
      } catch (error) {
        alert(`清空模块记录失败：${error instanceof Error ? error.message : String(error)}`);
      } finally {
        this.moduleLogAction = "";
      }
    },
    isSelectedBlueprintModule(module) {
      return Boolean(this.selectedBlueprintModule && module?.name === this.selectedBlueprintModule.name);
    },
    moduleSchematicUrl(module) {
      if (!this.project?.id || !module?.name) return "#";
      return `/api/projects/${this.project.id}/modules/${encodeURIComponent(module.name)}/schematic`;
    },
    moduleActionLabel(action) {
      const labels = {
        paste: "粘贴",
        clear: "清空",
        replace: "替换",
        rollback: "回滚",
      };
      return labels[action] || action || "粘贴";
    },
    roleText(role) {
      const labels = {
        foundation: "基础",
        void: "清空",
        mass: "体量",
        structure: "结构",
        circulation: "动线",
        facade: "立面",
        roof: "屋顶",
        interior: "室内",
        lighting: "灯光",
        detail: "细节",
        landscape: "景观",
        services: "设备",
        architecture: "建筑",
        entry: "入口",
        unknown: "未知",
      };
      return labels[role] || role || "-";
    },
    activePlacementCount() {
      return this.placements.filter((item) => item.active !== false).length;
    },
    latestPlacementText() {
      const latest = this.placements[0];
      if (!latest) return "-";
      const paste = latest.paste;
      return `${latest.project_name || latest.project_id} @ ${paste?.x ?? "-"}, ${paste?.y ?? "-"}, ${paste?.z ?? "-"}`;
    },
    hasLatestPlacement() {
      return Boolean(this.placements[0]);
    },
    projectSizeText(item) {
      if (item.preview?.size) return item.preview.size.join(" x ");
      return this.placementSize(item);
    },
    projectVolume(item) {
      const size = item.preview?.size;
      if (Array.isArray(size) && size.length >= 3) {
        return Number(size[0] || 0) * Number(size[1] || 0) * Number(size[2] || 0);
      }
      const placementSize = item.placement?.size;
      if (placementSize) {
        return Number(placementSize.x || 0) * Number(placementSize.y || 0) * Number(placementSize.z || 0);
      }
      return 0;
    },
    projectBlockCount(item) {
      return Number(item.preview?.block_count || 0);
    },
    projectSnapshotBytes(item) {
      return Number(item.snapshot_summary?.bytes || 0);
    },
    projectMissingSnapshotCount(item) {
      return Number(item.snapshot_summary?.missing_count || 0);
    },
    projectTimeValue(item) {
      const value = item.updated_at || item.created_at || "";
      const time = new Date(value).getTime();
      return Number.isNaN(time) ? 0 : time;
    },
    projectSearchText(item) {
      return [
        item.id,
        item.name,
        item.status,
        item.last_message,
        item.analysis_report?.template_guess,
        item.analysis_report?.design_blueprint?.building_type,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
    },
    projectMatchesStatusFilter(item, filter) {
      if (filter === "busy") return BUSY_STATUSES.includes(item.status);
      if (filter === "with_blueprint") return Boolean(item.analysis_report?.design_blueprint?.present);
      if (filter === "with_schematic") return Boolean(item.has_schematic);
      if (filter === "missing_snapshots") return this.projectMissingSnapshotCount(item) > 0;
      return item.status === filter;
    },
    compareProjects(left, right, sortKey) {
      const byUpdated = () => this.projectTimeValue(right) - this.projectTimeValue(left);
      const compareText = (a, b) => String(a || "").localeCompare(String(b || ""), "zh-CN");
      const tieBreak = byUpdated() || compareText(left.id, right.id);
      const sorters = {
        updated_desc: () => byUpdated() || compareText(left.id, right.id),
        name_asc: () => compareText(left.name || left.id, right.name || right.id) || byUpdated(),
        blocks_desc: () => this.projectBlockCount(right) - this.projectBlockCount(left) || tieBreak,
        volume_desc: () => this.projectVolume(right) - this.projectVolume(left) || tieBreak,
        snapshots_desc: () => this.projectSnapshotBytes(right) - this.projectSnapshotBytes(left) || tieBreak,
      };
      return (sorters[sortKey] || sorters.updated_desc)();
    },
    loadProjectListPrefs() {
      try {
        const raw = localStorage.getItem("mc_builder_project_list_prefs");
        if (!raw) return;
        const prefs = JSON.parse(raw);
        if (typeof prefs.search === "string") this.projectSearch = prefs.search;
        if (PROJECT_STATUS_FILTERS.includes(prefs.status)) this.projectStatusFilter = prefs.status;
        if (PROJECT_SORTS.includes(prefs.sort)) this.projectSort = prefs.sort;
      } catch (error) {
        console.warn("Failed to load project list prefs", error);
      }
    },
    saveProjectListPrefs() {
      try {
        localStorage.setItem(
          "mc_builder_project_list_prefs",
          JSON.stringify({
            search: this.projectSearch,
            status: this.projectStatusFilter,
            sort: this.projectSort,
          }),
        );
      } catch (error) {
        console.warn("Failed to save project list prefs", error);
      }
    },
    resetProjectListFilters() {
      this.projectSearch = "";
      this.projectStatusFilter = "all";
      this.projectSort = "updated_desc";
      this.saveProjectListPrefs();
    },
    projectSnapshotText(item) {
      const summary = item.snapshot_summary;
      if (!summary?.count) return "0";
      const latest = summary.latest_created_at ? ` · ${this.formatTime(summary.latest_created_at)}` : "";
      const bytes = summary.bytes ? ` · ${this.formatBytes(summary.bytes)}` : "";
      const missing = summary.missing_count ? ` · 缺失 ${summary.missing_count}` : "";
      return `${summary.available_count || 0}/${summary.count} 可用 · ${summary.module_count || 0} 模块${missing}${bytes}${latest}`;
    },
  },
}).mount("#app");
