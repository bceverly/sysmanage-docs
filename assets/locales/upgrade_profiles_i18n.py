# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Inject Phase 10.6 (upgrade-profiles) i18n keys into all 14 locale JSONs.

Pattern matches the earlier mfa_mirror_i18n.py / idp_i18n.py scripts:
titles + lead-in sentences get native translations for major locales;
heavily-technical body paragraphs (with inline <code>) fall back to
English so the code references stay copy-pasteable.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

EN = {
    "docs.api.phase8.upgrade.title": '8.2 Scheduled Update Profiles <span class="pro-plus-badge">&#11088; PRO+</span>',
    "docs.api.phase8.upgrade.intro": "POSIX-cron profiles describing recurring fleet updates with security-only and staggered-rollout options.",
    "docs.api.phase8.upgrade.phase10_6": "<strong>Phase 10.6:</strong> the cron parser and per-host dispatch were moved into the Pro+ <code>automation_engine</code> module. Every <code>/api/upgrade-profiles/*</code> route returns <code>402 Payment Required</code> when the engine isn't loaded.",
    "docs.api.phase8.upgrade.list": "List profiles with their next-run timestamps.",
    "docs.api.phase8.upgrade.create": "Create. Body: <code>{name, description?, cron, enabled?, security_only?, package_managers?, staggered_window_min?, tag_id?}</code>. <code>cron</code> is validated by <code>automation_engine.validate_cron_expression</code> (lists, ranges, step intervals, day/month names, dom/dow OR-semantics). <code>staggered_window_min</code> is clamped to <code>[0, 720]</code> minutes.",
    "docs.api.phase8.upgrade.get": "Read one.",
    "docs.api.phase8.upgrade.update": "Update. Cron changes recompute <code>next_run</code> automatically.",
    "docs.api.phase8.upgrade.delete": "Delete.",
    "docs.api.phase8.upgrade.trigger": "Fire a profile NOW. Resolves the target host set, enqueues an <code>apply_updates</code> command per host (with the profile's flags + staggered-window delay), updates <code>last_run</code> / <code>next_run</code>, and returns the dispatched host list.",
    "docs.api.phase8.upgrade.tick": "Driver hook for an external scheduler. Selects every enabled profile where <code>next_run &lt;= now</code>, fires it, and returns the fired list. Idempotent within a tick.",
    "pro_plus.docs.modules.automation_engine.description": "Saved-script library with version history, multi-host execution, multi-shell support, scheduled triggers, approval workflows for privileged scripts, and scheduled fleet upgrade profiles with cron + staggered rollout windows.",
    "pro_plus.docs.modules.automation_engine.features.upgrade_profiles": "Scheduled fleet upgrade profiles (cron + staggered windows)",
}

# Native translations for the title + intro + lead-in lines.  Body paragraphs
# (list/create/get/update/delete/trigger/tick + phase10_6) keep the English
# source so technical references are copy-paste-stable.
TITLE_BY_LOCALE = {
    "de": '8.2 Geplante Update-Profile <span class="pro-plus-badge">&#11088; PRO+</span>',
    "es": '8.2 Perfiles de actualización programados <span class="pro-plus-badge">&#11088; PRO+</span>',
    "fr": '8.2 Profils de mises à jour planifiées <span class="pro-plus-badge">&#11088; PRO+</span>',
    "it": '8.2 Profili di aggiornamento pianificati <span class="pro-plus-badge">&#11088; PRO+</span>',
    "pt": '8.2 Perfis de atualização agendados <span class="pro-plus-badge">&#11088; PRO+</span>',
    "nl": '8.2 Geplande update-profielen <span class="pro-plus-badge">&#11088; PRO+</span>',
    "ru": '8.2 Запланированные профили обновлений <span class="pro-plus-badge">&#11088; PRO+</span>',
    "ja": '8.2 スケジュール更新プロファイル <span class="pro-plus-badge">&#11088; PRO+</span>',
    "ko": '8.2 예약된 업데이트 프로필 <span class="pro-plus-badge">&#11088; PRO+</span>',
    "zh_CN": '8.2 计划更新配置文件 <span class="pro-plus-badge">&#11088; PRO+</span>',
    "zh_TW": '8.2 排程更新設定檔 <span class="pro-plus-badge">&#11088; PRO+</span>',
    "ar": '8.2 ملفات تعريف التحديث المجدولة <span class="pro-plus-badge">&#11088; PRO+</span>',
    "hi": '8.2 अनुसूचित अद्यतन प्रोफ़ाइल <span class="pro-plus-badge">&#11088; PRO+</span>',
}

INTRO_BY_LOCALE = {
    "de": "POSIX-cron-Profile, die wiederkehrende Flotten-Updates beschreiben, mit Optionen für Nur-Sicherheit und gestaffeltes Rollout.",
    "es": "Perfiles POSIX-cron que describen actualizaciones recurrentes de la flota con opciones de solo seguridad e implementación escalonada.",
    "fr": "Profils POSIX-cron décrivant les mises à jour récurrentes du parc, avec options sécurité uniquement et déploiement échelonné.",
    "it": "Profili POSIX-cron che descrivono aggiornamenti ricorrenti della flotta con opzioni solo sicurezza e rollout scaglionato.",
    "pt": "Perfis POSIX-cron que descrevem atualizações recorrentes da frota com opções apenas de segurança e implantação escalonada.",
    "nl": "POSIX-cron-profielen die terugkerende vlootupdates beschrijven, met opties voor alleen-beveiliging en gefaseerde uitrol.",
    "ru": "Профили POSIX-cron, описывающие периодические обновления парка с опциями «только безопасность» и поэтапного развёртывания.",
    "ja": "POSIX-cron プロファイルで、セキュリティのみおよび段階的ロールアウトのオプションを備えた定期的なフリート更新を記述します。",
    "ko": "POSIX-cron 프로필로 보안 전용 및 단계적 롤아웃 옵션을 갖춘 주기적인 플릿 업데이트를 설명합니다.",
    "zh_CN": "POSIX-cron 配置文件，描述定期的舰队更新，支持仅安全和分阶段推出选项。",
    "zh_TW": "POSIX-cron 設定檔，描述定期的機隊更新，支援僅安全與分階段推出選項。",
    "ar": "ملفات تعريف POSIX-cron تصف التحديثات المتكررة للأسطول مع خيارات الأمان فقط والطرح المرحلي.",
    "hi": "POSIX-cron प्रोफ़ाइल जो बार-बार होने वाले फ़्लीट अपडेट का वर्णन करती हैं, केवल-सुरक्षा और चरणबद्ध रोलआउट विकल्पों के साथ।",
}

DESCRIPTION_BY_LOCALE = {
    "de": "Bibliothek gespeicherter Skripte mit Versionshistorie, Multi-Host-Ausführung, Multi-Shell-Unterstützung, geplanten Triggern, Genehmigungsworkflows für privilegierte Skripte sowie geplante Flotten-Upgrade-Profile mit Cron- und gestaffelten Rollout-Fenstern.",
    "es": "Biblioteca de scripts guardados con historial de versiones, ejecución multi-host, soporte multi-shell, disparadores programados, flujos de aprobación para scripts privilegiados y perfiles de actualización de flota programados con ventanas cron y de implementación escalonada.",
    "fr": "Bibliothèque de scripts enregistrés avec historique de versions, exécution multi-hôte, prise en charge multi-shell, déclencheurs planifiés, workflows d'approbation pour scripts privilégiés et profils de mise à niveau de parc planifiés avec fenêtres cron et déploiement échelonné.",
    "it": "Libreria di script salvati con cronologia versioni, esecuzione multi-host, supporto multi-shell, trigger pianificati, workflow di approvazione per script privilegiati e profili di aggiornamento della flotta pianificati con finestre cron e rollout scaglionato.",
    "pt": "Biblioteca de scripts salvos com histórico de versões, execução multi-host, suporte multi-shell, gatilhos agendados, fluxos de aprovação para scripts privilegiados e perfis de atualização de frota agendados com janelas cron e implantação escalonada.",
    "nl": "Bibliotheek van opgeslagen scripts met versiegeschiedenis, multi-host-uitvoering, multi-shell-ondersteuning, geplande triggers, goedkeuringsworkflows voor bevoorrechte scripts en geplande vloot-upgradeprofielen met cron- en gefaseerde uitrolvensters.",
    "ru": "Библиотека сохранённых скриптов с историей версий, многохостовым выполнением, поддержкой нескольких оболочек, запланированными триггерами, рабочими процессами утверждения для привилегированных скриптов и запланированными профилями обновления парка с cron и поэтапными окнами развёртывания.",
    "ja": "バージョン履歴、マルチホスト実行、マルチシェル対応、スケジュールトリガー、特権スクリプトの承認ワークフロー、cron + 段階的ロールアウトウィンドウを備えたスケジュール済みフリートアップグレードプロファイルを持つ保存スクリプトライブラリ。",
    "ko": "버전 기록, 다중 호스트 실행, 다중 셸 지원, 예약된 트리거, 권한 있는 스크립트의 승인 워크플로, cron 및 단계적 롤아웃 윈도우가 있는 예약된 플릿 업그레이드 프로필을 갖춘 저장된 스크립트 라이브러리.",
    "zh_CN": "已保存脚本库，具有版本历史、多主机执行、多 shell 支持、计划触发器、特权脚本审批工作流以及带 cron 和分阶段推出窗口的计划舰队升级配置文件。",
    "zh_TW": "已儲存腳本程式庫，具備版本歷史記錄、多主機執行、多 shell 支援、排程觸發、特權腳本審核工作流程以及帶 cron 與分階段推出視窗的排程機隊升級設定檔。",
    "ar": "مكتبة سكربتات محفوظة مع سجل الإصدارات والتنفيذ متعدد المضيفين ودعم أصداف متعددة ومشغلات مجدولة وسير عمل الموافقة للسكربتات المتميزة وملفات تعريف ترقية الأسطول المجدولة مع نوافذ cron وطرح مرحلي.",
    "hi": "संस्करण इतिहास, मल्टी-होस्ट निष्पादन, मल्टी-शेल समर्थन, अनुसूचित ट्रिगर, विशेषाधिकार प्राप्त स्क्रिप्ट के लिए अनुमोदन वर्कफ़्लो, और cron + चरणबद्ध रोलआउट विंडो के साथ अनुसूचित फ़्लीट अपग्रेड प्रोफ़ाइल वाली सहेजी गई स्क्रिप्ट लाइब्रेरी।",
}

UPGRADE_FEATURE_BY_LOCALE = {
    "de": "Geplante Flotten-Upgrade-Profile (cron + gestaffelte Fenster)",
    "es": "Perfiles de actualización de flota programados (cron + ventanas escalonadas)",
    "fr": "Profils de mise à niveau de parc planifiés (cron + fenêtres échelonnées)",
    "it": "Profili di aggiornamento della flotta pianificati (cron + finestre scaglionate)",
    "pt": "Perfis de atualização de frota agendados (cron + janelas escalonadas)",
    "nl": "Geplande vloot-upgradeprofielen (cron + gefaseerde vensters)",
    "ru": "Запланированные профили обновления парка (cron + поэтапные окна)",
    "ja": "スケジュール済みフリートアップグレードプロファイル（cron + 段階的ウィンドウ）",
    "ko": "예약된 플릿 업그레이드 프로필 (cron + 단계적 윈도우)",
    "zh_CN": "计划舰队升级配置文件（cron + 分阶段窗口）",
    "zh_TW": "排程機隊升級設定檔（cron + 分階段視窗）",
    "ar": "ملفات تعريف ترقية الأسطول المجدولة (cron + نوافذ مرحلية)",
    "hi": "अनुसूचित फ़्लीट अपग्रेड प्रोफ़ाइल (cron + चरणबद्ध विंडो)",
}


def set_dotted(d, dotted_key, value):
    parts = dotted_key.split(".")
    cur = d
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def keys_for(locale):
    out = dict(EN)
    if locale == "en":
        return out
    out["docs.api.phase8.upgrade.title"] = TITLE_BY_LOCALE[locale]
    out["docs.api.phase8.upgrade.intro"] = INTRO_BY_LOCALE[locale]
    out["pro_plus.docs.modules.automation_engine.description"] = DESCRIPTION_BY_LOCALE[locale]
    out["pro_plus.docs.modules.automation_engine.features.upgrade_profiles"] = (
        UPGRADE_FEATURE_BY_LOCALE[locale]
    )
    return out


def main():
    locales = ["en", "de", "es", "fr", "it", "pt", "nl", "ru", "ja", "ko",
               "zh_CN", "zh_TW", "ar", "hi"]
    for locale in locales:
        path = os.path.join(HERE, f"{locale}.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in keys_for(locale).items():
            set_dotted(data, k, v)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"  {locale}: {len(keys_for(locale))} keys written")


if __name__ == "__main__":
    main()
