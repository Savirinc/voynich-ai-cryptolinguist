"""Pretrained reasoning-model backend for System C.

Uses the Claude Code CLI in headless mode (`claude -p`) with all tools, settings, MCP servers and
skills disabled and a task-specific system prompt (~0.6k tokens of total context, verified), so the model only sees what we pass it (no repository, no web,
no plaintext corpora). Every call is logged to agent_logs/ with prompt, response, model and cost.
The model proposes hypotheses and actions; it never sees secret answers or verifiers.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOGS = ROOT / "agent_logs"


class BudgetExceeded(RuntimeError):
    pass


class ClaudeCLI:
    def __init__(self, model: str = "sonnet", run_name: str = "run", max_calls: int = 200, timeout: int = 180):
        self.model, self.max_calls, self.timeout = model, max_calls, timeout
        self.calls, self.cost = 0, 0.0
        self.log_path = LOGS / f"{run_name}.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.workdir = tempfile.mkdtemp(prefix="vcl_agent_")   # empty cwd: nothing to read

    def __call__(self, system: str, prompt: str, role: str = "agent") -> str:
        if self.calls >= self.max_calls:
            raise BudgetExceeded(f"max_calls={self.max_calls} reached")
        cmd = ["claude", "-p", "--model", self.model, "--tools", "", "--no-session-persistence",
               "--setting-sources", "", "--strict-mcp-config", "--disable-slash-commands",
               "--output-format", "json", "--system-prompt", system]
        t0 = time.time()
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=self.timeout,
                           cwd=self.workdir, env=os.environ | {"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"})
        self.calls += 1
        try:
            out = json.loads(r.stdout)
            text, cost = out.get("result", ""), float(out.get("total_cost_usd") or 0)
        except json.JSONDecodeError:
            text, cost = r.stdout or r.stderr, 0.0
        self.cost += cost
        with open(self.log_path, "a") as f:
            f.write(json.dumps({"t": t0, "secs": round(time.time() - t0, 2), "role": role, "model": self.model,
                                "system_sha256": hashlib.sha256(system.encode()).hexdigest()[:16],
                                "prompt": prompt, "response": text, "cost_usd": cost,
                                "returncode": r.returncode}) + "\n")
        return text


def extract_json(text: str):
    """Return the last top-level JSON object in a model response, or None."""
    depth, start, last = 0, None, None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                last = text[start:i + 1]
    if last is None:
        return None
    try:
        return json.loads(last)
    except json.JSONDecodeError:
        return None
