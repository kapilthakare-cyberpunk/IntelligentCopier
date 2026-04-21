# Makefile for Intelligent File Copier

.PHONY: help install test lint clean build run

help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies"
	@echo "  install-dev - Install development dependencies"
	@echo "  run         - Run the application"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linter"
	@echo "  format      - Format code with black"
	@echo "  build       - Build standalone executable"
	@echo "  clean       - Clean build artifacts"
	@echo "  macos       - Create macOS app bundle"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

run:
	python3 src/intelligent_copier.py

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html

lint:
	flake8 src/ --max-line-length=100
	mypy src/

format:
	black src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf tests/__pycache__/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

build: clean
	pyinstaller --onefile --windowed \
		--name "IntelligentCopier" \
		--icon=assets/icon.icns \
		src/intelligent_copier.py

macos:
	chmod +x install_macos.sh
	./install_macos.sh
