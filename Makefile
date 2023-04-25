SHELL := /bin/bash
PWD := $(shell pwd)

default: build

all:

# docker-client-up:
# 	docker build -f ./client/Dockerfile -t "client:latest" .
# 	docker run --name client -v ./client/config.ini:/config.ini client:latest
# .PHONY: docker-client-up

# docker-client-logs:
# 	docker logs client -f
# .PHONY: docker-client-logs

# docker-client-down:
# 	docker stop client
# 	docker rm client
# .PHONY: docker-client-down

docker-image:
	docker build -f ./filter/Dockerfile -t "filter:latest" .
	docker build -f ./accepter/Dockerfile -t "accepter:latest" .
	docker build -f ./joiner/Dockerfile -t "joiner:latest" .
	docker build -f ./date_modifier/Dockerfile -t "date_modifier:latest" .
	docker build -f ./groupby/Dockerfile -t "groupby:latest" .
.PHONY: docker-image

docker-compose-up: docker-image
	docker compose -f docker-compose-dev.yaml up -d --build
.PHONY: docker-compose-up

docker-compose-down:
	docker compose -f docker-compose-dev.yaml stop -t 1
	docker compose -f docker-compose-dev.yaml down
.PHONY: docker-compose-down

docker-compose-logs:
	docker compose -f docker-compose-dev.yaml logs -f
.PHONY: docker-compose-logs