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
const context = {
  ...data,
  ...methods,
  projects: [
    {
      id: "old-small",
      name: "旧小楼",
      status: "done",
      updated_at: "2026-01-01T00:00:00+00:00",
      last_message: "low bridge",
      preview: { size: [10, 8, 10], block_count: 200 },
      snapshot_summary: { bytes: 1024 },
    },
    {
      id: "new-mid",
      name: "广州塔夜景",
      status: "done",
      updated_at: "2026-01-03T00:00:00+00:00",
      last_message: "rainbow led tower",
      preview: { size: [30, 120, 30], block_count: 7000 },
      snapshot_summary: { bytes: 4096 },
    },
    {
      id: "big-old",
      name: "苏州门",
      status: "failed",
      updated_at: "2026-01-02T00:00:00+00:00",
      last_message: "large gate",
      preview: { size: [80, 80, 80], block_count: 3000 },
      snapshot_summary: { bytes: 8192 },
    },
  ],
};

context.projectSearch = "rainbow";
let visible = computed.visibleProjects.call(context);
if (visible.length !== 1 || visible[0].id !== "new-mid") {
  throw new Error(`expected rainbow search to return new-mid, got ${visible.map((item) => item.id).join(",")}`);
}

context.projectSearch = "";
context.projectSort = "updated_desc";
visible = computed.visibleProjects.call(context);
if (visible.map((item) => item.id).join(",") !== "new-mid,big-old,old-small") {
  throw new Error("updated sort order mismatch");
}

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

console.log({ project_list_filter: "ok" });
