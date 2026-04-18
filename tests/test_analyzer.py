"""Tests for ACL core logic — runs without API credits using mock data."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from acl.analyzer import calculate_score
from acl.lang import detect_language, load_config
from acl.formatter import print_report
from acl.reporter import save_report

# ── Test data ────────────────────────────────────────────

MOCK_ITEMS_ZH = [
    {"level": "certain",   "message": "正確解析使用者輸入，符合 3 個約束條件", "source": "tool_result"},
    {"level": "uncertain", "message": "第 47 行推測使用者意圖，無明確指示",     "source": "transcript"},
    {"level": "review",    "message": "輸出依賴可能錯誤的假設，建議人工確認", "source": "transcript"},
]

MOCK_ITEMS_EN = [
    {"level": "certain",   "message": "parsed input correctly, matched 3 constraints", "source": "tool_result"},
    {"level": "uncertain", "message": "line 47 — inferred intent, no explicit instruction", "source": "transcript"},
    {"level": "review",    "message": "output depends on assumption that may be wrong", "source": "transcript"},
]

MOCK_SUMMARY_ZH = "本次對話整體校準程度中等，有一處需要人工確認。"
MOCK_SUMMARY_EN = "Overall calibration is moderate; one item requires human review."


# ── Test: calculate_score ─────────────────────────────────

def test_score_mixed():
    score = calculate_score(MOCK_ITEMS_ZH)
    assert score == 50, f"預期 50，得到 {score}"
    print(f"  ✓ 混合項目分數：{score} / 100")

def test_score_all_certain():
    items = [{"level": "certain"}, {"level": "certain"}, {"level": "certain"}]
    score = calculate_score(items)
    assert score == 100, f"預期 100，得到 {score}"
    print(f"  ✓ 全確定分數：{score} / 100")

def test_score_all_review():
    items = [{"level": "review"}, {"level": "review"}]
    score = calculate_score(items)
    assert score == 0, f"預期 0，得到 {score}"
    print(f"  ✓ 全需確認分數：{score} / 100")

def test_score_empty():
    score = calculate_score([])
    assert score == 0, f"預期 0，得到 {score}"
    print(f"  ✓ 空項目分數：{score} / 100")


# ── Test: detect_language ─────────────────────────────────

def test_lang_zh_tw():
    config = {"language": "auto"}
    lang = detect_language(config, "今天我們一起建立了一個很棒的工具，繁體中文測試。")
    assert lang == "zh-TW", f"預期 zh-TW，得到 {lang}"
    print(f"  ✓ 語言偵測繁體中文：{lang}")

def test_lang_explicit():
    config = {"language": "zh-TW"}
    lang = detect_language(config, "hello world this is english")
    assert lang == "zh-TW", f"設定值應優先，預期 zh-TW，得到 {lang}"
    print(f"  ✓ 明確設定語言優先：{lang}")

def test_lang_english_fallback():
    config = {"language": "auto"}
    lang = detect_language(config, "hello world this is a test transcript")
    assert lang == "en", f"預期 en，得到 {lang}"
    print(f"  ✓ 英文 fallback：{lang}")

def test_load_config_defaults():
    config = load_config("nonexistent_path.json")
    assert config["cleanup_mode"] == "semi"
    assert config["cleanup_days"] == 30
    assert config["language"] == "auto"
    print(f"  ✓ 預設 config 載入正確")


# ── Test: formatter (visual only) ────────────────────────

def test_formatter_zh():
    print("\n  [中文輸出預覽]")
    print_report(MOCK_ITEMS_ZH, 50, MOCK_SUMMARY_ZH, "zh-TW")

def test_formatter_en():
    print("\n  [English output preview]")
    print_report(MOCK_ITEMS_EN, 50, MOCK_SUMMARY_EN, "en")


# ── Test: reporter (file write) ───────────────────────────

def test_save_report():
    filepath = save_report(
        session_id="test_session_001",
        items=MOCK_ITEMS_ZH,
        score=50,
        summary=MOCK_SUMMARY_ZH,
        language="zh-TW",
    )
    assert os.path.exists(filepath), f"報告檔案不存在：{filepath}"
    print(f"  ✓ 報告已儲存：{filepath}")
    # Cleanup
    os.remove(filepath)
    print(f"  ✓ 測試報告已清除")


# ── Run all tests ─────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        ("calculate_score — 混合", test_score_mixed),
        ("calculate_score — 全確定", test_score_all_certain),
        ("calculate_score — 全需確認", test_score_all_review),
        ("calculate_score — 空", test_score_empty),
        ("detect_language — 繁體中文", test_lang_zh_tw),
        ("detect_language — 明確設定", test_lang_explicit),
        ("detect_language — 英文 fallback", test_lang_english_fallback),
        ("load_config — 預設值", test_load_config_defaults),
        ("formatter — 中文", test_formatter_zh),
        ("formatter — 英文", test_formatter_en),
        ("reporter — 寫檔", test_save_report),
    ]

    passed = 0
    failed = 0
    print("\n=== ACL 測試開始 ===\n")
    for name, fn in tests:
        print(f"▶ {name}")
        try:
            fn()
            passed += 1
        except Exception as e:
            print(f"  ✗ 失敗：{e}")
            failed += 1

    print(f"\n=== 結果：{passed} 通過 / {failed} 失敗 ===\n")
