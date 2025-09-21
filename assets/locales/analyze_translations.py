#!/usr/bin/env python3
"""
Translation Analysis Script for SysManage Docs
Analyzes all language files to identify missing translation keys compared to English reference.
"""

import json
import os
from typing import Dict, Set, Any
from collections import defaultdict

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten a nested dictionary into dot-notation keys."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def main():
    locales_dir = "/home/bceverly/dev/sysmanage-docs/assets/locales"

    # Load English reference
    en_path = os.path.join(locales_dir, "en.json")
    en_data = load_json_file(en_path)
    en_flat = flatten_dict(en_data)
    en_keys = set(en_flat.keys())

    print(f"English reference has {len(en_keys)} keys")
    print("=" * 80)

    # Language files to check
    language_files = [
        'fr.json', 'es.json', 'de.json', 'it.json', 'pt.json', 'nl.json',
        'ja.json', 'zh_CN.json', 'zh_TW.json', 'ko.json', 'ru.json', 'ar.json', 'hi.json'
    ]

    results = {}

    for lang_file in language_files:
        lang_path = os.path.join(locales_dir, lang_file)
        if not os.path.exists(lang_path):
            print(f"Warning: {lang_file} does not exist")
            continue

        lang_data = load_json_file(lang_path)
        lang_flat = flatten_dict(lang_data)
        lang_keys = set(lang_flat.keys())

        missing_keys = en_keys - lang_keys
        extra_keys = lang_keys - en_keys

        results[lang_file] = {
            'total_keys': len(lang_keys),
            'missing_keys': missing_keys,
            'extra_keys': extra_keys,
            'completion_rate': (len(lang_keys) / len(en_keys)) * 100 if en_keys else 0
        }

        print(f"\n{lang_file}:")
        print(f"  Total keys: {len(lang_keys)}")
        print(f"  Missing keys: {len(missing_keys)}")
        print(f"  Extra keys: {len(extra_keys)}")
        print(f"  Completion rate: {results[lang_file]['completion_rate']:.1f}%")

        if missing_keys:
            print("  First 10 missing keys:")
            for key in sorted(list(missing_keys))[:10]:
                print(f"    - {key}")
            if len(missing_keys) > 10:
                print(f"    ... and {len(missing_keys) - 10} more")

    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("=" * 80)

    # Show all missing server_docs keys for each language
    server_docs_missing = defaultdict(list)
    for lang_file, result in results.items():
        for key in result['missing_keys']:
            if key.startswith('server_docs.'):
                server_docs_missing[lang_file].append(key)

    print("\nMissing server_docs keys by language:")
    for lang_file, missing in server_docs_missing.items():
        if missing:
            print(f"\n{lang_file} missing {len(missing)} server_docs keys:")
            for key in sorted(missing)[:5]:  # Show first 5
                print(f"  - {key}")
            if len(missing) > 5:
                print(f"  ... and {len(missing) - 5} more")

    # Create comprehensive missing keys file
    all_missing_path = os.path.join(locales_dir, "missing_keys_analysis.json")
    missing_analysis = {}
    for lang_file, result in results.items():
        missing_analysis[lang_file] = {
            'completion_rate': result['completion_rate'],
            'missing_count': len(result['missing_keys']),
            'missing_keys': sorted(list(result['missing_keys']))
        }

    with open(all_missing_path, 'w', encoding='utf-8') as f:
        json.dump(missing_analysis, f, indent=2, ensure_ascii=False)

    print(f"\nDetailed analysis saved to: {all_missing_path}")

if __name__ == "__main__":
    main()