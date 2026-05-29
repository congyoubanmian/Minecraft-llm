const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync("frontend/preview.js", "utf8");
const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(source, sandbox);

const methods = sandbox.window.McPreview.methods;
const context = {
  preview: {
    blocks: [
      [0, 0, 0, "stone"],
      [2, 2, 2, "stone"],
      [5, 5, 5, "glass"],
    ],
  },
  selectedBlueprintModule: {
    name: "core",
    bbox: [
      [0, 0, 0],
      [3, 3, 3],
    ],
  },
};

let filtered = methods.filteredPreviewBlocks.call(context);
if (filtered.length !== 2) {
  throw new Error(`expected 2 filtered blocks, got ${filtered.length}`);
}

context.selectedBlueprintModule = null;
filtered = methods.filteredPreviewBlocks.call(context);
if (filtered.length !== 3) {
  throw new Error(`expected all blocks without selected module, got ${filtered.length}`);
}

console.log({ preview_module_filter: "ok" });
