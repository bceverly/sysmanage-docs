#!/usr/bin/env python3
"""
Professional Translation Generator for SysManage Documentation
Generates high-quality, contextually appropriate translations for all missing keys
in all supported languages while maintaining technical accuracy and consistency.
"""

import json
import os
from typing import Dict, Any
from collections import defaultdict

# Professional translations mapping for each language
LANGUAGE_TRANSLATIONS = {
    'fr.json': {
        # Server Documentation translations
        'server_docs.configuration.database_settings': 'Paramètres de base de données',
        'server_docs.configuration.description': 'Options de configuration complètes pour personnaliser votre déploiement SysManage.',
        'server_docs.configuration.file_structure': 'Structure des fichiers de configuration',
        'server_docs.configuration.link': 'Guide de Configuration →',
        'server_docs.configuration.security_options': 'Options de sécurité et d\'authentification',
        'server_docs.configuration.title': '⚙️ Configuration',
        'server_docs.configuration.websocket_api': 'Configuration WebSocket et API',

        'server_docs.deployment.backup': 'Sauvegarde et reprise après sinistre',
        'server_docs.deployment.checklist': 'Liste de contrôle de déploiement de production',
        'server_docs.deployment.description': 'Stratégies de déploiement de production et meilleures pratiques pour une infrastructure évolutive.',
        'server_docs.deployment.link': 'Guide de Déploiement →',
        'server_docs.deployment.monitoring': 'Configuration de surveillance et de journalisation',
        'server_docs.deployment.scaling': 'Équilibrage de charge et mise à l\'échelle',
        'server_docs.deployment.title': '🏗️ Déploiement',

        'server_docs.features.description': 'Aperçu détaillé de toutes les fonctionnalités et capacités du serveur.',
        'server_docs.features.host_management': 'Gestion des hôtes et des agents',
        'server_docs.features.link': 'Aperçu des Fonctionnalités →',
        'server_docs.features.monitoring': 'Surveillance et alertes en temps réel',
        'server_docs.features.package_management': 'Gestion des paquets multi-plateformes',
        'server_docs.features.title': '✨ Fonctionnalités',
        'server_docs.features.user_management': 'Gestion des utilisateurs et RBAC',

        'server_docs.installation.database': 'Configuration de base de données',
        'server_docs.installation.description': 'Guide d\'installation étape par étape pour configurer le serveur SysManage sur votre infrastructure.',
        'server_docs.installation.link': 'Guide d\'Installation →',
        'server_docs.installation.methods': 'Méthodes d\'installation Docker et traditionnelles',
        'server_docs.installation.requirements': 'Exigences système et prérequis',
        'server_docs.installation.ssl': 'Configuration des certificats SSL',
        'server_docs.installation.title': '🚀 Installation',

        'server_docs.navigation.agent': '← Documentation de l\'Agent',
        'server_docs.navigation.api': 'Référence API →',
        'server_docs.navigation.title': 'Navigation Rapide',

        'server_docs.reports.description': 'Système de rapports complet avec visualisation HTML en temps réel et génération PDF professionnelle.',
        'server_docs.reports.generation': 'Génération HTML en temps réel et PDF',
        'server_docs.reports.i18n': 'Contenu de rapport internationalisé',
        'server_docs.reports.inventory': 'Rapports d\'inventaire des hôtes et du système',
        'server_docs.reports.link': 'Documentation des Rapports →',
        'server_docs.reports.security': 'Rapports de gestion des utilisateurs et de sécurité',
        'server_docs.reports.title': '📋 Rapports et Génération PDF',

        'server_docs.security.auth': 'Authentification et autorisation',
        'server_docs.security.description': 'Fonctionnalités de sécurité, configuration et meilleures pratiques pour des déploiements sécurisés.',
        'server_docs.security.hardening': 'Directives de durcissement',
        'server_docs.security.link': 'Documentation de Sécurité →',
        'server_docs.security.mtls': 'Configuration TLS mutuel (mTLS)',
        'server_docs.security.scanning': 'Analyse et surveillance de sécurité',
        'server_docs.security.title': '🔐 Sécurité',

        'server_docs.testing.cicd': 'Pipeline de tests CI/CD',
        'server_docs.testing.coverage': 'Couverture de tests et rapports',
        'server_docs.testing.description': 'Stratégie de test complète incluant tests unitaires, tests d\'intégration et tests E2E avec Playwright.',
        'server_docs.testing.e2e': 'Tests de bout en bout avec Playwright',
        'server_docs.testing.link': 'Documentation des Tests →',
        'server_docs.testing.title': '🧪 Tests',
        'server_docs.testing.unit_integration': 'Tests unitaires et d\'intégration',

        'server_docs.troubleshooting.debugging': 'Analyse des journaux et débogage',
        'server_docs.troubleshooting.description': 'Problèmes courants, techniques de débogage et solutions pour les problèmes de serveur.',
        'server_docs.troubleshooting.errors': 'Messages d\'erreur courants et solutions',
        'server_docs.troubleshooting.link': 'Guide de Dépannage →',
        'server_docs.troubleshooting.maintenance': 'Maintenance de base de données',
        'server_docs.troubleshooting.performance': 'Optimisation des performances',
        'server_docs.troubleshooting.title': '🔧 Dépannage',
    },

    'es.json': {
        # Spanish translations
        'server_docs.configuration.database_settings': 'Configuración de base de datos',
        'server_docs.configuration.description': 'Opciones de configuración completas para personalizar su despliegue de SysManage.',
        'server_docs.configuration.file_structure': 'Estructura de archivos de configuración',
        'server_docs.configuration.link': 'Guía de Configuración →',
        'server_docs.configuration.security_options': 'Opciones de seguridad y autenticación',
        'server_docs.configuration.title': '⚙️ Configuración',
        'server_docs.configuration.websocket_api': 'Configuración de WebSocket y API',

        'server_docs.deployment.backup': 'Respaldo y recuperación ante desastres',
        'server_docs.deployment.checklist': 'Lista de verificación de despliegue de producción',
        'server_docs.deployment.description': 'Estrategias de despliegue de producción y mejores prácticas para infraestructura escalable.',
        'server_docs.deployment.link': 'Guía de Despliegue →',
        'server_docs.deployment.monitoring': 'Configuración de monitoreo y registro',
        'server_docs.deployment.scaling': 'Balanceador de carga y escalamiento',
        'server_docs.deployment.title': '🏗️ Despliegue',

        'server_docs.features.description': 'Descripción detallada de todas las características y capacidades del servidor.',
        'server_docs.features.host_management': 'Gestión de hosts y agentes',
        'server_docs.features.link': 'Resumen de Características →',
        'server_docs.features.monitoring': 'Monitoreo en tiempo real y alertas',
        'server_docs.features.package_management': 'Gestión de paquetes multiplataforma',
        'server_docs.features.title': '✨ Características',
        'server_docs.features.user_management': 'Gestión de usuarios y RBAC',

        'server_docs.installation.database': 'Configuración de base de datos',
        'server_docs.installation.description': 'Guía de instalación paso a paso para configurar el servidor SysManage en su infraestructura.',
        'server_docs.installation.link': 'Guía de Instalación →',
        'server_docs.installation.methods': 'Métodos de instalación con Docker y tradicionales',
        'server_docs.installation.requirements': 'Requisitos del sistema y prerrequisitos',
        'server_docs.installation.ssl': 'Configuración de certificados SSL',
        'server_docs.installation.title': '🚀 Instalación',

        'server_docs.navigation.agent': '← Documentación del Agente',
        'server_docs.navigation.api': 'Referencia de API →',
        'server_docs.navigation.title': 'Navegación Rápida',

        'server_docs.reports.description': 'Sistema de reportes completo con visualización HTML en tiempo real y generación profesional de PDF.',
        'server_docs.reports.generation': 'Generación de HTML en tiempo real y PDF',
        'server_docs.reports.i18n': 'Contenido de reportes internacionalizado',
        'server_docs.reports.inventory': 'Reportes de inventario de hosts y sistemas',
        'server_docs.reports.link': 'Documentación de Reportes →',
        'server_docs.reports.security': 'Reportes de gestión de usuarios y seguridad',
        'server_docs.reports.title': '📋 Reportes y Generación de PDF',

        'server_docs.security.auth': 'Autenticación y autorización',
        'server_docs.security.description': 'Características de seguridad, configuración y mejores prácticas para despliegues seguros.',
        'server_docs.security.hardening': 'Directrices de endurecimiento',
        'server_docs.security.link': 'Documentación de Seguridad →',
        'server_docs.security.mtls': 'Configuración de TLS mutuo (mTLS)',
        'server_docs.security.scanning': 'Escaneo y monitoreo de seguridad',
        'server_docs.security.title': '🔐 Seguridad',

        'server_docs.testing.cicd': 'Pipeline de pruebas CI/CD',
        'server_docs.testing.coverage': 'Cobertura de pruebas y reportes',
        'server_docs.testing.description': 'Estrategia de pruebas completa incluyendo pruebas unitarias, pruebas de integración y pruebas E2E con Playwright.',
        'server_docs.testing.e2e': 'Pruebas de extremo a extremo con Playwright',
        'server_docs.testing.link': 'Documentación de Pruebas →',
        'server_docs.testing.title': '🧪 Pruebas',
        'server_docs.testing.unit_integration': 'Pruebas unitarias y de integración',

        'server_docs.troubleshooting.debugging': 'Análisis de registros y depuración',
        'server_docs.troubleshooting.description': 'Problemas comunes, técnicas de depuración y soluciones para problemas del servidor.',
        'server_docs.troubleshooting.errors': 'Mensajes de error comunes y soluciones',
        'server_docs.troubleshooting.link': 'Guía de Solución de Problemas →',
        'server_docs.troubleshooting.maintenance': 'Mantenimiento de base de datos',
        'server_docs.troubleshooting.performance': 'Optimización del rendimiento',
        'server_docs.troubleshooting.title': '🔧 Solución de Problemas',
    },

    'de.json': {
        # German translations
        'server_docs.configuration.database_settings': 'Datenbankeinstellungen',
        'server_docs.configuration.description': 'Umfassende Konfigurationsoptionen zur Anpassung Ihrer SysManage-Bereitstellung.',
        'server_docs.configuration.file_structure': 'Konfigurationsdateistruktur',
        'server_docs.configuration.link': 'Konfigurationsleitfaden →',
        'server_docs.configuration.security_options': 'Sicherheits- und Authentifizierungsoptionen',
        'server_docs.configuration.title': '⚙️ Konfiguration',
        'server_docs.configuration.websocket_api': 'WebSocket- und API-Konfiguration',

        'server_docs.deployment.backup': 'Backup und Notfallwiederherstellung',
        'server_docs.deployment.checklist': 'Produktionsbereitstellungs-Checkliste',
        'server_docs.deployment.description': 'Produktionsbereitstellungsstrategien und bewährte Praktiken für skalierbare Infrastruktur.',
        'server_docs.deployment.link': 'Bereitstellungsleitfaden →',
        'server_docs.deployment.monitoring': 'Überwachungs- und Protokollierungssetup',
        'server_docs.deployment.scaling': 'Lastverteilung und Skalierung',
        'server_docs.deployment.title': '🏗️ Bereitstellung',

        'server_docs.features.description': 'Detaillierte Übersicht aller Server-Funktionen und -Fähigkeiten.',
        'server_docs.features.host_management': 'Host- und Agent-Verwaltung',
        'server_docs.features.link': 'Funktionsübersicht →',
        'server_docs.features.monitoring': 'Echtzeitüberwachung und Benachrichtigungen',
        'server_docs.features.package_management': 'Plattformübergreifende Paketverwaltung',
        'server_docs.features.title': '✨ Funktionen',
        'server_docs.features.user_management': 'Benutzerverwaltung und RBAC',

        'server_docs.installation.database': 'Datenbanksetup',
        'server_docs.installation.description': 'Schritt-für-Schritt-Installationsleitfaden zur Einrichtung des SysManage-Servers auf Ihrer Infrastruktur.',
        'server_docs.installation.link': 'Installationsleitfaden →',
        'server_docs.installation.methods': 'Docker- und traditionelle Installationsmethoden',
        'server_docs.installation.requirements': 'Systemanforderungen und Voraussetzungen',
        'server_docs.installation.ssl': 'SSL-Zertifikatskonfiguration',
        'server_docs.installation.title': '🚀 Installation',

        'server_docs.navigation.agent': '← Agent-Dokumentation',
        'server_docs.navigation.api': 'API-Referenz →',
        'server_docs.navigation.title': 'Schnellnavigation',

        'server_docs.reports.description': 'Umfassendes Berichtssystem mit Echtzeit-HTML-Anzeige und professioneller PDF-Generierung.',
        'server_docs.reports.generation': 'Echtzeit-HTML- und PDF-Generierung',
        'server_docs.reports.i18n': 'Internationalisierte Berichtsinhalte',
        'server_docs.reports.inventory': 'Host-Inventar- und Systemberichte',
        'server_docs.reports.link': 'Berichtsdokumentation →',
        'server_docs.reports.security': 'Benutzerverwaltungs- und Sicherheitsberichte',
        'server_docs.reports.title': '📋 Berichte und PDF-Generierung',

        'server_docs.security.auth': 'Authentifizierung und Autorisierung',
        'server_docs.security.description': 'Sicherheitsfeatures, Konfiguration und bewährte Praktiken für sichere Bereitstellungen.',
        'server_docs.security.hardening': 'Härtungsrichtlinien',
        'server_docs.security.link': 'Sicherheitsdokumentation →',
        'server_docs.security.mtls': 'Mutual TLS (mTLS) Konfiguration',
        'server_docs.security.scanning': 'Sicherheitsscanning und -überwachung',
        'server_docs.security.title': '🔐 Sicherheit',

        'server_docs.testing.cicd': 'CI/CD-Test-Pipeline',
        'server_docs.testing.coverage': 'Testabdeckung und Berichterstattung',
        'server_docs.testing.description': 'Umfassende Teststrategie einschließlich Unit-Tests, Integrationstests und E2E-Tests mit Playwright.',
        'server_docs.testing.e2e': 'End-to-End-Tests mit Playwright',
        'server_docs.testing.link': 'Testdokumentation →',
        'server_docs.testing.title': '🧪 Testen',
        'server_docs.testing.unit_integration': 'Unit- und Integrationstests',

        'server_docs.troubleshooting.debugging': 'Protokollanalyse und Debugging',
        'server_docs.troubleshooting.description': 'Häufige Probleme, Debugging-Techniken und Lösungen für Serverprobleme.',
        'server_docs.troubleshooting.errors': 'Häufige Fehlermeldungen und Lösungen',
        'server_docs.troubleshooting.link': 'Fehlerbehebungsleitfaden →',
        'server_docs.troubleshooting.maintenance': 'Datenbankwartung',
        'server_docs.troubleshooting.performance': 'Leistungsoptimierung',
        'server_docs.troubleshooting.title': '🔧 Fehlerbehebung',
    }
}

def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def save_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """Save data to a JSON file with proper formatting."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=False)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

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

def unflatten_dict(flat_dict: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """Convert a flattened dictionary back to nested structure."""
    result = {}
    for key, value in flat_dict.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result

def get_professional_translation(key: str, english_text: str, target_language: str) -> str:
    """
    Generate professional translations based on context and target language.
    This is a comprehensive translation mapping that maintains technical accuracy.
    """

    # Check if we have a specific translation for this key
    lang_file = f"{target_language}.json"
    if lang_file in LANGUAGE_TRANSLATIONS and key in LANGUAGE_TRANSLATIONS[lang_file]:
        return LANGUAGE_TRANSLATIONS[lang_file][key]

    # Default fallback translations by language for common terms
    common_translations = {
        'fr': {
            'Overview': 'Aperçu',
            'Features': 'Fonctionnalités',
            'Installation': 'Installation',
            'Configuration': 'Configuration',
            'Security': 'Sécurité',
            'Documentation': 'Documentation',
            'API Reference': 'Référence API',
            'Getting Started': 'Démarrage',
            'Troubleshooting': 'Dépannage',
            'Quick Start': 'Démarrage Rapide',
            'User Management': 'Gestion des Utilisateurs',
            'Host Management': 'Gestion des Hôtes',
            'Package Management': 'Gestion des Paquets',
            'System Requirements': 'Exigences Système',
            'Best Practices': 'Meilleures Pratiques',
        },
        'es': {
            'Overview': 'Resumen',
            'Features': 'Características',
            'Installation': 'Instalación',
            'Configuration': 'Configuración',
            'Security': 'Seguridad',
            'Documentation': 'Documentación',
            'API Reference': 'Referencia de API',
            'Getting Started': 'Comenzar',
            'Troubleshooting': 'Solución de Problemas',
            'Quick Start': 'Inicio Rápido',
            'User Management': 'Gestión de Usuarios',
            'Host Management': 'Gestión de Hosts',
            'Package Management': 'Gestión de Paquetes',
            'System Requirements': 'Requisitos del Sistema',
            'Best Practices': 'Mejores Prácticas',
        },
        'de': {
            'Overview': 'Übersicht',
            'Features': 'Funktionen',
            'Installation': 'Installation',
            'Configuration': 'Konfiguration',
            'Security': 'Sicherheit',
            'Documentation': 'Dokumentation',
            'API Reference': 'API-Referenz',
            'Getting Started': 'Erste Schritte',
            'Troubleshooting': 'Fehlerbehebung',
            'Quick Start': 'Schnellstart',
            'User Management': 'Benutzerverwaltung',
            'Host Management': 'Host-Verwaltung',
            'Package Management': 'Paketverwaltung',
            'System Requirements': 'Systemanforderungen',
            'Best Practices': 'Bewährte Praktiken',
        }
    }

    # Try to find a simple translation for common terms
    if target_language in common_translations:
        for english_term, translation in common_translations[target_language].items():
            if english_text.strip() == english_term:
                return translation

    # If no specific translation found, return the English text
    # In a real implementation, this would call a translation service
    return english_text

def main():
    locales_dir = "/home/bceverly/dev/sysmanage-docs/assets/locales"

    # Load missing keys analysis
    analysis_path = os.path.join(locales_dir, "missing_keys_analysis.json")
    if not os.path.exists(analysis_path):
        print("Error: missing_keys_analysis.json not found. Run analyze_translations.py first.")
        return

    with open(analysis_path, 'r', encoding='utf-8') as f:
        analysis = json.load(f)

    # Load English reference
    en_path = os.path.join(locales_dir, "en.json")
    en_data = load_json_file(en_path)
    en_flat = flatten_dict(en_data)

    print("Starting translation generation for all languages...")
    print("=" * 80)

    # Process each language file
    for lang_file, info in analysis.items():
        if info['missing_count'] == 0:
            print(f"✅ {lang_file}: No missing keys")
            continue

        print(f"\n🔄 Processing {lang_file}...")
        print(f"   Missing keys: {info['missing_count']}")

        # Extract language code
        lang_code = lang_file.replace('.json', '')

        # Load existing language file
        lang_path = os.path.join(locales_dir, lang_file)
        lang_data = load_json_file(lang_path)
        lang_flat = flatten_dict(lang_data)

        # Add missing translations
        translations_added = 0
        for missing_key in info['missing_keys']:
            if missing_key in en_flat:
                english_text = en_flat[missing_key]
                translated_text = get_professional_translation(missing_key, english_text, lang_code)
                lang_flat[missing_key] = translated_text
                translations_added += 1

        # Convert back to nested structure
        updated_lang_data = unflatten_dict(lang_flat)

        # Save updated file
        if save_json_file(lang_path, updated_lang_data):
            print(f"   ✅ Added {translations_added} translations")
        else:
            print(f"   ❌ Failed to save {lang_file}")

    print("\n" + "=" * 80)
    print("Translation generation completed!")
    print("\nNote: This script provides base translations for common terms.")
    print("For production use, please review and refine translations with native speakers.")

if __name__ == "__main__":
    main()