#!/usr/bin/env python3
"""
Add detailed alerting and compliance page translations to all locale files.
"""

import json
from pathlib import Path

LOCALES_PATH = Path("/home/bceverly/dev/sysmanage-docs/assets/locales")
LANGUAGES = ["en", "ar", "de", "es", "fr", "hi", "it", "ja", "ko", "nl", "pt", "ru", "zh_CN", "zh_TW"]

# Alerting page translations
ALERTING_TRANSLATIONS = {
    "en": {
        "page_title": "Alerting Engine - SysManage Professional+",
        "meta_description": "Configurable alerting with email, webhook, Slack, and Microsoft Teams notifications for proactive infrastructure monitoring.",
        "breadcrumb": "Alerting Engine",
        "header": {
            "title": "Alerting Engine Module",
            "description": "Configurable alerting with multiple notification channels to keep you informed about critical infrastructure events in real-time."
        },
        "overview": {
            "title": "Overview",
            "description": "The Alerting Engine provides proactive notification when your infrastructure needs attention. Define custom alert rules based on host conditions, and receive notifications through your preferred channels - email, webhooks, Slack, or Microsoft Teams."
        },
        "steps": {
            "rules": {"title": "Define Rules", "desc": "Set conditions that trigger alerts"},
            "channels": {"title": "Configure Channels", "desc": "Email, Slack, Teams, webhooks"},
            "respond": {"title": "Get Notified", "desc": "Respond to issues promptly"}
        },
        "conditions": {
            "title": "Alert Conditions",
            "description": "Create alert rules based on various infrastructure conditions:",
            "host_down": {"title": "Host Down", "description": "Alert when a host stops reporting for a configurable time threshold (default: 10 minutes)."},
            "reboot": {"title": "Reboot Required", "description": "Alert when a host requires a reboot to apply system updates or configuration changes."},
            "updates": {"title": "Updates Available", "description": "Alert when a host has pending package updates, with configurable minimum count."},
            "disk": {"title": "Disk Usage", "description": "Alert when disk usage exceeds a threshold percentage on specified mount points."},
            "cve": {"title": "CVE Severity", "description": "Alert when hosts have vulnerabilities at or above a specified severity level."},
            "custom": {"title": "Custom Metrics", "description": "Alert based on custom metric thresholds with configurable operators and values."}
        },
        "channels": {
            "title": "Notification Channels",
            "description": "Configure multiple notification channels to receive alerts:",
            "email": {"title": "Email", "recipients": "Multiple recipients per channel", "html": "HTML-formatted alert details", "severity": "Severity-based subject lines"},
            "webhook": {"title": "Webhook", "json": "JSON payload with full alert details", "headers": "Custom HTTP headers", "integration": "Integration with any webhook-capable system"},
            "slack": {"title": "Slack", "blocks": "Block Kit formatted messages", "colors": "Severity-based color coding", "emojis": "Alert type-specific emojis"},
            "teams": {"title": "Microsoft Teams", "adaptive": "Adaptive Card formatting", "colors": "Severity-based theme colors", "structured": "Structured alert presentation"}
        },
        "severity": {
            "title": "Alert Severity Levels",
            "description": "Alerts are classified by severity to help prioritize response:",
            "critical": {"label": "Critical", "description": "Immediate action required - critical system failures or security risks"},
            "high": {"label": "High", "description": "Urgent attention needed - significant issues affecting operations"},
            "medium": {"label": "Medium", "description": "Should be addressed soon - potential problems identified"},
            "low": {"label": "Low", "description": "Monitor - minor issues that can be addressed during maintenance"},
            "info": {"label": "Info", "description": "Informational - status changes and non-critical notifications"}
        },
        "features": {
            "title": "Key Features",
            "cooldown": {"title": "Alert Cooldown", "description": "Configure cooldown periods to prevent alert fatigue. Once an alert fires for a host+rule combination, subsequent alerts are suppressed for the cooldown duration (default: 60 minutes)."},
            "filters": {"title": "Host Filters", "description": "Apply alert rules to specific hosts using tag-based filters. For example, create different alerting policies for production vs. development environments."},
            "multi_channel": {"title": "Multi-Channel Routing", "description": "Link multiple notification channels to a single rule. Critical alerts can go to both email and Slack, while informational alerts might only go to a webhook."},
            "acknowledge": {"title": "Alert Acknowledgment", "description": "Acknowledge alerts to indicate they're being addressed. Acknowledged alerts are tracked with username and timestamp for audit purposes."},
            "resolution": {"title": "Alert Resolution", "description": "Mark alerts as resolved when the underlying issue is fixed. Resolution status helps track mean time to resolution (MTTR) metrics."}
        },
        "creating_rules": {
            "title": "Creating Alert Rules",
            "description": "To create an alert rule:",
            "steps": {
                "navigate": "Navigate to Alerts > Alert Rules in the main navigation",
                "create": "Click \"Create Rule\" to open the rule editor",
                "name": "Enter a descriptive name for the rule",
                "condition": "Select the condition type and configure its parameters",
                "severity": "Choose the alert severity level",
                "cooldown": "Set the cooldown period (in minutes)",
                "channels": "Select one or more notification channels",
                "save": "Save the rule - it will be evaluated on the next cycle"
            }
        },
        "configuring_channels": {
            "title": "Configuring Notification Channels",
            "description": "Configure notification channels in Settings > Alerting:",
            "email": {"title": "Email Channel"},
            "slack": {"title": "Slack Channel"},
            "teams": {"title": "Microsoft Teams Channel"},
            "webhook": {"title": "Webhook Channel"}
        },
        "api": {
            "title": "API Access",
            "description": "The Alerting Engine is fully accessible via the REST API:"
        },
        "evaluation": {
            "title": "Alert Evaluation",
            "description": "The alerting engine runs in the background and evaluates all enabled rules:",
            "interval": "Default evaluation interval: 60 seconds",
            "async": "Asynchronous evaluation prevents blocking the main application",
            "cooldown": "Cooldown periods prevent duplicate alerts for the same issue",
            "notifications": "Notifications are dispatched immediately when alerts fire"
        },
        "requirements": {
            "title": "Requirements",
            "license": "Professional or Enterprise license with alerting_engine module",
            "network": "Network connectivity to license server for module download",
            "email": "SMTP configuration for email notifications (optional)",
            "webhooks": "Outbound network access for webhook/Slack/Teams notifications"
        }
    }
}

# Compliance page translations
COMPLIANCE_TRANSLATIONS = {
    "en": {
        "page_title": "Compliance Engine - SysManage Professional+",
        "meta_description": "Automated compliance assessments against industry frameworks with detailed reporting and remediation guidance.",
        "breadcrumb": "Compliance Engine",
        "header": {
            "title": "Compliance Engine Module",
            "description": "Automated compliance assessments against industry frameworks with detailed reporting and remediation guidance for regulatory requirements."
        },
        "overview": {
            "title": "Overview",
            "description": "The Compliance Engine automates the assessment of your infrastructure against industry-standard security frameworks. It evaluates system configurations, identifies compliance gaps, and provides actionable remediation steps to help you meet regulatory requirements."
        },
        "demo": {"score_label": "Compliance"},
        "frameworks": {
            "title": "Supported Frameworks",
            "description": "Assess your infrastructure against multiple compliance frameworks:",
            "cis": {"title": "CIS Benchmarks", "description": "Center for Internet Security benchmarks for operating systems, including Level 1 and Level 2 profiles."},
            "nist": {"title": "NIST 800-53", "description": "Security and privacy controls for federal information systems and organizations."},
            "pci": {"title": "PCI DSS", "description": "Payment Card Industry Data Security Standard for organizations handling cardholder data."},
            "hipaa": {"title": "HIPAA", "description": "Health Insurance Portability and Accountability Act security requirements for healthcare data."},
            "soc2": {"title": "SOC 2", "description": "Service Organization Control 2 trust service criteria for security, availability, and confidentiality."},
            "custom": {"title": "Custom Policies", "description": "Define custom compliance policies tailored to your organization's specific requirements."}
        },
        "checks": {
            "title": "Compliance Checks",
            "description": "The compliance engine evaluates numerous configuration aspects:",
            "access": {"title": "Access Control", "accounts": "User account policies", "passwords": "Password requirements", "permissions": "File and directory permissions", "sudo": "Privileged access controls"},
            "network": {"title": "Network Security", "firewall": "Firewall configuration", "ports": "Open ports and services", "protocols": "Network protocols", "encryption": "Encryption in transit"},
            "logging": {"title": "Audit & Logging", "config": "Audit configuration", "retention": "Log retention policies", "integrity": "Log integrity protection", "monitoring": "System monitoring"},
            "system": {"title": "System Hardening", "services": "Unnecessary services", "kernel": "Kernel parameters", "boot": "Boot configuration", "packages": "Package integrity"}
        },
        "status": {
            "title": "Compliance Status",
            "description": "Each compliance check returns one of the following statuses:",
            "pass": {"label": "Pass", "description": "System configuration meets the compliance requirement"},
            "fail": {"label": "Fail", "description": "Configuration does not meet the requirement - remediation needed"},
            "warning": {"label": "Warning", "description": "Partially compliant or manual verification required"},
            "skip": {"label": "Skipped", "description": "Check not applicable to this system or platform"}
        },
        "reporting": {
            "title": "Compliance Reporting",
            "description": "Generate detailed compliance reports in multiple formats:",
            "features": {
                "pdf": "PDF reports for executive summaries and auditors",
                "csv": "CSV exports for data analysis and tracking",
                "json": "JSON format for integration with other tools",
                "scheduling": "Scheduled report generation (daily, weekly, monthly)",
                "distribution": "Automatic distribution via email"
            },
            "contents": {
                "title": "Report Contents",
                "summary": "Executive summary with compliance percentage",
                "details": "Detailed check results by category",
                "remediation": "Remediation steps for failed checks",
                "trends": "Historical compliance trends",
                "evidence": "Evidence collection for audit trails"
            }
        },
        "using": {
            "title": "Using Compliance Engine",
            "running": {
                "title": "Running an Assessment",
                "description": "To run a compliance assessment:",
                "steps": {
                    "navigate": "Navigate to the host detail page",
                    "tab": "Select the Compliance tab",
                    "framework": "Choose the compliance framework",
                    "run": "Click \"Run Assessment\""
                }
            },
            "viewing": {
                "title": "Viewing Results",
                "description": "Assessment results show:",
                "score": "Overall compliance score percentage",
                "breakdown": "Breakdown by check category",
                "failed": "List of failed checks with remediation steps",
                "evidence": "Evidence collected during the assessment"
            },
            "bulk": {
                "title": "Bulk Assessments",
                "description": "Run compliance assessments across multiple hosts at once from the Compliance dashboard. Filter by tags to assess specific groups of hosts."
            }
        },
        "api": {
            "title": "API Access",
            "description": "The Compliance Engine is accessible via the REST API:"
        },
        "remediation": {
            "title": "Remediation Guidance",
            "description": "Each failed check includes detailed remediation guidance:",
            "features": {
                "steps": "Step-by-step remediation instructions",
                "commands": "Platform-specific commands to apply fixes",
                "impact": "Impact assessment of the change",
                "references": "References to official documentation"
            }
        },
        "requirements": {
            "title": "Requirements",
            "license": "Enterprise license with compliance_engine module",
            "network": "Network connectivity to license server for module download",
            "agent": "SysManage agent with privileged execution for system inspection",
            "database": "PostgreSQL database for assessment storage"
        }
    }
}

def add_fallback_translations(base_translations, lang):
    """For non-English languages, use English as fallback for now."""
    # In a real scenario, you'd translate each string
    # For now, we'll use English as the base
    return base_translations.get("en", {})

def update_locale_file(lang: str):
    """Update a single locale file with alerting and compliance page translations."""
    filepath = LOCALES_PATH / f"{lang}.json"

    if not filepath.exists():
        print(f"Warning: {filepath} does not exist, skipping")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Ensure pro_plus structure exists
    if 'pro_plus' not in data:
        data['pro_plus'] = {}

    # Add alerting page translations (use English for all for now - can be translated later)
    data['pro_plus']['alerting'] = ALERTING_TRANSLATIONS.get(lang, ALERTING_TRANSLATIONS['en'])

    # Add compliance page translations
    data['pro_plus']['compliance'] = COMPLIANCE_TRANSLATIONS.get(lang, COMPLIANCE_TRANSLATIONS['en'])

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Updated {filepath}")

def main():
    for lang in LANGUAGES:
        update_locale_file(lang)
    print("\nDone! Added alerting and compliance page translations.")

if __name__ == "__main__":
    main()
