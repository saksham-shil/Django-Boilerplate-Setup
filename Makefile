SHELL := /bin/bash # Use bash syntax
ARG := $(word 2, $(MAKECMDGOALS) )

# Catch all targets to prevent "No rule to make target" errors
%:
	@:

clean:
	@find . -name "*.pyc" -exec rm -rf {} \;
	@find . -name "__pycache__" -delete

test:
	poetry run backend/manage.py test backend/ $(ARG) --parallel --keepdb

test_reset:
	poetry run backend/manage.py test backend/ $(ARG) --parallel

backend_format:
	black backend

# Commands for Docker version
docker_setup:
	docker volume create {{ project_name }}_dbdata
	docker compose build --no-cache backend
	docker compose run --rm backend python manage.py spectacular --color --file schema.yml

docker_test:
	docker compose run backend python manage.py test $(ARG) --parallel --keepdb

docker_test_reset:
	docker compose run backend python manage.py test $(ARG) --parallel

docker_up:
	docker compose up -d

docker_update_dependencies:
	docker compose down
	docker compose up -d --build

docker_down:
	docker compose down

docker_logs:
	docker compose logs -f $(ARG)

docker_makemigrations:
	docker compose run --rm backend python manage.py makemigrations

docker_migrate:
	docker compose run --rm backend python manage.py migrate

docker_fullmigrate:
	docker compose run --rm backend python manage.py makemigrations
	docker compose run --rm backend python manage.py migrate

docker_backend_shell:
	docker compose run --rm backend bash

docker_backend_update_schema:
	docker compose run --rm backend python manage.py spectacular --color --file schema.yml

docker_frontend_update_api:
	docker compose run --rm frontend npm run openapi-ts

# Generic command runner for Django management commands
docker_check:
	docker compose run --rm backend python manage.py $(ARG)

# Alias for common commands
docker_showmigrations:
	docker compose run --rm backend python manage.py showmigrations $(ARG)

docker_collectstatic:
	docker compose run --rm backend python manage.py collectstatic --noinput

docker_createsuperuser:
	docker compose run --rm backend python manage.py createsuperuser

docker_shell:
	docker compose run --rm backend python manage.py shell

docker_setup_permissions:
	docker compose run --rm backend python manage.py setup_groups_permissions

# i18n support (if enabled)
docker_compilemessages:
	docker compose run --rm backend python manage.py compilemessages

# Convenience command for creating new apps
docker_startapp:
	docker compose run --rm backend python manage.py startapp $(ARG) apps/$(ARG)
