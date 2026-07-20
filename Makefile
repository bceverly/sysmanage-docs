# Cross-platform Makefile for SysManage Documentation
# Supports Windows, macOS, Linux, OpenBSD, and FreeBSD

# Detect operating system
UNAME_S := $(shell uname -s 2>/dev/null || echo "Windows")
UNAME_M := $(shell uname -m 2>/dev/null || echo "unknown")

# Set platform-specific variables
ifeq ($(OS),Windows_NT)
    PLATFORM := windows
    # This repo's recipes are POSIX sh (unlike the sibling sysmanage repos, whose
    # Windows recipes are cmd batch). Force Git Bash explicitly so the shell is
    # deterministic and independent of PATH. Override if Git is elsewhere:
    #   make SHELL=C:/path/to/bash.exe <target>
    SHELL := C:/Program Files/Git/bin/bash.exe
    .SHELLFLAGS := -c
    NPM := npm.cmd
    NPX := npx.cmd
    NODE := node.exe
    # On Windows, bare `python3` hits the Microsoft Store app-execution-alias stub
    # ("Python was not found") — use the py launcher instead.
    PYTHON := py
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

# Non-Windows default (the Windows branch sets PYTHON := py above).  Prefer a plain
# ``python3``; on systems that only ship a versioned binary (e.g. NetBSD, where the
# interpreter is ``python3.13`` with no ``python3`` symlink) fall back to the newest
# versioned one. ``?=`` leaves the Windows ``py`` untouched, and where ``python3``
# exists (Linux/macOS/*BSD) this resolves to it — so nothing else changes.
PYTHON ?= $(shell for p in python3 python3.14 python3.13 python3.12 python3.11; do command -v $$p >/dev/null 2>&1 && { echo $$p; exit 0; }; done; echo python3)

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

.PHONY: help install-dev install-vm-deps install-browsers screenshot clean check-deps platform-info \
       test test-spelling test-markdown-lint test-vale test-accessibility test-links \
       check-test-deps website-package i18n-validate i18n-seed i18n-extract \
       translate translate-dry translate-check lint

# Default target
help:
	@echo "$(BLUE)SysManage Documentation Build Tools$(RESET)"
	@echo ""
	@echo "$(GREEN)Setup & environment:$(RESET)"
	@echo "  help                   - Show this help message"
	@echo "  install-dev            - Install all development and testing dependencies"
	@echo "  install-browsers       - Install Playwright browsers (screenshots + link/a11y tests)"
	@echo "  install-vm-deps        - Install screenshot VM prerequisites (Vagrant + libvirt)"
	@echo "  setup                  - Full dev environment (install-dev + install-browsers)"
	@echo "  check-deps             - Check if required build tools are installed"
	@echo "  check-test-deps        - Check if testing tools are installed"
	@echo "  platform-info          - Show detected platform information"
	@echo ""
	@echo "$(GREEN)Screenshots (reproducible docs images -> assets/images/):$(RESET)"
	@echo "  screenshot             - Generate the single dashboard hero screenshot"
	@echo "  screenshots            - Refresh ALL screenshots across tiers (Community -> Pro -> Enterprise)"
	@echo "  screenshots-community  - Refresh only Community/OSS-tier screenshots"
	@echo "  screenshots-vm-up      - Bring the screenshot VM up"
	@echo "  screenshots-vm-down    - Tear the screenshot VM down"
	@echo "  screenshots-pro-build  - Provision a Professional-tier VM (engines + self-signed license)"
	@echo "  screenshots-ent-build  - Provision an Enterprise-tier VM (all engines + self-signed license)"
	@echo "  screenshots-seed       - Seed base OSS demo data + host inventory into the VM"
	@echo "  screenshots-pro-seed   - Seed Professional engine demo data (in-VM ORM)"
	@echo "  screenshots-ent-seed   - Seed Enterprise engine demo data (in-VM ORM)"
	@echo "  screenshots-fleet-seed - Seed fleet-engine demo data (Pro+ REST)"
	@echo "  screenshots-capture    - Capture OSS-tier shots from the shotlist"
	@echo "  screenshots-pro-capture- Capture Professional-tier shots from the shotlist"
	@echo "  screenshots-ent-capture- Capture Enterprise-tier shots from the shotlist"
	@echo "  screenshots-ent-roles  - Capture Enterprise role-gated shots (federation/air-gap role flips)"
	@echo ""
	@echo "$(GREEN)Internationalization (docs i18n):$(RESET)"
	@echo "  i18n-validate          - Verify every data-i18n key in the HTML exists in every locale"
	@echo "  i18n-seed              - Fill missing locale keys with '[TODO] <English>' placeholders"
	@echo "  i18n-extract           - Print every data-i18n key referenced in the HTML"
	@echo "  translate              - Fill [TODO] placeholders via the GPU service (SERVICE=http://host:8765)"
	@echo "  translate-dry          - Show what translate would do (no service call, no writes)"
	@echo "  translate-check        - Offline gate: fail if any locale string is still untranslated"
	@echo "  lint                   - Run the docs i18n gates (i18n-validate + translate-check)"
	@echo ""
	@echo "$(GREEN)Testing targets (mirrors CI/CD):$(RESET)"
	@echo "  test                   - Run all tests (spelling, markdown lint, style, a11y, links, i18n)"
	@echo "  test-spelling          - Run typos spell checker"
	@echo "  test-markdown-lint     - Run markdownlint on README.md and SCREENSHOTS.md"
	@echo "  test-vale              - Run Vale documentation style checker"
	@echo "  test-accessibility     - Run pa11y accessibility tests on HTML pages"
	@echo "  test-links             - Run lychee link checker on all Markdown and HTML files"
	@echo ""
	@echo "$(GREEN)Packaging & maintenance:$(RESET)"
	@echo "  website-package        - Build .deb package for self-hosted sysmanage.org (nginx + certbot)"
	@echo "  clean                  - Clean generated files and dependencies"
	@echo "  prune-repo             - Remove stale/generated files from the working tree"
	@echo "  prune-repo-dry         - Show what prune-repo would remove (dry run)"
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
	@# Probe by running it: on Windows NPM is npm.cmd and Git Bash's `command -v`
	@# does not treat .cmd files as executable, so it would falsely report missing.
	@$(NPM) --version >/dev/null 2>&1 || { echo "$(RED)Error: npm is not installed$(RESET)"; exit 1; }
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
	@# `npm install -g` writes under the system-managed prefix
	@# (/usr/local/lib/node_modules on Linux), which requires elevated
	@# privileges.  Wrap with sudo when the prefix isn't writable.
	@echo "$(YELLOW)Installing npm global tools (markdownlint-cli2, pa11y, http-server)...$(RESET)"
	@NPM_PREFIX=$$($(NPM) prefix -g 2>/dev/null); \
	if [ -w "$$NPM_PREFIX/lib" ] || [ -w "$$NPM_PREFIX" ]; then \
		SUDO=""; \
	else \
		SUDO="sudo"; \
		echo "$(YELLOW)(npm prefix $$NPM_PREFIX is not user-writable; using sudo)$(RESET)"; \
	fi; \
	command -v markdownlint-cli2 >/dev/null 2>&1 && echo "$(GREEN)✓ markdownlint-cli2 already installed$(RESET)" || $$SUDO $(NPM) install -g markdownlint-cli2; \
	command -v pa11y >/dev/null 2>&1 && echo "$(GREEN)✓ pa11y already installed$(RESET)" || $$SUDO $(NPM) install -g pa11y || echo "$(YELLOW)⊘ pa11y unavailable (no OpenBSD Chrome) — skipping$(RESET)"; \
	command -v http-server >/dev/null 2>&1 && echo "$(GREEN)✓ http-server already installed$(RESET)" || $$SUDO $(NPM) install -g http-server
	@echo "$(GREEN)✓ npm global tools installed$(RESET)"
	@echo ""
	@# pa11y bundles puppeteer-core, which needs a Chrome binary downloaded
	@# separately into ~/.cache/puppeteer.  Without this, `make test-accessibility`
	@# fails with "Could not find Chrome (ver. ...)" — the Playwright chromium
	@# from `make install-browsers` lives in a different cache dir and isn't
	@# discoverable by puppeteer-core.
	@echo "$(YELLOW)Installing puppeteer Chrome for pa11y...$(RESET)"
	@if ! command -v pa11y >/dev/null 2>&1; then \
		echo "$(YELLOW)⊘ pa11y not installed (no OpenBSD Chrome) — skipping puppeteer Chrome$(RESET)"; \
	elif [ -d "$$HOME/.cache/puppeteer/chrome" ] && [ -n "$$(ls -A $$HOME/.cache/puppeteer/chrome 2>/dev/null)" ]; then \
		echo "$(GREEN)✓ puppeteer Chrome already installed in ~/.cache/puppeteer$(RESET)"; \
	else \
		$(NPX) puppeteer browsers install chrome || echo "$(YELLOW)⊘ puppeteer Chrome install failed — skipping (accessibility tests will skip)$(RESET)"; \
	fi
	@echo ""
	@# --- Cargo tools (typos, lychee) ---
	@echo "$(YELLOW)Installing cargo tools (typos-cli, lychee)...$(RESET)"
	@if ! command -v cargo >/dev/null 2>&1; then \
		echo "$(YELLOW)⊘ cargo not installed — skipping typos/lychee (Rust tools; unavailable on OpenBSD). Their checks will be skipped by 'make test'.$(RESET)"; \
	else \
		command -v typos >/dev/null 2>&1 && echo "$(GREEN)✓ typos already installed$(RESET)" || cargo install typos-cli@1.42.3 --locked; \
		command -v lychee >/dev/null 2>&1 && echo "$(GREEN)✓ lychee already installed$(RESET)" || cargo install lychee; \
		echo "$(GREEN)✓ Cargo tools installed$(RESET)"; \
	fi
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
			echo "$(YELLOW)⊘ vale not auto-installable on this platform (no OpenBSD build) — skipping. Manual: https://vale.sh/docs/install$(RESET)"; \
		fi; \
	}
	@echo "$(GREEN)✓ Vale step complete$(RESET)"
	@echo ""
	@# --- Screenshot VM prerequisites (Vagrant + libvirt) ---
	@$(MAKE) install-vm-deps
	@echo ""
	@echo "$(GREEN)✓ All development dependencies installed$(RESET)"
	@echo ""
	@echo "$(BLUE)Next steps:$(RESET)"
	@echo "1. Run 'make install-browsers' to install Playwright browser binaries (for screenshots)"
	@echo "2. Run 'make test' to run the full local test suite"
	@echo "3. If you were just added to the 'libvirt' group, log out/in (or 'newgrp libvirt') before 'make screenshots'"

# Screenshot-pipeline VM prerequisites: Vagrant + libvirt/KVM + the vagrant-libvirt
# plugin. Idempotent (skips what's already present). apt/Linux only — on other
# platforms it prints manual guidance (see screenshots/README.md) without failing.
# Called by install-dev; also runnable standalone.
install-vm-deps:
	@echo "$(YELLOW)Installing screenshot VM prerequisites (Vagrant + libvirt)...$(RESET)"
	@if ! command -v apt-get >/dev/null 2>&1; then \
		echo "$(YELLOW)Not an apt-based system — install Vagrant + a VM provider manually:$(RESET)"; \
		echo "  see screenshots/README.md -> Prerequisites"; \
	else \
		if command -v vagrant >/dev/null 2>&1; then \
			echo "$(GREEN)✓ vagrant already installed$(RESET)"; \
		else \
			echo "Adding HashiCorp apt repo + installing Vagrant..."; \
			wget -qO- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg; \
			echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $$(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list >/dev/null; \
			sudo apt-get update; \
			sudo apt-get install -y vagrant; \
		fi; \
		echo "Installing libvirt/KVM provider packages..."; \
		sudo apt-get install -y qemu-system-x86 libvirt-daemon-system libvirt-clients libvirt-dev ebtables dnsmasq-base build-essential; \
		if id -nG "$$USER" | tr ' ' '\n' | grep -qx libvirt; then \
			echo "$(GREEN)✓ already in libvirt group$(RESET)"; \
		else \
			sudo usermod -aG libvirt "$$USER"; \
			echo "$(YELLOW)Added $$USER to 'libvirt' — log out/in (or 'newgrp libvirt') before 'make screenshots'.$(RESET)"; \
		fi; \
		if vagrant plugin list 2>/dev/null | grep -q vagrant-libvirt; then \
			echo "$(GREEN)✓ vagrant-libvirt plugin already installed$(RESET)"; \
		else \
			echo "Installing vagrant-libvirt plugin..."; \
			vagrant plugin install vagrant-libvirt; \
		fi; \
	fi
	@echo "$(GREEN)✓ Screenshot VM prerequisites done$(RESET)"

# Install Playwright browsers
install-browsers:
	@echo "$(BLUE)Installing Playwright browsers...$(RESET)"
	@if [ ! -d node_modules/playwright ]; then \
		echo "$(RED)Error: Playwright not installed. Run 'make install-dev' first.$(RESET)"; \
		exit 1; \
	fi
	@if [ "$$(uname -s)" = "OpenBSD" ] || [ "$$(uname -s)" = "NetBSD" ] || [ "$$(uname -s)" = "FreeBSD" ]; then \
		echo "$(YELLOW)⊘ Playwright has no $$(uname -s) browser build — skipping Chromium install. Screenshots run on Linux/macOS/Windows.$(RESET)"; \
	else \
		echo "$(YELLOW)Installing Chromium browser...$(RESET)"; \
		$(NPX) playwright install chromium; \
		echo "$(GREEN)✓ Browsers installed successfully$(RESET)"; \
	fi

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

# ---- Automated documentation screenshots (screenshots/ pipeline) ------------
# Reproducible screenshots: provision a VM, seed demo data (REST + WS), drive the
# UI with Playwright, write PNGs into assets/images/. See screenshots/README.md.
.PHONY: screenshots screenshots-community screenshots-seed screenshots-capture screenshots-vm-up screenshots-vm-down screenshots-pro-build screenshots-pro-seed screenshots-pro-capture screenshots-ent-build screenshots-ent-seed screenshots-ent-capture screenshots-ent-roles screenshots-fleet-seed

SHOTS_DIR := screenshots
# Load screenshots/config.env (targets, admin + demo creds) if present.
-include $(SHOTS_DIR)/config.env
# Targets default to EMPTY: the seed/capture recipes then auto-resolve the VM's
# private (libvirt) IP and hit it directly. We can't use localhost: the VM forwards
# 8080/3000 to the host, but if you also run sysmanage on the host those ports
# collide and localhost answers from the wrong instance. Hitting the VM by IP is
# unambiguous. Set these in config.env to point seed/capture at any other instance.
SCREENSHOT_TARGET_API ?=
SCREENSHOT_TARGET_WEB ?=
SCREENSHOT_ADMIN ?= admin@sysmanage.org
# Capture as the built-in admin: it holds all security roles, so RBAC-gated UI
# (the host-detail "eye" icon, the audit-log viewer, etc.) actually renders. A
# role-less demo user would have those controls hidden. The demo users still appear
# on the Users page; we just don't log in as one.
SCREENSHOT_USER ?= admin@sysmanage.org
# Throwaway-VM dev defaults (not secrets): the admin password matches provision.sh's
# SYSMANAGE_ADMIN_PW fallback. Override in screenshots/config.env for a non-default instance.
SCREENSHOT_ADMIN_PW ?= ChangeMe-Dev-Only!
SCREENSHOT_PW ?= ChangeMe-Dev-Only!

# Lifecycle toggle:
#   FRESH=0 (default, while we get it working) — reuse/keep the VM. Idempotent:
#       re-running just re-seeds + re-captures against the running VM, and leaves
#       it up so you can inspect it. `vagrant up` won't re-provision a live VM.
#   FRESH=1 (once a full end-to-end run works) — destroy any existing VM first for
#       a clean slate, then tear it down again at the end. This is the intended
#       steady state (run at the end of a feature phase); flip the default below
#       to 1 when you're ready, or run `make screenshots FRESH=1`.
FRESH ?= 0

# Full pass: (optional clean) -> VM up -> seed -> capture into assets/images/.
# Capture EVERY tier in sequence — Community Edition (OSS) -> Professional ->
# Enterprise — re-provisioning + re-licensing the VM between each, then DESTROY the
# VM at the end on success. Long run: each tier re-provisions the box and
# Cython-builds the engines. A failure stops the chain and LEAVES the VM up for
# debugging (teardown only runs on full success). For quick single-tier iteration
# use screenshots-community / screenshots-pro-* / screenshots-ent-*.
#
# (Multi-Tenant SaaS is the planned 4th tier; it still needs saas shots in
# shotlist.json + a VM build that stands up OpenBAO + a provisioned tenant. Add a
# [4/4] block here once those exist.)
screenshots:
	@echo "$(BLUE)=== All-tier screenshots: Community Edition -> Professional -> Enterprise ===$(RESET)"
	@echo "$(YELLOW)Destroying any existing VM for a clean start...$(RESET)"
	@$(MAKE) screenshots-vm-down 2>/dev/null || true
	@echo "$(BLUE)--- [1/3] Community Edition ---$(RESET)"
	@$(MAKE) screenshots-vm-up
	@$(MAKE) screenshots-seed
	@$(MAKE) screenshots-capture
	@echo "$(BLUE)--- [2/3] Professional ---$(RESET)"
	@$(MAKE) screenshots-pro-build
	@$(MAKE) screenshots-seed
	@$(MAKE) screenshots-pro-seed
	@$(MAKE) screenshots-pro-capture
	@echo "$(BLUE)--- [3/3] Enterprise ---$(RESET)"
	@$(MAKE) screenshots-ent-build
	@$(MAKE) screenshots-seed
	@$(MAKE) screenshots-pro-seed
	@$(MAKE) screenshots-ent-seed
	@$(MAKE) screenshots-fleet-seed
	@$(MAKE) screenshots-ent-capture
	@$(MAKE) screenshots-ent-roles
	@echo "$(BLUE)All tiers captured — destroying the VM...$(RESET)"
	@$(MAKE) screenshots-vm-down
	@echo "$(GREEN)✓ All-tier screenshots refreshed in assets/images/; VM destroyed.$(RESET)"

# Community Edition (OSS) tier only — quick single-tier iteration. The VM is left
# running for fast re-runs; FRESH=1 destroys + reprovisions first and tears down
# after. (This was the old behavior of `make screenshots`.)
screenshots-community:
	@if [ "$(FRESH)" = "1" ]; then \
		echo "$(YELLOW)FRESH=1: destroying any existing VM for a clean run...$(RESET)"; \
		$(MAKE) screenshots-vm-down; \
	fi
	@$(MAKE) screenshots-vm-up
	@$(MAKE) screenshots-seed
	@$(MAKE) screenshots-capture
	@echo "$(GREEN)✓ Community Edition screenshots refreshed in assets/images/$(RESET)"
	@if [ "$(FRESH)" = "1" ]; then \
		echo "$(YELLOW)FRESH=1: tearing down the VM...$(RESET)"; \
		$(MAKE) screenshots-vm-down; \
	else \
		echo "$(BLUE)VM left running (FRESH=0). Re-run for quick iteration, or 'make screenshots-vm-down' to remove it.$(RESET)"; \
	fi

screenshots-vm-up:
	@command -v vagrant >/dev/null 2>&1 || { \
		echo "$(RED)Vagrant is not installed.$(RESET)"; \
		echo "Install Vagrant + a VM provider (libvirt recommended on Linux) —"; \
		echo "see screenshots/README.md → Prerequisites. Quick version:"; \
		echo "  wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg"; \
		echo "  echo \"deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $$(lsb_release -cs) main\" | sudo tee /etc/apt/sources.list.d/hashicorp.list"; \
		echo "  sudo apt update && sudo apt install -y vagrant qemu-system-x86 libvirt-daemon-system libvirt-clients libvirt-dev ebtables dnsmasq-base build-essential"; \
		echo "  sudo usermod -aG libvirt $$USER   # then re-login (or: newgrp libvirt)"; \
		echo "  vagrant plugin install vagrant-libvirt"; \
		exit 1; \
	}
	@echo "$(BLUE)Bringing up the screenshot VM...$(RESET)"
	@cd $(SHOTS_DIR) && SCREENSHOT_ADMIN_PW="$(SCREENSHOT_ADMIN_PW)" vagrant up
	@echo "$(YELLOW)Waiting for backend...$(RESET)"
	@cd $(SHOTS_DIR) && API="$(SCREENSHOT_TARGET_API)"; \
		[ -n "$$API" ] || API="http://$$(vagrant ssh -c 'hostname -I' 2>/dev/null | awk '{print $$1}' | tr -d '\r'):8080"; \
		echo "  backend target: $$API"; \
		for i in $$(seq 1 30); do curl -fsS $$API/api/health >/dev/null 2>&1 && { echo "  backend up"; break; }; sleep 5; done

screenshots-vm-down:
	@cd $(SHOTS_DIR) && vagrant destroy -f

# Professional tier (checkpoint): (re)provision the VM with SYSMANAGE_PRO=1 so the
# provisioner syncs sysmanage-professional-plus, Cython-builds + installs the engines,
# self-signs a Professional license, and verifies the engines load (then reverts the
# box to OSS state). Needs the sysmanage-professional-plus sibling repo present.
# For a clean build, run 'make screenshots-vm-down' first.
screenshots-pro-build:
	@command -v vagrant >/dev/null 2>&1 || { echo "$(RED)Vagrant not installed (see screenshots/README.md).$(RESET)"; exit 1; }
	@[ -d ../sysmanage-professional-plus ] || { echo "$(RED)../sysmanage-professional-plus not found.$(RESET)"; exit 1; }
	@echo "$(BLUE)Provisioning a Professional-tier VM (engine build + self-signed license)...$(RESET)"
	@# rsync only runs at boot, NOT on a later `vagrant up --provision` against a
	@# live VM. Force it so a rebuilt storage/modules (e.g. a freshly-rebuilt
	@# *-plugin.iife.js) reaches /srv/src before provision copies it into place.
	@cd $(SHOTS_DIR) && vagrant rsync 2>/dev/null || true
	@cd $(SHOTS_DIR) && SYSMANAGE_PRO=1 SYSMANAGE_TIER=professional SCREENSHOT_ADMIN_PW="$(SCREENSHOT_ADMIN_PW)" vagrant up --provision

# Provision an ENTERPRISE-tier VM: same prebuilt-bundle mechanism, but installs the
# full Enterprise engine set (federation, air-gap, virtualization, observability,
# fleet, automation, IdP, mirroring, AV, firewall) and signs a tier=enterprise
# self-signed license. Engine/feature lists are derived from the tier, so this and
# screenshots-pro-build share one provision path.
screenshots-ent-build:
	@command -v vagrant >/dev/null 2>&1 || { echo "$(RED)Vagrant not installed (see screenshots/README.md).$(RESET)"; exit 1; }
	@[ -d ../sysmanage-professional-plus ] || { echo "$(RED)../sysmanage-professional-plus not found.$(RESET)"; exit 1; }
	@echo "$(BLUE)Provisioning an Enterprise-tier VM (all engines + self-signed enterprise license)...$(RESET)"
	@# rsync only runs at boot, NOT on a later `vagrant up --provision` against a
	@# live VM. Force it so a rebuilt storage/modules (e.g. a freshly-rebuilt
	@# *-plugin.iife.js) reaches /srv/src before provision copies it into place.
	@cd $(SHOTS_DIR) && vagrant rsync 2>/dev/null || true
	@cd $(SHOTS_DIR) && SYSMANAGE_PRO=1 SYSMANAGE_TIER=enterprise SCREENSHOT_ADMIN_PW="$(SCREENSHOT_ADMIN_PW)" vagrant up --provision

# Seed demo data. REST (seed.py, stdlib-only) creates hosts/updates/tags/users/
# scripts; the rest of the inventory (OS, hardware, storage, network, software) is
# written straight into the DB by gen_seed_sql.py -> seed_inventory.sql, applied
# inside the VM. Targets SCREENSHOT_TARGET_API if set, else the running VM's IP.
# Seed fleet_engine demo data (groups / bulk / rolling) via the licensed Pro+ fleet
# REST API so the host-detail Fleet tab isn't empty. fleet_engine owns its tables
# internally (no ORM model / no migration in source), so unlike the other seeders this
# MUST go through the engine's own endpoints. seed_fleet.py is defensive — it skips on
# 402/errors and never fails — so this is safe to call in the Enterprise pass only.
screenshots-fleet-seed:
	@cd $(SHOTS_DIR) && API="$(SCREENSHOT_TARGET_API)"; \
		if [ -z "$$API" ]; then \
			VMIP=$$(vagrant ssh -c 'hostname -I' 2>/dev/null | awk '{print $$1}' | tr -d '\r'); \
			[ -n "$$VMIP" ] || { echo "$(RED)Screenshot VM not running.$(RESET)"; exit 1; }; \
			API="http://$$VMIP:8080"; \
		fi; \
		echo "$(BLUE)Seeding fleet data -> $$API$(RESET)"; \
		SCREENSHOT_TARGET="$$API" SCREENSHOT_ADMIN="$(SCREENSHOT_ADMIN)" SCREENSHOT_ADMIN_PW="$(SCREENSHOT_ADMIN_PW)" \
			$(PYTHON) seed_fleet.py || true

screenshots-seed:
	@cd $(SHOTS_DIR) && API="$(SCREENSHOT_TARGET_API)"; \
		if [ -z "$$API" ]; then \
			VMIP=$$(vagrant ssh -c 'hostname -I' 2>/dev/null | awk '{print $$1}' | tr -d '\r'); \
			[ -n "$$VMIP" ] || { echo "$(RED)Screenshot VM not running. Run 'make screenshots' (creates+provisions it), or 'cd screenshots && vagrant up'.$(RESET)"; exit 1; }; \
			API="http://$$VMIP:8080"; \
		fi; \
		echo "$(BLUE)Seeding demo data -> $$API$(RESET)"; \
		SCREENSHOT_TARGET="$$API" SCREENSHOT_ADMIN="$(SCREENSHOT_ADMIN)" SCREENSHOT_ADMIN_PW="$(SCREENSHOT_ADMIN_PW)" \
			$(PYTHON) seed.py; \
		$(PYTHON) gen_seed_sql.py; \
		if [ -z "$(SCREENSHOT_TARGET_API)" ]; then \
			echo "$(BLUE)Applying inventory + map coordinates directly (seed_inventory.sql, seed_geo.sql)...$(RESET)"; \
			cat seed_inventory.sql seed_geo.sql | vagrant ssh -c "sudo -u postgres psql -d sysmanage -v ON_ERROR_STOP=1 -q" 2>/dev/null \
				| sed 's/^/  /' || echo "$(YELLOW)direct seed skipped (could not reach VM psql)$(RESET)"; \
		else \
			echo "$(YELLOW)External target set — skipping direct SQL seed (VM-only).$(RESET)"; \
		fi

# Seed Professional-tier engine demo data (vulnerabilities, compliance, health,
# alerts, containers, secrets) straight into the engine result tables via the
# ORM, run INSIDE the Pro VM. Requires a Pro-licensed VM (make screenshots-pro-build)
# AND the OSS hosts seeded first (make screenshots-seed) — engine data attaches to
# those demo hosts. VM-only (needs the in-VM DB + models).
screenshots-pro-seed:
	@cd $(SHOTS_DIR) && VMIP=$$(vagrant ssh -c 'hostname -I' 2>/dev/null | awk '{print $$1}' | tr -d '\r'); \
		[ -n "$$VMIP" ] || { echo "$(RED)Screenshot VM not running. Run 'make screenshots-pro-build' first.$(RESET)"; exit 1; }; \
		echo "$(BLUE)Seeding Professional engine demo data (in-VM ORM)...$(RESET)"; \
		cat seed_pro.py | vagrant ssh -c "cd /opt/sysmanage && sudo env PYTHONPATH=/opt/sysmanage /opt/sysmanage/.venv/bin/python - 2>&1" 2>/dev/null \
			| sed 's/^/  /' || echo "$(YELLOW)pro seed failed (is the Pro-licensed VM up and OSS-seeded?)$(RESET)"

# Seed Enterprise-tier engine demo data (antivirus, firewall, fleet, automation,
# mirroring, access-groups, virtualization, observability, IdP, federation,
# air-gap) into their tables via the ORM, run INSIDE the Enterprise VM. Requires
# an Enterprise-licensed VM (make screenshots-ent-build) + the OSS hosts seeded
# first (make screenshots-seed); run after screenshots-pro-seed for the shared
# Pro engine data. VM-only.
screenshots-ent-seed:
	@cd $(SHOTS_DIR) && VMIP=$$(vagrant ssh -c 'hostname -I' 2>/dev/null | awk '{print $$1}' | tr -d '\r'); \
		[ -n "$$VMIP" ] || { echo "$(RED)Screenshot VM not running. Run 'make screenshots-ent-build' first.$(RESET)"; exit 1; }; \
		echo "$(BLUE)Seeding Enterprise engine demo data (in-VM ORM)...$(RESET)"; \
		cat seed_ent.py | vagrant ssh -c "cd /opt/sysmanage && sudo env PYTHONPATH=/opt/sysmanage /opt/sysmanage/.venv/bin/python - 2>&1" 2>/dev/null \
			| sed 's/^/  /' || echo "$(YELLOW)ent seed failed (is the Enterprise-licensed VM up and OSS-seeded?)$(RESET)"

# Capture into assets/images/. Targets SCREENSHOT_TARGET_WEB if set, else the
# running VM's private IP (resolved via vagrant ssh).
screenshots-capture: install-browsers
	@echo "$(BLUE)Capturing screenshots -> assets/images/$(RESET)"
	@cd $(SHOTS_DIR) && WEB="$(SCREENSHOT_TARGET_WEB)"; \
		if [ -z "$$WEB" ]; then \
			VMIP=$$(vagrant ssh -c 'hostname -I' 2>/dev/null | awk '{print $$1}' | tr -d '\r'); \
			[ -n "$$VMIP" ] || { echo "$(RED)Screenshot VM not running. Run 'make screenshots' (creates+provisions it), or 'cd screenshots && vagrant up'.$(RESET)"; exit 1; }; \
			WEB="http://$$VMIP:3000"; \
		fi; \
		echo "  web target: $$WEB"; \
		SCREENSHOT_TARGET="$$WEB" SCREENSHOT_USER="$(SCREENSHOT_USER)" SCREENSHOT_PW="$(SCREENSHOT_PW)" \
			$(NODE) capture.mjs

# Capture the Professional-tier shots (tier=pro in shotlist.json) against the
# Pro-licensed VM. Run AFTER: screenshots-pro-build, screenshots-seed,
# screenshots-pro-seed. Identical to screenshots-capture but with SCREENSHOT_TIER=pro,
# so it only captures the Pro pages and leaves the OSS shots untouched.
screenshots-pro-capture: install-browsers
	@echo "$(BLUE)Capturing Professional-tier screenshots -> assets/images/$(RESET)"
	@cd $(SHOTS_DIR) && WEB="$(SCREENSHOT_TARGET_WEB)"; \
		if [ -z "$$WEB" ]; then \
			VMIP=$$(vagrant ssh -c 'hostname -I' 2>/dev/null | awk '{print $$1}' | tr -d '\r'); \
			[ -n "$$VMIP" ] || { echo "$(RED)Screenshot VM not running. Run 'make screenshots-pro-build' first.$(RESET)"; exit 1; }; \
			WEB="http://$$VMIP:3000"; \
		fi; \
		echo "  web target: $$WEB"; \
		SCREENSHOT_TIER=pro SCREENSHOT_TARGET="$$WEB" SCREENSHOT_USER="$(SCREENSHOT_USER)" SCREENSHOT_PW="$(SCREENSHOT_PW)" \
			$(NODE) capture.mjs

# Capture the Enterprise-tier shots (tier=enterprise in shotlist.json) against the
# Enterprise-licensed VM. Run AFTER: screenshots-ent-build, screenshots-seed,
# screenshots-pro-seed, screenshots-ent-seed.
screenshots-ent-capture: install-browsers
	@echo "$(BLUE)Capturing Enterprise-tier screenshots -> assets/images/$(RESET)"
	@cd $(SHOTS_DIR) && WEB="$(SCREENSHOT_TARGET_WEB)"; \
		if [ -z "$$WEB" ]; then \
			VMIP=$$(vagrant ssh -c 'hostname -I' 2>/dev/null | awk '{print $$1}' | tr -d '\r'); \
			[ -n "$$VMIP" ] || { echo "$(RED)Screenshot VM not running. Run 'make screenshots-ent-build' first.$(RESET)"; exit 1; }; \
			WEB="http://$$VMIP:3000"; \
		fi; \
		echo "  web target: $$WEB"; \
		SCREENSHOT_TIER=enterprise SCREENSHOT_TARGET="$$WEB" SCREENSHOT_USER="$(SCREENSHOT_USER)" SCREENSHOT_PW="$(SCREENSHOT_PW)" \
			$(NODE) capture.mjs

# Re-capture the role-gated Enterprise shots (federation Sites + air-gap), which
# render real content only when the server's federation_role/air_gap_role match
# (route mounting happens at backend startup, so each role change needs a
# restart). Two passes: (A) coordinator+collector -> Sites x3 + Air-Gap
# Collections; (B) repository -> Air-Gap Repositories. Run after screenshots-ent-seed.
screenshots-ent-roles: install-browsers
	@cd $(SHOTS_DIR) && VMIP=$$(vagrant ssh -c 'hostname -I' 2>/dev/null | awk '{print $$1}' | tr -d '\r'); \
		[ -n "$$VMIP" ] || { echo "$(RED)Screenshot VM not running.$(RESET)"; exit 1; }; \
		WEB="http://$$VMIP:3000"; \
		echo "$(BLUE)Pass A: federation_role=coordinator, air_gap_role=collector$(RESET)"; \
		cat set_roles.py | vagrant ssh -c "cd /opt/sysmanage && sudo env PYTHONPATH=/opt/sysmanage FEDERATION_ROLE=coordinator AIR_GAP_ROLE=collector /opt/sysmanage/.venv/bin/python - 2>&1" 2>/dev/null | sed 's/^/  /'; \
		echo "$(BLUE)  restarting backend to re-mount role routes...$(RESET)"; \
		vagrant ssh -c "cd /opt/sysmanage && sudo make stop >/dev/null 2>&1; sudo bash -c 'cd /opt/sysmanage && setsid make start >/var/log/sysmanage-start.log 2>&1 </dev/null &'" 2>/dev/null; \
		sleep 45; \
		SCREENSHOT_TIER=enterprise SCREENSHOT_ONLY=ent-sites,ent-sites-map,ent-sites-tiles,ent-airgap-collections,ent-federation-hosts \
			SCREENSHOT_TARGET="$$WEB" SCREENSHOT_USER="$(SCREENSHOT_USER)" SCREENSHOT_PW="$(SCREENSHOT_PW)" $(NODE) capture.mjs || true; \
		echo "$(BLUE)Pass B: air_gap_role=repository, federation_role=none$(RESET)"; \
		cat set_roles.py | vagrant ssh -c "cd /opt/sysmanage && sudo env PYTHONPATH=/opt/sysmanage AIR_GAP_ROLE=repository FEDERATION_ROLE=none /opt/sysmanage/.venv/bin/python - 2>&1" 2>/dev/null | sed 's/^/  /'; \
		echo "$(BLUE)  restarting backend...$(RESET)"; \
		vagrant ssh -c "cd /opt/sysmanage && sudo make stop >/dev/null 2>&1; sudo bash -c 'cd /opt/sysmanage && setsid make start >/var/log/sysmanage-start.log 2>&1 </dev/null &'" 2>/dev/null; \
		sleep 45; \
		SCREENSHOT_TIER=enterprise SCREENSHOT_ONLY=ent-airgap-repositories \
			SCREENSHOT_TARGET="$$WEB" SCREENSHOT_USER="$(SCREENSHOT_USER)" SCREENSHOT_PW="$(SCREENSHOT_PW)" $(NODE) capture.mjs || true; \
		echo "$(GREEN)Role-gated re-capture done. (Box left as air_gap_role=repository / federation_role=none.)$(RESET)"

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

# Package-repo retention (R2 is the source of truth; repo/ is not in git).
# Pulls the current repo/ down from R2, keeps only the latest 5 versions of each
# package (across apt/rpm/alpine/win/mac/bsd, regenerating the apt/rpm/alpine
# indexes), then mirrors the pruned tree back to R2 with --delete so old versions
# drop off R2.  Run occasionally (it's independent of releases, which publish
# additively).  Needs AWS creds + R2_ACCOUNT_ID in your env (same as the seed),
# and local dpkg-dev/apt-utils, createrepo_c, apk for index regen.
R2_BUCKET ?= sysmanage-repo
R2_ENDPOINT ?= https://$(R2_ACCOUNT_ID).r2.cloudflarestorage.com
_R2_ARGS = --endpoint-url $(R2_ENDPOINT) --region auto --only-show-errors
.PHONY: prune-repo prune-repo-dry
prune-repo-dry:
	@aws s3 sync s3://$(R2_BUCKET)/ repo/ $(_R2_ARGS)
	@KEEP=5 DRY_RUN=1 ./scripts/prune-package-repo.sh

prune-repo:
	@aws s3 sync s3://$(R2_BUCKET)/ repo/ $(_R2_ARGS)
	@test "$$(find repo -type f 2>/dev/null | wc -l)" -gt 50 || { echo "ERROR: R2 pull returned <50 files — refusing to prune + --delete (a bad/empty pull could wipe the bucket)"; exit 1; }
	@KEEP=5 DRY_RUN=0 ./scripts/prune-package-repo.sh
	@aws s3 sync repo/ s3://$(R2_BUCKET)/ $(_R2_ARGS) --size-only --delete

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
	command -v markdownlint-cli2 >/dev/null 2>&1 && echo "$(GREEN)✓ markdownlint-cli2 found$(RESET)" || { echo "$(RED)✗ markdownlint-cli2 not found (install: npm install -g markdownlint-cli2)$(RESET)"; MISSING=1; }; \
	command -v http-server >/dev/null 2>&1 && echo "$(GREEN)✓ http-server found$(RESET)" || { echo "$(RED)✗ http-server not found (install: npm install -g http-server)$(RESET)"; MISSING=1; }; \
	for t in typos vale pa11y lychee; do \
		if command -v $$t >/dev/null 2>&1; then echo "$(GREEN)✓ $$t found$(RESET)"; \
		else echo "$(YELLOW)○ $$t not found — its checks will be skipped (no build for this platform, e.g. OpenBSD)$(RESET)"; fi; \
	done; \
	if [ $$MISSING -ne 0 ]; then echo ""; echo "$(YELLOW)Required tools (markdownlint-cli2, http-server) missing — install them before 'make test'.$(RESET)"; exit 1; fi
	@echo "$(GREEN)Testing dependency check complete (browser/Rust tools optional)$(RESET)"

# Spell checking (mirrors .github/workflows/spellcheck.yml)
test-spelling:
	@echo "$(BLUE)=== Spell Check ===$(RESET)"
	@command -v typos >/dev/null 2>&1 || { echo "$(YELLOW)⊘ typos not installed — skipping (no OpenBSD/BSD build)$(RESET)"; exit 0; }; \
	typos && echo "$(GREEN)✓ Spell check passed$(RESET)"

# Markdown linting (mirrors .github/workflows/markdown-lint.yml)
test-markdown-lint:
	@echo "$(BLUE)=== Markdown Lint ===$(RESET)"
	markdownlint-cli2 README.md SCREENSHOTS.md
	@echo "$(GREEN)✓ Markdown lint passed$(RESET)"

# Vale documentation style (mirrors .github/workflows/vale.yml)
test-vale:
	@echo "$(BLUE)=== Vale Documentation Style ===$(RESET)"
	@# Vale's exit code only reflects ERRORS; warnings (MinAlertLevel=warning in
	@# .vale.ini) are displayed but don't fail the build, so they can scroll past
	@# unnoticed. Capture the run and fail if the summary reports any warnings or
	@# errors — no warning hides.
	@command -v vale >/dev/null 2>&1 || { echo "$(YELLOW)⊘ vale not installed — skipping (no OpenBSD build)$(RESET)"; exit 0; }; \
	out=$$(vale docs 2>&1); echo "$$out"; \
		if echo "$$out" | grep -qE '[1-9][0-9]* (error|warning)'; then \
			echo "$(RED)✗ Vale reported warnings/errors (failing — warnings are not allowed to hide)$(RESET)"; \
			exit 1; \
		fi; \
	echo "$(GREEN)✓ Vale style check passed$(RESET)"

# Accessibility testing (mirrors .github/workflows/accessibility.yml)
#
# Self-healing on two fronts:
#   1. pa11y bundles puppeteer-core which needs a Chrome binary in
#      ~/.cache/puppeteer.  If absent, fetch it on the fly so a fresh
#      checkout works without a separate `make install-dev`.
#   2. A previous run that crashed mid-test can leave the http-server
#      backgrounded on port 8087.  Kill any squatter before starting,
#      and trap cleanup so this run never leaves a zombie either.
test-accessibility:
	@echo "$(BLUE)=== Accessibility Check ===$(RESET)"
	@command -v pa11y >/dev/null 2>&1 || { echo "$(YELLOW)⊘ pa11y/Chrome not available — skipping accessibility (no OpenBSD browser)$(RESET)"; exit 0; }; \
	if [ ! -d "$$HOME/.cache/puppeteer/chrome" ] || [ -z "$$(ls -A $$HOME/.cache/puppeteer/chrome 2>/dev/null)" ]; then \
		echo "$(YELLOW)puppeteer Chrome missing — installing...$(RESET)"; \
		$(NPX) puppeteer browsers install chrome; \
	fi; \
	PORT_HOLDER=$$(lsof -ti :8087 2>/dev/null); \
	if [ -n "$$PORT_HOLDER" ]; then \
		echo "$(YELLOW)Killing stale process on :8087 (pid $$PORT_HOLDER)$(RESET)"; \
		kill $$PORT_HOLDER 2>/dev/null; \
		sleep 1; \
	fi; \
	http-server . -p 8087 -s >/dev/null 2>&1 & \
	SERVER_PID=$$!; \
	trap "kill $$SERVER_PID 2>/dev/null || true" EXIT INT TERM; \
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
	if [ $$FAIL -ne 0 ]; then echo "$(RED)Accessibility tests failed$(RESET)"; exit 1; fi; \
	echo "$(GREEN)✓ Accessibility tests passed$(RESET)"

# Link checking (mirrors .github/workflows/link-check.yml)
test-links:
	@echo "$(BLUE)=== Link Check ===$(RESET)"
	@command -v lychee >/dev/null 2>&1 || { echo "$(YELLOW)⊘ lychee not installed — skipping (no OpenBSD/BSD build)$(RESET)"; exit 0; }; \
	lychee --verbose --no-progress --root-dir . --max-retries 3 --retry-wait-time 2 --exclude-path node_modules --exclude-path .git --exclude-path SignPath --exclude 'http://localhost:*' '**/*.md' '**/*.html' && echo "$(GREEN)✓ Link check passed$(RESET)"

# Run all tests (mirrors full CI/CD test suite).
# Front-loads check-test-deps so a missing tool fails with a clear install
# hint instead of an opaque "make: <tool>: No such file or directory".
test: check-test-deps test-spelling test-markdown-lint test-vale test-accessibility test-links i18n-validate
	@echo ""
	@echo "$(GREEN)========================================$(RESET)"
	@echo "$(GREEN)  All tests passed$(RESET)"
	@echo "$(GREEN)========================================$(RESET)"

# Lightweight gate the shared pre-push hook runs (it invokes ``make lint`` in
# every repo with a ``lint:`` target).  Keeps the i18n checks — key existence
# AND offline translation completeness — out of the heavy ``test`` target so an
# untranslated string is caught before a push, with no translation service.
# File-length gate: no source file may exceed 1000 lines (scripts/ exempt).
# Keyed on code extensions only, so docs content (.html/.md/.json/.css) is
# inherently exempt — only actual code (.py/.ts/.js) is subject to the limit.
lint-file-length:
	@echo "Checking file lengths (max 1000 lines; scripts/ + generated i18n exempt)..."
	@bad=$$(git ls-files '*.py' '*.pyx' '*.pxi' '*.ts' '*.tsx' '*.js' '*.jsx' \
		| grep -vE '(^|/)scripts/|-i18n\.ts$$' \
		| while read f; do \
			n=$$(wc -l < "$$f"); \
			if [ "$$n" -gt 1000 ]; then printf '  %6d  %s\n' "$$n" "$$f"; fi; \
		done); \
	if [ -n "$$bad" ]; then \
		echo "ERROR: source files exceed the 1000-line limit:"; \
		echo "$$bad"; \
		exit 1; \
	fi; \
	echo "[OK] all source files within 1000 lines"

lint: lint-file-length i18n-validate translate-check
	@echo "[OK] docs lint (i18n) passed"

# i18n: collect data-i18n="..." attributes from every .html and verify
# every key exists in every locale .json within budget.  Run
# ``make i18n-seed`` to populate gaps with [TODO]-prefixed placeholders.
i18n-validate:
	@echo "=== i18n validation ==="
	@$(PYTHON) scripts/i18n_validate.py --validate
	@echo "[OK] i18n validation completed"

i18n-seed:
	@echo "=== i18n seeding ==="
	@$(PYTHON) scripts/i18n_validate.py --seed
	@echo "[OK] i18n seed completed"

i18n-extract:
	@$(PYTHON) scripts/i18n_validate.py --extract

# i18n translation backfill via the GPU translation service (lives in the
# sysmanage repo at scripts/translation-service/).  Idempotent: only the
# untranslated [TODO] strings are sent, so re-run any time to fill new gaps.
# Point at your running service with either:
#   export TRANSLATION_SERVICE_URL=http://beast:8765
#   or:  make translate SERVICE=http://beast:8765
SERVICE ?= $(or $(TRANSLATION_SERVICE_URL),http://localhost:8765)

translate:
	@$(PYTHON) scripts/translate_i18n.py --service "$(SERVICE)" --fail-on-gaps

translate-dry:
	@$(PYTHON) scripts/translate_i18n.py --dry-run

# Offline completeness GATE — no service, no writes, no network.  Fails loudly
# (non-zero) if any locale string is still untranslated.  Safe for CI / release.
translate-check:
	@$(PYTHON) scripts/translate_i18n.py --check

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