"""Core calibration analysis — Sonnet 4.6 (API) or local rule-based mode."""

import json
import os
import re


# ── Keyword patterns ──────────────────────────────────────

UNCERTAIN_PATTERNS_ZH = [
    r"我認為", r"可能", r"應該是", r"推測", r"我猜", r"也許",
    r"不確定", r"感覺像", r"看起來像", r"似乎",
]
UNCERTAIN_PATTERNS_EN = [
    r"\bprobably\b", r"\bmaybe\b", r"\bI think\b", r"\bI assume\b",
    r"\bI guess\b", r"\bseems like\b", r"\bnot sure\b", r"\bperhaps\b",
    r"\bI believe\b", r"\bI infer\b",
]

REVIEW_PATTERNS_ZH = [
    r"我假設", r"假設你", r"如果我理解正確", r"請確認",
    r"你應該是指", r"我推斷", r"沒有明確",
]
REVIEW_PATTERNS_EN = [
    r"\bI assumed\b", r"\bassuming\b", r"\bif I understand correctly\b",
    r"\bplease confirm\b", r"\byou might mean\b", r"\bno explicit\b",
    r"\bI inferred\b",
]

CERTAIN_PATTERNS_ZH = [
    r"已確認", r"成功", r"完成", r"找到", r"執行完畢", r"結果顯示",
]
CERTAIN_PATTERNS_EN = [
    r"\bconfirmed\b", r"\bsuccessfully\b", r"\bcompleted\b",
    r"\bfound\b", r"\bresult shows\b", r"\bverified\b",
]


# ── Local analysis ────────────────────────────────────────

def analyze_local(transcript_text: str, language: str = "en") -> dict:
    """Rule-based calibration analysis — no API key required."""
    is_zh = language.startswith("zh")
    lines = transcript_text.split("\n")
    assistant_lines = [l for l in lines if l.strip().startswith("assistant:")]

    uncertain_patterns = UNCERTAIN_PATTERNS_ZH if is_zh else UNCERTAIN_PATTERNS_EN
    review_patterns    = REVIEW_PATTERNS_ZH    if is_zh else REVIEW_PATTERNS_EN
    certain_patterns   = CERTAIN_PATTERNS_ZH   if is_zh else CERTAIN_PATTERNS_EN

    items = []

    for line in assistant_lines:
        content = line[len("assistant:"):].strip()
        if not content:
            continue

        matched_review = _first_match(content, review_patterns)
        if matched_review and len(items) < 9:
            items.append({
                "level": "review",
                "message": _trim(content, is_zh),
                "source": "transcript",
            })
            continue

        matched_uncertain = _first_match(content, uncertain_patterns)
        if matched_uncertain and len(items) < 9:
            items.append({
                "level": "uncertain",
                "message": _trim(content, is_zh),
                "source": "transcript",
            })
            continue

        matched_certain = _first_match(content, certain_patterns)
        if matched_certain and len(items) < 9:
            items.append({
                "level": "certain",
                "message": _trim(content, is_zh),
                "source": "transcript",
            })

    # Cap at 3 per level
    items = _cap_per_level(items)

    if not items:
        items = [{
            "level": "certain",
            "message": "對話內容無明顯推測或假設語句" if is_zh else "No uncertain or assumption patterns detected",
            "source": "local",
        }]

    counts = {l: sum(1 for i in items if i["level"] == l) for l in ("certain", "uncertain", "review")}
    if is_zh:
        summary = f"確定 {counts['certain']} 項，推測 {counts['uncertain']} 項，需確認 {counts['review']} 項。"
    else:
        summary = f"Certain: {counts['certain']}, Uncertain: {counts['uncertain']}, Review: {counts['review']}."

    return {"items": items, "summary": summary}


def _first_match(text: str, patterns: list) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _trim(text: str, is_zh: bool) -> str:
    limit = 40 if is_zh else 80
    return text[:limit] + "…" if len(text) > limit else text


def _cap_per_level(items: list, max_per: int = 3) -> list:
    counts = {"certain": 0, "uncertain": 0, "review": 0}
    result = []
    for item in items:
        lvl = item.get("level", "review")
        if counts.get(lvl, 0) < max_per:
            result.append(item)
            counts[lvl] = counts.get(lvl, 0) + 1
    return result


# ── API analysis ──────────────────────────────────────────

SYSTEM_PROMPT_ZH = """你是一個 AI 自我校準分析器。
分析這段 Claude Code 對話記錄，判斷 AI 每個行動的確定程度。
輸出嚴格使用以下 JSON 格式，不要有任何其他文字：
{"items":[{"level":"certain","message":"一句話","source":"tool_result 或 transcript"}],"summary":"一句話"}
level: certain=有明確依據 / uncertain=推測可能正確 / review=依賴可能錯誤的假設
每個 level 最多 3 條。"""

SYSTEM_PROMPT_EN = """You are an AI self-calibration analyzer.
Analyze this Claude Code transcript and assess certainty levels.
Output strictly as JSON, no other text:
{"items":[{"level":"certain","message":"one sentence","source":"tool_result or transcript"}],"summary":"one sentence"}
Levels: certain=clear basis / uncertain=inferred, may be correct / review=depends on assumption that may be wrong
Max 3 items per level."""


def analyze(transcript_text: str, language: str = "en") -> dict:
    """
    Analyze transcript. Uses Sonnet 4.6 if API key available, otherwise local mode.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return analyze_local(transcript_text, language)

    try:
        import anthropic
        system_prompt = SYSTEM_PROMPT_ZH if language.startswith("zh") else SYSTEM_PROMPT_EN
        trimmed = transcript_text[-6000:] if len(transcript_text) > 6000 else transcript_text
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Transcript:\n\n{trimmed}"}],
        )
        return json.loads(message.content[0].text.strip())
    except Exception:
        return analyze_local(transcript_text, language)


def calculate_score(items: list) -> int:
    """certain=1.0, uncertain=0.5, review=0.0"""
    if not items:
        return 0
    weights = {"certain": 1.0, "uncertain": 0.5, "review": 0.0}
    total = sum(weights.get(item.get("level", "review"), 0.0) for item in items)
    return round((total / len(items)) * 100)
