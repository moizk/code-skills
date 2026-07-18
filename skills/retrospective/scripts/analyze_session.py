#!/usr/bin/env python3
"""Deterministic extractor for a Claude Code session transcript.

Reads a session JSONL transcript and emits a compact, structured summary that a
retrospective agent can reason over WITHOUT pulling the whole transcript (and its
raw chain-of-thought) into context. Raw `thinking` blocks are never emitted; only
counts, metrics, and short evidence snippets keyed by record uuid are returned so
the agent can grep the source file for any moment it wants to inspect closely.

Stdlib only. Safe to run against a transcript that is still being appended to.

Usage:
    analyze_session.py                  # newest transcript for the current cwd
    analyze_session.py --file PATH      # a specific transcript file
    analyze_session.py --session ID     # <ID>.jsonl under the cwd's project dir
    analyze_session.py --cwd DIR        # resolve the project dir for another cwd
    analyze_session.py --list           # list available transcripts, newest first
    analyze_session.py --skip-newest    # use the 2nd-newest (when the newest IS
                                        # the retrospective run itself)
"""

import argparse
import glob
import json
import os
import re
import sys


PROJECTS_ROOT = os.path.expanduser("~/.claude/projects")

# A user turn matching one of these reads as a correction or a re-request: a
# strong signal that the previous result did not meet expectations. Conservative
# on purpose; the agent confirms each hit against the surrounding context.
CORRECTION_PATTERNS = [
    r"\bno[,.]", r"\bnope\b", r"\bactually\b", r"\binstead\b", r"\bnot what\b",
    r"\bthat'?s not\b", r"\bthat'?s wrong\b", r"\bincorrect\b", r"\bwrong\b",
    r"\brevert\b", r"\bundo\b", r"\broll ?back\b", r"\bredo\b", r"\bre-?do\b",
    r"\byou forgot\b", r"\byou missed\b", r"\bshould have\b", r"\bwhy did you\b",
    r"\bi said\b", r"\bas i (said|asked)\b", r"\bstill (not|broken|failing)\b",
    r"\bdon'?t\b", r"\bstop\b", r"\bnot quite\b", r"\bagain\b", r"\bbut i\b",
    r"\bthat'?s not what i\b", r"\bfix (it|this|that)\b", r"\bbroke\b",
]

# Heuristic markers of a failed tool result when `is_error` is not set.
ERROR_TEXT_MARKERS = [
    "exit code 1", "exit code 2", "command not found", "no such file",
    "traceback (most recent call last)", "permission denied",
    "syntaxerror", "fatal:", "npm err!", "error:", "failed",
]

CORRECTION_REGEX = re.compile("|".join(CORRECTION_PATTERNS), re.IGNORECASE)


def cwd_to_project_dir(cwd):
    """Map a working directory to its Claude Code transcript folder.

    The folder name is the absolute path with every "/" and "." turned into "-",
    e.g. /Users/me/app -> -Users-me-app and /Users/me/.x -> -Users-me--x.
    """
    slug = re.sub(r"[/.]", "-", os.path.abspath(cwd))
    return os.path.join(PROJECTS_ROOT, slug)


def list_transcripts(project_dir):
    files = glob.glob(os.path.join(project_dir, "*.jsonl"))
    files.sort(key=os.path.getmtime, reverse=True)
    return files


def resolve_transcript(args):
    if args.file:
        return args.file
    project_dir = args.project_dir or cwd_to_project_dir(args.cwd or os.getcwd())
    if args.session:
        return os.path.join(project_dir, f"{args.session}.jsonl")
    transcripts = list_transcripts(project_dir)
    if not transcripts:
        raise SystemExit(f"No transcripts found in {project_dir}")
    return transcripts[1] if args.skip_newest and len(transcripts) > 1 else transcripts[0]


def load_records(path):
    """Load JSONL records, tolerating a trailing partial line on a live file."""
    records = []
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def snippet(text, limit=200):
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text[:limit] + ("…" if len(text) > limit else "")


def is_injected_text(text):
    head = text.lstrip()[:40].lower()
    return head.startswith("<system-reminder") or head.startswith("<command-")


def blocks_of(record):
    content = record.get("message", {}).get("content")
    if isinstance(content, list):
        return [block for block in content if isinstance(block, dict)]
    return []


def collect_user_prompts(records):
    """Return the genuine human turns in order (not tool outputs, not reminders)."""
    prompts = []
    for record in records:
        if record.get("type") != "user" or record.get("isSidechain"):
            continue
        content = record.get("message", {}).get("content")
        text = None
        if isinstance(content, str):
            text = content
        elif isinstance(content, list):
            has_tool_result = any(b.get("type") == "tool_result" for b in blocks_of(record))
            if has_tool_result:
                continue
            text = " ".join(b.get("text", "") for b in blocks_of(record) if b.get("type") == "text")
        if not text or not text.strip() or is_injected_text(text):
            continue
        prompts.append({
            "ts": record.get("timestamp"),
            "uuid": record.get("uuid"),
            "text": snippet(text, 280),
        })
    return prompts


def find_corrections(prompts):
    flagged = []
    for prompt in prompts:
        match = CORRECTION_REGEX.search(prompt["text"])
        if match:
            flagged.append({**prompt, "matched": match.group(0)})
    return flagged


def looks_like_error(block):
    if block.get("is_error"):
        return True
    content = block.get("content")
    text = content if isinstance(content, str) else json.dumps(content)
    low = text.lower()[:600]
    return any(marker in low for marker in ERROR_TEXT_MARKERS)


def analyze(records):
    tool_names = {}        # tool_use_id -> tool name
    tool_counts = {}
    skill_counts = {}
    file_activity = {}     # path -> {reads, edits, writes}
    tool_errors = []
    tokens = {"input": 0, "output": 0, "cache_read": 0, "cache_creation": 0}
    user_turns = assistant_turns = sidechain_records = 0
    subagent_calls = 0
    timestamps = []

    def touch_file(path, kind):
        entry = file_activity.setdefault(path, {"reads": 0, "edits": 0, "writes": 0})
        entry[kind] += 1

    for record in records:
        kind = record.get("type")
        if record.get("timestamp"):
            timestamps.append(record["timestamp"])
        if record.get("isSidechain"):
            sidechain_records += 1

        if kind == "assistant":
            assistant_turns += 1
            skill = record.get("attributionSkill")
            if skill:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
            usage = record.get("message", {}).get("usage", {}) or {}
            tokens["input"] += usage.get("input_tokens", 0) or 0
            tokens["output"] += usage.get("output_tokens", 0) or 0
            tokens["cache_read"] += usage.get("cache_read_input_tokens", 0) or 0
            tokens["cache_creation"] += usage.get("cache_creation_input_tokens", 0) or 0
            for block in blocks_of(record):
                if block.get("type") != "tool_use":
                    continue
                name = block.get("name", "?")
                tool_names[block.get("id")] = name
                tool_counts[name] = tool_counts.get(name, 0) + 1
                inputs = block.get("input", {}) or {}
                if name in ("Read", "NotebookEdit") and inputs.get("file_path"):
                    touch_file(inputs["file_path"], "reads")
                elif name == "Edit" and inputs.get("file_path"):
                    touch_file(inputs["file_path"], "edits")
                elif name == "Write" and inputs.get("file_path"):
                    touch_file(inputs["file_path"], "writes")
                elif name in ("Agent", "Task"):
                    subagent_calls += 1

        elif kind == "user":
            if not record.get("isSidechain"):
                content = record.get("message", {}).get("content")
                if isinstance(content, str) or not any(
                    b.get("type") == "tool_result" for b in blocks_of(record)
                ):
                    user_turns += 1
            for block in blocks_of(record):
                if block.get("type") == "tool_result" and looks_like_error(block):
                    tool_errors.append({
                        "ts": record.get("timestamp"),
                        "uuid": record.get("uuid"),
                        "tool": tool_names.get(block.get("tool_use_id"), "?"),
                        "snippet": snippet(
                            block.get("content") if isinstance(block.get("content"), str)
                            else json.dumps(block.get("content")), 240),
                    })

    cache_total = tokens["cache_read"] + tokens["cache_creation"]
    cache_hit_ratio = round(tokens["cache_read"] / cache_total, 3) if cache_total else None
    rework_files = sorted(
        ({"path": p, **a} for p, a in file_activity.items()
         if a["reads"] >= 3 or a["edits"] >= 3 or (a["reads"] + a["edits"] + a["writes"]) >= 4),
        key=lambda f: f["reads"] + f["edits"] + f["writes"], reverse=True,
    )

    return {
        "messages": {
            "user_turns": user_turns,
            "assistant_turns": assistant_turns,
            "sidechain_records": sidechain_records,
            "subagent_calls": subagent_calls,
        },
        "started": timestamps[0] if timestamps else None,
        "ended": timestamps[-1] if timestamps else None,
        "skills_invoked": dict(sorted(skill_counts.items(), key=lambda x: -x[1])),
        "tools": dict(sorted(tool_counts.items(), key=lambda x: -x[1])),
        "tool_error_count": len(tool_errors),
        "tool_errors": tool_errors[:40],
        "tokens": {**tokens, "cache_hit_ratio": cache_hit_ratio},
        "rework_files": rework_files[:20],
    }


def build_report(path, records):
    first = next((r for r in records if r.get("sessionId")), {})
    summary = analyze(records)
    prompts = collect_user_prompts(records)
    corrections = find_corrections(prompts)
    return {
        "session": {
            "file": path,
            "sessionId": first.get("sessionId"),
            "cwd": first.get("cwd"),
            "gitBranch": first.get("gitBranch"),
            "version": first.get("version"),
            "num_records": len(records),
            "started": summary.pop("started"),
            "ended": summary.pop("ended"),
        },
        **summary,
        "user_prompt_count": len(prompts),
        "user_prompts": prompts,
        "correction_candidates": corrections,
    }


def main():
    parser = argparse.ArgumentParser(description="Summarize a Claude Code session transcript.")
    parser.add_argument("--file")
    parser.add_argument("--session")
    parser.add_argument("--cwd")
    parser.add_argument("--project-dir")
    parser.add_argument("--skip-newest", action="store_true")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        project_dir = args.project_dir or cwd_to_project_dir(args.cwd or os.getcwd())
        for transcript in list_transcripts(project_dir):
            print(transcript)
        return

    path = resolve_transcript(args)
    if not os.path.exists(path):
        raise SystemExit(f"Transcript not found: {path}")
    report = build_report(path, load_records(path))
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
