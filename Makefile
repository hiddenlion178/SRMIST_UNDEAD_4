install:
	python -m pip install -r requirements.txt

index:
	python scripts/build_index.py

api:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

ui:
	streamlit run ui/streamlit_app.py

test:
	pytest -q

benchmark:
	python scripts/run_benchmark.py

ablation-hybrid:
	python scripts/run_ablation.py --mode hybrid_vs_sparse

ablation-controller:
	python scripts/run_ablation.py --mode controller_vs_always_retrieve
