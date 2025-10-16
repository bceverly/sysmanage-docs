#!/usr/bin/env python3
"""Add missing NetBSD prerequisite keys to all locale files."""

import json
from pathlib import Path

# Translation mappings for all supported languages
TRANSLATIONS = {
    "en": {
        "gcc14_required": "GCC 14 is required:",
        "gcc14_reason": "NetBSD's base system GCC 10.5 doesn't properly support C++17 features needed by grpcio and other packages. Installing GCC 14 ensures proper C++17 support.",
        "rust_required": "Rust is required:",
        "rust_reason": "The agent uses certificate-based authentication which requires cryptography support for security.",
        "profile_note": "Note:",
        "profile_note_text": "On BSD systems, use <code>. ~/.profile</code> instead of <code>source ~/.profile</code> to reload your shell environment."
    },
    "es": {
        "gcc14_required": "Se requiere GCC 14:",
        "gcc14_reason": "El GCC 10.5 del sistema base de NetBSD no soporta adecuadamente las características de C++17 necesarias para grpcio y otros paquetes. Instalar GCC 14 asegura el soporte adecuado de C++17.",
        "rust_required": "Se requiere Rust:",
        "rust_reason": "El agente utiliza autenticación basada en certificados que requiere soporte criptográfico para seguridad.",
        "profile_note": "Nota:",
        "profile_note_text": "En sistemas BSD, use <code>. ~/.profile</code> en lugar de <code>source ~/.profile</code> para recargar el entorno del shell."
    },
    "fr": {
        "gcc14_required": "GCC 14 est requis :",
        "gcc14_reason": "Le GCC 10.5 du système de base de NetBSD ne prend pas correctement en charge les fonctionnalités C++17 nécessaires pour grpcio et d'autres packages. L'installation de GCC 14 assure une prise en charge appropriée de C++17.",
        "rust_required": "Rust est requis :",
        "rust_reason": "L'agent utilise une authentification basée sur des certificats qui nécessite un support cryptographique pour la sécurité.",
        "profile_note": "Remarque :",
        "profile_note_text": "Sur les systèmes BSD, utilisez <code>. ~/.profile</code> au lieu de <code>source ~/.profile</code> pour recharger l'environnement du shell."
    },
    "de": {
        "gcc14_required": "GCC 14 ist erforderlich:",
        "gcc14_reason": "NetBSDs Basissystem GCC 10.5 unterstützt C++17-Funktionen, die für grpcio und andere Pakete benötigt werden, nicht ordnungsgemäß. Die Installation von GCC 14 gewährleistet ordnungsgemäße C++17-Unterstützung.",
        "rust_required": "Rust ist erforderlich:",
        "rust_reason": "Der Agent verwendet zertifikatbasierte Authentifizierung, die kryptographische Unterstützung für Sicherheit erfordert.",
        "profile_note": "Hinweis:",
        "profile_note_text": "Auf BSD-Systemen verwenden Sie <code>. ~/.profile</code> anstelle von <code>source ~/.profile</code>, um die Shell-Umgebung neu zu laden."
    },
    "it": {
        "gcc14_required": "È richiesto GCC 14:",
        "gcc14_reason": "Il GCC 10.5 del sistema base di NetBSD non supporta correttamente le funzionalità C++17 necessarie per grpcio e altri pacchetti. L'installazione di GCC 14 garantisce un supporto appropriato per C++17.",
        "rust_required": "È richiesto Rust:",
        "rust_reason": "L'agente utilizza l'autenticazione basata su certificati che richiede supporto crittografico per la sicurezza.",
        "profile_note": "Nota:",
        "profile_note_text": "Sui sistemi BSD, usa <code>. ~/.profile</code> invece di <code>source ~/.profile</code> per ricaricare l'ambiente della shell."
    },
    "pt": {
        "gcc14_required": "GCC 14 é necessário:",
        "gcc14_reason": "O GCC 10.5 do sistema base do NetBSD não suporta adequadamente os recursos C++17 necessários para grpcio e outros pacotes. Instalar o GCC 14 garante suporte adequado para C++17.",
        "rust_required": "Rust é necessário:",
        "rust_reason": "O agente usa autenticação baseada em certificado que requer suporte criptográfico para segurança.",
        "profile_note": "Nota:",
        "profile_note_text": "Em sistemas BSD, use <code>. ~/.profile</code> em vez de <code>source ~/.profile</code> para recarregar o ambiente do shell."
    },
    "nl": {
        "gcc14_required": "GCC 14 is vereist:",
        "gcc14_reason": "NetBSD's basissysteem GCC 10.5 ondersteunt C++17-functies die nodig zijn voor grpcio en andere pakketten niet correct. Het installeren van GCC 14 zorgt voor correcte C++17-ondersteuning.",
        "rust_required": "Rust is vereist:",
        "rust_reason": "De agent gebruikt certificaatgebaseerde authenticatie die cryptografische ondersteuning vereist voor beveiliging.",
        "profile_note": "Opmerking:",
        "profile_note_text": "Op BSD-systemen gebruik je <code>. ~/.profile</code> in plaats van <code>source ~/.profile</code> om de shell-omgeving opnieuw te laden."
    },
    "ja": {
        "gcc14_required": "GCC 14が必要です：",
        "gcc14_reason": "NetBSDのベースシステムGCC 10.5は、grpcioおよび他のパッケージに必要なC++17機能を適切にサポートしていません。GCC 14をインストールすると、適切なC++17サポートが確保されます。",
        "rust_required": "Rustが必要です：",
        "rust_reason": "エージェントは、セキュリティのために暗号化サポートを必要とする証明書ベースの認証を使用します。",
        "profile_note": "注意：",
        "profile_note_text": "BSDシステムでは、シェル環境をリロードするには<code>source ~/.profile</code>の代わりに<code>. ~/.profile</code>を使用してください。"
    },
    "zh_CN": {
        "gcc14_required": "需要 GCC 14：",
        "gcc14_reason": "NetBSD 的基础系统 GCC 10.5 不能正确支持 grpcio 和其他包所需的 C++17 功能。安装 GCC 14 可确保正确的 C++17 支持。",
        "rust_required": "需要 Rust：",
        "rust_reason": "代理使用基于证书的身份验证，需要加密支持以确保安全。",
        "profile_note": "注意：",
        "profile_note_text": "在 BSD 系统上，使用 <code>. ~/.profile</code> 而不是 <code>source ~/.profile</code> 来重新加载 shell 环境。"
    },
    "zh_TW": {
        "gcc14_required": "需要 GCC 14：",
        "gcc14_reason": "NetBSD 的基礎系統 GCC 10.5 不能正確支援 grpcio 和其他套件所需的 C++17 功能。安裝 GCC 14 可確保正確的 C++17 支援。",
        "rust_required": "需要 Rust：",
        "rust_reason": "代理程式使用基於憑證的身份驗證，需要加密支援以確保安全。",
        "profile_note": "注意：",
        "profile_note_text": "在 BSD 系統上，使用 <code>. ~/.profile</code> 而不是 <code>source ~/.profile</code> 來重新載入 shell 環境。"
    },
    "ko": {
        "gcc14_required": "GCC 14가 필요합니다:",
        "gcc14_reason": "NetBSD의 기본 시스템 GCC 10.5는 grpcio 및 기타 패키지에 필요한 C++17 기능을 제대로 지원하지 않습니다. GCC 14를 설치하면 적절한 C++17 지원이 보장됩니다.",
        "rust_required": "Rust가 필요합니다:",
        "rust_reason": "에이전트는 보안을 위해 암호화 지원이 필요한 인증서 기반 인증을 사용합니다.",
        "profile_note": "참고:",
        "profile_note_text": "BSD 시스템에서는 셸 환경을 다시 로드하려면 <code>source ~/.profile</code> 대신 <code>. ~/.profile</code>을 사용하세요."
    },
    "ru": {
        "gcc14_required": "Требуется GCC 14:",
        "gcc14_reason": "Базовый системный GCC 10.5 NetBSD не поддерживает должным образом функции C++17, необходимые для grpcio и других пакетов. Установка GCC 14 обеспечивает надлежащую поддержку C++17.",
        "rust_required": "Требуется Rust:",
        "rust_reason": "Агент использует аутентификацию на основе сертификатов, которая требует криптографической поддержки для безопасности.",
        "profile_note": "Примечание:",
        "profile_note_text": "В системах BSD используйте <code>. ~/.profile</code> вместо <code>source ~/.profile</code> для перезагрузки окружения оболочки."
    },
    "ar": {
        "gcc14_required": "مطلوب GCC 14:",
        "gcc14_reason": "لا يدعم GCC 10.5 لنظام NetBSD الأساسي ميزات C++17 المطلوبة لـ grpcio والحزم الأخرى بشكل صحيح. يضمن تثبيت GCC 14 الدعم الصحيح لـ C++17.",
        "rust_required": "مطلوب Rust:",
        "rust_reason": "يستخدم الوكيل المصادقة القائمة على الشهادات التي تتطلب دعم التشفير للأمان.",
        "profile_note": "ملاحظة:",
        "profile_note_text": "في أنظمة BSD، استخدم <code>. ~/.profile</code> بدلاً من <code>source ~/.profile</code> لإعادة تحميل بيئة الshell."
    },
    "hi": {
        "gcc14_required": "GCC 14 आवश्यक है:",
        "gcc14_reason": "NetBSD की बेस सिस्टम GCC 10.5 grpcio और अन्य पैकेज के लिए आवश्यक C++17 सुविधाओं का ठीक से समर्थन नहीं करता। GCC 14 स्थापित करने से उचित C++17 समर्थन सुनिश्चित होता है।",
        "rust_required": "Rust आवश्यक है:",
        "rust_reason": "एजेंट प्रमाणपत्र-आधारित प्रमाणीकरण का उपयोग करता है जिसे सुरक्षा के लिए क्रिप्टोग्राफी समर्थन की आवश्यकता होती है।",
        "profile_note": "नोट:",
        "profile_note_text": "BSD सिस्टम पर, शेल वातावरण को पुनः लोड करने के लिए <code>source ~/.profile</code> के बजाय <code>. ~/.profile</code> का उपयोग करें।"
    }
}

def add_netbsd_keys(lang_code, translations):
    """Add NetBSD prerequisite keys to a specific language file."""
    locale_dir = Path(__file__).parent
    file_path = locale_dir / f"{lang_code}.json"

    if not file_path.exists():
        print(f"Warning: {lang_code}.json not found, skipping")
        return

    # Read existing translations
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Navigate to agent_installation.prerequisites.netbsd
    if 'agent_installation' not in data:
        print(f"Warning: agent_installation not found in {lang_code}.json, skipping")
        return

    if 'prerequisites' not in data['agent_installation']:
        print(f"Warning: prerequisites section not found in {lang_code}.json, skipping")
        return

    if 'netbsd' not in data['agent_installation']['prerequisites']:
        print(f"Warning: netbsd section not found in {lang_code}.json, skipping")
        return

    # Add the missing keys
    for key, value in translations.items():
        data['agent_installation']['prerequisites']['netbsd'][key] = value

    # Write back with proper formatting
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Updated {lang_code}.json with NetBSD keys")

def main():
    """Add NetBSD prerequisite keys to all language files."""
    print("Adding missing NetBSD prerequisite keys to all locale files...\n")

    for lang_code, translations in TRANSLATIONS.items():
        add_netbsd_keys(lang_code, translations)

    print("\n✅ All NetBSD keys added successfully!")
    print("\nTranslations updated for languages:")
    for lang_code in TRANSLATIONS.keys():
        print(f"  - {lang_code}")

if __name__ == '__main__':
    main()
