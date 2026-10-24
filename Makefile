AZURE_CONTAINER_REGISTRY ?= registry
AZURE_CONTAINER_APP ?= app

all: js-build test django

django:
	python manage.py runserver

makemigrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

js:
	cd fantasycalendar && yarn run dev

js-build:
	cd fantasycalendar && yarn run build

test:
	python manage.py test

build:
	docker build --tag ${AZURE_CONTAINER_REGISTRY}.azurecr.io/${AZURE_CONTAINER_APP} .

run:
	docker run -d -p 8000:8000 ${AZURE_CONTAINER_REGISTRY}.azurecr.io/${AZURE_CONTAINER_APP}

rm:
	docker rm $(docker ps -a -q --filter "ancestor=${AZURE_CONTAINER_REGISTRY}.azurecr.io/${AZURE_CONTAINER_APP}") -f

push:
	az login && \
	az acr login -n ${AZURE_CONTAINER_REGISTRY} && \
	docker push ${AZURE_CONTAINER_REGISTRY}.azurecr.io/${AZURE_CONTAINER_APP}

up:
	docker-compose up -d --build

down:
	docker-compose down

reload:
	sudo nginx -s reload