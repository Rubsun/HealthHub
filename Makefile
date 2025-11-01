.PHONY: up down build test migrate-users migrate-health migrate-nutrition migrate-integrations migrate-all

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

test:
	pytest --cov=services --cov-report=term-missing --cov-report=html

install-dev:
	pip install -r requirements-dev.txt

migrate-users:
	cd services/users-service && alembic upgrade head

migrate-health:
	cd services/health-service && alembic upgrade head

migrate-nutrition:
	cd services/nutrition-service && alembic upgrade head

migrate-integrations:
	cd services/integrations-service && alembic upgrade head

migrate-all: migrate-users migrate-health migrate-nutrition migrate-integrations

