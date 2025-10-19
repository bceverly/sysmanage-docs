#!/usr/bin/env python3
"""Fix missing translation keys in all locale files."""

import json
from pathlib import Path

# Translation mappings for all supported languages
TRANSLATIONS = {
    "en": {
        "other": {
            "tab": "Other Platforms"
        },
        "method1": {
            "title": "Installation from Source",
            "desc": "For FreeBSD, OpenBSD, NetBSD, and other platforms, install manually from source:"
        }
    },
    "es": {
        "other": {
            "tab": "Otras Plataformas"
        },
        "method1": {
            "title": "Instalación desde el Código Fuente",
            "desc": "Para FreeBSD, OpenBSD, NetBSD y otras plataformas, instale manualmente desde el código fuente:"
        }
    },
    "fr": {
        "other": {
            "tab": "Autres Plateformes"
        },
        "method1": {
            "title": "Installation depuis le Code Source",
            "desc": "Pour FreeBSD, OpenBSD, NetBSD et d'autres plateformes, installez manuellement depuis le code source :"
        }
    },
    "de": {
        "other": {
            "tab": "Andere Plattformen"
        },
        "method1": {
            "title": "Installation aus dem Quellcode",
            "desc": "Für FreeBSD, OpenBSD, NetBSD und andere Plattformen installieren Sie manuell aus dem Quellcode:"
        }
    },
    "it": {
        "other": {
            "tab": "Altre Piattaforme"
        },
        "method1": {
            "title": "Installazione dal Codice Sorgente",
            "desc": "Per FreeBSD, OpenBSD, NetBSD e altre piattaforme, installare manualmente dal codice sorgente:"
        }
    },
    "pt": {
        "other": {
            "tab": "Outras Plataformas"
        },
        "method1": {
            "title": "Instalação do Código Fonte",
            "desc": "Para FreeBSD, OpenBSD, NetBSD e outras plataformas, instale manualmente do código fonte:"
        }
    },
    "nl": {
        "other": {
            "tab": "Andere Platforms"
        },
        "method1": {
            "title": "Installatie vanuit de Broncode",
            "desc": "Voor FreeBSD, OpenBSD, NetBSD en andere platforms, installeer handmatig vanuit de broncode:"
        }
    },
    "ja": {
        "other": {
            "tab": "その他のプラットフォーム"
        },
        "method1": {
            "title": "ソースからのインストール",
            "desc": "FreeBSD、OpenBSD、NetBSDおよびその他のプラットフォームの場合は、ソースから手動でインストールしてください："
        }
    },
    "zh_CN": {
        "other": {
            "tab": "其他平台"
        },
        "method1": {
            "title": "从源代码安装",
            "desc": "对于FreeBSD、OpenBSD、NetBSD和其他平台，请从源代码手动安装："
        }
    },
    "zh_TW": {
        "other": {
            "tab": "其他平台"
        },
        "method1": {
            "title": "從原始碼安裝",
            "desc": "對於FreeBSD、OpenBSD、NetBSD和其他平台，請從原始碼手動安裝："
        }
    },
    "ko": {
        "other": {
            "tab": "기타 플랫폼"
        },
        "method1": {
            "title": "소스에서 설치",
            "desc": "FreeBSD, OpenBSD, NetBSD 및 기타 플랫폼의 경우 소스에서 수동으로 설치하십시오:"
        }
    },
    "ru": {
        "other": {
            "tab": "Другие платформы"
        },
        "method1": {
            "title": "Установка из исходного кода",
            "desc": "Для FreeBSD, OpenBSD, NetBSD и других платформ установите вручную из исходного кода:"
        }
    },
    "ar": {
        "other": {
            "tab": "منصات أخرى"
        },
        "method1": {
            "title": "التثبيت من الكود المصدري",
            "desc": "لـ FreeBSD و OpenBSD و NetBSD والمنصات الأخرى، قم بالتثبيت يدويًا من الكود المصدري:"
        }
    },
    "hi": {
        "other": {
            "tab": "अन्य प्लेटफ़ॉर्म"
        },
        "method1": {
            "title": "स्रोत से स्थापना",
            "desc": "FreeBSD, OpenBSD, NetBSD और अन्य प्लेटफ़ॉर्म के लिए, स्रोत से मैन्युअल रूप से स्थापित करें:"
        }
    }
}

def fix_translations_in_file(lang_code, translations):
    """Add missing translation keys to a specific language file."""
    locale_dir = Path(__file__).parent
    file_path = locale_dir / f"{lang_code}.json"

    # Read existing translations
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Navigate to agent_installation.installation and add missing keys
    if 'agent_installation' not in data:
        print(f"Warning: agent_installation not found in {lang_code}.json")
        return

    if 'installation' not in data['agent_installation']:
        print(f"Warning: installation section not found in {lang_code}.json")
        return

    # Add missing translations
    data['agent_installation']['installation']['other'] = translations['other']
    data['agent_installation']['installation']['method1'] = translations['method1']

    # Write back with proper formatting
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Updated {lang_code}.json")

def main():
    """Fix missing translation keys in all language files."""
    print("Fixing missing translation keys in all locale files...\\n")

    for lang_code, translations in TRANSLATIONS.items():
        fix_translations_in_file(lang_code, translations)

    print("\\n[SUCCESS] All translations fixed successfully!")
    print("\\nFixed keys in languages:")
    for lang_code in TRANSLATIONS.keys():
        print(f"  - {lang_code}")

if __name__ == '__main__':
    main()
