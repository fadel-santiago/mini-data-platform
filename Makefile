.PHONY: help build up down demo pipeline test logs clean-data

DEMO_AS_OF ?= 2026-10-11

help:
	@echo "make demo       Lance la stack puis charge et transforme les donnees"
	@echo "make pipeline   Rejoue le pipeline incremental"
	@echo "make test       Lance les tests Python et dbt"
	@echo "make down       Arrete les services"
	@echo "make clean-data ATTENTION : supprime les volumes PostgreSQL ET Dagster du projet Compose"

build:
	docker compose build

up:
	docker compose up -d warehouse orchestrator dashboard

demo: up
	docker compose run --rm orchestrator python scripts/generate_demo_data.py --as-of $(DEMO_AS_OF)
	docker compose run --rm orchestrator python -m pme_data_stack.cli pipeline
	@echo "Dashboard: http://$$(docker compose port dashboard 8501) | Dagster: http://$$(docker compose port orchestrator 3000)"

pipeline:
	docker compose run --rm orchestrator python -m pme_data_stack.cli pipeline

test:
	docker compose run --rm orchestrator pytest -q
	docker compose run --rm orchestrator python -m pme_data_stack.cli pipeline

logs:
	docker compose logs -f orchestrator dashboard

down:
	docker compose down

clean-data:
	docker compose down -v

