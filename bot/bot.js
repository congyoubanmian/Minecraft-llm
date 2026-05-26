import express from "express";
import mineflayer from "mineflayer";

const app = express();
app.use(express.json());

const config = {
  host: process.env.MC_HOST || "localhost",
  port: Number(process.env.MC_PORT || 25565),
  username: process.env.BOT_USERNAME || "BuilderBot",
  version: process.env.MC_VERSION || false,
};

let bot = null;
let ready = false;
let reconnectTimer = null;

function connect() {
  ready = false;
  bot = mineflayer.createBot(config);

  bot.once("spawn", () => {
    bot.physicsEnabled = false;
    ready = true;
    console.log(`[bot] spawned as ${config.username}`);
  });

  bot.on("end", () => scheduleReconnect("ended"));
  bot.on("kicked", (reason) => scheduleReconnect(`kicked: ${reason}`));
  bot.on("error", (error) => console.error("[bot] error", error.message));
}

function scheduleReconnect(reason) {
  ready = false;
  console.log(`[bot] ${reason}; reconnecting soon`);
  if (reconnectTimer) return;
  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    connect();
  }, 5000);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitUntilReady(timeoutMs = 45000) {
  const startedAt = Date.now();
  while (!ready) {
    if (Date.now() - startedAt > timeoutMs) {
      throw new Error("bot is not ready");
    }
    await sleep(500);
  }
}

async function chatCommand(command, delayMs = 1200) {
  bot.chat(command);
  await sleep(delayMs);
  return command;
}

app.get("/health", (_req, res) => {
  res.json({ ready, username: config.username });
});

app.post("/paste", async (req, res) => {
  try {
    await waitUntilReady();
    const { schematic, x = 0, y = 80, z = 0 } = req.body || {};
    if (!schematic) {
      res.status(400).json({ error: "schematic is required" });
      return;
    }

    const commands = [];
    commands.push(await chatCommand(`/tp ${config.username} ${x} ${y} ${z}`));
    commands.push(await chatCommand(`/schem load ${schematic}`, 1800));
    commands.push(await chatCommand("//paste -a", 2500));
    res.json({ ok: true, commands });
  } catch (error) {
    res.status(500).json({ error: error instanceof Error ? error.message : String(error) });
  }
});

const port = Number(process.env.BOT_HTTP_PORT || 3001);
app.listen(port, () => {
  console.log(`[bot] http listening on ${port}`);
  connect();
});
