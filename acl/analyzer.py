"""Core calibration analysis — calls Sonnet 4.6 to assess the transcript."""

import json
import os
import anthropic


SYSTEM_PROMPT_ZH = """你是一個 AI 自我校準分析器。

你的任務：分析這段 Claude Code 對話記錄，判斷 AI 每個行動的確定程度。

輸出嚴格使用以下 JSON 格式，不要有任何其他文字：
{
  "items": [
    {
      "level": "certain",
      "message": "具體說明（一句話）",
      "source": "tool_result 或 transcript"
    }
  ],
  "summary": "整體評估（一句話）"
}

level 的定義：
- certain：AI 有明確依據，推論可信
- uncertain：AI 做了推測，可能正確但無法確認
- review：AI 的輸出依賴可能錯誤的假設，需要人工確認

每個 level 最多列 3 條，選最重要的。"""

SYSTEM_PROMPT_EN = """You are an AI self-calibration analyzer.

Your task: analyze this Claude Code conversation transcript and assess the certainty level of each AI action.

Output strictly in the following JSON format, no other text:
{
  "items": [
    {
      "level": "certain",
      "message": "specific description (one sentence)",
      "source": "tool_result or transcript"
    }
  ],
  "summary": "overall assessment (one sentence)"
}

Level definitions:
- certain: AI had clear basis, output is reliable
- uncertain: AI made an inference, may be correct but unverifiable
- review: AI output depends on an assumption that may be wrong, needs human review

Maximum 3 items per level. Pick the most important ones."""


def analyze(transcript_text: str, language: str = "en") -> dict:
    """
    Send transcript to Sonnet 4.6 for calibration analysis.
    Returns dict with 'items' and 'summary'.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_result(language)

    system_prompt = SYSTEM_PROMPT_ZH if language.startswith("zh") else SYSTEM_PROMPT_EN

    # Trim transcript to avoid hitting token limits
    trimmed = transcript_text[-6000:] if len(transcript_text) > 6000 else transcript_text

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"Transcript:\n\n{trimmed}",
                }
            ],
        )
        raw = message.content[0].text.strip()
        return json.loads(raw)
    except (json.JSONDecodeError, anthropic.APIError, IndexError):
        return _fallback_result(language)


def _fallback_result(language: str) -> dict:
    """Return a minimal result when analysis cannot be performed."""
    if language.startswith("zh"):
        return {
            "items": [
                {
                    "level": "uncertain",
                    "message": "無法完成校準分析（API 未連線或回應格式錯誤）",
                    "source": "system",
                }
            ],
            "summary": "校準分析未完成",
        }
    return {
        "items": [
            {
                "level": "uncertain",
                "message": "Calibration analysis unavailable (API not connected or response format error)",
                "source": "system",
            }
        ],
        "summary": "Calibration analysis incomplete",
    }


def calculate_score(items: list) -> int:
    """Calculate calibration score: certain=1.0, uncertain=0.5, review=0.0"""
    if not items:
        return 0
    weights = {"certain": 1.0, "uncertain": 0.5, "review": 0.0}
    total = sum(weights.get(item.get("level", "review"), 0.0) for item in items)
    return round((total / len(items)) * 100)
