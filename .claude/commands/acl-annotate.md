Add a user annotation to the most recent ACL report.

## Your task

1. Find the most recent ACL report in `.acl/reports/` (sort by filename timestamp, take the latest).

2. Read the report and display a summary to the user:
   - Session ID
   - Timestamp
   - Honesty Score
   - Assessment (one-line summary)

3. Ask the user for their verdict:
   ```
   How does this score feel to you?
   (1) agree — the score reflects what you observed
   (2) score_too_high — the AI was less reliable than the score suggests
   (3) score_too_low — the AI was more reliable than the score suggests
   ```

4. Optionally ask: "Any note to add? (press Enter to skip)"

5. Write the annotation back to the JSON file. Update the `user_annotations` field:
   ```json
   "user_annotations": {
     "verdict": "agree" | "score_too_high" | "score_too_low",
     "note": "user's note or null",
     "annotated_at": "ISO timestamp"
   }
   ```

6. Confirm: "Annotation saved to [filename]."

## Notes

- Use Bash to list, read, and write the JSON file.
- If no reports exist, say: "No ACL reports found. Run /acl first."
- To annotate a specific report: `/acl-annotate <session_id>` — search reports for matching session_id.
- User annotations are the only external anchor in ACL. Even sparse annotation (5%) is meaningfully better than none.
