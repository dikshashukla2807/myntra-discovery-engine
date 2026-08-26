# Actual collection vs targets. Never fabricated to fill gaps.

## Targets

| Source | Target |
| --- | --- |
| Google Play | 3,000 |
| Apple App Store | 1,000 |
| Reddit | 300 |
| YouTube | 500 |

## Actual (this repository)

See `data/raw/collection_summary.json` for the machine-readable snapshot.

YouTube: 0 live comments. `YOUTUBE_API_KEY` was not set. Use `scripts/import_youtube.py` with a public export. Demo Mode includes clearly labeled sample YouTube comments that must not be presented as public-source research.

App Store RSS typically returns fewer than 1,000 unique reviews; the actual unique count is stored.

Play Store newest-sort reviews are recency-biased (many from the collection month). That is a dataset limitation, not a finding about users.

Wishlist language is rare in app-store reviews. That is a **coverage gap**, not evidence that users do not wishlist.
