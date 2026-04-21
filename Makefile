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
	python3.14 -m pip install -r requirements.txt

install-dev:
	python3.14 -m pip install -r requirements.txt
	python3.14 -m pip install -r requirements-dev.txt

run:
	python3.14 src/intelligent_copier.py

test:
	python3.14 -m pytest tests/ -v

test-cov:
	python3.14 -m pytest tests/ --cov=src --cov-report=html

lint:
	python3.14 -m flake8 src/ --max-line-length=100
	python3.14 -m mypy src/

format:
	python3.14 -m black src/ tests/

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
