from __future__ import annotations

from .candidates import CandidateRepository


BLR_SAMPLES = [
    {
        "id": "kanakapura",
        "label": "Kanakapura Road",
        "text": (
            "Turn left onto Kanakapura Rd "
            "after 500m"
        ),
        "difficulty": "standard",
    },
    {
        "id": "basavanagudi",
        "label": "Basavanagudi",
        "text": "Continue towards Basavanagudi.",
        "difficulty": "standard",
    },
    {
        "id": "marathahalli",
        "label": "Marathahalli",
        "text": (
            "In 300m, turn right towards "
            "Marathahalli."
        ),
        "difficulty": "morphology",
    },
    {
        "id": "kadubeesanahalli",
        "label": "Kadubeesanahalli",
        "text": (
            "Keep left towards "
            "Kadubeesanahalli."
        ),
        "difficulty": "hard",
    },
    {
        "id": "chikkabanavara",
        "label": "Chikkabanavara",
        "text": (
            "Proceed straight through "
            "Chikkabanavara."
        ),
        "difficulty": "hard",
    },
    {
        "id": "rajajinagar",
        "label": "Rajajinagar",
        "text": (
            "At the next junction, turn right "
            "towards Rajajinagar."
        ),
        "difficulty": "morphology",
    },
]


def samples_for_pack(
    *,
    pack_id: str,
    candidate_repository: CandidateRepository,
    limit: int = 6,
) -> list[dict]:
    if pack_id == "blr-kn":
        return BLR_SAMPLES

    rows = candidate_repository.list(
        limit=limit,
    )

    result = []
    for row in rows:
        name = (
            row.get("latin_name")
            or row.get("english_name")
            or ""
        ).strip()
        if not name:
            continue

        result.append({
            "id": row["candidate_id"],
            "label": name,
            "text": f"Continue towards {name}.",
            "difficulty": "scaffold",
        })

    return result


# Legacy import compatibility.
SAMPLES = BLR_SAMPLES
