#!/usr/bin/env python3
"""
Chrome Extension Orchestrator

This module restores the original Charter generation CLI (for creating
CHARTER.md, COMMANDS.json, task.json under ~/.tab_orchestrator/tasks/<slug>/)
while keeping the Memory Store integration for /harvest and /synthesize.

It also introduces a minimal persistent StateTracker that writes STATUS.json
so agents and utilities (e.g., Siri bridge) can query progress.

Usage:
  python orchestrator.py "<Task Title>" domain1 [domain2 ...]
  python orchestrator.py "<Task Title>" --phase triage

Notes:
- The CLI primarily generates the Charter. Phase hooks are lightweight and
  only update STATUS.json; runtime work is done by the browser agent.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional
import argparse
import importlib.util
import json
import re
import sys
import textwrap

# ---------------------------------------------------------------------------
# Paths and constants
ROOT = Path.home() / ".tab_orchestrator"
(ROOT / "tasks").mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Charter generation (ported from tab-group-orchestrator)
@dataclass
class TaskSpec:
    title: str
    allowed_domains: List[str]
    outputs_doc_title: str
    outputs_sheet_title: Optional[str] = None
    risk_mode: str = "ask-before-acting"   # or "always-allow-listed"
    notes: str = ""


def slugify(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return (s[:60] if len(s) > 60 else s) or "task"


CHARTER_TMPL = """\
# === TASK CHARTER (Paste in first tab doc) ===

task: "{title}"
created: "{created}"
risk_mode: "{risk_mode}"
allowed_domains:
{domains}
forbidden_actions:
  - login
  - financial_tx
  - cookie_consent_beyond_reject
stop_conditions:
  - "permission stalled > 60s"
  - "domain not in allowed_domains"
outputs:
  - doc: "{doc_title}"
{sheet_line}review_protocol: |
  - All findings must be written into the doc above.
  - Cite source URL + last-updated date for every claim.
  - Ask before creating any files or sheets.
notes: |
{notes}
"""

COMMANDS: Dict[str, str] = {
    "init-group": """\
Read the Task Charter visible in this tab. Restate:
- goals
- allowed_domains
- risk_mode
Then propose a 3-phase plan: triage → harvest → synthesize. Ask me to confirm before acting.""",
    "triage": """\
Open up to 6 high-signal sources within allowed_domains in this tab group.
For each page: extract title/author/date/claims/URL into a table in the charter doc
(or a new Google Sheet named in the charter if it exists). Do not log in. Stop if a domain is outside the allowlist.""",
    "harvest": """\
From every open tab in this group, extract structured fields relevant to the task
(e.g., API: name, endpoint, auth, rate limit, version, license; Research: claim, method, dataset, limitations).
Append rows to the doc/Sheet. Flag contradictions and outdated content.""",
    "synthesize": """\
In the charter doc, write a concise synthesis:
- what is known vs. uncertain (bullets)
- ranked sources with reasons
- 3 recommended next actions
Include a 'DATA APPENDIX' with the table summary and source URLs.""",
    "report": """\
Answer the specific user question using ONLY the material captured in this tab group.
If evidence is insufficient, say exactly what’s missing and propose where to get it (allowed_domains only).""",
    "clean": """\
Close non-source tabs, keep charter + synthesis open. Print a final checklist in the doc:
- decisions made
- open questions
- blocked on (with owners)
- exact next steps (who/what/when).""",
}

PERSONA_SNIPPET = """\
<persona>
You are a Metacognitive Planner, an advanced AI designed for the rigorous architecture of complex workflows and the strategic decomposition of high-level goals. You operate as a master of first-principles thinking, analyzing a desired outcome and constructing the most efficient, logical, and executable plan to achieve it. Your final product is not the answer itself, but a high-quality, step-by-step plan for another agent (AI or human) to execute. Your function is to architect the "how" before execution begins.
</persona>

<axioms>
<Axiom_1_Epistemic_Humility_and_Verification>
Your core assumption is that a plan built on outdated or incorrect information is useless. Therefore, before finalizing a plan, you MUST use your web search tool or other tools to verify foundational facts, identify best practices, and understand the current context of the problem domain. The principle is: Research before you architect.
</Axiom_1_Epistemic_Humility_and_Verification>

<Axiom_2_Principled_Deconstruction>
No goal is to be accepted at face value. Every objective must be systematically deconstructed into its constituent parts, identifying the required inputs, processes, and desired outputs to ensure the resulting plan is comprehensive and addresses all implicit needs.
</Axiom_2_Principled_Deconstruction>

<Axiom_3_Strategic_Intentionality>
Every step in the generated plan must be a deliberate, justified, and actionable task. There are no vague steps. Each task must have a clear purpose that contributes directly to the final objective, and the plan as a whole must represent the most logical sequence of operations.
</Axiom_3_Strategic_Intentionality>
</axioms>
"""


def make_charter(ts: TaskSpec) -> str:
    doms = "\n".join(f"  - {d}" for d in ts.allowed_domains)
    sheet = f'  - sheet: "{ts.outputs_sheet_title}"' if ts.outputs_sheet_title else ""
    return CHARTER_TMPL.format(
        title=ts.title,
        created=datetime.now().isoformat(timespec="seconds"),
        risk_mode=ts.risk_mode,
        domains=doms or "  - (add domains)",
        doc_title=ts.outputs_doc_title,
        sheet_line=sheet,
        notes=textwrap.indent(ts.notes.strip() or "(add notes)", "  "),
    )


def emit_shortcuts_json() -> str:
    return json.dumps({name: PERSONA_SNIPPET + prompt for name, prompt in COMMANDS.items()}, indent=2)


def save_task(ts: TaskSpec, charter: str) -> Path:
    slug = f"{slugify(ts.title)}_{datetime.now().strftime('%Y%m%d')}"
    tdir = ROOT / "tasks" / slug
    tdir.mkdir(parents=True, exist_ok=True)
    (tdir / "CHARTER.md").write_text(charter, encoding="utf-8")
    (tdir / "COMMANDS.json").write_text(emit_shortcuts_json(), encoding="utf-8")
    (tdir / "task.json").write_text(json.dumps(asdict(ts), indent=2), encoding="utf-8")
    return tdir


def _dynamic_import_from(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:  # pragma: no cover
        raise ImportError(f"Failed to load module from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


# Load Memory (packages/memory-store) with a synthetic package so relative imports work
_MEM_DIR = Path(__file__).resolve().parents[2] / "packages" / "memory-store"
_MEM_FILE = _MEM_DIR / "memory.py"
import types
# Create a synthetic package named 'memory_store' that points to the directory
pkg_name = "memory_store"
if pkg_name not in sys.modules:
    pkg = types.ModuleType(pkg_name)
    pkg.__path__ = [str(_MEM_DIR)]  # allow submodule imports from this directory
    sys.modules[pkg_name] = pkg
_mem_spec = importlib.util.spec_from_file_location(f"{pkg_name}.memory", _MEM_FILE)
if not _mem_spec or not _mem_spec.loader:  # pragma: no cover
    raise ImportError(f"Failed to load Memory module from {_MEM_FILE}")
_mem_mod = importlib.util.module_from_spec(_mem_spec)
sys.modules[f"{pkg_name}.memory"] = _mem_mod
_mem_spec.loader.exec_module(_mem_mod)  # type: ignore[attr-defined]
Memory = getattr(_mem_mod, "Memory")
Hit = getattr(_mem_mod, "Hit")

# Load StateTracker (same directory)
_STATE_FILE = Path(__file__).resolve().parent / "state_tracker.py"
_state_mod = _dynamic_import_from(_STATE_FILE, "state_tracker_mod")
StateTracker = getattr(_state_mod, "StateTracker")


# ---------------------------------------------------------------------------
# Runtime hooks for agent use
@dataclass
class Page:
    url: str
    text: str
    selector: str = "body"
    last_updated: Optional[str] = None


class ChromeOrchestrator:
    """Runtime hooks for agent during /harvest and /synthesize."""

    def __init__(self, charter_id: str, allowed_domains: List[str]) -> None:
        self.charter_id = charter_id
        self.allowed_domains = allowed_domains
        self.mem = Memory(charter_id)
        self.state = StateTracker(charter_id)

    def harvest(self, pages: Iterable[Page]) -> int:
        self.state.start_phase("harvest", metadata={"sources_total": len(list(pages)) if hasattr(pages, "__len__") else None})
        cnt = 0
        for p in pages:
            if not self._allowed(p.url):
                continue
            self.mem.add(p.url, p.text, selector=p.selector, last_updated=p.last_updated)
            self.state.log_source_processed(p.url)
            cnt += 1
        self.state.complete_phase("harvest", metadata={"sources_processed": cnt})
        return cnt

    def synthesize(self, queries: List[str], k: int = 5) -> List[List[Hit]]:
        self.state.start_phase("synthesize")
        results: List[List[Hit]] = []
        filters = {"allowed_domains": self.allowed_domains}
        for q in queries:
            hits = self.mem.search(q, k=k, filters=filters, filter_allowed=True)
            results.append(hits)
        self.state.complete_phase("synthesize")
        return results

    def clean(self, snapshot_path: Optional[str] = None) -> None:
        if snapshot_path:
            self.mem.snapshot(snapshot_path)
        self.mem.reset()

    def _allowed(self, url: str) -> bool:
        for pat in self.allowed_domains:
            if pat.endswith("*"):
                if url.startswith(pat[:-1]):
                    return True
            else:
                if url.startswith(pat):
                    return True
        return False


# ---------------------------------------------------------------------------
# CLI

def _init_status(tdir: Path) -> None:
    charter_id = tdir.name
    StateTracker(charter_id)  # constructor ensures STATUS.json exists


def _find_latest_task_dir(title: str) -> Optional[Path]:
    prefix = slugify(title) + "_"
    troot = ROOT / "tasks"
    if not troot.exists():
        return None
    candidates = [p for p in troot.iterdir() if p.is_dir() and p.name.startswith(prefix)]
    if not candidates:
        return None
    # Names end with YYYYMMDD → lexicographic max is latest
    candidates.sort(key=lambda p: p.name)
    return candidates[-1]


def main(argv: List[str]) -> int:
    p = argparse.ArgumentParser(description="Chrome Extension Orchestrator CLI")
    p.add_argument("title", help="Task title")
    p.add_argument("domains", nargs="*", help="Allowed domains (prefixes; * suffix allowed)")
    p.add_argument("--phase", choices=["init-group", "triage", "harvest", "synthesize", "report", "clean"], help="Optional phase hook to mark in STATUS.json")
    args = p.parse_args(argv[1:])

    if args.phase:
        # Phase hook: update STATUS.json for the latest task matching title
        tdir = _find_latest_task_dir(args.title)
        if not tdir:
            print(f"No existing task directory found for title '{args.title}'. Generate the Charter first.", file=sys.stderr)
            return 4
        st = StateTracker(tdir.name)
        st.start_phase(args.phase)
        st.complete_phase(args.phase)
        print(json.dumps({"ok": True, "charter_id": tdir.name, "phase": args.phase, "status": "marked"}, indent=2))
        return 0

    # Charter generation path
    if not args.domains:
        print("Usage: python orchestrator.py \"<Task Title>\" domain1 [domain2 ...]", file=sys.stderr)
        return 1

    ts = TaskSpec(
        title=args.title.strip(),
        allowed_domains=[d.strip() for d in args.domains if d.strip()],
        outputs_doc_title=f"{slugify(args.title)} — Charter & Synthesis",
        outputs_sheet_title=f"{slugify(args.title)}_table",
    )
    charter = make_charter(ts)
    try:
        tdir = save_task(ts, charter)
    except OSError as e:
        print(f"Failed to save task files: {e}", file=sys.stderr)
        return 2
    _init_status(tdir)
    print(f"[OK] Created task folder: {tdir}")
    print("\n=== Paste this in the first tab doc ===\n")
    print(charter)
    print("\n=== Add these to Claude Shortcuts (/commands) ===\n")
    print(emit_shortcuts_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
