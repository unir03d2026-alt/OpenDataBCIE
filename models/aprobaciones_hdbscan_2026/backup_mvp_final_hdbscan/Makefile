# Makefile for BCIE HDBSCAN Project

IMAGE_NAME = bcie_hdbscan_pipeline
CONTAINER_NAME = bcie_hdbscan_run

.PHONY: build run optimize clean help

help: ## Show this help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build the Docker image
	docker build -t $(IMAGE_NAME) .

run: ## Run the pipeline (ETL + Train + Dashboard)
	docker run --rm -v "$(PWD)/data:/app/data" -v "$(PWD)/config:/app/config" $(IMAGE_NAME)

optimize: ## Run the pipeline with Hyperparameter Optimization
	docker run --rm -v "$(PWD)/data:/app/data" -v "$(PWD)/config:/app/config" $(IMAGE_NAME) python run.py --optimize

clean: ## Remove the docker image
	docker rmi $(IMAGE_NAME)
