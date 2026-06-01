const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync("frontend/app.js", "utf8");
let capturedOptions = null;
const sandbox = {
  Vue: {
    createApp(options) {
      capturedOptions = options;
      return { mount() {} };
    },
  },
  confirm() {
    return true;
  },
  localStorage: {
    value: "",
    getItem(key) {
      return key === "mc_builder_project_list_prefs" ? this.value : null;
    },
    setItem(key, value) {
      if (key === "mc_builder_project_list_prefs") this.value = value;
    },
  },
  console,
  window: { McPreview: {}, McHelpers: {} },
};
vm.createContext(sandbox);
vm.runInContext(source, sandbox);

if (!capturedOptions) {
  throw new Error("Vue app options were not captured");
}

const data = capturedOptions.data();
const methods = capturedOptions.methods;
const computed = capturedOptions.computed;
const cleanupResponses = {
  "big-old": {
    count: 1,
    available_count: 1,
    missing_count: 0,
    module_count: 1,
    bytes: 256,
  },
  "old-small": {
    count: 2,
    available_count: 2,
    missing_count: 0,
    module_count: 1,
    bytes: 512,
  },
};
const context = {
  ...data,
  ...methods,
  async apiFetch(url, options) {
    const match = url.match(/^\/api\/projects\/([^/]+)\/module-snapshots\/cleanup$/);
    if (!match) {
      throw new Error(`unexpected api url ${url}`);
    }
    const projectId = match[1];
    const body = JSON.parse(options.body);
    if (body.confirm !== "CLEANUP_MISSING_MODULE_SNAPSHOTS" || body.module !== null) {
      throw new Error(`unexpected cleanup body ${options.body}`);
    }
    if (!cleanupResponses[projectId]) {
      throw new Error(`unexpected cleanup project ${projectId}`);
    }
    return {
      ok: true,
      async json() {
        return {
          snapshot_summary: cleanupResponses[projectId],
        };
      },
    };
  },
  formatBytes(value) {
    return `${value} B`;
  },
  projects: [
    {
      id: "old-small",
      name: "旧小楼",
      status: "done",
      updated_at: "2026-01-01T00:00:00+00:00",
      last_message: "low bridge",
      preview: { size: [10, 8, 10], block_count: 200 },
      snapshot_summary: { count: 2, available_count: 1, missing_count: 1, module_count: 1, bytes: 1024 },
    },
    {
      id: "new-mid",
      name: "广州塔夜景",
      status: "done",
      updated_at: "2026-01-03T00:00:00+00:00",
      last_message: "rainbow led tower",
      preview: { size: [30, 120, 30], block_count: 7000 },
      snapshot_summary: { bytes: 4096 },
      analysis_report: { design_blueprint: { present: true } },
      has_schematic: true,
    },
    {
      id: "big-old",
      name: "苏州门",
      status: "failed",
      updated_at: "2026-01-02T00:00:00+00:00",
      last_message: "large gate",
      preview: { size: [80, 80, 80], block_count: 3000 },
      snapshot_summary: { count: 3, available_count: 1, missing_count: 2, module_count: 2, bytes: 8192 },
    },
  ],
};
Object.defineProperty(context, "visibleProjects", {
  get() {
    return computed.visibleProjects.call(context);
  },
});

context.projectSearch = "rainbow";
let visible = computed.visibleProjects.call(context);
if (visible.length !== 1 || visible[0].id !== "new-mid") {
  throw new Error(`expected rainbow search to return new-mid, got ${visible.map((item) => item.id).join(",")}`);
}

context.projectSearch = "";
context.projectStatusFilter = "all";
context.projectSort = "updated_desc";
visible = computed.visibleProjects.call(context);
if (visible.map((item) => item.id).join(",") !== "new-mid,big-old,old-small") {
  throw new Error("updated sort order mismatch");
}

context.projectStatusFilter = "failed";
visible = computed.visibleProjects.call(context);
if (visible.length !== 1 || visible[0].id !== "big-old") {
  throw new Error(`expected failed filter to return big-old, got ${visible.map((item) => item.id).join(",")}`);
}

context.projectStatusFilter = "with_blueprint";
visible = computed.visibleProjects.call(context);
if (visible.length !== 1 || visible[0].id !== "new-mid") {
  throw new Error(`expected blueprint filter to return new-mid, got ${visible.map((item) => item.id).join(",")}`);
}

context.projectStatusFilter = "missing_snapshots";
visible = computed.visibleProjects.call(context);
if (visible.map((item) => item.id).join(",") !== "big-old,old-small") {
  throw new Error(`expected missing snapshots filter to return big-old and old-small, got ${visible.map((item) => item.id).join(",")}`);
}
if (methods.visibleMissingSnapshotProjectCount.call(context) !== 2 || methods.visibleMissingSnapshotCount.call(context) !== 3) {
  throw new Error("expected visible missing snapshot counts to include both matching projects");
}
if (methods.visibleMissingSnapshotText.call(context) !== "2 个项目 · 3 条缺失快照") {
  throw new Error(`expected visible missing snapshot summary, got ${methods.visibleMissingSnapshotText.call(context)}`);
}
if (methods.visibleSnapshotStorageText.call(context) !== "快照占用 9216 B") {
  throw new Error(`expected visible snapshot storage summary, got ${methods.visibleSnapshotStorageText.call(context)}`);
}

context.projectStatusFilter = "all";
context.projectSort = "volume_desc";
visible = computed.visibleProjects.call(context);
if (visible[0].id !== "big-old") {
  throw new Error(`expected largest volume first, got ${visible[0].id}`);
}

context.projectSort = "snapshots_desc";
visible = computed.visibleProjects.call(context);
if (visible[0].id !== "big-old") {
  throw new Error(`expected largest snapshot storage first, got ${visible[0].id}`);
}

context.projectSort = "missing_desc";
visible = computed.visibleProjects.call(context);
if (visible.map((item) => item.id).join(",") !== "big-old,old-small,new-mid") {
  throw new Error(`expected missing snapshot sort order, got ${visible.map((item) => item.id).join(",")}`);
}

const snapshotText = methods.projectSnapshotText.call(context, context.projects[2]);
if (!snapshotText.includes("缺失 2")) {
  throw new Error(`expected missing snapshot count in text, got ${snapshotText}`);
}
if (methods.projectMissingSnapshotCount.call(context, context.projects[2]) !== 2) {
  throw new Error("expected missing snapshot count helper to return 2");
}

context.projectSearch = "tower";
context.projectStatusFilter = "missing_snapshots";
context.projectSort = "missing_desc";
methods.saveProjectListPrefs.call(context);

const restored = { ...data, ...methods };
methods.loadProjectListPrefs.call(restored);
if (restored.projectSearch !== "tower" || restored.projectStatusFilter !== "missing_snapshots" || restored.projectSort !== "missing_desc") {
  throw new Error("project list prefs did not round-trip through localStorage");
}

methods.resetProjectListFilters.call(restored);
if (restored.projectSearch !== "" || restored.projectStatusFilter !== "all" || restored.projectSort !== "updated_desc") {
  throw new Error("project list reset did not restore defaults");
}

const resetAgain = { ...data, ...methods };
methods.loadProjectListPrefs.call(resetAgain);
if (resetAgain.projectSearch !== "" || resetAgain.projectStatusFilter !== "all" || resetAgain.projectSort !== "updated_desc") {
  throw new Error("project list reset did not persist defaults");
}

methods.cleanupProjectMissingSnapshots.call(context, context.projects[2]).then(() => {
  const updated = context.projects.find((item) => item.id === "big-old");
  if (updated.snapshot_summary.missing_count !== 0 || updated.snapshot_summary.bytes !== 256) {
    throw new Error("project cleanup did not update snapshot summary");
  }
  const untouched = context.projects.find((item) => item.id === "new-mid");
  if (untouched.snapshot_summary.bytes !== 4096) {
    throw new Error("project cleanup changed the wrong project");
  }
  context.projectSearch = "";
  context.projectStatusFilter = "missing_snapshots";
  const afterCleanupVisible = computed.visibleProjects.call(context);
  if (afterCleanupVisible.length !== 1 || afterCleanupVisible[0].id !== "old-small") {
    throw new Error(`expected old-small after single cleanup, got ${afterCleanupVisible.map((item) => item.id).join(",")}`);
  }
  return methods.cleanupVisibleMissingSnapshots.call(context);
}).then(() => {
  const oldSmall = context.projects.find((item) => item.id === "old-small");
  if (oldSmall.snapshot_summary.missing_count !== 0 || oldSmall.snapshot_summary.bytes !== 512) {
    throw new Error("visible cleanup did not update remaining missing snapshot project");
  }
  context.projectSearch = "";
  context.projectStatusFilter = "missing_snapshots";
  const afterVisibleCleanup = computed.visibleProjects.call(context);
  if (afterVisibleCleanup.length !== 0) {
    throw new Error(`expected no projects after visible cleanup, got ${afterVisibleCleanup.length}`);
  }
  if (methods.emptyProjectListText.call(context) !== "没有缺失快照的项目。") {
    throw new Error("expected missing snapshot empty state text");
  }
  if (methods.visibleMissingSnapshotText.call(context) !== "") {
    throw new Error("expected empty missing snapshot summary after cleanup");
  }
  if (methods.visibleSnapshotStorageText.call(context) !== "") {
    throw new Error("expected empty storage summary after cleanup in missing snapshot filter");
  }
  console.log({ project_list_filter: "ok" });
});
