"""Language detection for ACL reports."""

import os
import json


def detect_language(config: dict, transcript_text: str = "") -> str:
    """
    Detect report language.
    Priority: config setting > LANG env var > transcript content > default 'en'
    """
    lang_setting = config.get("language", "auto")

    if lang_setting != "auto":
        return lang_setting

    # Check system environment
    env_lang = os.environ.get("LANG", "") or os.environ.get("LC_ALL", "")
    if "zh_TW" in env_lang or "zh-TW" in env_lang:
        return "zh-TW"
    if "zh_CN" in env_lang or "zh-CN" in env_lang:
        return "zh-CN"

    # Detect from transcript content (check first 500 chars)
    sample = transcript_text[:500]
    zh_chars = sum(1 for c in sample if "\u4e00" <= c <= "\u9fff")
    if zh_chars > 10:
        # Traditional vs Simplified: check for common Traditional-only chars
        trad_markers = "繁體為的說話這個來過時從對後是"
        simp_markers = "简体为的说话这个来过时从对后是"
        trad_count = sum(1 for c in sample if c in trad_markers)
        simp_count = sum(1 for c in sample if c in simp_markers)
        return "zh-TW" if trad_count >= simp_count else "zh-CN"

    return "en"


def load_config(config_path: str = ".acl/config.json") -> dict:
    """Load ACL config, return defaults if file not found."""
    defaults = {
        "cleanup_mode": "semi",
        "cleanup_days": 30,
        "language": "auto",
    }
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
            defaults.update(user_config)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return defaults
