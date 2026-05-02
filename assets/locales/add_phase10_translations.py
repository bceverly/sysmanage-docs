#!/usr/bin/env python3
"""Add Phase 10 translations for the new doc keys.

Covers:
  * docs.api.engines.*               (Pro+ Engines API Reference page)
  * docs.getting_started.profile.*   (Profile & Account page)
  * docs.getting_started.host_details.*  (Host Details Walkthrough)

Strategy (per the DOCS_AUDIT.md plan): translate short UI labels (titles,
tab names, breadcrumbs) into all 14 supported languages.  For long
descriptive paragraphs, keep the English value and write a parallel
``__needs_translation__: true`` companion entry under the same
parent so a later translation pass can find them.

Run from any cwd; uses absolute paths.
"""

import json
from pathlib import Path

LOCALES_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Short-key translations — applied directly.  Each row is the dot-path key
# and a 13-tuple of translations in the order:
# (de, es, fr, it, pt, nl, ja, ko, zh_CN, zh_TW, ar, hi, ru)
# English is the canonical, kept in en.json as-is.
# ---------------------------------------------------------------------------

SHORT_TRANSLATIONS: dict = {
    # --- docs.api.engines (Pro+ Engines API Reference) ---
    "docs.api.engines.alerting.title": (
        "Alerting Engine", "Motor de alertas", "Moteur d'alerting", "Motore di alerting",
        "Motor de alertas", "Alerting-engine",
        "アラートエンジン", "알림 엔진", "告警引擎", "告警引擎",
        "محرك التنبيهات", "अलर्टिंग इंजन", "Движок алертов",
    ),
    "docs.api.engines.audit.title": (
        "Audit-Engine", "Motor de auditoría", "Moteur d'audit", "Motore di audit",
        "Motor de auditoria", "Audit-engine",
        "監査エンジン", "감사 엔진", "审计引擎", "稽核引擎",
        "محرك التدقيق", "ऑडिट इंजन", "Движок аудита",
    ),
    "docs.api.engines.automation.title": (
        "Automatisierungs-Engine", "Motor de automatización", "Moteur d'automatisation",
        "Motore di automazione", "Motor de automação", "Automatiseringsengine",
        "自動化エンジン", "자동화 엔진", "自动化引擎", "自動化引擎",
        "محرك الأتمتة", "स्वचालन इंजन", "Движок автоматизации",
    ),
    "docs.api.engines.av.title": (
        "AV-Management-Engine", "Motor de gestión AV", "Moteur de gestion AV",
        "Motore di gestione AV", "Motor de gestão de AV", "AV-beheerengine",
        "AV管理エンジン", "AV 관리 엔진", "AV 管理引擎", "AV 管理引擎",
        "محرك إدارة مكافحة الفيروسات", "एवी प्रबंधन इंजन", "Движок управления AV",
    ),
    "docs.api.engines.breadcrumb": (
        "Pro+ Engines", "Motores Pro+", "Moteurs Pro+", "Motori Pro+",
        "Motores Pro+", "Pro+ engines",
        "Pro+ エンジン", "Pro+ 엔진", "Pro+ 引擎", "Pro+ 引擎",
        "محركات Pro+", "Pro+ इंजन", "Движки Pro+",
    ),
    "docs.api.engines.compliance.title": (
        "Compliance-Engine", "Motor de cumplimiento", "Moteur de conformité",
        "Motore di compliance", "Motor de conformidade", "Compliance-engine",
        "コンプライアンスエンジン", "규정 준수 엔진", "合规引擎", "合規引擎",
        "محرك الامتثال", "अनुपालन इंजन", "Движок соответствия",
    ),
    "docs.api.engines.containers.title": (
        "Container-Engine", "Motor de contenedores", "Moteur de conteneurs",
        "Motore container", "Motor de contêineres", "Container-engine",
        "コンテナエンジン", "컨테이너 엔진", "容器引擎", "容器引擎",
        "محرك الحاويات", "कंटेनर इंजन", "Движок контейнеров",
    ),
    "docs.api.engines.firewall.title": (
        "Firewall-Orchestrierungs-Engine", "Motor de orquestación de firewall",
        "Moteur d'orchestration de pare-feu", "Motore di orchestrazione firewall",
        "Motor de orquestração de firewall", "Firewall-orkestratie-engine",
        "ファイアウォール統合エンジン", "방화벽 오케스트레이션 엔진",
        "防火墙编排引擎", "防火牆編排引擎",
        "محرك تنسيق جدار الحماية", "फ़ायरवॉल ऑर्केस्ट्रेशन इंजन",
        "Движок оркестрации брандмауэра",
    ),
    "docs.api.engines.fleet.title": (
        "Flotten-Engine", "Motor de flota", "Moteur de flotte", "Motore della flotta",
        "Motor de frota", "Vloot-engine",
        "フリートエンジン", "플릿 엔진", "舰队引擎", "艦隊引擎",
        "محرك الأسطول", "फ्लीट इंजन", "Движок флота",
    ),
    "docs.api.engines.header.title": (
        "Pro+ Engines API-Referenz", "Referencia API de motores Pro+",
        "Référence API des moteurs Pro+", "Riferimento API motori Pro+",
        "Referência da API dos motores Pro+", "Pro+ engines API-referentie",
        "Pro+ エンジン API リファレンス", "Pro+ 엔진 API 참조",
        "Pro+ 引擎 API 参考", "Pro+ 引擎 API 參考",
        "مرجع API محركات Pro+", "Pro+ इंजन API संदर्भ",
        "Справочник API движков Pro+",
    ),
    "docs.api.engines.health.title": (
        "Health-Engine", "Motor de salud", "Moteur de santé", "Motore di salute",
        "Motor de saúde", "Health-engine",
        "ヘルスエンジン", "헬스 엔진", "健康引擎", "健康引擎",
        "محرك الصحة", "स्वास्थ्य इंजन", "Движок состояния",
    ),
    "docs.api.engines.observability.title": (
        "Observability-Engine", "Motor de observabilidad", "Moteur d'observabilité",
        "Motore di osservabilità", "Motor de observabilidade", "Observability-engine",
        "オブザーバビリティエンジン", "관측성 엔진", "可观测性引擎", "可觀測性引擎",
        "محرك المراقبة", "ऑब्ज़र्वबिलिटी इंजन", "Движок наблюдаемости",
    ),
    "docs.api.engines.page_title": (
        "Pro+ Engines API-Referenz - SysManage",
        "Referencia API de motores Pro+ - SysManage",
        "Référence API des moteurs Pro+ - SysManage",
        "Riferimento API motori Pro+ - SysManage",
        "Referência da API dos motores Pro+ - SysManage",
        "Pro+ engines API-referentie - SysManage",
        "Pro+ エンジン API リファレンス - SysManage",
        "Pro+ 엔진 API 참조 - SysManage",
        "Pro+ 引擎 API 参考 - SysManage",
        "Pro+ 引擎 API 參考 - SysManage",
        "مرجع API محركات Pro+ - SysManage",
        "Pro+ इंजन API संदर्भ - SysManage",
        "Справочник API движков Pro+ - SysManage",
    ),
    "docs.api.engines.secrets.title": (
        "Secrets-Engine", "Motor de secretos", "Moteur de secrets", "Motore segreti",
        "Motor de segredos", "Secrets-engine",
        "シークレットエンジン", "시크릿 엔진", "密钥引擎", "密鑰引擎",
        "محرك الأسرار", "सीक्रेट्स इंजन", "Движок секретов",
    ),
    "docs.api.engines.virtualization.title": (
        "Virtualisierungs-Engine", "Motor de virtualización", "Moteur de virtualisation",
        "Motore di virtualizzazione", "Motor de virtualização", "Virtualisatie-engine",
        "仮想化エンジン", "가상화 엔진", "虚拟化引擎", "虛擬化引擎",
        "محرك الافتراضية", "वर्चुअलाइज़ेशन इंजन", "Движок виртуализации",
    ),
    "docs.api.engines.vulns.title": (
        "Schwachstellen-Engine", "Motor de vulnerabilidades", "Moteur de vulnérabilités",
        "Motore vulnerabilità", "Motor de vulnerabilidades", "Kwetsbaarheids-engine",
        "脆弱性エンジン", "취약점 엔진", "漏洞引擎", "漏洞引擎",
        "محرك الثغرات", "भेद्यता इंजन", "Движок уязвимостей",
    ),

    # --- docs.getting_started.profile (Profile & Account page) ---
    "docs.getting_started.profile.api_tokens.title": (
        "API-Tokens", "Tokens de API", "Jetons API", "Token API",
        "Tokens da API", "API-tokens",
        "API トークン", "API 토큰", "API 令牌", "API 權杖",
        "رموز API", "API टोकन", "Токены API",
    ),
    "docs.getting_started.profile.audit.title": (
        "Mein Audit-Log", "Mi registro de auditoría", "Mon journal d'audit",
        "Il mio log di audit", "Meu log de auditoria", "Mijn auditlogboek",
        "私の監査ログ", "내 감사 로그", "我的审计日志", "我的稽核日誌",
        "سجل التدقيق الخاص بي", "मेरा ऑडिट लॉग", "Мой журнал аудита",
    ),
    "docs.getting_started.profile.breadcrumb": (
        "Profil & Konto", "Perfil y cuenta", "Profil & compte", "Profilo e account",
        "Perfil e conta", "Profiel & account",
        "プロフィール & アカウント", "프로필 및 계정", "个人资料和账户", "個人資料與帳號",
        "الملف الشخصي والحساب", "प्रोफ़ाइल और खाता", "Профиль и учётная запись",
    ),
    "docs.getting_started.profile.header.title": (
        "Profil & Konto", "Perfil y cuenta", "Profil & compte", "Profilo e account",
        "Perfil e conta", "Profiel & account",
        "プロフィール & アカウント", "프로필 및 계정", "个人资料和账户", "個人資料與帳號",
        "الملف الشخصي والحساب", "प्रोफ़ाइल और खाता", "Профиль и учётная запись",
    ),
    "docs.getting_started.profile.language.title": (
        "Sprache", "Idioma", "Langue", "Lingua",
        "Idioma", "Taal",
        "言語", "언어", "语言", "語言",
        "اللغة", "भाषा", "Язык",
    ),
    "docs.getting_started.profile.mfa.title": (
        "Multi-Faktor-Authentifizierung", "Autenticación multifactor",
        "Authentification multi-facteurs", "Autenticazione multi-fattore",
        "Autenticação multifator", "Multifactor-authenticatie",
        "多要素認証", "다중 요소 인증", "多因素认证", "多因素驗證",
        "المصادقة متعددة العوامل", "बहु-कारक प्रमाणीकरण",
        "Многофакторная аутентификация",
    ),
    "docs.getting_started.profile.page_title": (
        "Profil & Konto - SysManage", "Perfil y cuenta - SysManage",
        "Profil & compte - SysManage", "Profilo e account - SysManage",
        "Perfil e conta - SysManage", "Profiel & account - SysManage",
        "プロフィール & アカウント - SysManage", "프로필 및 계정 - SysManage",
        "个人资料和账户 - SysManage", "個人資料與帳號 - SysManage",
        "الملف الشخصي والحساب - SysManage", "प्रोफ़ाइल और खाता - SysManage",
        "Профиль и учётная запись - SysManage",
    ),
    "docs.getting_started.profile.password.title": (
        "Passwort ändern", "Cambiar contraseña", "Changer le mot de passe",
        "Cambia password", "Alterar senha", "Wachtwoord wijzigen",
        "パスワード変更", "비밀번호 변경", "更改密码", "變更密碼",
        "تغيير كلمة المرور", "पासवर्ड बदलें", "Сменить пароль",
    ),

    # --- docs.getting_started.host_details (Host Details Walkthrough) ---
    "docs.getting_started.host_details.action_menu.title": (
        "Aktionsmenü (oben rechts)", "Menú de acciones (superior derecha)",
        "Menu d'actions (en haut à droite)", "Menu azioni (in alto a destra)",
        "Menu de ações (canto superior direito)", "Actiemenu (rechtsboven)",
        "アクションメニュー(右上)", "작업 메뉴 (우측 상단)",
        "操作菜单(右上)", "動作選單(右上)",
        "قائمة الإجراءات (أعلى اليمين)", "क्रिया मेनू (ऊपर दाएँ)",
        "Меню действий (вверху справа)",
    ),
    "docs.getting_started.host_details.breadcrumb": (
        "Host-Details-Anleitung", "Tutorial de detalles del host",
        "Visite guidée des détails de l'hôte", "Tour dei dettagli dell'host",
        "Tour dos detalhes do host", "Hostdetails-rondleiding",
        "ホスト詳細ガイド", "호스트 상세 가이드",
        "主机详情演练", "主機詳細導覽",
        "جولة تفاصيل المضيف", "होस्ट विवरण वॉकथ्रू",
        "Обзор сведений о хосте",
    ),
    "docs.getting_started.host_details.header.title": (
        "Host-Details-Anleitung", "Tutorial de detalles del host",
        "Visite guidée des détails de l'hôte", "Tour dei dettagli dell'host",
        "Tour dos detalhes do host", "Hostdetails-rondleiding",
        "ホスト詳細ガイド", "호스트 상세 가이드",
        "主机详情演练", "主機詳細導覽",
        "جولة تفاصيل المضيف", "होस्ट विवरण वॉकथ्रू",
        "Обзор сведений о хосте",
    ),
    "docs.getting_started.host_details.intro.title": (
        "Host-Details öffnen", "Abrir detalles del host", "Ouvrir les détails de l'hôte",
        "Apri i dettagli dell'host", "Abrir detalhes do host", "Hostdetails openen",
        "ホスト詳細を開く", "호스트 상세 열기", "打开主机详情", "開啟主機詳細",
        "فتح تفاصيل المضيف", "होस्ट विवरण खोलें", "Открыть сведения о хосте",
    ),
    "docs.getting_started.host_details.page_title": (
        "Host-Details-Anleitung - SysManage", "Tutorial de detalles del host - SysManage",
        "Visite guidée des détails de l'hôte - SysManage",
        "Tour dei dettagli dell'host - SysManage",
        "Tour dos detalhes do host - SysManage",
        "Hostdetails-rondleiding - SysManage",
        "ホスト詳細ガイド - SysManage", "호스트 상세 가이드 - SysManage",
        "主机详情演练 - SysManage", "主機詳細導覽 - SysManage",
        "جولة تفاصيل المضيف - SysManage", "होस्ट विवरण वॉकथ्रू - SysManage",
        "Обзор сведений о хосте - SysManage",
    ),
    "docs.getting_started.host_details.tabs.title": (
        "Tab-für-Tab-Referenz", "Referencia pestaña a pestaña",
        "Référence onglet par onglet", "Riferimento per scheda",
        "Referência aba a aba", "Tab-voor-tab-referentie",
        "タブ別リファレンス", "탭별 참조",
        "逐标签参考", "逐標籤參考",
        "مرجع علامة تبويب تلو الأخرى", "टैब-दर-टैब संदर्भ",
        "Справочник по вкладкам",
    ),
    "docs.getting_started.host_details.tabs.access": (
        "Zugriff", "Acceso", "Accès", "Accesso",
        "Acesso", "Toegang",
        "アクセス", "접근", "访问", "存取",
        "الوصول", "एक्सेस", "Доступ",
    ),
    "docs.getting_started.host_details.tabs.certificates": (
        "Zertifikate", "Certificados", "Certificats", "Certificati",
        "Certificados", "Certificaten",
        "証明書", "인증서", "证书", "憑證",
        "الشهادات", "प्रमाणपत्र", "Сертификаты",
    ),
    "docs.getting_started.host_details.tabs.child_hosts": (
        "Untergeordnete Hosts", "Hosts secundarios", "Hôtes enfants", "Host figli",
        "Hosts filhos", "Onderliggende hosts",
        "子ホスト", "자식 호스트", "子主机", "子主機",
        "المضيفون التابعون", "चाइल्ड होस्ट", "Дочерние хосты",
    ),
    "docs.getting_started.host_details.tabs.compliance": (
        "Compliance", "Cumplimiento", "Conformité", "Conformità",
        "Conformidade", "Compliance",
        "コンプライアンス", "규정 준수", "合规", "合規",
        "الامتثال", "अनुपालन", "Соответствие",
    ),
    "docs.getting_started.host_details.tabs.diagnostics": (
        "Diagnose", "Diagnóstico", "Diagnostics", "Diagnostica",
        "Diagnóstico", "Diagnostiek",
        "診断", "진단", "诊断", "診斷",
        "التشخيص", "निदान", "Диагностика",
    ),
    "docs.getting_started.host_details.tabs.hardware": (
        "Hardware", "Hardware", "Matériel", "Hardware",
        "Hardware", "Hardware",
        "ハードウェア", "하드웨어", "硬件", "硬體",
        "العتاد", "हार्डवेयर", "Оборудование",
    ),
    "docs.getting_started.host_details.tabs.info": (
        "Info", "Información", "Info", "Info",
        "Informações", "Info",
        "情報", "정보", "信息", "資訊",
        "معلومات", "जानकारी", "Информация",
    ),
    "docs.getting_started.host_details.tabs.security": (
        "Sicherheit", "Seguridad", "Sécurité", "Sicurezza",
        "Segurança", "Beveiliging",
        "セキュリティ", "보안", "安全", "安全",
        "الأمان", "सुरक्षा", "Безопасность",
    ),
    "docs.getting_started.host_details.tabs.server_roles": (
        "Server-Rollen", "Roles de servidor", "Rôles serveur", "Ruoli server",
        "Funções do servidor", "Serverrollen",
        "サーバーロール", "서버 역할", "服务器角色", "伺服器角色",
        "أدوار الخادم", "सर्वर भूमिकाएँ", "Роли сервера",
    ),
    "docs.getting_started.host_details.tabs.software": (
        "Software", "Software", "Logiciels", "Software",
        "Software", "Software",
        "ソフトウェア", "소프트웨어", "软件", "軟體",
        "البرامج", "सॉफ़्टवेयर", "Программное обеспечение",
    ),
    "docs.getting_started.host_details.tabs.software_changes": (
        "Software-Änderungen", "Cambios de software", "Modifications logiciel",
        "Modifiche software", "Mudanças de software", "Softwarewijzigingen",
        "ソフトウェア変更", "소프트웨어 변경 사항",
        "软件变更", "軟體變更",
        "تغييرات البرامج", "सॉफ़्टवेयर परिवर्तन", "Изменения ПО",
    ),
    "docs.getting_started.host_details.tabs.third_party_repos": (
        "Drittanbieter-Repositories", "Repositorios de terceros",
        "Dépôts tiers", "Repository di terze parti",
        "Repositórios de terceiros", "Externe repositories",
        "サードパーティリポジトリ", "타사 저장소",
        "第三方仓库", "第三方儲存庫",
        "مستودعات الطرف الثالث", "तृतीय-पक्ष रिपॉजिटरी",
        "Сторонние репозитории",
    ),
    "docs.getting_started.host_details.tabs.ubuntu_pro": (
        "Ubuntu Pro", "Ubuntu Pro", "Ubuntu Pro", "Ubuntu Pro",
        "Ubuntu Pro", "Ubuntu Pro",
        "Ubuntu Pro", "Ubuntu Pro",
        "Ubuntu Pro", "Ubuntu Pro",
        "Ubuntu Pro", "Ubuntu Pro", "Ubuntu Pro",
    ),
}


# ---------------------------------------------------------------------------
# Long descriptive paragraphs — leave English value, but mark for follow-up
# translation.  These accompany the *.description, *_desc, *.intro.description,
# *.header.description, *.meta_description keys.  We add a sibling
# `__needs_translation__` field at the section level so a translation pass
# can find them programmatically.
# ---------------------------------------------------------------------------

# Sections where the long-form copy is intentionally left English with a
# needs-translation marker.  Each entry is the dot-prefix; we'll set
# `<prefix>.__needs_translation__` = True in every non-en locale.
LONG_FORM_SECTIONS = [
    "docs.api.engines",
    "docs.getting_started.profile",
    "docs.getting_started.host_details",
]


# ---------------------------------------------------------------------------
# Apply
# ---------------------------------------------------------------------------

LANG_ORDER = ("de", "es", "fr", "it", "pt", "nl",
              "ja", "ko", "zh_CN", "zh_TW",
              "ar", "hi", "ru")


def set_nested(d: dict, path: str, value):
    parts = path.split(".")
    cur = d
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
        if not isinstance(cur, dict):
            return False
    cur[parts[-1]] = value
    return True


def main():
    for idx, lang in enumerate(LANG_ORDER):
        path = LOCALES_DIR / f"{lang}.json"
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        applied = 0
        for key, tup in SHORT_TRANSLATIONS.items():
            if set_nested(data, key, tup[idx]):
                applied += 1
        # Mark long-form sections as needing translation
        for sec in LONG_FORM_SECTIONS:
            set_nested(data, f"{sec}.__needs_translation__", True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False, sort_keys=False)
        print(f"  {lang}: {applied} short translations applied")


if __name__ == "__main__":
    main()
