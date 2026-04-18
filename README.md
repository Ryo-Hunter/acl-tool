# Agent Calibration Log (ACL)

> An honest meter for Claude Code — not what the AI did, but how certain it was.

ACL is a Claude Code slash command that lets the AI analyze its own conversation and generate a calibration report — showing which responses were certain, which were inferred, and which need human review.

No extra API calls. No additional cost. The AI already running in your session does the analysis.

---

## How it works

Type `/acl` at any point in your Claude Code session:

```
── ACL 校準報告 ────────────────────────────────────
✓ 確定    parsed input correctly, matched 3 constraints
⚠ 推測    inferred user intent — no explicit instruction given
✗ 需確認  assumed project structure may be wrong, please verify
────────────────────────────────────────────────────
校準分數：83 / 100  |  High confidence session with one assumption to verify.
────────────────────────────────────────────────────
```

The report is also saved to `.acl/reports/` as JSON for later review.

---

## Why ACL?

Most AI tools record *what* the AI did. ACL records *how confident* the AI was.

This matters because the biggest problem with AI today isn't capability — it's that users can't tell when to trust the output. ACL makes the AI's uncertainty visible.

Built on [LDRIT](https://github.com/Ryo-Hunter/fourgods) — **q_calibration**: an AI that can honestly assess its own uncertainty is more trustworthy than one that always sounds confident.

---

## Installation

```bash
git clone https://github.com/Ryo-Hunter/acl-tool
```

Copy the slash command to your Claude Code project:

```bash
cp acl-tool/.claude/commands/acl.md /your-project/.claude/commands/
```

That's it. No API key. No dependencies.

---

## Usage

In any Claude Code session, type:

```
/acl
```

Claude will analyze the current session and output a calibration report.

**Reading the report:**

| Symbol | Meaning | Action |
|--------|---------|--------|
| ✓ Certain | AI had clear evidence | Trust it |
| ⚠ Uncertain | AI made an inference | Worth a quick check |
| ✗ Review | AI was making assumptions | Verify before using |

**Honesty Score:**
- **80–100**: High confidence session
- **50–79**: Some inferences made, check key outputs
- **Below 50**: Many assumptions — review carefully

> The Honesty Score measures what LDRIT theory calls **q_calibration** — the degree to which an AI honestly knows what it knows versus what it's guessing. High fluency does not equal high honesty.

---

## Report storage

Reports are saved to `.acl/reports/acl_{timestamp}.json` in your project.

Configure cleanup behavior in `.acl/config.json`:

```json
{
  "cleanup_mode": "semi",
  "cleanup_days": 30,
  "language": "auto"
}
```

| Option | Values | Default |
|--------|--------|---------|
| `cleanup_mode` | `auto` / `semi` | `semi` — prompts before deleting |
| `cleanup_days` | integer | `30` |
| `language` | `auto` / `zh-TW` / `en` | `auto` — detects from environment |

---

## Theory

ACL is built on [LDRIT](https://github.com/Ryo-Hunter/fourgods) — Life-Death Recursive Intelligence Theory.

Key concept: **q_calibration** — the degree to which an AI can honestly assess its own output quality, rather than just producing fluent responses.

An AI with high q_calibration knows what it knows, knows what it's guessing, and tells you the difference.

---

## License

MIT
