.PHONY: help install setup test clean run

help:
	@echo "Partner Scope - Makefile Commands"
	@echo ""
	@echo "  make install    - Install Python dependencies"
	@echo "  make setup      - Set up configuration files"
	@echo "  make test       - Run test suite"
	@echo "  make clean      - Clean generated files"
	@echo "  make run        - Run example pipeline"
	@echo ""

install:
	pip install -r requirements.txt

setup:
	@if [ ! -f config.yaml ]; then \
		cp config.yaml.template config.yaml; \
		echo "Created config.yaml from template"; \
	fi
	@if [ ! -f .env ]; then \
		cp .env.template .env; \
		echo "Created .env from template"; \
	fi
	@echo "Please edit config.yaml and .env with your API keys"

test:
	pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf work/*
	@echo "Cleaned generated files"

run:
	@echo "Example run command:"
	@echo 'python main.py --startup-name "TempTrack" --investment-stage "Seed" --product-stage "MVP" --partner-needs "Large logistics company for pilot testing" --industry "Food Safety"'
