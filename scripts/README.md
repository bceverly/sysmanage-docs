# SysManage Documentation Translation Scripts

This directory contains scripts for adding translations to the documentation locale files.

## add_proplus_translations.py

Adds Professional+ documentation translations (health analysis, vulnerability scanning, alerting engine, compliance engine) to all 14 supported language locale files.

### Usage

```bash
python3 /home/bceverly/dev/sysmanage-docs/scripts/add_proplus_translations.py
```

## add_alerting_page_translations.py

Adds detailed alerting and compliance page translations to all 14 supported language locale files.

### Usage

```bash
python3 /home/bceverly/dev/sysmanage-docs/scripts/add_alerting_page_translations.py
```

## generate_sysmanage_pptx.py

Generates the SysManage overview PowerPoint presentation used for product talks and demos.

### Prerequisites

```bash
pip install python-pptx cairosvg
```

### Usage

```bash
python3 ~/dev/sysmanage-docs/scripts/generate_sysmanage_pptx.py
```

### Output

`~/dev/sysmanage-docs/Presentations/SysManage.pptx` -- a 25-slide, 16:9 branded presentation.

### How It Works

1. **SVG-to-PNG conversion** -- Uses `cairosvg` to convert the SysManage logo and icon SVGs from `assets/images/` into PNGs stored in this `scripts/` directory. These PNGs are embedded into the slides.

2. **Slide generation** -- Uses `python-pptx` to programmatically build each slide from scratch (blank layout). Every slide is constructed with shapes, textboxes, tables, and images positioned via code rather than a template. This gives full control over branding and layout.

3. **Branding** -- Colors, fonts, and layout conventions are defined as constants at the top of the script, derived from the sysmanage-docs website CSS:
   - Primary Blue: `#1976d2`
   - Dark Blue (headers/backgrounds): `#0d3d5c`
   - Green (accents): `#388e3c`
   - Button Green: `#2e7d47`
   - Font: Arial

4. **Slide structure** -- Each slide has its own builder function (`slide_01_title`, `slide_02_agenda`, etc.), making it straightforward to find and edit individual slides. Helper functions handle common patterns like bullet slides, table slides, header/footer bars, and accent shapes.

### Slide Outline

| # | Slide | Section |
|---|-------|---------|
| 1 | Title | Opening |
| 2 | Agenda | Opening |
| 3 | The Problem | Opening |
| 4 | What is SysManage? | Opening |
| 5 | Architecture | Opening |
| 6 | Cross-Platform Support | Opening |
| 7 | Packaging Formats & OS Versions | Opening |
| 8 | Internationalization | Opening |
| 9 | Open Source Features | Features |
| 10 | Monitoring & Management | Features |
| 11 | Pro+ Licensing Model | Features |
| 12 | Pro+ Professional Tier | Features |
| 13 | Pro+ Enterprise Tier | Features |
| 14 | Why Security Matters | Security |
| 15 | Security-First Architecture | Security |
| 16 | Security in Development Process | Security |
| 17 | Demo Agenda | Demo |
| 18 | LIVE DEMO | Demo |
| 19 | What You Just Saw | Post-Demo |
| 20 | Roadmap Overview | Futures |
| 21 | Futures: Near-Term (Phases 3-5) | Futures |
| 22 | Futures: Mid-Term (Phases 6-9) | Futures |
| 23 | Futures: Long-Term (Phases 10-12) | Futures |
| 24 | Key Takeaways | Closing |
| 25 | Thank You | Closing |

### Making Changes

To modify slide content, edit the corresponding `slide_XX_*` function in `generate_sysmanage_pptx.py` and re-run the script. The PPTX is regenerated from scratch each time -- there is no incremental editing.

To change branding colors or fonts, update the constants at the top of the script.

### Generated Files

| File | Purpose |
|------|---------|
| `sysmanage-logo.png` | Converted logo (generated from SVG by the script) |
| `sysmanage-icon.png` | Converted icon (generated from SVG by the script) |

## Notes

- All JSON files are saved with UTF-8 encoding and proper formatting
- Technical terms are preserved in English when appropriate
- Scripts can be run multiple times safely - they will update existing translations
