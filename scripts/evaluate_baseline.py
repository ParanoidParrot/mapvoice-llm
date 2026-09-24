from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from mapvoice_llm.baseline import RuleBaseline
from mapvoice_llm.dataset import read_jsonl
from evaluation.metrics import character_error_rate


def main() -> None:
    test_path = PROJECT_ROOT / "data" / "processed" / "test.jsonl"
    if not test_path.exists():
        raise SystemExit(
            "Missing test.jsonl. Run generate_training_data.py and split_dataset.py first."
        )

    baseline = RuleBaseline(
        PROJECT_ROOT / "data" / "raw" / "bengaluru_entities_v0.1.csv"
    )
    examples = read_jsonl(test_path)

    exact = 0
    cer_total = 0.0
    rows = []

    for example in examples:
        prediction = baseline.predict(example["input"]["text"])
        reference = example["target"]["place_name_kn"]
        hypothesis = prediction.pronunciation_form or ""

        exact += int(reference == hypothesis)
        cer_total += character_error_rate(reference, hypothesis)

        rows.append(
            {
                "example_id": example["example_id"],
                "reference": reference,
                "hypothesis": hypothesis,
            }
        )

    count = max(len(examples), 1)
    report = {
        "examples": len(examples),
        "exact_match": exact / count,
        "mean_character_error_rate": cer_total / count,
        "sample_predictions": rows[:10],
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
