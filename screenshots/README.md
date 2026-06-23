# Documentation Screenshots

Automated, reproducible screenshots for the SysManage docs. `make screenshots`
brings up a clean instance, seeds deterministic demo data, drives the web UI with
Playwright, and writes PNGs into `../assets/images/` — the exact paths the docs
already embed.

## Pipeline (decoupled stages)

```
  ┌─ environment ─┐   ┌──────── reusable core (target-agnostic) ────────┐
   Vagrant VM  ───►   seed.py (REST)  ─►  fixture_agent.py (WS)  ─►  capture.mjs
   install server      hosts/updates/      OS/inventory per host      Playwright
   + agent             tags/users                                     → assets/images/
  └───────────────┘   └─────────────────────────────────────────────────┘
```

The **core (seed + capture) is independent of the environment.** Point it at the
VM *or any running instance* with `SCREENSHOT_TARGET_*`, so you can iterate on
seeding/capture in seconds without rebuilding the VM (this mirrors the old
`screenshot-generator.js`, which drove a live box).

## Why two seed steps

The REST API can create **hosts, available updates, tags, and users** — but host
**OS/hardware/software inventory has no REST path**; it only arrives over the agent
WebSocket (`os_version_update`). So:

- `seed.py` — REST for everything REST supports.
- `fixture_agent.py` — a tiny WebSocket client that reports a realistic OS per host
  (so the dashboard OS-distribution tile and platform columns aren't blank).
- The VM's **own agent** also registers and reports one genuinely-real host for free.

## Prerequisites

`make screenshots` needs **Vagrant** + a **VM provider** on the host (it can't
install these itself). On Linux, libvirt/KVM is the native choice.

**Vagrant (current version, via HashiCorp's apt repo):**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install -y vagrant
```

**Provider — option A: libvirt/KVM (recommended on Linux):**
```bash
# Newer Ubuntu: use qemu-system-x86 (the qemu-kvm meta-package is gone).
sudo apt install -y qemu-system-x86 libvirt-daemon-system libvirt-clients libvirt-dev ebtables dnsmasq-base build-essential
sudo usermod -aG libvirt $USER          # then log out/in, or: newgrp libvirt
vagrant plugin install vagrant-libvirt
```

**Provider — option B: VirtualBox (simpler, but conflicts with running KVM VMs):**
```bash
sudo apt install -y virtualbox
```

Install exactly **one** provider and Vagrant auto-selects it (no flag needed). All
of the above is also installed by **`make install-dev`** (target `install-vm-deps`).

**Box:** the default is `generic/ubuntu2204` (the `generic/` namespace has no 24.04
image — `generic/ubuntu2404` 404s). The guest OS version doesn't matter; sysmanage
installs its deps via apt either way. Override with `SCREENSHOT_BOX=<box>` if you
prefer another libvirt image (e.g. `generic/ubuntu2304`, `alvistack/ubuntu-24.04`).
Node + Playwright (for capture) come via `make install-dev && make install-browsers`.

## Quick start (Vagrant path)

```bash
cp config.example.env config.env      # fill in SCREENSHOT_ADMIN_PW etc. (gitignored)
make screenshots                      # vagrant up → install → seed → capture → place
```

## Lifecycle (`FRESH`)

`make screenshots` has two modes, controlled by `FRESH` (default `0`):

- **`FRESH=0` (default — while we get it working):** idempotent and non-destructive.
  Reuses the VM if it exists, re-seeds + re-captures, and **leaves the VM running**
  so you can inspect it. Re-run `make screenshots` to iterate fast. `vagrant up`
  won't re-provision a live VM, so re-runs are quick. (If you `vagrant halt` the VM,
  bring services back with `cd screenshots && vagrant up --provision`.)
- **`FRESH=1` (steady state — once a full run works):** **destroys any existing VM
  for a clean slate, then tears it down again at the end.** This is the intended way
  to run it at the end of a feature phase. Use `make screenshots FRESH=1`, or flip
  the `FRESH ?= 0` default to `1` in the root `Makefile` once you're confident.

Teardown anytime: `make screenshots-vm-down`.

## Iterating against an existing instance (fast loop)

```bash
# point at a box you already have running, skip the VM entirely
export SCREENSHOT_TARGET_API=http://my-dev-box:8080
export SCREENSHOT_TARGET_WEB=http://my-dev-box:3000
export SCREENSHOT_ADMIN_PW=...  SCREENSHOT_PW=Demo-Pass-1!
make screenshots-seed                 # seed.py + fixture_agent.py
make screenshots-capture              # capture.mjs only
```

## Pass-one targets (the 6 screenshots the docs already use)

| PNG (in `assets/images/`) | Used by | Shot |
|---|---|---|
| `dashboard-screenshot.png` | `index.html` | dashboard, 1920×1080 |
| `updates-page.png` | `index.html` | updates page |
| `dashboard-preview.png` | `docs/server/reports.html` | dashboard, 1200×874 |
| `registered-hosts-report.png` | `docs/server/reports.html` | report |
| `hosts-with-tags-report.png` | `docs/server/reports.html` | report |
| `users-report.png` | `docs/server/reports.html` | report |

All OSS-tier, so **no license/tier juggling in pass one.**

## Adding screenshots later

1. Add an entry to `shotlist.json` (`type: "route"` or `"report"`, viewport, `out`).
2. If it needs new demo data, extend `fixtures.json`.
3. `make screenshots-capture`. Done — no code change.

## Pass two (deferred): tiers

Pro/Enterprise/SaaS screenshots will add a tier loop: inject a license key (kept in
a gitignored file, see `config.example.env`), restart the backend, capture that
tier's shots. Not built yet — pass one is OSS-only by design.

## Known first-run iteration points

I built and ground-truthed the seed/capture core against the live API, but a few
things can only be verified on a real run:

- **`provision/provision.sh`** wraps the project installer; the `[VERIFY]` stages
  (OpenBAO/migrate, non-interactive admin-create, `make start` daemonization) may
  need a tweak to match the current install flow.
- **`fixture_agent.py`** uses a best-effort `os_version_update` envelope. If hosts
  seed but show no OS, diff it against `sysmanage-agent`'s real outbound messages.
- **Report shots** click report cards by visible name (`reportName` in
  `shotlist.json`); adjust those strings if the UI labels differ.

## Files

| File | Role |
|---|---|
| `fixtures.json` | the deterministic demo dataset (edit this to change shots) |
| `seed.py` | REST seeder (hosts/updates/tags/users) |
| `fixture_agent.py` | WebSocket OS/inventory reporter |
| `capture.mjs` | Playwright capture driver |
| `shotlist.json` | declarative shot definitions |
| `Vagrantfile`, `provision/provision.sh` | the throwaway VM |
| `config.example.env` | copy to `config.env` (gitignored) |
