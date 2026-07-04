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

demo: chain
	@echo "Start API (terminal 1): make api"
	@echo "Start frontend (terminal 2): make frontend"
	@echo "Then run: python3 scripts/demo_live.py"
	python3 scripts/demo_live.py
