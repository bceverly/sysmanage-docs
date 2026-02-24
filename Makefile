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

.PHONY: help install-dev install-browsers screenshot clean check-deps platform-info \
       test test-spelling test-markdown-lint test-vale test-accessibility test-links \
       check-test-deps website-package

# Default target
help:
	@echo "$(BLUE)SysManage Documentation Build Tools$(RESET)"
	@echo ""
	@echo "$(GREEN)Available targets:$(RESET)"
	@echo "  help           - Show this help message"
	@echo "  install-dev    - Install all development and testing dependencies"
	@echo "  install-browsers - Install Playwright browsers"
	@echo "  screenshot     - Generate dashboard screenshot"
	@echo "  clean          - Clean generated files and dependencies"
	@echo "  check-deps     - Check if required tools are installed"
	@echo "  platform-info  - Show detected platform information"
	@echo ""
	@echo "$(GREEN)Packaging targets:$(RESET)"
	@echo "  website-package     - Build .deb package for self-hosted sysmanage.org (nginx + certbot)"
	@echo ""
	@echo "$(GREEN)Testing targets (mirrors CI/CD):$(RESET)"
	@echo "  test                - Run all tests (spellcheck, lint, style, accessibility, links)"
	@echo "  test-spelling       - Run typos spell checker"
	@echo "  test-markdown-lint  - Run markdownlint on README.md and SCREENSHOTS.md"
	@echo "  test-vale           - Run Vale documentation style checker"
	@echo "  test-accessibility  - Run pa11y accessibility tests on HTML pages"
	@echo "  test-links          - Run lychee link checker on all Markdown and HTML files"
	@echo "  check-test-deps     - Check if testing tools are installed"
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

# Install development dependencies (screenshots + all testing tools)
install-dev: check-deps
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	@echo ""
	@# --- Playwright (for screenshots) ---
	@if [ ! -f package.json ]; then \
		echo "$(YELLOW)Initializing package.json...$(RESET)"; \
		$(NPM) init -y; \
	fi
	@echo "$(YELLOW)Installing Playwright...$(RESET)"
	@$(NPM) install playwright@^1.55.0
	@echo "$(GREEN)✓ Playwright installed$(RESET)"
	@echo ""
	@# --- npm global tools ---
	@echo "$(YELLOW)Installing npm global tools (markdownlint-cli2, pa11y, http-server)...$(RESET)"
	@command -v markdownlint-cli2 >/dev/null 2>&1 && echo "$(GREEN)✓ markdownlint-cli2 already installed$(RESET)" || $(NPM) install -g markdownlint-cli2
	@command -v pa11y >/dev/null 2>&1 && echo "$(GREEN)✓ pa11y already installed$(RESET)" || $(NPM) install -g pa11y
	@command -v http-server >/dev/null 2>&1 && echo "$(GREEN)✓ http-server already installed$(RESET)" || $(NPM) install -g http-server
	@echo "$(GREEN)✓ npm global tools installed$(RESET)"
	@echo ""
	@# --- Cargo tools (typos, lychee) ---
	@echo "$(YELLOW)Installing cargo tools (typos-cli, lychee)...$(RESET)"
	@command -v cargo >/dev/null 2>&1 || { echo "$(RED)Error: cargo is not installed. Install Rust from https://rustup.rs$(RESET)"; exit 1; }
	@command -v typos >/dev/null 2>&1 && echo "$(GREEN)✓ typos already installed$(RESET)" || cargo install typos-cli@1.42.3 --locked
	@command -v lychee >/dev/null 2>&1 && echo "$(GREEN)✓ lychee already installed$(RESET)" || cargo install lychee
	@echo "$(GREEN)✓ Cargo tools installed$(RESET)"
	@echo ""
	@# --- Vale (platform-specific) ---
	@echo "$(YELLOW)Installing Vale...$(RESET)"
	@command -v vale >/dev/null 2>&1 && echo "$(GREEN)✓ vale already installed$(RESET)" || { \
		if [ "$(PLATFORM)" = "macos" ]; then \
			echo "Installing vale via Homebrew..."; \
			brew install vale; \
		elif [ "$(PLATFORM)" = "linux" ] && command -v snap >/dev/null 2>&1; then \
			echo "Installing vale via snap..."; \
			sudo snap install vale; \
		else \
			echo "$(RED)Error: Could not auto-install vale.$(RESET)"; \
			echo "$(YELLOW)Please install manually: https://vale.sh/docs/install$(RESET)"; \
			exit 1; \
		fi; \
	}
	@echo "$(GREEN)✓ Vale installed$(RESET)"
	@echo ""
	@echo "$(GREEN)✓ All development dependencies installed$(RESET)"
	@echo ""
	@echo "$(BLUE)Next steps:$(RESET)"
	@echo "1. Run 'make install-browsers' to install Playwright browser binaries (for screenshots)"
	@echo "2. Run 'make test' to run the full local test suite"

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

# ============================================================================
# Testing targets - mirrors CI/CD workflows for local pre-push validation
# ============================================================================

# Check if testing tools are installed
check-test-deps:
	@echo "$(BLUE)Checking testing dependencies...$(RESET)"
	@MISSING=0; \
	command -v typos >/dev/null 2>&1 && echo "$(GREEN)✓ typos found$(RESET)" || { echo "$(RED)✗ typos not found (install: cargo install typos-cli)$(RESET)"; MISSING=1; }; \
	command -v markdownlint-cli2 >/dev/null 2>&1 && echo "$(GREEN)✓ markdownlint-cli2 found$(RESET)" || { echo "$(RED)✗ markdownlint-cli2 not found (install: npm install -g markdownlint-cli2)$(RESET)"; MISSING=1; }; \
	command -v vale >/dev/null 2>&1 && echo "$(GREEN)✓ vale found$(RESET)" || { echo "$(RED)✗ vale not found (install: brew install vale / snap install vale)$(RESET)"; MISSING=1; }; \
	command -v pa11y >/dev/null 2>&1 && echo "$(GREEN)✓ pa11y found$(RESET)" || { echo "$(RED)✗ pa11y not found (install: npm install -g pa11y)$(RESET)"; MISSING=1; }; \
	command -v http-server >/dev/null 2>&1 && echo "$(GREEN)✓ http-server found$(RESET)" || { echo "$(RED)✗ http-server not found (install: npm install -g http-server)$(RESET)"; MISSING=1; }; \
	command -v lychee >/dev/null 2>&1 && echo "$(GREEN)✓ lychee found$(RESET)" || { echo "$(RED)✗ lychee not found (install: cargo install lychee)$(RESET)"; MISSING=1; }; \
	if [ $$MISSING -ne 0 ]; then echo ""; echo "$(YELLOW)Some tools are missing. Install them before running 'make test'.$(RESET)"; exit 1; fi
	@echo "$(GREEN)All testing tools are available$(RESET)"

# Spell checking (mirrors .github/workflows/spellcheck.yml)
test-spelling:
	@echo "$(BLUE)=== Spell Check ===$(RESET)"
	typos
	@echo "$(GREEN)✓ Spell check passed$(RESET)"

# Markdown linting (mirrors .github/workflows/markdown-lint.yml)
test-markdown-lint:
	@echo "$(BLUE)=== Markdown Lint ===$(RESET)"
	markdownlint-cli2 README.md SCREENSHOTS.md
	@echo "$(GREEN)✓ Markdown lint passed$(RESET)"

# Vale documentation style (mirrors .github/workflows/vale.yml)
test-vale:
	@echo "$(BLUE)=== Vale Documentation Style ===$(RESET)"
	vale docs
	@echo "$(GREEN)✓ Vale style check passed$(RESET)"

# Accessibility testing (mirrors .github/workflows/accessibility.yml)
test-accessibility:
	@echo "$(BLUE)=== Accessibility Check ===$(RESET)"
	@http-server . -p 8087 -s &>/dev/null & \
	SERVER_PID=$$!; \
	sleep 2; \
	FAIL=0; \
	echo "$(YELLOW)Testing index.html...$(RESET)"; \
	pa11y --config .pa11yrc.json http://localhost:8087/index.html || FAIL=1; \
	echo "$(YELLOW)Testing docs/index.html...$(RESET)"; \
	pa11y --config .pa11yrc.json http://localhost:8087/docs/index.html || FAIL=1; \
	if [ -f "docs/api/index.html" ]; then \
		echo "$(YELLOW)Testing docs/api/index.html...$(RESET)"; \
		pa11y --config .pa11yrc.json http://localhost:8087/docs/api/index.html || FAIL=1; \
	fi; \
	if [ -f "docs/agent/index.html" ]; then \
		echo "$(YELLOW)Testing docs/agent/index.html...$(RESET)"; \
		pa11y --config .pa11yrc.json http://localhost:8087/docs/agent/index.html || FAIL=1; \
	fi; \
	if [ -f "docs/server/index.html" ]; then \
		echo "$(YELLOW)Testing docs/server/index.html...$(RESET)"; \
		pa11y --config .pa11yrc.json http://localhost:8087/docs/server/index.html || FAIL=1; \
	fi; \
	kill $$SERVER_PID 2>/dev/null; \
	if [ $$FAIL -ne 0 ]; then echo "$(RED)Accessibility tests failed$(RESET)"; exit 1; fi
	@echo "$(GREEN)✓ Accessibility tests passed$(RESET)"

# Link checking (mirrors .github/workflows/link-check.yml)
test-links:
	@echo "$(BLUE)=== Link Check ===$(RESET)"
	lychee --verbose --no-progress --root-dir . --max-retries 3 --retry-wait-time 2 --exclude-path node_modules --exclude-path .git --exclude-path SignPath --exclude 'http://localhost:*' '**/*.md' '**/*.html'
	@echo "$(GREEN)✓ Link check passed$(RESET)"

# Run all tests (mirrors full CI/CD test suite)
test: test-spelling test-markdown-lint test-vale test-accessibility test-links
	@echo ""
	@echo "$(GREEN)========================================$(RESET)"
	@echo "$(GREEN)  All tests passed$(RESET)"
	@echo "$(GREEN)========================================$(RESET)"

# ============================================================================
# Packaging target - build .deb for self-hosted sysmanage.org
# ============================================================================

# Build a .deb package that installs the sysmanage.org website with nginx + certbot SSL
# Usage: make website-package
# Usage: VERSION=1.3.0.0 make website-package
website-package:
	@echo "$(BLUE)=================================================$(RESET)"
	@echo "$(BLUE)Building sysmanage.org website .deb package$(RESET)"
	@echo "$(BLUE)=================================================$(RESET)"
	@echo ""
	@CURDIR=$$(pwd); \
	export CURDIR; \
	if [ -n "$$VERSION" ]; then \
		echo "Using VERSION from environment: $$VERSION"; \
	else \
		VERSION=$$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//'); \
		if [ -z "$$VERSION" ]; then \
			VERSION="1.0.0"; \
			echo "No git tags found, using default version: $$VERSION"; \
		else \
			echo "Using version from git tag: $$VERSION"; \
		fi; \
	fi; \
	export VERSION; \
	echo ""; \
	exec sh "$$CURDIR/scripts/build-website-deb.sh"