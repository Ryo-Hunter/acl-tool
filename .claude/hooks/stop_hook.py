#!/usr/bin/env python3
"""
ACL Stop Hook — triggered by Claude Code when a session ends.
Reads transcript, runs calibration analysis, outputs report.
"""

import json
import sys
import os

# Allow running from any working directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from acl.lang import detect_language, load_config
from acl.analyzer import analyze, calculate_score
from acl.formatter import print_report
from acl.reporter import save_report, run_cleanup


def read_transcript(data: dict) -> str:
    """Extract readable text from hook input data."""
    # Try transcript_path first (Claude Code passes a file path)
    transcript_path = data.get("transcript_path", "")
    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # Flatten messages to plain text
            lines = []
            for msg in raw if isinstance(raw, list) else []:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if isinstance(content, list):
                    content = " ".join(
                        c.get("text", "") for c in content if isinstance(c, dict)
                    )
                lines.append(f"{role}: {content}")
            return "\n".join(lines)
        except (json.JSONDecodeError, OSError):
            pass

    # Fallback: use raw transcript field if present
    transcript = data.get("transcript", [])
    if isinstance(transcript, list):
        lines = []
        for msg in transcript:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    c.get("text", "") for c in content if isinstance(c, dict)
                )
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    return str(transcript)


def main():
    # Read hook input from stdin
    try:
        raw_input = sys.stdin.read()
        data = json.loads(raw_input) if raw_input.strip() else {}
    except json.JSONDecodeError:
        data = {}

    session_id = data.get("session_id", "unknown")

    # Load config
    config = load_config()

    # Get transcript text
    transcript_text = read_transcript(data)

    if not transcript_text.strip():
        print("[ACL] 沒有對話記錄可分析。" if os.environ.get("LANG", "").startswith("zh") else "[ACL] No transcript to analyze.")
        return

    # Detect language
    language = detect_language(config, transcript_text)

    # Run analysis
    result = analyze(transcript_text, language)
    items = result.get("items", [])
    summary = result.get("summary", "")
    score = calculate_score(items)

    # Print to terminal
    print_report(items, score, summary, language)

    # Save to file
    filepath = save_report(session_id, items, score, summary, language)
    label = "報告已儲存：" if language.startswith("zh") else "Report saved: "
    print(f"[ACL] {label}{filepath}\n")

    # Run cleanup check
    run_cleanup(config)


if __name__ == "__main__":
    main()
