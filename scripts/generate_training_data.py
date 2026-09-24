from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from mapvoice_llm.dataset import generate_examples, read_entities, write_jsonl


def main() -> None:
    source = PROJECT_ROOT / "data" / "raw" / "bengaluru_entities_v0.1.csv"
    output = PROJECT_ROOT / "data" / "processed" / "navigation_examples.jsonl"

    entities = read_entities(source)
    examples = generate_examples(entities)
    write_jsonl(examples, output)

    print(f"Entities: {len(entities)}")
    print(f"Examples: {len(examples)}")
    print(f"Wrote: {output}")


if __name__ == "__main__":
    main()
