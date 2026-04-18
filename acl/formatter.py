"""Terminal output formatter for ACL reports."""

ICONS = {"certain": "✓", "uncertain": "⚠", "review": "✗"}
LABELS_ZH = {"certain": "確定", "uncertain": "推測", "review": "需確認"}
LABELS_EN = {"certain": "Certain  ", "uncertain": "Uncertain", "review": "Review   "}


def print_report(items: list, score: int, summary: str, language: str = "en") -> None:
    """Print formatted ACL report to terminal."""
    width = 52
    border = "─" * width

    if language.startswith("zh"):
        _print_zh(items, score, summary, border)
    else:
        _print_en(items, score, summary, border)


def _print_zh(items, score, summary, border):
    print(f"\n── ACL 校準報告 {border[:width(border)//2]}")
    for item in items:
        icon = ICONS.get(item.get("level", "review"), "?")
        label = LABELS_ZH.get(item.get("level", "review"), "未知")
        msg = item.get("message", "")
        print(f"{icon} {label:<4}  {msg}")
    print(border)
    print(f"校準分數：{score} / 100  |  {summary}")
    print(f"{'─' * 52}\n")


def _print_en(items, score, summary, border):
    print(f"\n── ACL Report {'─' * 38}")
    for item in items:
        icon = ICONS.get(item.get("level", "review"), "?")
        label = LABELS_EN.get(item.get("level", "review"), "Unknown  ")
        msg = item.get("message", "")
        print(f"{icon} {label}  {msg}")
    print(f"{'─' * 52}")
    print(f"Calibration Score: {score} / 100  |  {summary}")
    print(f"{'─' * 52}\n")


def width(s: str) -> int:
    return len(s)
