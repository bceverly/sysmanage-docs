#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Add zypper (openSUSE and SLES) installation translations to all locale files."""

import json
from pathlib import Path

# Translation mappings for all supported languages
TRANSLATIONS = {
    "es": {  # Spanish
        "zypper_opensuse": {
            "title": "📦 Repositorio Zypper (openSUSE - Recomendado)",
            "supported": "Plataformas soportadas:",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11 (2021+)",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+ (Rolling)",
            "platforms_note": "El paquete incluye todas las dependencias de Python en un virtualenv autónomo.",
            "quick_start_leap": "Instalación Rápida - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "Instalación Rápida - openSUSE Tumbleweed",
            "benefits_title": "✨ Beneficios de la Instalación Zypper",
            "automatic": "Actualizaciones Automáticas:",
            "automatic_desc": "Obtenga nuevas versiones a través de zypper update estándar",
            "dependencies": "Gestión de Dependencias:",
            "dependencies_desc": "Todas las dependencias de Python incluidas en el paquete",
            "systemd": "Integración con Systemd:",
            "systemd_desc": "Servicio configurado y habilitado automáticamente",
            "isolation": "Entorno Aislado:",
            "isolation_desc": "No entra en conflicto con paquetes Python del sistema",
            "version_management": "🔄 Gestión de Versiones",
            "uninstall": "🗑️ Desinstalación"
        },
        "zypper_sles": {
            "title": "📦 Repositorio Zypper (SLES - Recomendado)",
            "supported": "Plataformas soportadas:",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11 (2018+)",
            "platforms_note": "El paquete incluye todas las dependencias de Python en un virtualenv autónomo.",
            "quick_start": "Instalación Rápida - SLES 15",
            "benefits_title": "✨ Beneficios de la Instalación Zypper",
            "automatic": "Actualizaciones Automáticas:",
            "automatic_desc": "Obtenga nuevas versiones a través de zypper update estándar",
            "dependencies": "Gestión de Dependencias:",
            "dependencies_desc": "Todas las dependencias de Python incluidas en el paquete",
            "systemd": "Integración con Systemd:",
            "systemd_desc": "Servicio configurado y habilitado automáticamente",
            "enterprise": "Soporte Empresarial:",
            "enterprise_desc": "Listo para producción en entornos empresariales SUSE",
            "version_management": "🔄 Gestión de Versiones",
            "uninstall": "🗑️ Desinstalación",
            "enterprise_note": "🏢 Consideraciones Empresariales",
            "subscription": "Suscripción:",
            "subscription_desc": "SLES requiere una suscripción activa para actualizaciones del sistema",
            "firewall": "Firewall:",
            "firewall_desc": "Configure SuSEfirewall2 o firewalld para HTTPS saliente",
            "apparmor": "AppArmor:",
            "apparmor_desc": "Puede requerir ajustes de perfil si se usa AppArmor"
        }
    },
    "fr": {  # French
        "zypper_opensuse": {
            "title": "📦 Dépôt Zypper (openSUSE - Recommandé)",
            "supported": "Plateformes prises en charge :",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11 (2021+)",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+ (Rolling)",
            "platforms_note": "Le paquet inclut toutes les dépendances Python dans un virtualenv autonome.",
            "quick_start_leap": "Installation Rapide - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "Installation Rapide - openSUSE Tumbleweed",
            "benefits_title": "✨ Avantages de l'Installation Zypper",
            "automatic": "Mises à Jour Automatiques :",
            "automatic_desc": "Obtenez de nouvelles versions via zypper update standard",
            "dependencies": "Gestion des Dépendances :",
            "dependencies_desc": "Toutes les dépendances Python incluses dans le paquet",
            "systemd": "Intégration Systemd :",
            "systemd_desc": "Service automatiquement configuré et activé",
            "isolation": "Environnement Isolé :",
            "isolation_desc": "N'entre pas en conflit avec les paquets Python système",
            "version_management": "🔄 Gestion des Versions",
            "uninstall": "🗑️ Désinstallation"
        },
        "zypper_sles": {
            "title": "📦 Dépôt Zypper (SLES - Recommandé)",
            "supported": "Plateformes prises en charge :",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11 (2018+)",
            "platforms_note": "Le paquet inclut toutes les dépendances Python dans un virtualenv autonome.",
            "quick_start": "Installation Rapide - SLES 15",
            "benefits_title": "✨ Avantages de l'Installation Zypper",
            "automatic": "Mises à Jour Automatiques :",
            "automatic_desc": "Obtenez de nouvelles versions via zypper update standard",
            "dependencies": "Gestion des Dépendances :",
            "dependencies_desc": "Toutes les dépendances Python incluses dans le paquet",
            "systemd": "Intégration Systemd :",
            "systemd_desc": "Service automatiquement configuré et activé",
            "enterprise": "Support Entreprise :",
            "enterprise_desc": "Prêt pour la production dans les environnements d'entreprise SUSE",
            "version_management": "🔄 Gestion des Versions",
            "uninstall": "🗑️ Désinstallation",
            "enterprise_note": "🏢 Considérations d'Entreprise",
            "subscription": "Abonnement :",
            "subscription_desc": "SLES nécessite un abonnement actif pour les mises à jour système",
            "firewall": "Pare-feu :",
            "firewall_desc": "Configurez SuSEfirewall2 ou firewalld pour HTTPS sortant",
            "apparmor": "AppArmor :",
            "apparmor_desc": "Peut nécessiter des ajustements de profil si AppArmor est utilisé"
        }
    },
    "de": {  # German
        "zypper_opensuse": {
            "title": "📦 Zypper-Repository (openSUSE - Empfohlen)",
            "supported": "Unterstützte Plattformen:",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11 (2021+)",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+ (Rolling)",
            "platforms_note": "Das Paket enthält alle Python-Abhängigkeiten in einer eigenständigen virtualenv.",
            "quick_start_leap": "Schnellinstallation - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "Schnellinstallation - openSUSE Tumbleweed",
            "benefits_title": "✨ Vorteile der Zypper-Installation",
            "automatic": "Automatische Updates:",
            "automatic_desc": "Neue Versionen über standard zypper update erhalten",
            "dependencies": "Abhängigkeitsverwaltung:",
            "dependencies_desc": "Alle Python-Abhängigkeiten im Paket enthalten",
            "systemd": "Systemd-Integration:",
            "systemd_desc": "Service automatisch konfiguriert und aktiviert",
            "isolation": "Isolierte Umgebung:",
            "isolation_desc": "Keine Konflikte mit System-Python-Paketen",
            "version_management": "🔄 Versionsverwaltung",
            "uninstall": "🗑️ Deinstallation"
        },
        "zypper_sles": {
            "title": "📦 Zypper-Repository (SLES - Empfohlen)",
            "supported": "Unterstützte Plattformen:",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11 (2018+)",
            "platforms_note": "Das Paket enthält alle Python-Abhängigkeiten in einer eigenständigen virtualenv.",
            "quick_start": "Schnellinstallation - SLES 15",
            "benefits_title": "✨ Vorteile der Zypper-Installation",
            "automatic": "Automatische Updates:",
            "automatic_desc": "Neue Versionen über standard zypper update erhalten",
            "dependencies": "Abhängigkeitsverwaltung:",
            "dependencies_desc": "Alle Python-Abhängigkeiten im Paket enthalten",
            "systemd": "Systemd-Integration:",
            "systemd_desc": "Service automatisch konfiguriert und aktiviert",
            "enterprise": "Unternehmensunterstützung:",
            "enterprise_desc": "Produktionsbereit für SUSE-Unternehmensumgebungen",
            "version_management": "🔄 Versionsverwaltung",
            "uninstall": "🗑️ Deinstallation",
            "enterprise_note": "🏢 Unternehmensüberlegungen",
            "subscription": "Abonnement:",
            "subscription_desc": "SLES benötigt ein aktives Abonnement für System-Updates",
            "firewall": "Firewall:",
            "firewall_desc": "SuSEfirewall2 oder firewalld für ausgehende HTTPS konfigurieren",
            "apparmor": "AppArmor:",
            "apparmor_desc": "Kann Profilanpassungen erfordern, wenn AppArmor verwendet wird"
        }
    },
    "it": {  # Italian
        "zypper_opensuse": {
            "title": "📦 Repository Zypper (openSUSE - Consigliato)",
            "supported": "Piattaforme supportate:",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11 (2021+)",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+ (Rolling)",
            "platforms_note": "Il pacchetto include tutte le dipendenze Python in un virtualenv autonomo.",
            "quick_start_leap": "Installazione Rapida - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "Installazione Rapida - openSUSE Tumbleweed",
            "benefits_title": "✨ Vantaggi dell'Installazione Zypper",
            "automatic": "Aggiornamenti Automatici:",
            "automatic_desc": "Ottieni nuove versioni tramite zypper update standard",
            "dependencies": "Gestione delle Dipendenze:",
            "dependencies_desc": "Tutte le dipendenze Python incluse nel pacchetto",
            "systemd": "Integrazione Systemd:",
            "systemd_desc": "Servizio configurato e abilitato automaticamente",
            "isolation": "Ambiente Isolato:",
            "isolation_desc": "Non entra in conflitto con i pacchetti Python di sistema",
            "version_management": "🔄 Gestione delle Versioni",
            "uninstall": "🗑️ Disinstallazione"
        },
        "zypper_sles": {
            "title": "📦 Repository Zypper (SLES - Consigliato)",
            "supported": "Piattaforme supportate:",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11 (2018+)",
            "platforms_note": "Il pacchetto include tutte le dipendenze Python in un virtualenv autonomo.",
            "quick_start": "Installazione Rapida - SLES 15",
            "benefits_title": "✨ Vantaggi dell'Installazione Zypper",
            "automatic": "Aggiornamenti Automatici:",
            "automatic_desc": "Ottieni nuove versioni tramite zypper update standard",
            "dependencies": "Gestione delle Dipendenze:",
            "dependencies_desc": "Tutte le dipendenze Python incluse nel pacchetto",
            "systemd": "Integrazione Systemd:",
            "systemd_desc": "Servizio configurato e abilitato automaticamente",
            "enterprise": "Supporto Aziendale:",
            "enterprise_desc": "Pronto per la produzione in ambienti aziendali SUSE",
            "version_management": "🔄 Gestione delle Versioni",
            "uninstall": "🗑️ Disinstallazione",
            "enterprise_note": "🏢 Considerazioni Aziendali",
            "subscription": "Abbonamento:",
            "subscription_desc": "SLES richiede un abbonamento attivo per gli aggiornamenti del sistema",
            "firewall": "Firewall:",
            "firewall_desc": "Configurare SuSEfirewall2 o firewalld per HTTPS in uscita",
            "apparmor": "AppArmor:",
            "apparmor_desc": "Può richiedere regolazioni del profilo se si usa AppArmor"
        }
    },
    "pt": {  # Portuguese
        "zypper_opensuse": {
            "title": "📦 Repositório Zypper (openSUSE - Recomendado)",
            "supported": "Plataformas suportadas:",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11 (2021+)",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+ (Rolling)",
            "platforms_note": "O pacote inclui todas as dependências Python em um virtualenv autônomo.",
            "quick_start_leap": "Instalação Rápida - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "Instalação Rápida - openSUSE Tumbleweed",
            "benefits_title": "✨ Benefícios da Instalação Zypper",
            "automatic": "Atualizações Automáticas:",
            "automatic_desc": "Obtenha novas versões via zypper update padrão",
            "dependencies": "Gerenciamento de Dependências:",
            "dependencies_desc": "Todas as dependências Python incluídas no pacote",
            "systemd": "Integração Systemd:",
            "systemd_desc": "Serviço configurado e habilitado automaticamente",
            "isolation": "Ambiente Isolado:",
            "isolation_desc": "Não entra em conflito com pacotes Python do sistema",
            "version_management": "🔄 Gerenciamento de Versões",
            "uninstall": "🗑️ Desinstalação"
        },
        "zypper_sles": {
            "title": "📦 Repositório Zypper (SLES - Recomendado)",
            "supported": "Plataformas suportadas:",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11 (2018+)",
            "platforms_note": "O pacote inclui todas as dependências Python em um virtualenv autônomo.",
            "quick_start": "Instalação Rápida - SLES 15",
            "benefits_title": "✨ Benefícios da Instalação Zypper",
            "automatic": "Atualizações Automáticas:",
            "automatic_desc": "Obtenha novas versões via zypper update padrão",
            "dependencies": "Gerenciamento de Dependências:",
            "dependencies_desc": "Todas as dependências Python incluídas no pacote",
            "systemd": "Integração Systemd:",
            "systemd_desc": "Serviço configurado e habilitado automaticamente",
            "enterprise": "Suporte Empresarial:",
            "enterprise_desc": "Pronto para produção em ambientes empresariais SUSE",
            "version_management": "🔄 Gerenciamento de Versões",
            "uninstall": "🗑️ Desinstalação",
            "enterprise_note": "🏢 Considerações Empresariais",
            "subscription": "Assinatura:",
            "subscription_desc": "SLES requer uma assinatura ativa para atualizações do sistema",
            "firewall": "Firewall:",
            "firewall_desc": "Configure SuSEfirewall2 ou firewalld para HTTPS de saída",
            "apparmor": "AppArmor:",
            "apparmor_desc": "Pode exigir ajustes de perfil se estiver usando AppArmor"
        }
    },
    "nl": {  # Dutch
        "zypper_opensuse": {
            "title": "📦 Zypper Repository (openSUSE - Aanbevolen)",
            "supported": "Ondersteunde platforms:",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11 (2021+)",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+ (Rolling)",
            "platforms_note": "Het pakket bevat alle Python-afhankelijkheden in een zelfstandige virtualenv.",
            "quick_start_leap": "Snelle Installatie - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "Snelle Installatie - openSUSE Tumbleweed",
            "benefits_title": "✨ Voordelen van Zypper-installatie",
            "automatic": "Automatische Updates:",
            "automatic_desc": "Nieuwe versies verkrijgen via standaard zypper update",
            "dependencies": "Beheer van Afhankelijkheden:",
            "dependencies_desc": "Alle Python-afhankelijkheden inbegrepen in pakket",
            "systemd": "Systemd-integratie:",
            "systemd_desc": "Service automatisch geconfigureerd en ingeschakeld",
            "isolation": "Geïsoleerde Omgeving:",
            "isolation_desc": "Conflicteert niet met systeem Python-pakketten",
            "version_management": "🔄 Versiebeheer",
            "uninstall": "🗑️ Verwijderen"
        },
        "zypper_sles": {
            "title": "📦 Zypper Repository (SLES - Aanbevolen)",
            "supported": "Ondersteunde platforms:",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11 (2018+)",
            "platforms_note": "Het pakket bevat alle Python-afhankelijkheden in een zelfstandige virtualenv.",
            "quick_start": "Snelle Installatie - SLES 15",
            "benefits_title": "✨ Voordelen van Zypper-installatie",
            "automatic": "Automatische Updates:",
            "automatic_desc": "Nieuwe versies verkrijgen via standaard zypper update",
            "dependencies": "Beheer van Afhankelijkheden:",
            "dependencies_desc": "Alle Python-afhankelijkheden inbegrepen in pakket",
            "systemd": "Systemd-integratie:",
            "systemd_desc": "Service automatisch geconfigureerd en ingeschakeld",
            "enterprise": "Bedrijfsondersteuning:",
            "enterprise_desc": "Productierijp voor SUSE-bedrijfsomgevingen",
            "version_management": "🔄 Versiebeheer",
            "uninstall": "🗑️ Verwijderen",
            "enterprise_note": "🏢 Bedrijfsoverwegingen",
            "subscription": "Abonnement:",
            "subscription_desc": "SLES vereist een actief abonnement voor systeemupdates",
            "firewall": "Firewall:",
            "firewall_desc": "Configureer SuSEfirewall2 of firewalld voor uitgaande HTTPS",
            "apparmor": "AppArmor:",
            "apparmor_desc": "Kan profielaanpassingen vereisen bij gebruik van AppArmor"
        }
    },
    "ja": {  # Japanese
        "zypper_opensuse": {
            "title": "📦 Zypperリポジトリ（openSUSE - 推奨）",
            "supported": "サポートされているプラットフォーム：",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11（2021+）",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+（ローリング）",
            "platforms_note": "パッケージには、自己完結型のvirtualenv内にすべてのPython依存関係が含まれています。",
            "quick_start_leap": "クイックインストール - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "クイックインストール - openSUSE Tumbleweed",
            "benefits_title": "✨ Zypperインストールの利点",
            "automatic": "自動更新：",
            "automatic_desc": "標準zypper updateで新しいバージョンを取得",
            "dependencies": "依存関係の管理：",
            "dependencies_desc": "すべてのPython依存関係がパッケージに含まれています",
            "systemd": "Systemd統合：",
            "systemd_desc": "サービスが自動的に構成され有効化されます",
            "isolation": "分離環境：",
            "isolation_desc": "システムPythonパッケージと競合しません",
            "version_management": "🔄 バージョン管理",
            "uninstall": "🗑️ アンインストール"
        },
        "zypper_sles": {
            "title": "📦 Zypperリポジトリ（SLES - 推奨）",
            "supported": "サポートされているプラットフォーム：",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11（2018+）",
            "platforms_note": "パッケージには、自己完結型のvirtualenv内にすべてのPython依存関係が含まれています。",
            "quick_start": "クイックインストール - SLES 15",
            "benefits_title": "✨ Zypperインストールの利点",
            "automatic": "自動更新：",
            "automatic_desc": "標準zypper updateで新しいバージョンを取得",
            "dependencies": "依存関係の管理：",
            "dependencies_desc": "すべてのPython依存関係がパッケージに含まれています",
            "systemd": "Systemd統合：",
            "systemd_desc": "サービスが自動的に構成され有効化されます",
            "enterprise": "エンタープライズサポート：",
            "enterprise_desc": "SUSEエンタープライズ環境で本番環境に対応",
            "version_management": "🔄 バージョン管理",
            "uninstall": "🗑️ アンインストール",
            "enterprise_note": "🏢 エンタープライズに関する考慮事項",
            "subscription": "サブスクリプション：",
            "subscription_desc": "SLESはシステム更新のためにアクティブなサブスクリプションが必要です",
            "firewall": "ファイアウォール：",
            "firewall_desc": "送信HTTPSのためにSuSEfirewall2またはfirewalldを設定します",
            "apparmor": "AppArmor：",
            "apparmor_desc": "AppArmorを使用している場合、プロファイルの調整が必要な場合があります"
        }
    },
    "zh_CN": {  # Simplified Chinese
        "zypper_opensuse": {
            "title": "📦 Zypper仓库（openSUSE - 推荐）",
            "supported": "支持的平台：",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11（2021+）",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+（滚动发行）",
            "platforms_note": "软件包在自包含的virtualenv中包含所有Python依赖项。",
            "quick_start_leap": "快速安装 - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "快速安装 - openSUSE Tumbleweed",
            "benefits_title": "✨ Zypper安装的优势",
            "automatic": "自动更新：",
            "automatic_desc": "通过标准zypper update获取新版本",
            "dependencies": "依赖项管理：",
            "dependencies_desc": "软件包中包含所有Python依赖项",
            "systemd": "Systemd集成：",
            "systemd_desc": "服务自动配置和启用",
            "isolation": "隔离环境：",
            "isolation_desc": "不与系统Python包冲突",
            "version_management": "🔄 版本管理",
            "uninstall": "🗑️ 卸载"
        },
        "zypper_sles": {
            "title": "📦 Zypper仓库（SLES - 推荐）",
            "supported": "支持的平台：",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11（2018+）",
            "platforms_note": "软件包在自包含的virtualenv中包含所有Python依赖项。",
            "quick_start": "快速安装 - SLES 15",
            "benefits_title": "✨ Zypper安装的优势",
            "automatic": "自动更新：",
            "automatic_desc": "通过标准zypper update获取新版本",
            "dependencies": "依赖项管理：",
            "dependencies_desc": "软件包中包含所有Python依赖项",
            "systemd": "Systemd集成：",
            "systemd_desc": "服务自动配置和启用",
            "enterprise": "企业支持：",
            "enterprise_desc": "适用于SUSE企业环境的生产就绪",
            "version_management": "🔄 版本管理",
            "uninstall": "🗑️ 卸载",
            "enterprise_note": "🏢 企业考虑事项",
            "subscription": "订阅：",
            "subscription_desc": "SLES需要有效订阅才能进行系统更新",
            "firewall": "防火墙：",
            "firewall_desc": "为出站HTTPS配置SuSEfirewall2或firewalld",
            "apparmor": "AppArmor：",
            "apparmor_desc": "如果使用AppArmor，可能需要调整配置文件"
        }
    },
    "zh_TW": {  # Traditional Chinese
        "zypper_opensuse": {
            "title": "📦 Zypper儲存庫（openSUSE - 推薦）",
            "supported": "支援的平台：",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11（2021+）",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+（滾動發行）",
            "platforms_note": "套件在自包含的virtualenv中包含所有Python相依性。",
            "quick_start_leap": "快速安裝 - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "快速安裝 - openSUSE Tumbleweed",
            "benefits_title": "✨ Zypper安裝的優勢",
            "automatic": "自動更新：",
            "automatic_desc": "透過標準zypper update獲取新版本",
            "dependencies": "相依性管理：",
            "dependencies_desc": "套件中包含所有Python相依性",
            "systemd": "Systemd整合：",
            "systemd_desc": "服務自動配置和啟用",
            "isolation": "隔離環境：",
            "isolation_desc": "不與系統Python套件衝突",
            "version_management": "🔄 版本管理",
            "uninstall": "🗑️ 解除安裝"
        },
        "zypper_sles": {
            "title": "📦 Zypper儲存庫（SLES - 推薦）",
            "supported": "支援的平台：",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11（2018+）",
            "platforms_note": "套件在自包含的virtualenv中包含所有Python相依性。",
            "quick_start": "快速安裝 - SLES 15",
            "benefits_title": "✨ Zypper安裝的優勢",
            "automatic": "自動更新：",
            "automatic_desc": "透過標準zypper update獲取新版本",
            "dependencies": "相依性管理：",
            "dependencies_desc": "套件中包含所有Python相依性",
            "systemd": "Systemd整合：",
            "systemd_desc": "服務自動配置和啟用",
            "enterprise": "企業支援：",
            "enterprise_desc": "適用於SUSE企業環境的生產就緒",
            "version_management": "🔄 版本管理",
            "uninstall": "🗑️ 解除安裝",
            "enterprise_note": "🏢 企業考量",
            "subscription": "訂閱：",
            "subscription_desc": "SLES需要有效訂閱才能進行系統更新",
            "firewall": "防火牆：",
            "firewall_desc": "為出站HTTPS配置SuSEfirewall2或firewalld",
            "apparmor": "AppArmor：",
            "apparmor_desc": "如果使用AppArmor，可能需要調整設定檔"
        }
    },
    "ko": {  # Korean
        "zypper_opensuse": {
            "title": "📦 Zypper 저장소 (openSUSE - 권장)",
            "supported": "지원되는 플랫폼:",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11 (2021+)",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+ (롤링)",
            "platforms_note": "패키지는 자체 포함 virtualenv에 모든 Python 종속성을 포함합니다.",
            "quick_start_leap": "빠른 설치 - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "빠른 설치 - openSUSE Tumbleweed",
            "benefits_title": "✨ Zypper 설치의 이점",
            "automatic": "자동 업데이트:",
            "automatic_desc": "표준 zypper update를 통해 새 버전 받기",
            "dependencies": "종속성 관리:",
            "dependencies_desc": "패키지에 모든 Python 종속성 포함",
            "systemd": "Systemd 통합:",
            "systemd_desc": "서비스가 자동으로 구성되고 활성화됨",
            "isolation": "격리된 환경:",
            "isolation_desc": "시스템 Python 패키지와 충돌하지 않음",
            "version_management": "🔄 버전 관리",
            "uninstall": "🗑️ 제거"
        },
        "zypper_sles": {
            "title": "📦 Zypper 저장소 (SLES - 권장)",
            "supported": "지원되는 플랫폼:",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11 (2018+)",
            "platforms_note": "패키지는 자체 포함 virtualenv에 모든 Python 종속성을 포함합니다.",
            "quick_start": "빠른 설치 - SLES 15",
            "benefits_title": "✨ Zypper 설치의 이점",
            "automatic": "자동 업데이트:",
            "automatic_desc": "표준 zypper update를 통해 새 버전 받기",
            "dependencies": "종속성 관리:",
            "dependencies_desc": "패키지에 모든 Python 종속성 포함",
            "systemd": "Systemd 통합:",
            "systemd_desc": "서비스가 자동으로 구성되고 활성화됨",
            "enterprise": "엔터프라이즈 지원:",
            "enterprise_desc": "SUSE 엔터프라이즈 환경을 위한 프로덕션 준비 완료",
            "version_management": "🔄 버전 관리",
            "uninstall": "🗑️ 제거",
            "enterprise_note": "🏢 엔터프라이즈 고려 사항",
            "subscription": "구독:",
            "subscription_desc": "SLES는 시스템 업데이트를 위해 활성 구독이 필요합니다",
            "firewall": "방화벽:",
            "firewall_desc": "아웃바운드 HTTPS를 위해 SuSEfirewall2 또는 firewalld 구성",
            "apparmor": "AppArmor:",
            "apparmor_desc": "AppArmor를 사용하는 경우 프로필 조정이 필요할 수 있습니다"
        }
    },
    "ru": {  # Russian
        "zypper_opensuse": {
            "title": "📦 Репозиторий Zypper (openSUSE - Рекомендуется)",
            "supported": "Поддерживаемые платформы:",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11 (2021+)",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+ (Rolling)",
            "platforms_note": "Пакет включает все зависимости Python в автономной virtualenv.",
            "quick_start_leap": "Быстрая установка - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "Быстрая установка - openSUSE Tumbleweed",
            "benefits_title": "✨ Преимущества установки Zypper",
            "automatic": "Автоматические обновления:",
            "automatic_desc": "Получайте новые версии через стандартный zypper update",
            "dependencies": "Управление зависимостями:",
            "dependencies_desc": "Все зависимости Python включены в пакет",
            "systemd": "Интеграция Systemd:",
            "systemd_desc": "Служба автоматически настраивается и включается",
            "isolation": "Изолированная среда:",
            "isolation_desc": "Не конфликтует с системными пакетами Python",
            "version_management": "🔄 Управление версиями",
            "uninstall": "🗑️ Удаление"
        },
        "zypper_sles": {
            "title": "📦 Репозиторий Zypper (SLES - Рекомендуется)",
            "supported": "Поддерживаемые платформы:",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11 (2018+)",
            "platforms_note": "Пакет включает все зависимости Python в автономной virtualenv.",
            "quick_start": "Быстрая установка - SLES 15",
            "benefits_title": "✨ Преимущества установки Zypper",
            "automatic": "Автоматические обновления:",
            "automatic_desc": "Получайте новые версии через стандартный zypper update",
            "dependencies": "Управление зависимостями:",
            "dependencies_desc": "Все зависимости Python включены в пакет",
            "systemd": "Интеграция Systemd:",
            "systemd_desc": "Служба автоматически настраивается и включается",
            "enterprise": "Корпоративная поддержка:",
            "enterprise_desc": "Готов к производству в корпоративных средах SUSE",
            "version_management": "🔄 Управление версиями",
            "uninstall": "🗑️ Удаление",
            "enterprise_note": "🏢 Корпоративные соображения",
            "subscription": "Подписка:",
            "subscription_desc": "SLES требует активную подписку для обновлений системы",
            "firewall": "Брандмауэр:",
            "firewall_desc": "Настройте SuSEfirewall2 или firewalld для исходящего HTTPS",
            "apparmor": "AppArmor:",
            "apparmor_desc": "Может потребоваться настройка профиля при использовании AppArmor"
        }
    },
    "ar": {  # Arabic
        "zypper_opensuse": {
            "title": "📦 مستودع Zypper (openSUSE - موصى به)",
            "supported": "المنصات المدعومة:",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11 (2021+)",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+ (متداول)",
            "platforms_note": "تتضمن الحزمة جميع تبعيات Python في virtualenv مستقلة.",
            "quick_start_leap": "التثبيت السريع - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "التثبيت السريع - openSUSE Tumbleweed",
            "benefits_title": "✨ فوائد تثبيت Zypper",
            "automatic": "التحديثات التلقائية:",
            "automatic_desc": "احصل على إصدارات جديدة عبر zypper update القياسي",
            "dependencies": "إدارة التبعيات:",
            "dependencies_desc": "جميع تبعيات Python مضمنة في الحزمة",
            "systemd": "تكامل Systemd:",
            "systemd_desc": "يتم تكوين الخدمة وتمكينها تلقائيًا",
            "isolation": "بيئة معزولة:",
            "isolation_desc": "لا يتعارض مع حزم Python النظام",
            "version_management": "🔄 إدارة الإصدارات",
            "uninstall": "🗑️ إلغاء التثبيت"
        },
        "zypper_sles": {
            "title": "📦 مستودع Zypper (SLES - موصى به)",
            "supported": "المنصات المدعومة:",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11 (2018+)",
            "platforms_note": "تتضمن الحزمة جميع تبعيات Python في virtualenv مستقلة.",
            "quick_start": "التثبيت السريع - SLES 15",
            "benefits_title": "✨ فوائد تثبيت Zypper",
            "automatic": "التحديثات التلقائية:",
            "automatic_desc": "احصل على إصدارات جديدة عبر zypper update القياسي",
            "dependencies": "إدارة التبعيات:",
            "dependencies_desc": "جميع تبعيات Python مضمنة في الحزمة",
            "systemd": "تكامل Systemd:",
            "systemd_desc": "يتم تكوين الخدمة وتمكينها تلقائيًا",
            "enterprise": "الدعم المؤسسي:",
            "enterprise_desc": "جاهز للإنتاج في بيئات SUSE المؤسسية",
            "version_management": "🔄 إدارة الإصدارات",
            "uninstall": "🗑️ إلغاء التثبيت",
            "enterprise_note": "🏢 الاعتبارات المؤسسية",
            "subscription": "الاشتراك:",
            "subscription_desc": "يتطلب SLES اشتراكًا نشطًا لتحديثات النظام",
            "firewall": "جدار الحماية:",
            "firewall_desc": "قم بتكوين SuSEfirewall2 أو firewalld لـ HTTPS الصادر",
            "apparmor": "AppArmor:",
            "apparmor_desc": "قد يتطلب تعديلات الملف الشخصي إذا كنت تستخدم AppArmor"
        }
    },
    "hi": {  # Hindi
        "zypper_opensuse": {
            "title": "📦 Zypper रिपॉजिटरी (openSUSE - अनुशंसित)",
            "supported": "समर्थित प्लेटफ़ॉर्म:",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11 (2021+)",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+ (रोलिंग)",
            "platforms_note": "पैकेज में एक स्व-निहित virtualenv में सभी Python निर्भरताएं शामिल हैं।",
            "quick_start_leap": "त्वरित स्थापना - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "त्वरित स्थापना - openSUSE Tumbleweed",
            "benefits_title": "✨ Zypper स्थापना के लाभ",
            "automatic": "स्वचालित अपडेट:",
            "automatic_desc": "मानक zypper update के माध्यम से नए संस्करण प्राप्त करें",
            "dependencies": "निर्भरता प्रबंधन:",
            "dependencies_desc": "पैकेज में सभी Python निर्भरताएं शामिल हैं",
            "systemd": "Systemd एकीकरण:",
            "systemd_desc": "सेवा स्वचालित रूप से कॉन्फ़िगर और सक्षम की गई",
            "isolation": "पृथक वातावरण:",
            "isolation_desc": "सिस्टम Python पैकेज के साथ संघर्ष नहीं करता",
            "version_management": "🔄 संस्करण प्रबंधन",
            "uninstall": "🗑️ स्थापना रद्द करें"
        },
        "zypper_sles": {
            "title": "📦 Zypper रिपॉजिटरी (SLES - अनुशंसित)",
            "supported": "समर्थित प्लेटफ़ॉर्म:",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11 (2018+)",
            "platforms_note": "पैकेज में एक स्व-निहित virtualenv में सभी Python निर्भरताएं शामिल हैं।",
            "quick_start": "त्वरित स्थापना - SLES 15",
            "benefits_title": "✨ Zypper स्थापना के लाभ",
            "automatic": "स्वचालित अपडेट:",
            "automatic_desc": "मानक zypper update के माध्यम से नए संस्करण प्राप्त करें",
            "dependencies": "निर्भरता प्रबंधन:",
            "dependencies_desc": "पैकेज में सभी Python निर्भरताएं शामिल हैं",
            "systemd": "Systemd एकीकरण:",
            "systemd_desc": "सेवा स्वचालित रूप से कॉन्फ़िगर और सक्षम की गई",
            "enterprise": "एंटरप्राइज़ समर्थन:",
            "enterprise_desc": "SUSE एंटरप्राइज़ वातावरण के लिए उत्पादन के लिए तैयार",
            "version_management": "🔄 संस्करण प्रबंधन",
            "uninstall": "🗑️ स्थापना रद्द करें",
            "enterprise_note": "🏢 एंटरप्राइज़ विचार",
            "subscription": "सदस्यता:",
            "subscription_desc": "SLES को सिस्टम अपडेट के लिए एक सक्रिय सदस्यता की आवश्यकता है",
            "firewall": "फ़ायरवॉल:",
            "firewall_desc": "आउटबाउंड HTTPS के लिए SuSEfirewall2 या firewalld कॉन्फ़िगर करें",
            "apparmor": "AppArmor:",
            "apparmor_desc": "यदि AppArmor का उपयोग कर रहे हैं तो प्रोफ़ाइल समायोजन की आवश्यकता हो सकती है"
        }
    }
}

def add_translations_to_file(lang_code, translations):
    """Add zypper translations to a specific language file."""
    locale_dir = Path(__file__).parent
    file_path = locale_dir / f"{lang_code}.json"

    # Read existing translations
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Navigate to agent_installation.installation and add zypper translations
    if 'agent_installation' not in data:
        print(f"Warning: agent_installation not found in {lang_code}.json")
        return

    if 'installation' not in data['agent_installation']:
        print(f"Warning: installation section not found in {lang_code}.json")
        return

    # Add zypper translations
    data['agent_installation']['installation']['zypper_opensuse'] = translations['zypper_opensuse']
    data['agent_installation']['installation']['zypper_sles'] = translations['zypper_sles']

    # Write back with proper formatting
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Updated {lang_code}.json")

def main():
    """Add zypper translations to all language files."""
    print("Adding zypper (openSUSE and SLES) installation translations to all locale files...\\n")

    for lang_code, translations in TRANSLATIONS.items():
        add_translations_to_file(lang_code, translations)

    # Also update English file
    add_translations_to_file('en', {
        "zypper_opensuse": {
            "title": "📦 Zypper Repository (openSUSE - Recommended)",
            "supported": "Supported Platforms:",
            "platforms_leap": "openSUSE Leap 15.x - Python 3.11 (2021+)",
            "platforms_tumbleweed": "openSUSE Tumbleweed - Python 3.11+ (Rolling)",
            "platforms_note": "The package includes all Python dependencies in a self-contained virtualenv.",
            "quick_start_leap": "Quick Installation - openSUSE Leap 15.x",
            "quick_start_tumbleweed": "Quick Installation - openSUSE Tumbleweed",
            "benefits_title": "✨ Benefits of Zypper Installation",
            "automatic": "Automatic Updates:",
            "automatic_desc": "Get new versions via standard zypper update",
            "dependencies": "Dependency Management:",
            "dependencies_desc": "All Python dependencies included in package",
            "systemd": "Systemd Integration:",
            "systemd_desc": "Service automatically configured and enabled",
            "isolation": "Isolated Environment:",
            "isolation_desc": "Doesn't conflict with system Python packages",
            "version_management": "🔄 Version Management",
            "uninstall": "🗑️ Uninstallation"
        },
        "zypper_sles": {
            "title": "📦 Zypper Repository (SLES - Recommended)",
            "supported": "Supported Platforms:",
            "platforms_sles15": "SUSE Linux Enterprise Server 15 - Python 3.11 (2018+)",
            "platforms_note": "The package includes all Python dependencies in a self-contained virtualenv.",
            "quick_start": "Quick Installation - SLES 15",
            "benefits_title": "✨ Benefits of Zypper Installation",
            "automatic": "Automatic Updates:",
            "automatic_desc": "Get new versions via standard zypper update",
            "dependencies": "Dependency Management:",
            "dependencies_desc": "All Python dependencies included in package",
            "systemd": "Systemd Integration:",
            "systemd_desc": "Service automatically configured and enabled",
            "enterprise": "Enterprise Support:",
            "enterprise_desc": "Production-ready for SUSE enterprise environments",
            "version_management": "🔄 Version Management",
            "uninstall": "🗑️ Uninstallation",
            "enterprise_note": "🏢 Enterprise Considerations",
            "subscription": "Subscription:",
            "subscription_desc": "SLES requires an active subscription for system updates",
            "firewall": "Firewall:",
            "firewall_desc": "Configure SuSEfirewall2 or firewalld for outbound HTTPS",
            "apparmor": "AppArmor:",
            "apparmor_desc": "May require profile adjustments if using AppArmor"
        }
    })

    print("\\n[SUCCESS] All zypper translations added successfully!")
    print("\\nTranslations added for languages:")
    print("  - en (English)")
    for lang_code in TRANSLATIONS:
        print(f"  - {lang_code}")

if __name__ == '__main__':
    main()
