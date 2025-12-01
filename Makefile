# ------------------------
# Makefile (cross-platform, CI-aware)
# ------------------------

VENV := .venv

# Detect OS and set VENV_PYTHON
ifeq ($(OS),Windows_NT)
    VENV_PYTHON := $(VENV)/Scripts/python.exe
else
    VENV_PYTHON := $(VENV)/bin/python
endif

# Detect CI & choose the PYTHON executable
ifeq ($(CI),true)
    USE_VENV := false
    PYTHON := python
else
    USE_VENV := true
    PYTHON := $(VENV_PYTHON)
endif

.PHONY: install run web test ingest clean

# ------------------------
# Install dependencies
# ------------------------
install:
ifeq ($(USE_VENV),true)
	@echo "Creating virtual environment and installing dependencies..."
ifeq ($(OS),Windows_NT)
	@if not exist "$(VENV)" python -m venv $(VENV)
else
	@if [ ! -d "$(VENV)" ]; then python -m venv $(VENV); fi
endif
	"$(PYTHON)" -m pip install --upgrade pip
	"$(PYTHON)" -m pip install -r requirements.txt
else
	@echo "CI detected, installing dependencies without venv..."
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt
endif

# ------------------------------------------------------------------------------------------------
# Run ADK agent (dev)
# ------------------------------------------------------------------------------------------------
run:
ifeq ($(OS),Windows_NT)
	@echo "Running ADK agent..."
	.venv\Scripts\adk run agents/repo_navigator
else
	@echo "Running ADK agent..."
	"$(PYTHON)" -m adk run agents/repo_navigator
endif

# ------------------------------------------------------------------------------------------------
# Run ADK web server
# ------------------------------------------------------------------------------------------------
web:
ifeq ($(OS),Windows_NT)
	@echo "Starting ADK web server..."
	.venv\Scripts\adk web --port 8000 agents/
else
	@echo "Starting ADK web server..."
	"$(PYTHON)" -m adk web --port 8000 agents/
endif

# ------------------------
# Run tests with coverage
# ------------------------
test:
	@echo "Running tests with coverage..."
	"$(PYTHON)" -m pytest tests --maxfail=1 --disable-warnings -q --cov=. --cov-report=term-missing --cov-fail-under=80

# ------------------------
# Remove virtual environment
# ------------------------
clean:
ifeq ($(USE_VENV),true)
	@echo "Removing virtual environment..."
ifeq ($(OS),Windows_NT)
	if exist "$(VENV)" rmdir /s /q $(VENV)
else
	if [ -d "$(VENV)" ]; then rm -rf $(VENV); fi
endif
else
	@echo "Skipping venv removal in CI"
endif
