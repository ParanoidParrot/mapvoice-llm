# MapVoice reviewer integration

Added Railway `mapvoice-review` -> `mapvoice-llm` bridge.

Key additions:
- `src/mapvoice_llm/railway_review_import.py`
- `scripts/import_reviewer_export.py`
- Railway review metadata preserved on `ReviewEvent`
- idempotent import keyed by Railway `review_id`
- candidate resolution by canonical ID, or fallback to language pack + normalized Latin name
- conservative mapping for `correct`, `incorrect`, `unsure`, and `not_applicable`
- 30 candidate rows synchronized for Tamil, Telugu, Marathi, Malayalam
- reviewer-app Kannada candidates synchronized into the Kannada candidate file
- `tests/fixtures/railway_reviews_sample.csv`
- `tests/test_railway_review_import.py`

Verified:
- full suite: 83 passed
- first import of 5 real sample reviews: 5 appended, 0 unknown
- repeated import: 0 appended, 5 duplicates

## N-reviewer-aware progress reporting

Added `src/mapvoice_llm/review_analytics.py` and enhanced review progress/status commands.

```bash
python scripts/review_progress.py
python scripts/review_progress.py --json
python scripts/review_progress.py --pack-id blr-kn --json
python scripts/review_status.py --pack-id blr-kn --details
```

Progress now reports candidates with 0, 1, 2, and 3+ distinct reviewers, an exact reviewer-count histogram, disagreements/adjudication readiness, materialization readiness, and pronunciation readiness. Candidate-level analytics preserve agreement ratios for any number of reviewers. Verification remains conservative: all independent reviews must agree; any dissent after the minimum two reviewers requires adjudication.
