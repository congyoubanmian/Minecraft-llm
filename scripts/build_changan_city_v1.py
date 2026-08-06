from __future__ import annotations

import json
import sys
import time
import argparse
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]
COMMANDS_PATH = ROOT / "backend/projects/changan_city_v1/commands.json"
BOT_URL = "http://127.0.0.1:3001"


def command_batches(commands: list[str], batch_size: int) -> list[list[str]]:
    executable = [command for command in commands if command.strip() and not command.lstrip().startswith("#")]
    return [executable[index : index + batch_size] for index in range(0, len(executable), batch_size)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Chang'an city v1 from generated command list.")
    parser.add_argument("batch_size", nargs="?", type=int, default=250)
    parser.add_argument("--start-batch", type=int, default=1, help="1-based batch index to start from.")
    parser.add_argument("--limit-batches", type=int, default=None)
    parser.add_argument("--delay-ms", type=int, default=60)
    parser.add_argument("--timeout", type=float, default=180)
    args = parser.parse_args()

    payload = json.loads(COMMANDS_PATH.read_text(encoding="utf-8"))
    batches = command_batches(payload["commands"], args.batch_size)
    selected = batches[args.start_batch - 1 :]
    if args.limit_batches is not None:
        selected = selected[: args.limit_batches]
    print(
        json.dumps(
            {
                "commands": sum(len(batch) for batch in batches),
                "batches": len(batches),
                "batch_size": args.batch_size,
                "start_batch": args.start_batch,
                "selected_batches": len(selected),
                "delay_ms": args.delay_ms,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    with httpx.Client(timeout=args.timeout) as client:
        for index, batch in enumerate(selected, start=args.start_batch):
            response = client.post(f"{BOT_URL}/commands", json={"commands": batch, "delay_ms": args.delay_ms})
            response.raise_for_status()
            print(
                json.dumps(
                    {"batch": index, "total_batches": len(batches), "commands": len(batch), "ok": response.json().get("ok")},
                    ensure_ascii=False,
                ),
                flush=True,
            )
            time.sleep(0.25)


if __name__ == "__main__":
    main()
