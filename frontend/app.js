const { createApp } = Vue;

const BUSY_STATUSES = ["queued", "analyzing", "planning", "generating_schematic", "pasting"];
const TERMINAL_STATUSES = ["done", "failed", "cancelled"];

createApp({
  mixins: [window.McPreview, window.McHelpers],
  data() {
    return {
      health: "checking",
      route: "list",
      projects: [],
      projectListLoading: false,
      world: null,
      placements: [],
      worldLoading: false,
      worldAction: "",
      moduleAction: "",
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
      await this.loadPreview(this.previewMode);
    },
    async clearBlueprintModule() {
      this.selectedBlueprintModule = null;
      await this.loadPreview(this.previewMode);
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
      if (!confirm(`粘贴模块 ${module.name} 到 Minecraft？这会覆盖该模块所在区域。`)) return;
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
      if (!confirm(`清空 Minecraft 中的模块区域 ${module.name}？`)) return;
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
    isSelectedBlueprintModule(module) {
      return Boolean(this.selectedBlueprintModule && module?.name === this.selectedBlueprintModule.name);
    },
    moduleSchematicUrl(module) {
      if (!this.project?.id || !module?.name) return "#";
      return `/api/projects/${this.project.id}/modules/${encodeURIComponent(module.name)}/schematic`;
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
  },
}).mount("#app");
