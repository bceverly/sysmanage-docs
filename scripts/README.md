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

## Notes

- All JSON files are saved with UTF-8 encoding and proper formatting
- Technical terms are preserved in English when appropriate
- Scripts can be run multiple times safely - they will update existing translations
