# Cross-platform Makefile for SysManage Documentation
# Supports Windows, macOS, Linux, OpenBSD, and FreeBSD

# Detect operating system
UNAME_S := $(shell uname -s 2>/dev/null || echo "Windows")
UNAME_M := $(shell uname -m 2>/dev/null || echo "unknown")

# Set platform-specific variables
ifeq ($(OS),Windows_NT)
    PLATFORM := windows
    NPM := npm.cmd
    NPX := npx.cmd
    NODE := node.exe
else ifeq ($(UNAME_S),Darwin)
    PLATFORM := macos
    NPM := npm
    NPX := npx
    NODE := node
else ifeq ($(UNAME_S),Linux)
    PLATFORM := linux
    NPM := npm
    NPX := npx
    NODE := node
else ifeq ($(UNAME_S),OpenBSD)
    PLATFORM := openbsd
    NPM := npm
    NPX := npx
    NODE := node
else ifeq ($(UNAME_S),FreeBSD)
    PLATFORM := freebsd
    NPM := npm
    NPX := npx
    NODE := node
else
    PLATFORM := unknown
    NPM := npm
    NPX := npx
    NODE := node
endif

# Colors for output (if supported)
ifdef TERM
    RED := \033[31m
    GREEN := \033[32m
    YELLOW := \033[33m
    BLUE := \033[34m
    RESET := \033[0m
else
    RED :=
    GREEN :=
    YELLOW :=
    BLUE :=
    RESET :=
endif

.PHONY: help install-dev install-browsers screenshot clean check-deps platform-info

# Default target
help:
	@echo "$(BLUE)SysManage Documentation Build Tools$(RESET)"
	@echo ""
	@echo "$(GREEN)Available targets:$(RESET)"
	@echo "  help           - Show this help message"
	@echo "  install-dev    - Install development dependencies for screenshots"
	@echo "  install-browsers - Install Playwright browsers"
	@echo "  screenshot     - Generate dashboard screenshot"
	@echo "  clean          - Clean generated files and dependencies"
	@echo "  check-deps     - Check if required tools are installed"
	@echo "  platform-info  - Show detected platform information"
	@echo ""
	@echo "$(YELLOW)Platform detected: $(PLATFORM)$(RESET)"

# Show platform information
platform-info:
	@echo "$(BLUE)Platform Information:$(RESET)"
	@echo "Operating System: $(UNAME_S)"
	@echo "Architecture: $(UNAME_M)"
	@echo "Platform: $(PLATFORM)"
	@echo "NPM command: $(NPM)"
	@echo "NPX command: $(NPX)"
	@echo "Node command: $(NODE)"

# Check if required tools are available
check-deps:
	@echo "$(BLUE)Checking dependencies...$(RESET)"
	@command -v $(NODE) >/dev/null 2>&1 || { echo "$(RED)Error: Node.js is not installed$(RESET)"; exit 1; }
	@echo "$(GREEN)✓ Node.js found: $$($(NODE) --version)$(RESET)"
	@command -v $(NPM) >/dev/null 2>&1 || { echo "$(RED)Error: npm is not installed$(RESET)"; exit 1; }
	@echo "$(GREEN)✓ npm found: $$($(NPM) --version)$(RESET)"
	@echo "$(GREEN)All required tools are available$(RESET)"

# Install development dependencies
install-dev: check-deps
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	@if [ ! -f package.json ]; then \
		echo "$(YELLOW)Initializing package.json...$(RESET)"; \
		$(NPM) init -y; \
	fi
	@echo "$(YELLOW)Installing Playwright...$(RESET)"
	@$(NPM) install playwright@^1.55.0
	@echo "$(GREEN)✓ Dependencies installed successfully$(RESET)"
	@echo ""
	@echo "$(BLUE)Next steps:$(RESET)"
	@echo "1. Run 'make install-browsers' to install browser binaries"
	@echo "2. Run 'make screenshot' to generate screenshots"

# Install Playwright browsers
install-browsers:
	@echo "$(BLUE)Installing Playwright browsers...$(RESET)"
	@if [ ! -d node_modules/playwright ]; then \
		echo "$(RED)Error: Playwright not installed. Run 'make install-dev' first.$(RESET)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Installing Chromium browser...$(RESET)"
	@$(NPX) playwright install chromium
	@echo "$(GREEN)✓ Browsers installed successfully$(RESET)"

# Generate screenshot
screenshot:
	@echo "$(BLUE)Generating dashboard screenshot...$(RESET)"
	@if [ ! -f screenshot-generator.js ]; then \
		echo "$(RED)Error: screenshot-generator.js not found$(RESET)"; \
		exit 1; \
	fi
	@if [ ! -d node_modules/playwright ]; then \
		echo "$(RED)Error: Playwright not installed. Run 'make install-dev' first.$(RESET)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Running screenshot generator...$(RESET)"
	@$(NODE) screenshot-generator.js
	@echo "$(GREEN)✓ Screenshot generated successfully$(RESET)"

# Clean generated files and dependencies
clean:
	@echo "$(BLUE)Cleaning up...$(RESET)"
	@echo "$(YELLOW)Removing node_modules...$(RESET)"
	@rm -rf node_modules
	@echo "$(YELLOW)Removing package-lock.json...$(RESET)"
	@rm -f package-lock.json
	@echo "$(YELLOW)Removing generated screenshots...$(RESET)"
	@rm -f assets/images/dashboard-screenshot.png
	@rm -f assets/images/dashboard-preview.png
	@rm -f assets/images/error-screenshot.png
	@echo "$(GREEN)✓ Cleanup completed$(RESET)"

# Install everything needed for development
setup: install-dev install-browsers
	@echo "$(GREEN)✓ Development environment setup completed$(RESET)"
	@echo "$(BLUE)You can now run 'make screenshot' to generate screenshots$(RESET)"