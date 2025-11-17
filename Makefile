# ------------------------
# Makefile (cross-platform)
# ------------------------

VENV := .venv

# Detect OS
ifeq ($(OS),Windows_NT)
    PYTHON := $(VENV)/Scripts/python.exe
    ACTIVATE := $(VENV)/Scripts/activate
else
    PYTHON := $(VENV)/bin/python
    ACTIVATE := $(VENV)/bin/activate
endif

.PHONY: install run test ingest clean

# ------------------------
# Create venv if it doesn't exist
# ------------------------
$(ACTIVATE):
	@echo "Creating virtual environment..."
ifeq ($(OS),Windows_NT)
	if not exist "$(VENV)" (python -m venv $(VENV))
else
	if [ ! -d "$(VENV)" ]; then python -m venv $(VENV); fi
endif

# ------------------------
# Install dependencies
# ------------------------
install: $(ACTIVATE)
	@echo "Upgrading pip and installing requirements..."
	"$(PYTHON)" -m pip install --upgrade pip
	"$(PYTHON)" -m pip install -r requirements.txt

# ------------------------
# Run tests with coverage
# ------------------------
test: $(ACTIVATE)
	@echo "Running tests with coverage..."
	"$(PYTHON)" -m pytest tests/ --maxfail=1 --disable-warnings -q --cov=. --cov-report=term-missing --cov-fail-under=80

# ------------------------
# Remove virtual environment
# ------------------------
clean:
	@echo "Deactivating and removing virtual environment..."
ifeq ($(OS),Windows_NT)
	if exist "$(VENV)" rmdir /s /q $(VENV)
else
	if [ -d "$(VENV)" ]; then rm -rf $(VENV); fi
endif
