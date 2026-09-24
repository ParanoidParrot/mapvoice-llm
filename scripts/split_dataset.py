from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.dataset import read_jsonl, split_by_entity, write_jsonl


def main() -> None:
    source = PROJECT_ROOT / "data" / "processed" / "navigation_examples.jsonl"
    output_dir = PROJECT_ROOT / "data" / "processed"

    examples = read_jsonl(source)
    train, validation, test = split_by_entity(examples)

    write_jsonl(train, output_dir / "train.jsonl")
    write_jsonl(validation, output_dir / "validation.jsonl")
    write_jsonl(test, output_dir / "test.jsonl")

    print(f"Train examples: {len(train)}")
    print(f"Validation examples: {len(validation)}")
    print(f"Test examples: {len(test)}")


if __name__ == "__main__":
    main()
