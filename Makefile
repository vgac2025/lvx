.PHONY: chain test api

chain:
	$(MAKE) -C src/c all

test: chain
	python3 -m pytest tests/ -v

api: chain
	uvicorn api.main:app --app-dir src --host 0.0.0.0 --port 8000 --reload
