const fs = require("fs");
const vm = require("vm");

const source = fs.readFileSync("frontend/helpers.js", "utf8");
const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(source, sandbox);

const methods = sandbox.window.McHelpers.methods;
const prompt = methods.buildDiagnosticRepairPrompt({
  template_guess: "modern_glass_gate",
  warnings: [
    "门形地标需要清晰中央空洞和高玻璃比例。",
    "现代高层灯光比例偏低。",
  ],
  design_blueprint: {
    building_type: "landmark_gate",
    interface_checks: [
      {
        ok: false,
        from: "left_tower",
        from_face: "east",
        to: "skybridge",
        to_face: "west",
        status: "gap",
        message: "bbox 没有按声明面接触或一格重叠。",
      },
      {
        ok: true,
        from: "podium",
        from_face: "top",
        to: "left_tower",
        to_face: "bottom",
        status: "ok",
      },
    ],
    stage_checks: [
      {
        executable: false,
        role: "facade",
        message: "阶段 facade 有模块缺少 bbox。",
      },
    ],
  },
});

for (const expected of [
  "请根据当前生成诊断修复",
  "landmark_gate / modern_glass_gate",
  "门形地标需要清晰中央空洞",
  "left_tower.east -> skybridge.west",
  "阶段 facade 有模块缺少 bbox",
  "保持用户原始建筑意图不变",
]) {
  if (!prompt.includes(expected)) {
    throw new Error(`expected prompt to include ${expected}\n${prompt}`);
  }
}

if (prompt.includes("podium.top")) {
  throw new Error(`expected healthy interface to be omitted\n${prompt}`);
}

console.log({ diagnostic_repair_prompt: "ok" });
