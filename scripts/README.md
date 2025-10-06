# SysManage Documentation Translation Scripts

This directory contains scripts for translating documentation keys to multiple languages.

## translate_grafana_keys.py

This script translates the Grafana setup documentation keys from English to all 14 supported languages.

### Prerequisites

- Python 3.7 or higher
- Anthropic API key
- `anthropic` Python package

### Installation

```bash
pip install anthropic
```

### Usage

1. Set your Anthropic API key as an environment variable:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

2. Run the script:

```bash
python3 /home/bceverly/dev/sysmanage-docs/scripts/translate_grafana_keys.py
```

### What It Does

The script will:

1. Load the English locale file (`en.json`)
2. Extract all `grafana_setup` keys from both:
   - `homepage.administration.grafana_setup`
   - `administration.grafana_setup.*`
3. Translate each key to all 14 supported languages using Claude API
4. Update each language locale file with the translations
5. Preserve all existing translations in each file

### Supported Languages

- Arabic (ar)
- German (de)
- Spanish (es)
- French (fr)
- Hindi (hi)
- Italian (it)
- Japanese (ja)
- Korean (ko)
- Dutch (nl)
- Portuguese (pt)
- Russian (ru)
- Simplified Chinese (zh_CN)
- Traditional Chinese (zh_TW)

### Translation Process

The script uses Claude 3.5 Sonnet to perform high-quality translations that:

- Maintain technical accuracy
- Preserve technical terminology (e.g., "OpenTelemetry", "Grafana", "OTLP")
- Keep a professional tone appropriate for system administrators
- Ensure consistency across all languages

### Batch Processing

The script processes translations in batches of 30 keys to avoid API token limits and ensure reliable translations.

### Error Handling

If a translation fails for any reason, the script will:
- Display a warning message
- Fall back to the English text for that key
- Continue processing remaining languages

### Output

The script provides progress updates showing:
- Number of keys found to translate
- Current language being processed
- Batch progress for each language
- Final summary of completed translations

### Example Output

```
Loading English source file...
Found 62 keys to translate

Keys to translate:
  - homepage.administration.grafana_setup
  - administration.grafana_setup.title
  - administration.grafana_setup.subtitle
  ...

Translating to Arabic (ar)...
  Translating batch 1/3...
  Translating batch 2/3...
  Translating batch 3/3...
  ✓ Updated /path/to/locales/ar.json

...

============================================================
Translation complete!
Translated 62 keys to 14 languages
============================================================
```

## Notes

- The script creates backups before modifying files (not implemented yet, but recommended)
- All JSON files are saved with UTF-8 encoding and proper formatting
- Technical terms are preserved in English when appropriate
- The script can be run multiple times safely - it will update existing translations
