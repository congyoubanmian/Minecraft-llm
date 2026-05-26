const { createApp } = Vue;

createApp({
  data() {
    return {
      health: "checking",
      route: "list",
      projects: [],
      projectListLoading: false,
      file: null,
      imagePreviewUrl: "",
      initialPrompt: "",
      chatInput: "",
      submitting: false,
      project: null,
      preview: null,
      placementForm: {
        x: null,
        y: null,
        z: null,
        spawn_x: null,
        spawn_y: null,
        spawn_z: null,
      },
      pollTimer: null,
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
      return ["queued", "analyzing", "planning", "generating_schematic", "pasting"].includes(
        this.project?.status,
      );
    },
    canChat() {
      return Boolean(this.project && this.chatInput.trim() && !this.busy);
    },
    messages() {
      return this.project?.messages || [];
    },
    previewMeta() {
      if (!this.preview) return "暂无预览";
      const size = this.preview.size?.join(" x ") || "-";
      const sampled = this.preview.sampled ? "，已抽样" : "";
      const mode = this.renderMode === "webgl" ? "WebGL 3D" : "Canvas 2D";
      return `${size}，${this.preview.preview_count} 个预览方块${sampled}，${mode}`;
    },
  },
  mounted() {
    this.checkHealth();
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
      this.clearPreview();
      this.destroyPreviewRenderer();
      this.loadProjects();
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
        const response = await fetch(`/api/projects?ts=${Date.now()}`);
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
      this.clearPreview();

      const form = new FormData();
      if (this.file) form.append("image", this.file);
      form.append("prompt", this.initialPrompt.trim());

      try {
        const response = await fetch("/api/projects", {
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
        const response = await fetch(`/api/projects/${this.project.id}/chat`, {
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
        const response = await fetch(`/api/projects/${this.project.id}/paste`, { method: "POST" });
        if (!response.ok) throw new Error(await response.text());
        await this.fetchProject(this.project.id);
      } catch (error) {
        this.project.error = error instanceof Error ? error.message : String(error);
      }
    },
    async savePlacement() {
      if (!this.project?.id || !this.project?.plan || this.busy) return;
      try {
        const response = await fetch(`/api/projects/${this.project.id}/placement`, {
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
      this.pollTimer = window.setInterval(async () => {
        await this.fetchProject(projectId);
        if (["done", "failed"].includes(this.project?.status)) {
          window.clearInterval(this.pollTimer);
          this.pollTimer = null;
          await this.loadPreview();
        }
      }, 1400);
    },
    stopPolling() {
      if (this.pollTimer) {
        window.clearInterval(this.pollTimer);
        this.pollTimer = null;
      }
    },
    async fetchProject(projectId) {
      const response = await fetch(`/api/projects/${projectId}`);
      if (!response.ok) return;
      this.project = await response.json();
      this.syncPlacementForm();
      if (this.project?.preview_path && !this.busy) {
        await this.loadPreview();
      }
      this.$nextTick(this.scrollChat);
    },
    async loadPreview() {
      if (!this.project?.id || !this.project?.preview_path) return;
      const response = await fetch(`/api/projects/${this.project.id}/preview?ts=${Date.now()}`);
      if (!response.ok) return;
      this.preview = await response.json();
      this.renderPreview();
    },
    formatJson(value) {
      return JSON.stringify(value, null, 2);
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
    projectSizeText(item) {
      if (item.preview?.size) return item.preview.size.join(" x ");
      return this.placementSize(item);
    },
    formatTime(value) {
      if (!value) return "-";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return value;
      return date.toLocaleString("zh-CN", {
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      });
    },
    ensurePreviewRenderer() {
      if (this.renderer || this.canvas2d) return;
      this.initPreviewRenderer();
    },
    destroyPreviewRenderer() {
      if (this.resizeObserver) {
        this.resizeObserver.disconnect();
        this.resizeObserver = null;
      }
      window.removeEventListener("pointermove", this.onPointerMove);
      window.removeEventListener("pointerup", this.onPointerUp);
      if (this.renderer) {
        this.renderer.domElement?.remove?.();
        this.renderer.dispose();
      }
      if (this.canvas2d) {
        this.canvas2d.remove();
      }
      this.renderer = null;
      this.canvas2d = null;
      this.scene = null;
      this.camera = null;
      this.previewGroup = null;
      this.renderMode = "loading";
    },
    initPreviewRenderer() {
      const viewport = this.$refs.viewport;
      if (!viewport) return;

      try {
        if (!window.THREE) throw new Error("THREE is not loaded");
        if (!this.canUseWebGL()) {
          this.initCanvasPreview(viewport);
          this.installPreviewListeners(viewport);
          return;
        }
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf3f6f4);

        this.camera = new THREE.PerspectiveCamera(45, 1, 0.1, 2000);
        this.camera.position.set(70, 54, 86);
        this.camera.lookAt(0, 12, 0);

        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.setSize(viewport.clientWidth, viewport.clientHeight);
        viewport.appendChild(this.renderer.domElement);

        this.scene.add(new THREE.HemisphereLight(0xffffff, 0x6b7280, 2.6));
        const sun = new THREE.DirectionalLight(0xffffff, 2.0);
        sun.position.set(50, 80, 40);
        this.scene.add(sun);

        const grid = new THREE.GridHelper(160, 32, 0x9aa5a0, 0xd2d8d4);
        grid.position.y = -0.52;
        this.scene.add(grid);

        this.previewGroup = new THREE.Group();
        this.scene.add(this.previewGroup);
        this.renderer.domElement.addEventListener("pointerdown", this.onPointerDown);
        this.renderer.domElement.addEventListener("wheel", this.onWheel, { passive: true });
        this.renderMode = "webgl";
        this.animate();
      } catch (error) {
        console.warn("WebGL unavailable, falling back to 2D preview:", error);
        this.initCanvasPreview(viewport);
      }

      this.installPreviewListeners(viewport);
    },
    installPreviewListeners(viewport) {
      window.addEventListener("pointermove", this.onPointerMove);
      window.addEventListener("pointerup", this.onPointerUp);
      this.resizeObserver = new ResizeObserver(this.resizePreview);
      this.resizeObserver.observe(viewport);
    },
    canUseWebGL() {
      const canvas = document.createElement("canvas");
      const options = {
        alpha: false,
        antialias: false,
        depth: true,
        failIfMajorPerformanceCaveat: false,
        powerPreference: "default",
        stencil: false,
      };
      const context =
        canvas.getContext("webgl2", options) ||
        canvas.getContext("webgl", options) ||
        canvas.getContext("experimental-webgl", options);
      if (!context) return false;
      const loseContext = context.getExtension("WEBGL_lose_context");
      loseContext?.loseContext();
      return true;
    },
    initCanvasPreview(viewport) {
      this.renderMode = "canvas";
      this.renderer = null;
      this.scene = null;
      this.camera = null;
      this.previewGroup = null;
      this.canvas2d = document.createElement("canvas");
      this.canvas2d.className = "fallback-canvas";
      viewport.appendChild(this.canvas2d);
      this.canvas2d.addEventListener("pointerdown", this.onPointerDown);
      this.canvas2d.addEventListener("wheel", this.onWheel, { passive: true });
      this.resizeCanvasPreview();
    },
    animate() {
      window.requestAnimationFrame(this.animate);
      if (this.renderer && this.scene && this.camera) {
        this.renderer.render(this.scene, this.camera);
      }
    },
    resizePreview() {
      if (this.renderMode === "webgl") {
        this.resizeThree();
      } else {
        this.resizeCanvasPreview();
      }
    },
    resizeThree() {
      const viewport = this.$refs.viewport;
      if (!viewport || !this.renderer || !this.camera) return;
      const width = Math.max(1, viewport.clientWidth);
      const height = Math.max(1, viewport.clientHeight);
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height);
    },
    resizeCanvasPreview() {
      const viewport = this.$refs.viewport;
      if (!viewport || !this.canvas2d) return;
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      const width = Math.max(1, viewport.clientWidth);
      const height = Math.max(1, viewport.clientHeight);
      this.canvas2d.width = Math.floor(width * ratio);
      this.canvas2d.height = Math.floor(height * ratio);
      this.canvas2d.style.width = `${width}px`;
      this.canvas2d.style.height = `${height}px`;
      const ctx = this.canvas2d.getContext("2d");
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      this.renderCanvasPreview();
    },
    clearPreview() {
      if (!this.previewGroup) {
        this.renderCanvasPreview();
        return;
      }
      while (this.previewGroup.children.length) {
        const child = this.previewGroup.children.pop();
        child.geometry?.dispose?.();
        if (Array.isArray(child.material)) {
          child.material.forEach((material) => material.dispose?.());
        } else {
          child.material?.dispose?.();
        }
      }
    },
    renderPreview() {
      if (!this.preview) return;
      if (this.renderMode === "canvas" || !this.previewGroup || !window.THREE) {
        this.renderCanvasPreview();
        return;
      }
      this.clearPreview();

      const blocksByType = new Map();
      for (const [x, y, z, block] of this.preview.blocks || []) {
        if (!blocksByType.has(block)) blocksByType.set(block, []);
        blocksByType.get(block).push([x, y, z]);
      }

      const [sx, sy, sz] = this.preview.size || [1, 1, 1];
      const offsetX = sx / 2;
      const offsetZ = sz / 2;
      const geometry = new THREE.BoxGeometry(1, 1, 1);
      const matrix = new THREE.Matrix4();

      for (const [block, positions] of blocksByType.entries()) {
        const color = this.preview.palette?.[block] || this.colorForBlock(block);
        const material = new THREE.MeshLambertMaterial({
          color,
          transparent: block.includes("glass"),
          opacity: block.includes("glass") ? 0.45 : 1,
        });
        const mesh = new THREE.InstancedMesh(geometry, material, positions.length);
        positions.forEach(([x, y, z], index) => {
          matrix.makeTranslation(x - offsetX, y, z - offsetZ);
          mesh.setMatrixAt(index, matrix);
        });
        mesh.instanceMatrix.needsUpdate = true;
        this.previewGroup.add(mesh);
      }

      this.frameCamera(sx, sy, sz);
    },
    renderCanvasPreview() {
      if (!this.preview || !this.canvas2d) return;
      const ctx = this.canvas2d.getContext("2d");
      const width = this.canvas2d.clientWidth || 1;
      const height = this.canvas2d.clientHeight || 1;
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = "#f3f6f4";
      ctx.fillRect(0, 0, width, height);

      const [sx, sy, sz] = this.preview.size || [1, 1, 1];
      const base = Math.min(width / Math.max(sx + sz, 1), height / Math.max((sx + sz) * 0.45 + sy, 1));
      const scale = Math.max(3, Math.min(11, base * 1.25));
      const originX = width / 2;
      const originY = Math.max(80, height * 0.58);
      const blocks = this.sampleCanvasBlocks(this.preview.blocks || []);

      blocks.sort((a, b) => {
        const da = a[0] + a[2] + a[1] * 0.15;
        const db = b[0] + b[2] + b[1] * 0.15;
        return da - db;
      });

      for (const [x, y, z, block] of blocks) {
        const px = originX + (x - z) * scale * 0.72;
        const py = originY + (x + z - sx - sz) * scale * 0.34 - y * scale * 0.62;
        const color = this.preview.palette?.[block] || this.colorForBlock(block);
        ctx.fillStyle = color;
        ctx.globalAlpha = block.includes("glass") ? 0.5 : 0.92;
        ctx.fillRect(px, py, Math.max(1.4, scale * 0.86), Math.max(1.4, scale * 0.86));
      }

      ctx.globalAlpha = 1;
      ctx.fillStyle = "#405047";
      ctx.font = "12px system-ui, sans-serif";
      ctx.fillText("WebGL 不可用，当前为 Canvas 2D 等距预览", 14, 24);
    },
    sampleCanvasBlocks(blocks) {
      const limit = 18000;
      if (blocks.length <= limit) return blocks;
      const step = Math.ceil(blocks.length / limit);
      return blocks.filter((_, index) => index % step === 0);
    },
    colorForBlock(block) {
      if (block.includes("dark_oak")) return "#3f2a1a";
      if (block.includes("spruce")) return "#6b4728";
      if (block.includes("stone")) return "#7f8587";
      if (block.includes("glass")) return "#9bd7e8";
      if (block.includes("brick")) return "#9b4635";
      if (block.includes("sand")) return "#d7c083";
      if (block.includes("white")) return "#e8e4d8";
      if (block.includes("black")) return "#202429";
      return "#9b9f94";
    },
    frameCamera(sx, sy, sz) {
      if (!this.camera) return;
      const radius = Math.max(sx, sy, sz);
      this.camera.position.set(radius * 0.95, Math.max(28, sy * 0.75), radius * 1.2);
      this.camera.lookAt(0, sy * 0.35, 0);
      this.camera.near = 0.1;
      this.camera.far = radius * 8 + 300;
      this.camera.updateProjectionMatrix();
    },
    resetCamera() {
      if (!this.preview) return;
      if (this.renderMode === "canvas") {
        this.renderCanvasPreview();
        return;
      }
      const [sx, sy, sz] = this.preview.size || [40, 24, 40];
      this.previewGroup.rotation.set(0, 0, 0);
      this.frameCamera(sx, sy, sz);
    },
    onPointerDown(event) {
      this.drag.active = true;
      this.drag.x = event.clientX;
      this.drag.y = event.clientY;
      event.currentTarget?.setPointerCapture?.(event.pointerId);
    },
    onPointerMove(event) {
      if (!this.drag.active) return;
      const dx = event.clientX - this.drag.x;
      const dy = event.clientY - this.drag.y;
      this.drag.x = event.clientX;
      this.drag.y = event.clientY;
      if (!this.previewGroup) return;
      this.previewGroup.rotation.y += dx * 0.008;
      this.previewGroup.rotation.x = Math.max(-0.9, Math.min(0.45, this.previewGroup.rotation.x + dy * 0.006));
    },
    onPointerUp() {
      this.drag.active = false;
    },
    onWheel(event) {
      if (!this.camera) return;
      const scale = event.deltaY > 0 ? 1.08 : 0.92;
      this.camera.position.multiplyScalar(scale);
    },
  },
}).mount("#app");
