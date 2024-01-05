THIS_FILE := $(lastword $(MAKEFILE_LIST))
.PHONY: help build run stop restart  destroy log shell manage makemigrations migrate test

docker_file := docker-compose.yaml

help:
	make -pRrq  -f $(THIS_FILE) : 2>/dev/null |	awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

build:
	docker-compose -f $(docker_file) build $(c)
run:
	docker-compose -f $(docker_file) up -d $(c)
stop:
	docker-compose -f $(docker_file) stop $(c)
restart:
	sudo docker-compose -f $(docker_file) stop $(c)
	sudo docker-compose -f $(docker_file) up -d $(c)
destroy:
	docker-compose -f $(docker_file) down -v $(c)
log:
	docker-compose -f $(docker_file) logs --tail=100 -f cb-app
shell:
	docker-compose -f $(docker_file) exec cb-app /bin/bash
manage:
	docker-compose -f $(docker_file) exec cb-app python manage.py $(c)
makemigrations:
	docker-compose -f $(docker_file) exec cb-app python manage.py makemigrations
migrate:
	docker-compose -f $(docker_file) exec cb-app python manage.py migrate
test:
	docker-compose -f $(docker_file) exec cb-app python manage.py test
celery:
	docker-compose -f $(docker_file) exec cb-celery celery -A _project worker --loglevel=debug
celery2:
	docker-compose -f $(docker_file) exec cb-celery celery -A _project inspect active
celery-stop:
	docker-compose -f $(docker_file) exec cb-celery ps aux | grep 'celery -A _project worker'
celery-start:
	docker-compose -f $(docker_file) exec cb-celery celery -A project worker --detach

