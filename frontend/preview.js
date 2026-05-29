window.McPreview = {
  methods: {
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
      const previewBlocks = this.filteredPreviewBlocks();
      for (const [x, y, z, block] of previewBlocks) {
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
        const isGlass = block.includes("glass");
        const material = new THREE.MeshLambertMaterial({
          color,
          transparent: isGlass,
          opacity: isGlass ? 0.45 : 1,
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
      const blocks = this.sampleCanvasBlocks(this.filteredPreviewBlocks());

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
      const module = this.selectedBlueprintModule?.name ? ` · ${this.selectedBlueprintModule.name}` : "";
      ctx.fillText(`WebGL 不可用，当前为 Canvas 2D 等距预览${module}`, 14, 24);
    },
    filteredPreviewBlocks() {
      const blocks = this.preview?.blocks || [];
      if (this.preview?.module_filtered) return blocks;
      const bbox = this.selectedBlueprintModule?.bbox;
      if (!bbox) return blocks;
      const [min, max] = bbox;
      return blocks.filter(([x, y, z]) => (
        x >= min[0] &&
        y >= min[1] &&
        z >= min[2] &&
        x <= max[0] &&
        y <= max[1] &&
        z <= max[2]
      ));
    },
    sampleCanvasBlocks(blocks) {
      const limit = 18000;
      if (blocks.length <= limit) return blocks;
      const step = Math.ceil(blocks.length / limit);
      return blocks.filter((_, index) => index % step === 0);
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
};
