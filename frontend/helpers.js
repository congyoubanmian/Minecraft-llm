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
  },
};
