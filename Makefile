.PHONY: dev test build migrate lint

dev:
	docker compose up --build

test:
	docker compose run --rm backend pytest --cov=app --cov-report=term-missing

migrate:
	docker compose run --rm backend alembic upgrade head

lint:
	docker compose run --rm backend ruff check app/
	docker compose run --rm backend mypy app/

build:
	docker compose build

down:
	docker compose down

reset-db:
	docker compose down -v
	docker compose up -d db
	docker compose run --rm backend alembic upgrade head
