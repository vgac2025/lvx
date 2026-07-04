.PHONY: chain test api frontend demo

chain:
	$(MAKE) -C src/c all

test: chain
	python3 -m pytest tests/ -v

api: chain
	uvicorn api.main:app --app-dir src --host 0.0.0.0 --port 8000 --reload

frontend:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm install && npm run build

demo:
	@echo "Requires API already running: make api  (port 8000)"
	@echo "No browser / no frontend required."
	python3 scripts/demo_live.py
