#!/usr/bin/env python3
"""
Translation script for Grafana setup documentation keys.
This script extracts the new grafana_setup keys from en.json and translates them
to all 14 supported languages using the Anthropic Claude API.
"""

import json
import os
import sys
from pathlib import Path
import anthropic

# Language mapping
LANGUAGES = {
    'ar': 'Arabic',
    'de': 'German',
    'es': 'Spanish',
    'fr': 'French',
    'hi': 'Hindi',
    'it': 'Italian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'nl': 'Dutch',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh_CN': 'Simplified Chinese',
    'zh_TW': 'Traditional Chinese'
}

def load_json_file(file_path):
    """Load and parse a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(file_path, data):
    """Save data to a JSON file with proper formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')  # Add trailing newline

def extract_grafana_keys(data, path=''):
    """Extract all keys and values from the grafana_setup section."""
    keys = {}

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, dict):
                keys.update(extract_grafana_keys(value, current_path))
            else:
                keys[current_path] = value

    return keys

def translate_text_batch(client, texts, target_language):
    """Translate a batch of texts to the target language using Claude."""

    # Create a prompt with all texts
    text_list = "\n".join([f"{i+1}. {text}" for i, text in enumerate(texts)])

    prompt = f"""Translate the following English technical documentation strings to {target_language}.
These are UI labels and documentation section titles for a system administration tool called SysManage.

Important guidelines:
- Maintain technical accuracy and terminology
- Keep the professional tone appropriate for system administrators
- Preserve any technical terms that are commonly used in English (e.g., "OpenTelemetry", "Grafana", "OTLP", "Prometheus")
- Return ONLY the translations, numbered exactly as provided below
- Each translation should be on its own line with its number
- Do not add explanations or notes

English strings to translate:

{text_list}

Provide the translations:"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Parse the response
    response_text = message.content[0].text.strip()

    # Extract translations from numbered list
    translations = []
    for line in response_text.split('\n'):
        line = line.strip()
        if line and line[0].isdigit():
            # Remove the number prefix
            parts = line.split('.', 1)
            if len(parts) > 1:
                translations.append(parts[1].strip())

    return translations

def set_nested_value(data, path, value):
    """Set a value in a nested dictionary using dot notation path."""
    keys = path.split('.')
    current = data

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[keys[-1]] = value

def main():
    # Get API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set it with: export ANTHROPIC_API_KEY='your-api-key'")
        sys.exit(1)

    # Initialize Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Define paths
    script_dir = Path(__file__).parent
    locales_dir = script_dir.parent / 'assets' / 'locales'
    en_file = locales_dir / 'en.json'

    print("Loading English source file...")
    en_data = load_json_file(en_file)

    # Extract grafana_setup keys from both locations
    grafana_keys = {}

    # From docs.administration.grafana_setup
    if 'docs' in en_data and 'administration' in en_data['docs']:
        if 'grafana_setup' in en_data['docs']['administration']:
            grafana_keys['docs.administration.grafana_setup'] = en_data['docs']['administration']['grafana_setup']

    # From administration.grafana_setup
    if 'administration' in en_data and 'grafana_setup' in en_data['administration']:
        admin_grafana = extract_grafana_keys(
            en_data['administration']['grafana_setup'],
            'administration.grafana_setup'
        )
        grafana_keys.update(admin_grafana)

    if not grafana_keys:
        print("Error: No grafana_setup keys found in en.json")
        sys.exit(1)

    print(f"Found {len(grafana_keys)} keys to translate")
    print("\nKeys to translate:")
    for key in grafana_keys.keys():
        print(f"  - {key}")

    # Translate for each language
    for lang_code, lang_name in LANGUAGES.items():
        print(f"\nTranslating to {lang_name} ({lang_code})...")

        lang_file = locales_dir / f'{lang_code}.json'

        # Load existing translations
        if lang_file.exists():
            lang_data = load_json_file(lang_file)
        else:
            print(f"Warning: {lang_file} does not exist, creating new file")
            lang_data = {}

        # Prepare texts for translation
        keys_list = list(grafana_keys.keys())
        texts_list = [grafana_keys[key] for key in keys_list]

        # Translate in batches (to avoid token limits)
        batch_size = 30
        all_translations = []

        for i in range(0, len(texts_list), batch_size):
            batch_texts = texts_list[i:i+batch_size]
            print(f"  Translating batch {i//batch_size + 1}/{(len(texts_list) + batch_size - 1)//batch_size}...")

            try:
                translations = translate_text_batch(client, batch_texts, lang_name)

                if len(translations) != len(batch_texts):
                    print(f"  Warning: Expected {len(batch_texts)} translations but got {len(translations)}")
                    # Pad with original texts if translations are missing
                    while len(translations) < len(batch_texts):
                        translations.append(batch_texts[len(translations)])

                all_translations.extend(translations)
            except Exception as e:
                print(f"  Error translating batch: {e}")
                # Use original English text as fallback
                all_translations.extend(batch_texts)

        # Update the language file with translations
        for key, translation in zip(keys_list, all_translations):
            set_nested_value(lang_data, key, translation)

        # Save the updated file
        save_json_file(lang_file, lang_data)
        print(f"  ✓ Updated {lang_file}")

    print("\n" + "="*60)
    print("Translation complete!")
    print(f"Translated {len(grafana_keys)} keys to {len(LANGUAGES)} languages")
    print("="*60)

if __name__ == '__main__':
    main()
