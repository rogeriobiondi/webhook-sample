# include .env
# export $(shell sed 's/=.*//' .env)
export PYTHONPATH=$(CURDIR)

define set_user_id
    export USER_ID=$(shell id -u)
	$(eval export USER_ID=$(shell id -u))
endef

.PHONY: help
help: ## Command help
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: infra-start
infra-start:  ## Start infra
	@docker-compose up -d

.PHONY: infra-stop
infra-stop:  ## Stop infra
	@docker-compose down

.PHONY: run-api
run-api:  ## Stop infra
	@poetry run uvicorn app.api:app --port 9090 --host 0.0.0.0 --reload

.PHONY: run-system
run-system:  ## Stop infra
	@clear
	@poetry run python system.py

.PHONY: run-processor
run-processor:  ## Execute the Event Processor
	@clear
	@poetry run python processor.py

.PHONY: run-webhook
run-webhook:  ## Stop infra
	@poetry run uvicorn webhook:app --port 9099 --host 0.0.0.0 --reload
