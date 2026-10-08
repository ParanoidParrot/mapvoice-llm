# Candidate provenance

Every bulk ingestion writes an immutable JSON manifest under `data/provenance/ingestions/`.

The candidate row retains:
- source registry ID
- source record ID
- source URL
- source license
- source retrieval timestamp
- source snapshot SHA-256
- coordinates when available
- provenance status / review priority

Candidates are never promoted directly to verified training data by ingestion.
