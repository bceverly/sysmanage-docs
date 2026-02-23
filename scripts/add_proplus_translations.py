#!/usr/bin/env python3
"""
Add Professional+ documentation translations to all locale files.
"""

import json
import os
from pathlib import Path

# Base path for locale files
LOCALES_PATH = Path("/home/bceverly/dev/sysmanage-docs/assets/locales")

# New keys to add to docs section (for main docs index)
DOCS_PRO_PLUS = {
    "en": {
        "title": "Professional+",
        "description": "Advanced features with AI-powered health analysis, vulnerability scanning, compliance reports, and configurable alerting.",
        "health": "Health Analysis",
        "vulnerability": "Vulnerability Scanning",
        "alerting": "Alerting Engine",
        "compliance": "Compliance Engine",
        "view_docs": "View Pro+ Docs ->"
    },
    "ar": {
        "title": "الاحترافي+",
        "description": "ميزات متقدمة مع تحليل الصحة بالذكاء الاصطناعي وفحص الثغرات وتقارير الامتثال والتنبيهات القابلة للتكوين.",
        "health": "تحليل الصحة",
        "vulnerability": "فحص الثغرات",
        "alerting": "محرك التنبيهات",
        "compliance": "محرك الامتثال",
        "view_docs": "عرض وثائق Pro+ ->"
    },
    "de": {
        "title": "Professional+",
        "description": "Erweiterte Funktionen mit KI-gestützter Gesundheitsanalyse, Schwachstellenscanning, Compliance-Berichten und konfigurierbaren Warnungen.",
        "health": "Gesundheitsanalyse",
        "vulnerability": "Schwachstellenscan",
        "alerting": "Alarmierungs-Engine",
        "compliance": "Compliance-Engine",
        "view_docs": "Pro+ Docs anzeigen ->"
    },
    "es": {
        "title": "Professional+",
        "description": "Funciones avanzadas con análisis de salud impulsado por IA, escaneo de vulnerabilidades, informes de cumplimiento y alertas configurables.",
        "health": "Análisis de Salud",
        "vulnerability": "Escaneo de Vulnerabilidades",
        "alerting": "Motor de Alertas",
        "compliance": "Motor de Cumplimiento",
        "view_docs": "Ver Docs Pro+ ->"
    },
    "fr": {
        "title": "Professional+",
        "description": "Fonctionnalités avancées avec analyse de santé alimentée par l'IA, scan de vulnérabilités, rapports de conformité et alertes configurables.",
        "health": "Analyse de Santé",
        "vulnerability": "Scan de Vulnérabilités",
        "alerting": "Moteur d'Alertes",
        "compliance": "Moteur de Conformité",
        "view_docs": "Voir Docs Pro+ ->"
    },
    "hi": {
        "title": "प्रोफ़ेशनल+",
        "description": "AI-संचालित हेल्थ विश्लेषण, कमज़ोरी स्कैनिंग, अनुपालन रिपोर्ट और कॉन्फ़िगरेबल अलर्ट के साथ उन्नत सुविधाएँ।",
        "health": "हेल्थ विश्लेषण",
        "vulnerability": "कमज़ोरी स्कैनिंग",
        "alerting": "अलर्टिंग इंजन",
        "compliance": "अनुपालन इंजन",
        "view_docs": "Pro+ Docs देखें ->"
    },
    "it": {
        "title": "Professional+",
        "description": "Funzionalità avanzate con analisi della salute basata su AI, scansione delle vulnerabilità, report di conformità e avvisi configurabili.",
        "health": "Analisi della Salute",
        "vulnerability": "Scansione Vulnerabilità",
        "alerting": "Motore di Avvisi",
        "compliance": "Motore di Conformità",
        "view_docs": "Vedi Docs Pro+ ->"
    },
    "ja": {
        "title": "Professional+",
        "description": "AI駆動のヘルス分析、脆弱性スキャン、コンプライアンスレポート、構成可能なアラートを備えた高度な機能。",
        "health": "ヘルス分析",
        "vulnerability": "脆弱性スキャン",
        "alerting": "アラートエンジン",
        "compliance": "コンプライアンスエンジン",
        "view_docs": "Pro+ Docsを見る ->"
    },
    "ko": {
        "title": "Professional+",
        "description": "AI 기반 건강 분석, 취약성 스캔, 규정 준수 보고서 및 구성 가능한 알림을 포함한 고급 기능.",
        "health": "건강 분석",
        "vulnerability": "취약성 스캔",
        "alerting": "알림 엔진",
        "compliance": "규정 준수 엔진",
        "view_docs": "Pro+ Docs 보기 ->"
    },
    "nl": {
        "title": "Professional+",
        "description": "Geavanceerde functies met AI-gestuurde gezondheidsanalyse, kwetsbaarheidsscanning, nalevingsrapporten en configureerbare waarschuwingen.",
        "health": "Gezondheidsanalyse",
        "vulnerability": "Kwetsbaarheidsscan",
        "alerting": "Waarschuwingsengine",
        "compliance": "Nalevingsengine",
        "view_docs": "Pro+ Docs bekijken ->"
    },
    "pt": {
        "title": "Professional+",
        "description": "Recursos avançados com análise de saúde alimentada por IA, varredura de vulnerabilidades, relatórios de conformidade e alertas configuráveis.",
        "health": "Análise de Saúde",
        "vulnerability": "Varredura de Vulnerabilidades",
        "alerting": "Motor de Alertas",
        "compliance": "Motor de Conformidade",
        "view_docs": "Ver Docs Pro+ ->"
    },
    "ru": {
        "title": "Professional+",
        "description": "Расширенные функции с анализом здоровья на базе ИИ, сканированием уязвимостей, отчётами о соответствии и настраиваемыми оповещениями.",
        "health": "Анализ здоровья",
        "vulnerability": "Сканирование уязвимостей",
        "alerting": "Модуль оповещений",
        "compliance": "Модуль соответствия",
        "view_docs": "Смотреть Pro+ Docs ->"
    },
    "zh_CN": {
        "title": "Professional+",
        "description": "包含 AI 驱动的健康分析、漏洞扫描、合规报告和可配置警报的高级功能。",
        "health": "健康分析",
        "vulnerability": "漏洞扫描",
        "alerting": "警报引擎",
        "compliance": "合规引擎",
        "view_docs": "查看 Pro+ 文档 ->"
    },
    "zh_TW": {
        "title": "Professional+",
        "description": "包含 AI 驅動的健康分析、漏洞掃描、合規報告和可配置警報的高級功能。",
        "health": "健康分析",
        "vulnerability": "漏洞掃描",
        "alerting": "警報引擎",
        "compliance": "合規引擎",
        "view_docs": "查看 Pro+ 文檔 ->"
    }
}

# New keys to add to pro_plus.docs.modules section
PRO_PLUS_MODULES_ALERTING = {
    "en": {
        "title": "Alerting Engine",
        "description": "Configurable alerting with email, webhook, Slack, and Teams notifications.",
        "features": {
            "conditions": "Multiple alert conditions",
            "channels": "Multi-channel notifications",
            "cooldown": "Cooldown management",
            "acknowledge": "Acknowledge & resolve"
        },
        "link": "Alerting Engine Guide ->"
    },
    "ar": {
        "title": "محرك التنبيهات",
        "description": "تنبيهات قابلة للتكوين عبر البريد الإلكتروني وwebhook وSlack وTeams.",
        "features": {
            "conditions": "شروط تنبيه متعددة",
            "channels": "إشعارات متعددة القنوات",
            "cooldown": "إدارة فترة التهدئة",
            "acknowledge": "الإقرار والحل"
        },
        "link": "دليل محرك التنبيهات ->"
    },
    "de": {
        "title": "Alarmierungs-Engine",
        "description": "Konfigurierbare Alarmierung mit E-Mail, Webhook, Slack und Teams-Benachrichtigungen.",
        "features": {
            "conditions": "Mehrere Alarmbedingungen",
            "channels": "Mehrkanal-Benachrichtigungen",
            "cooldown": "Cooldown-Verwaltung",
            "acknowledge": "Bestätigen & Lösen"
        },
        "link": "Alarmierungs-Engine Handbuch ->"
    },
    "es": {
        "title": "Motor de Alertas",
        "description": "Alertas configurables con notificaciones por correo, webhook, Slack y Teams.",
        "features": {
            "conditions": "Múltiples condiciones de alerta",
            "channels": "Notificaciones multicanal",
            "cooldown": "Gestión de enfriamiento",
            "acknowledge": "Reconocer y resolver"
        },
        "link": "Guía del Motor de Alertas ->"
    },
    "fr": {
        "title": "Moteur d'Alertes",
        "description": "Alertes configurables avec notifications par e-mail, webhook, Slack et Teams.",
        "features": {
            "conditions": "Conditions d'alerte multiples",
            "channels": "Notifications multicanaux",
            "cooldown": "Gestion du délai",
            "acknowledge": "Accuser réception et résoudre"
        },
        "link": "Guide du Moteur d'Alertes ->"
    },
    "hi": {
        "title": "अलर्टिंग इंजन",
        "description": "ईमेल, वेबहुक, Slack और Teams नोटिफिकेशन के साथ कॉन्फ़िगरेबल अलर्टिंग।",
        "features": {
            "conditions": "अनेक अलर्ट शर्तें",
            "channels": "मल्टी-चैनल नोटिफिकेशन",
            "cooldown": "कूलडाउन प्रबंधन",
            "acknowledge": "स्वीकार करें और हल करें"
        },
        "link": "अलर्टिंग इंजन गाइड ->"
    },
    "it": {
        "title": "Motore di Avvisi",
        "description": "Avvisi configurabili con notifiche via email, webhook, Slack e Teams.",
        "features": {
            "conditions": "Condizioni di avviso multiple",
            "channels": "Notifiche multicanale",
            "cooldown": "Gestione del cooldown",
            "acknowledge": "Riconoscere e risolvere"
        },
        "link": "Guida al Motore di Avvisi ->"
    },
    "ja": {
        "title": "アラートエンジン",
        "description": "メール、Webhook、Slack、Teams通知を使用した構成可能なアラート。",
        "features": {
            "conditions": "複数のアラート条件",
            "channels": "マルチチャネル通知",
            "cooldown": "クールダウン管理",
            "acknowledge": "確認と解決"
        },
        "link": "アラートエンジンガイド ->"
    },
    "ko": {
        "title": "알림 엔진",
        "description": "이메일, 웹훅, Slack 및 Teams 알림을 통한 구성 가능한 알림.",
        "features": {
            "conditions": "다양한 알림 조건",
            "channels": "다채널 알림",
            "cooldown": "쿨다운 관리",
            "acknowledge": "확인 및 해결"
        },
        "link": "알림 엔진 가이드 ->"
    },
    "nl": {
        "title": "Waarschuwingsengine",
        "description": "Configureerbare waarschuwingen met e-mail, webhook, Slack en Teams-meldingen.",
        "features": {
            "conditions": "Meerdere waarschuwingsvoorwaarden",
            "channels": "Meerkanaals meldingen",
            "cooldown": "Cooldown-beheer",
            "acknowledge": "Bevestigen en oplossen"
        },
        "link": "Waarschuwingsengine Handleiding ->"
    },
    "pt": {
        "title": "Motor de Alertas",
        "description": "Alertas configuráveis com notificações por e-mail, webhook, Slack e Teams.",
        "features": {
            "conditions": "Múltiplas condições de alerta",
            "channels": "Notificações multicanais",
            "cooldown": "Gerenciamento de cooldown",
            "acknowledge": "Reconhecer e resolver"
        },
        "link": "Guia do Motor de Alertas ->"
    },
    "ru": {
        "title": "Модуль оповещений",
        "description": "Настраиваемые оповещения через электронную почту, webhook, Slack и Teams.",
        "features": {
            "conditions": "Несколько условий оповещения",
            "channels": "Многоканальные уведомления",
            "cooldown": "Управление паузой",
            "acknowledge": "Подтвердить и решить"
        },
        "link": "Руководство по модулю оповещений ->"
    },
    "zh_CN": {
        "title": "警报引擎",
        "description": "可配置的警报，支持电子邮件、webhook、Slack和Teams通知。",
        "features": {
            "conditions": "多种警报条件",
            "channels": "多渠道通知",
            "cooldown": "冷却时间管理",
            "acknowledge": "确认和解决"
        },
        "link": "警报引擎指南 ->"
    },
    "zh_TW": {
        "title": "警報引擎",
        "description": "可配置的警報，支持電子郵件、webhook、Slack和Teams通知。",
        "features": {
            "conditions": "多種警報條件",
            "channels": "多渠道通知",
            "cooldown": "冷卻時間管理",
            "acknowledge": "確認和解決"
        },
        "link": "警報引擎指南 ->"
    }
}

# Update pro_plus.docs.modules.compliance with full links (remove "Coming Soon")
PRO_PLUS_MODULES_COMPLIANCE_UPDATE = {
    "en": {
        "title": "Compliance Engine",
        "description": "Automated compliance assessments against industry frameworks with detailed reporting.",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "Automated assessments",
            "export": "Export to PDF/CSV",
            "scheduling": "Scheduled reports"
        },
        "link": "Compliance Engine Guide ->"
    },
    "ar": {
        "title": "محرك الامتثال",
        "description": "تقييمات الامتثال الآلية وفقًا لأطر الصناعة مع تقارير مفصلة.",
        "features": {
            "frameworks": "CIS، NIST، PCI DSS، HIPAA",
            "automated": "تقييمات آلية",
            "export": "تصدير إلى PDF/CSV",
            "scheduling": "تقارير مجدولة"
        },
        "link": "دليل محرك الامتثال ->"
    },
    "de": {
        "title": "Compliance-Engine",
        "description": "Automatisierte Compliance-Bewertungen gegen Industriestandards mit detaillierten Berichten.",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "Automatisierte Bewertungen",
            "export": "Export nach PDF/CSV",
            "scheduling": "Geplante Berichte"
        },
        "link": "Compliance-Engine Handbuch ->"
    },
    "es": {
        "title": "Motor de Cumplimiento",
        "description": "Evaluaciones de cumplimiento automatizadas contra marcos de la industria con informes detallados.",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "Evaluaciones automatizadas",
            "export": "Exportar a PDF/CSV",
            "scheduling": "Informes programados"
        },
        "link": "Guía del Motor de Cumplimiento ->"
    },
    "fr": {
        "title": "Moteur de Conformité",
        "description": "Évaluations de conformité automatisées contre les cadres industriels avec rapports détaillés.",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "Évaluations automatisées",
            "export": "Exporter en PDF/CSV",
            "scheduling": "Rapports planifiés"
        },
        "link": "Guide du Moteur de Conformité ->"
    },
    "hi": {
        "title": "अनुपालन इंजन",
        "description": "विस्तृत रिपोर्टिंग के साथ उद्योग फ्रेमवर्क के विरुद्ध स्वचालित अनुपालन मूल्यांकन।",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "स्वचालित मूल्यांकन",
            "export": "PDF/CSV में निर्यात करें",
            "scheduling": "शेड्यूल्ड रिपोर्ट्स"
        },
        "link": "अनुपालन इंजन गाइड ->"
    },
    "it": {
        "title": "Motore di Conformità",
        "description": "Valutazioni di conformità automatizzate contro framework industriali con reportistica dettagliata.",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "Valutazioni automatizzate",
            "export": "Esporta in PDF/CSV",
            "scheduling": "Report programmati"
        },
        "link": "Guida al Motore di Conformità ->"
    },
    "ja": {
        "title": "コンプライアンスエンジン",
        "description": "詳細なレポートを伴う業界フレームワークに対する自動コンプライアンス評価。",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "自動評価",
            "export": "PDF/CSVにエクスポート",
            "scheduling": "スケジュールレポート"
        },
        "link": "コンプライアンスエンジンガイド ->"
    },
    "ko": {
        "title": "규정 준수 엔진",
        "description": "상세한 보고서를 포함한 업계 프레임워크에 대한 자동 규정 준수 평가.",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "자동 평가",
            "export": "PDF/CSV로 내보내기",
            "scheduling": "예약된 보고서"
        },
        "link": "규정 준수 엔진 가이드 ->"
    },
    "nl": {
        "title": "Nalevingsengine",
        "description": "Geautomatiseerde nalevingsbeoordelingen tegen industriestandaarden met gedetailleerde rapportage.",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "Geautomatiseerde beoordelingen",
            "export": "Exporteren naar PDF/CSV",
            "scheduling": "Geplande rapporten"
        },
        "link": "Nalevingsengine Handleiding ->"
    },
    "pt": {
        "title": "Motor de Conformidade",
        "description": "Avaliações de conformidade automatizadas contra frameworks da indústria com relatórios detalhados.",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "Avaliações automatizadas",
            "export": "Exportar para PDF/CSV",
            "scheduling": "Relatórios agendados"
        },
        "link": "Guia do Motor de Conformidade ->"
    },
    "ru": {
        "title": "Модуль соответствия",
        "description": "Автоматизированные оценки соответствия отраслевым стандартам с подробной отчётностью.",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "Автоматизированные оценки",
            "export": "Экспорт в PDF/CSV",
            "scheduling": "Запланированные отчёты"
        },
        "link": "Руководство по модулю соответствия ->"
    },
    "zh_CN": {
        "title": "合规引擎",
        "description": "对行业框架进行自动合规评估，提供详细报告。",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "自动评估",
            "export": "导出为 PDF/CSV",
            "scheduling": "计划报告"
        },
        "link": "合规引擎指南 ->"
    },
    "zh_TW": {
        "title": "合規引擎",
        "description": "對行業框架進行自動合規評估，提供詳細報告。",
        "features": {
            "frameworks": "CIS, NIST, PCI DSS, HIPAA",
            "automated": "自動評估",
            "export": "導出為 PDF/CSV",
            "scheduling": "計劃報告"
        },
        "link": "合規引擎指南 ->"
    }
}

# Languages list
LANGUAGES = ["en", "ar", "de", "es", "fr", "hi", "it", "ja", "ko", "nl", "pt", "ru", "zh_CN", "zh_TW"]

def update_locale_file(lang: str):
    """Update a single locale file with new translations."""
    filepath = LOCALES_PATH / f"{lang}.json"

    if not filepath.exists():
        print(f"Warning: {filepath} does not exist, skipping")
        return

    # Read existing content
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Add docs.pro_plus section
    if 'docs' not in data:
        data['docs'] = {}
    data['docs']['pro_plus'] = DOCS_PRO_PLUS.get(lang, DOCS_PRO_PLUS['en'])

    # Add/update pro_plus.docs.modules.alerting
    if 'pro_plus' not in data:
        data['pro_plus'] = {}
    if 'docs' not in data['pro_plus']:
        data['pro_plus']['docs'] = {}
    if 'modules' not in data['pro_plus']['docs']:
        data['pro_plus']['docs']['modules'] = {}

    data['pro_plus']['docs']['modules']['alerting'] = PRO_PLUS_MODULES_ALERTING.get(lang, PRO_PLUS_MODULES_ALERTING['en'])

    # Update pro_plus.docs.modules.compliance (add link, remove coming_soon)
    data['pro_plus']['docs']['modules']['compliance'] = PRO_PLUS_MODULES_COMPLIANCE_UPDATE.get(lang, PRO_PLUS_MODULES_COMPLIANCE_UPDATE['en'])

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Updated {filepath}")

def main():
    """Main function to update all locale files."""
    for lang in LANGUAGES:
        update_locale_file(lang)

    print("\nDone! Updated all locale files.")

if __name__ == "__main__":
    main()
