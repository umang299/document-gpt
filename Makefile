.PHONY: install test lint clean

# Define variables for commands
PYTHON=python3
PIP=pip3
TEST_DIR=test

# Install dependencies
install:
	$(PIP) install -r requirements.txt

# Run tests
test:
	$(PYTHON) -m unittest discover -s $(TEST_DIR)

# Linting
lint:
	flake8 src