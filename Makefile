.PHONY: doctor validate build evalsets lint test api baseline preview

doctor:
	python scripts/doctor.py

validate:
	python scripts/validate_entities.py

build:
	python scripts/build_dataset.py

evalsets:
	python scripts/build_eval_sets.py

lint:
	python scripts/lint_dataset.py

test:
	pytest -q

api:
	python -m uvicorn mapvoice_llm.api:app --reload --app-dir src

baseline:
	python scripts/benchmark.py

preview:
	python scripts/export_training_preview.py
