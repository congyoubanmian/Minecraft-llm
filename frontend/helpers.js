window.McHelpers = {
  methods: {
    formatJson(value) {
      return JSON.stringify(value, null, 2);
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
    ratioText(value) {
      if (typeof value !== "number") return "-";
      return `${Math.round(value * 1000) / 10}%`;
    },
    formatBytes(value) {
      if (typeof value !== "number") return "-";
      if (value < 1024) return `${value} B`;
      const units = ["KB", "MB", "GB", "TB"];
      let size = value / 1024;
      let unit = 0;
      while (size >= 1024 && unit < units.length - 1) {
        size /= 1024;
        unit += 1;
      }
      return `${size.toFixed(size >= 100 ? 0 : size >= 10 ? 1 : 2)} ${units[unit]}`;
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
    buildDiagnosticRepairPrompt(report) {
      const warnings = (report?.warnings || []).slice(0, 8);
      const blueprint = report?.design_blueprint || {};
      const interfaceIssues = (blueprint.interface_checks || [])
        .filter((item) => !item.ok)
        .slice(0, 6)
        .map((item) => `${item.from}.${item.from_face} -> ${item.to}.${item.to_face}: ${item.message || item.status}`);
      const stageIssues = (blueprint.stage_checks || [])
        .filter((item) => !item.executable)
        .slice(0, 6)
        .map((item) => `${item.role}: ${item.message || "阶段不可单独施工"}`);
      const lines = [
        "请根据当前生成诊断修复这个 Minecraft 建筑方案。",
        "先更新 analysis.design_spec，再同步修改 parts，确保模块 bbox、接口面和实际方块一致。",
      ];
      if (blueprint.building_type || report?.template_guess) {
        lines.push(`建筑类型/模板：${blueprint.building_type || "-"} / ${report.template_guess || "-"}`);
      }
      if (warnings.length) {
        lines.push("需要处理的 warning：");
        warnings.forEach((item) => lines.push(`- ${item}`));
      }
      if (interfaceIssues.length) {
        lines.push("接口切口问题：");
        interfaceIssues.forEach((item) => lines.push(`- ${item}`));
      }
      if (stageIssues.length) {
        lines.push("施工阶段问题：");
        stageIssues.forEach((item) => lines.push(`- ${item}`));
      }
      lines.push("保持用户原始建筑意图不变，只修正比例、模块、接口、材料、灯光或性能问题。");
      return lines.join("\n");
    },
  },
};
