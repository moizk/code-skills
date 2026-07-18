#!/usr/bin/env python3
"""Behavioral tests for analyze_session. Run: python3 test_analyze_session.py

No third-party deps. Builds a tiny in-memory transcript that exercises every
signal the retrospective relies on, then asserts the extractor reports it.
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_session as mod


def fixture_records():
    return [
        {"type": "user", "userType": "external", "uuid": "u1",
         "timestamp": "2026-06-14T10:00:00Z", "sessionId": "s1",
         "cwd": "/Users/me/app", "gitBranch": "main",
         "message": {"role": "user", "content": "Build a login form"}},
        {"type": "assistant", "uuid": "a1", "timestamp": "2026-06-14T10:00:05Z",
         "attributionSkill": "implement-feature",
         "message": {"role": "assistant", "usage": {
             "input_tokens": 100, "output_tokens": 50,
             "cache_read_input_tokens": 900, "cache_creation_input_tokens": 100},
             "content": [
                 {"type": "thinking", "thinking": "secret reasoning"},
                 {"type": "tool_use", "id": "t1", "name": "Read",
                  "input": {"file_path": "/app/login.rb"}},
                 {"type": "tool_use", "id": "t2", "name": "Bash",
                  "input": {"command": "rspec"}}]}},
        {"type": "user", "uuid": "u2", "timestamp": "2026-06-14T10:00:10Z",
         "message": {"role": "user", "content": [
             {"type": "tool_result", "tool_use_id": "t1", "is_error": False,
              "content": "file contents"},
             {"type": "tool_result", "tool_use_id": "t2", "is_error": True,
              "content": "1 example, 1 failure\nExit code 1"}]}},
        # Repeated reads of the same file -> rework signal (>=3 reads).
        *[{"type": "assistant", "uuid": f"a-r{i}", "timestamp": "2026-06-14T10:01:0%d" % i,
           "message": {"role": "assistant", "usage": {},
                       "content": [{"type": "tool_use", "id": f"r{i}", "name": "Read",
                                    "input": {"file_path": "/app/login.rb"}}]}}
          for i in range(3)],
        # A genuine correction turn -> expectation gap signal.
        {"type": "user", "userType": "external", "uuid": "u3",
         "timestamp": "2026-06-14T10:02:00Z",
         "message": {"role": "user", "content": "No, that's wrong, I said use email not username"}},
        # Injected reminder must NOT count as a user prompt.
        {"type": "user", "userType": "external", "uuid": "u4",
         "timestamp": "2026-06-14T10:02:30Z",
         "message": {"role": "user", "content": "<system-reminder>be nice</system-reminder>"}},
    ]


def write_fixture(records):
    handle = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    for record in records:
        handle.write(json.dumps(record) + "\n")
    handle.close()
    return handle.name


def check(name, condition):
    print(("PASS" if condition else "FAIL"), name)
    if not condition:
        check.failed += 1
check.failed = 0


def main():
    path = write_fixture(fixture_records())
    report = mod.build_report(path, mod.load_records(path))
    raw = json.dumps(report)

    check("session metadata resolved", report["session"]["sessionId"] == "s1")
    check("two genuine user prompts (reminder excluded)", report["user_prompt_count"] == 2)
    check("first prompt is the real ask",
          report["user_prompts"][0]["text"].startswith("Build a login form"))
    check("skill attribution captured",
          report["skills_invoked"].get("implement-feature") == 1)
    check("failed tool result detected", report["tool_error_count"] == 1)
    check("failed tool named correctly", report["tool_errors"][0]["tool"] == "Bash")
    check("rework file flagged", any(f["path"] == "/app/login.rb" for f in report["rework_files"]))
    check("correction candidate flagged", len(report["correction_candidates"]) == 1)
    check("cache hit ratio computed", report["tokens"]["cache_hit_ratio"] == 0.9)
    check("raw thinking never emitted", "secret reasoning" not in raw)

    os.unlink(path)
    if check.failed:
        print(f"\n{check.failed} test(s) failed")
        sys.exit(1)
    print("\nAll tests passed")


if __name__ == "__main__":
    main()
