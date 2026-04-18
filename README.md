# Agent Calibration Log (ACL)

> An honest meter for Claude Code — not what the AI did, but how certain it was.

ACL is a Claude Code hook tool that automatically generates a calibration report at the end of every session. It shows which parts of the AI's output were certain, which were inferred, and which need human review.

---

## Why ACL?

Most AI tools record *what* the AI did. ACL records *how confident* the AI was about what it did.

This is based on LDRIT's concept of **q_calibration**: an AI that can honestly assess its own uncertainty is more trustworthy than one that always sounds confident.

```
── ACL Report ─────────────────────────────────────
✓ Certain      parsed input correctly, matched 3 constraints
⚠ Uncertain    line 47 — inferred intent, no explicit instruction
✗ Review       output depends on assumption that may be wrong
───────────────────────────────────────────────────
Calibration Score: 78 / 100
```

---

## Installation

```bash
git clone https://github.com/your-repo/acl-tool
cd acl-tool
pip install -r requirements.txt
```

Copy the hook into your Claude Code project:

```bash
cp .claude/hooks/stop_hook.py /your-project/.claude/hooks/
```

---

## Configuration

Create `.acl/config.json` in your project root:

```json
{
  "cleanup_mode": "semi",
  "cleanup_days": 30,
  "language": "auto"
}
```

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `cleanup_mode` | `auto` / `semi` | `semi` | Auto-delete old reports or prompt first |
| `cleanup_days` | integer | `30` | Reports older than N days are eligible for cleanup |
| `language` | `auto` / `zh-TW` / `zh-CN` / `en` | `auto` | Report language |

---

## Output

Reports are saved to `.acl/reports/acl_{session_id}_{timestamp}.json`.

---

## Theory

ACL is built on [LDRIT](https://github.com/Ryo-Hunter/fourgods) — Life-Death Recursive Intelligence Theory.

Key concepts used:
- **q_calibration**: AI's ability to honestly assess its own output quality
- **Self-seeding**: How the AI's expressed confidence affects its next generation
- **c_eff conflict**: When system/user/dialogue layers conflict, reliability drops

---

## License

MIT
