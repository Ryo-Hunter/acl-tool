"""JSON report writer and cleanup manager for ACL."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path


REPORTS_DIR = ".acl/reports"


def save_report(session_id: str, items: list, score: int, summary: str, language: str) -> str:
    """Save ACL report as JSON. Returns the file path."""
    Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"acl_{session_id[:8]}_{timestamp}.json"
    filepath = os.path.join(REPORTS_DIR, filename)

    report = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "language": language,
        "calibration_score": score,
        "summary": summary,
        "items": items,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return filepath


def run_cleanup(config: dict) -> None:
    """
    Check for old reports and handle based on cleanup_mode.
    - 'auto': delete without asking
    - 'semi': prompt user before deleting
    """
    mode = config.get("cleanup_mode", "semi")
    days = config.get("cleanup_days", 30)
    cutoff = datetime.now() - timedelta(days=days)

    reports_path = Path(REPORTS_DIR)
    if not reports_path.exists():
        return

    old_files = [
        f for f in reports_path.glob("acl_*.json")
        if datetime.fromtimestamp(f.stat().st_mtime) < cutoff
    ]

    if not old_files:
        return

    if mode == "auto":
        for f in old_files:
            f.unlink()
        print(f"[ACL] 已自動清理 {len(old_files)} 份過期報告。")

    elif mode == "semi":
        print(f"\n[ACL] 發現 {len(old_files)} 份超過 {days} 天的報告。")
        answer = input("是否刪除？(y/N) ").strip().lower()
        if answer == "y":
            for f in old_files:
                f.unlink()
            print(f"[ACL] 已刪除 {len(old_files)} 份報告。")
        else:
            print("[ACL] 略過清理。")
