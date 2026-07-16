# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Inject Phase 10.4.2 (per-platform tab-strip) i18n keys into all 14 locales.

Pattern matches earlier 10.x i18n scripts: titles + lead-in sentences
get native translations for major locales; heavily-technical body
paragraphs (with inline <code>) keep the English source so code
references stay copy-paste-stable.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

EN = {
    # API doc bullets
    "docs.proplus.mirror.api.platform_list": "list per-platform configs",
    "docs.proplus.mirror.api.platform_create": "create a platform config",
    "docs.proplus.mirror.api.platform_update": "update a platform config",
    "docs.proplus.mirror.api.platform_delete": "delete a platform config (refuses while it owns mirrors)",
    "docs.proplus.mirror.api.setup_status": "read tooling setup status for a host",
    "docs.proplus.mirror.api.setup_refresh": "queue a tooling probe (asynchronous)",
    "docs.proplus.mirror.api.setup_install": "queue an install of the tooling for a package manager",
    "docs.proplus.mirror.api.settings": "admin settings (legacy singleton)",
    # New section: per-platform tab strip
    "docs.proplus.mirror.platforms.title": "Per-platform tab strip (Phase 10.4.2)",
    "docs.proplus.mirror.platforms.intro": "The Settings → Repository Mirroring page is laid out as a tab strip with one tab per supported platform. Today the supported platforms are <strong>Linux</strong> and <strong>FreeBSD</strong>; OpenBSD, NetBSD, macOS, and Windows are deferred until their own tooling probes and install plans are written.",
    "docs.proplus.mirror.platforms.layout": "Each tab contains three cards stacked vertically:",
    "docs.proplus.mirror.platforms.card1": "<strong>Platform Settings</strong> — searchable host picker, mirror root path on the host, retention window, integrity-check cadence, default bandwidth cap, and snapshot keep count. These values are scoped to this platform on this host, so a Linux mirror on one host and a FreeBSD mirror on another can have completely independent storage layouts.",
    "docs.proplus.mirror.platforms.card2": "<strong>Mirror Setup Status</strong> — chips for each tool the engine's plan-builders shell out to (apt-mirror, reposync, createrepo_c, trickle, rsync, curl, etc.). Refresh button queues a probe; Install Tools button queues a sudo install of the platform-appropriate package set. Both go through the agent's standard apply_deployment_plan path; the card polls the cached status row until the agent's command_result lands.",
    "docs.proplus.mirror.platforms.card3": "<strong>Mirror Repositories</strong> — the table of upstream URLs being mirrored on this platform, plus inline sync/snapshot/edit/delete actions and an Add Mirror dialog. The package manager dropdown in the dialog is filtered to those the active platform supports (apt/dnf/zypper for Linux, pkg for FreeBSD).",
    "docs.proplus.mirror.platforms.empty": "If the active tab has no platform configuration yet, an empty-state card prompts you to pick a host. The host picker only lists hosts whose detected platform matches the tab — Linux hosts on the Linux tab, FreeBSD hosts on the FreeBSD tab — to prevent misconfigured pairings.",
}

# Native translations for the section title + intro/empty sentences.
# Bullet body text + API descriptions stay English (heavy code refs).
TITLE_BY_LOCALE = {
    "de": "Plattform-spezifische Tab-Leiste (Phase 10.4.2)",
    "es": "Pestañas por plataforma (Fase 10.4.2)",
    "fr": "Barre d'onglets par plateforme (Phase 10.4.2)",
    "it": "Barra delle schede per piattaforma (Fase 10.4.2)",
    "pt": "Barra de abas por plataforma (Fase 10.4.2)",
    "nl": "Per-platform tabbalk (Fase 10.4.2)",
    "ru": "Вкладки по платформам (Этап 10.4.2)",
    "ja": "プラットフォーム別タブストリップ（フェーズ 10.4.2）",
    "ko": "플랫폼별 탭 스트립 (10.4.2 단계)",
    "zh_CN": "按平台的标签栏（阶段 10.4.2）",
    "zh_TW": "依平台分頁列（階段 10.4.2）",
    "ar": "شريط علامات تبويب لكل منصة (المرحلة 10.4.2)",
    "hi": "प्लेटफ़ॉर्म-वार टैब स्ट्रिप (चरण 10.4.2)",
}

INTRO_BY_LOCALE = {
    "de": "Die Seite Einstellungen → Repository-Spiegelung ist als Tab-Leiste mit einer Registerkarte pro unterstützter Plattform aufgebaut. Heute werden <strong>Linux</strong> und <strong>FreeBSD</strong> unterstützt; OpenBSD, NetBSD, macOS und Windows sind zurückgestellt, bis ihre eigenen Tool-Sonden und Installationspläne geschrieben sind.",
    "es": "La página Configuración → Espejado de repositorios se presenta como una barra de pestañas con una pestaña por plataforma compatible. Actualmente se admiten <strong>Linux</strong> y <strong>FreeBSD</strong>; OpenBSD, NetBSD, macOS y Windows quedan pospuestos hasta que se escriban sus propias sondas de herramientas y planes de instalación.",
    "fr": "La page Paramètres → Mise en miroir des dépôts est présentée comme une barre d'onglets avec un onglet par plateforme prise en charge. Actuellement, <strong>Linux</strong> et <strong>FreeBSD</strong> sont pris en charge ; OpenBSD, NetBSD, macOS et Windows sont reportés jusqu'à ce que leurs sondes d'outils et plans d'installation soient écrits.",
    "it": "La pagina Impostazioni → Mirroring repository è organizzata come una barra di schede con una scheda per piattaforma supportata. Attualmente sono supportate <strong>Linux</strong> e <strong>FreeBSD</strong>; OpenBSD, NetBSD, macOS e Windows sono rimandati finché non vengono scritte le rispettive sonde e piani di installazione.",
    "pt": "A página Configurações → Espelhamento de repositórios é apresentada como uma barra de abas com uma aba por plataforma suportada. Atualmente suportadas: <strong>Linux</strong> e <strong>FreeBSD</strong>; OpenBSD, NetBSD, macOS e Windows ficam adiados até que suas próprias sondas e planos de instalação sejam escritos.",
    "nl": "De pagina Instellingen → Repository-mirroring is opgezet als een tabbalk met één tabblad per ondersteund platform. Vandaag worden <strong>Linux</strong> en <strong>FreeBSD</strong> ondersteund; OpenBSD, NetBSD, macOS en Windows zijn uitgesteld totdat hun eigen tooling-probes en installatieplannen zijn geschreven.",
    "ru": "Страница «Настройки → Зеркалирование репозиториев» оформлена как панель вкладок с одной вкладкой на каждую поддерживаемую платформу. Сегодня поддерживаются <strong>Linux</strong> и <strong>FreeBSD</strong>; OpenBSD, NetBSD, macOS и Windows отложены до написания собственных проб инструментов и планов установки.",
    "ja": "設定 → リポジトリミラーリングページは、サポートされているプラットフォームごとに 1 つのタブを持つタブストリップとして構成されています。現在サポートされているのは <strong>Linux</strong> と <strong>FreeBSD</strong> です。OpenBSD、NetBSD、macOS、Windows は、それぞれのツールプローブとインストールプランが書かれるまで延期されています。",
    "ko": "설정 → 저장소 미러링 페이지는 지원되는 플랫폼별로 탭 하나가 있는 탭 스트립으로 구성됩니다. 현재 <strong>Linux</strong>와 <strong>FreeBSD</strong>가 지원되며, OpenBSD, NetBSD, macOS, Windows는 각자의 도구 프로브와 설치 플랜이 작성될 때까지 연기되었습니다.",
    "zh_CN": "设置 → 仓库镜像页面以标签栏形式展示，每个支持的平台对应一个标签。目前支持 <strong>Linux</strong> 和 <strong>FreeBSD</strong>；OpenBSD、NetBSD、macOS 和 Windows 推迟到其各自的工具探测和安装计划编写完成后再支持。",
    "zh_TW": "設定 → 儲存庫鏡像頁面以分頁列形式呈現，每個支援的平台對應一個分頁。目前支援 <strong>Linux</strong> 與 <strong>FreeBSD</strong>；OpenBSD、NetBSD、macOS 與 Windows 延後至各自的工具探測與安裝計畫撰寫完成後再支援。",
    "ar": "صفحة الإعدادات ← نسخ المستودعات معروضة كشريط علامات تبويب بعلامة تبويب لكل منصة مدعومة. المنصات المدعومة حاليًا هي <strong>Linux</strong> و<strong>FreeBSD</strong>؛ تم تأجيل OpenBSD وNetBSD وmacOS وWindows حتى كتابة مسبارات الأدوات وخطط التثبيت الخاصة بها.",
    "hi": "सेटिंग्स → रिपॉजिटरी मिररिंग पृष्ठ एक टैब स्ट्रिप के रूप में व्यवस्थित है, जिसमें प्रत्येक समर्थित प्लेटफ़ॉर्म के लिए एक टैब है। वर्तमान में <strong>Linux</strong> और <strong>FreeBSD</strong> समर्थित हैं; OpenBSD, NetBSD, macOS, और Windows को उनके स्वयं के टूल प्रोब और इंस्टॉल प्लान लिखे जाने तक स्थगित कर दिया गया है।",
}

EMPTY_BY_LOCALE = {
    "de": "Wenn die aktive Registerkarte noch keine Plattformkonfiguration hat, fordert eine Leerzustandskarte zum Auswählen eines Hosts auf. Die Host-Auswahl listet nur Hosts auf, deren erkannte Plattform zur Registerkarte passt — Linux-Hosts auf der Linux-Registerkarte, FreeBSD-Hosts auf der FreeBSD-Registerkarte — um Fehlkonfigurationen zu verhindern.",
    "es": "Si la pestaña activa aún no tiene configuración de plataforma, una tarjeta de estado vacío le pide que seleccione un host. El selector de host solo enumera hosts cuya plataforma detectada coincide con la pestaña — hosts Linux en la pestaña Linux, hosts FreeBSD en la pestaña FreeBSD — para evitar emparejamientos mal configurados.",
    "fr": "Si l'onglet actif n'a pas encore de configuration de plateforme, une carte d'état vide vous invite à choisir un hôte. Le sélecteur d'hôte ne liste que les hôtes dont la plateforme détectée correspond à l'onglet — les hôtes Linux sur l'onglet Linux, les hôtes FreeBSD sur l'onglet FreeBSD — pour éviter les appariements mal configurés.",
    "it": "Se la scheda attiva non ha ancora una configurazione della piattaforma, una scheda di stato vuoto richiede di selezionare un host. Il selettore di host elenca solo gli host la cui piattaforma rilevata corrisponde alla scheda — host Linux sulla scheda Linux, host FreeBSD sulla scheda FreeBSD — per evitare accoppiamenti mal configurati.",
    "pt": "Se a aba ativa ainda não tiver configuração de plataforma, um cartão de estado vazio solicita a escolha de um host. O seletor de host lista apenas hosts cuja plataforma detectada corresponde à aba — hosts Linux na aba Linux, hosts FreeBSD na aba FreeBSD — para evitar emparelhamentos mal configurados.",
    "nl": "Als het actieve tabblad nog geen platformconfiguratie heeft, vraagt een leeg-statuskaart u een host te kiezen. De host-kiezer toont alleen hosts waarvan het gedetecteerde platform overeenkomt met het tabblad — Linux-hosts op het Linux-tabblad, FreeBSD-hosts op het FreeBSD-tabblad — om verkeerd geconfigureerde combinaties te voorkomen.",
    "ru": "Если у активной вкладки ещё нет конфигурации платформы, карточка пустого состояния предлагает выбрать узел. Селектор узлов перечисляет только узлы, обнаруженная платформа которых совпадает со вкладкой — Linux-узлы на вкладке Linux, FreeBSD-узлы на вкладке FreeBSD — чтобы предотвратить неправильно настроенные пары.",
    "ja": "アクティブなタブにまだプラットフォーム設定がない場合、空状態のカードがホストの選択を促します。ホストピッカーは、検出されたプラットフォームがタブと一致するホスト（Linux タブには Linux ホスト、FreeBSD タブには FreeBSD ホスト）のみをリストし、誤った組み合わせの設定を防ぎます。",
    "ko": "활성 탭에 아직 플랫폼 구성이 없으면 빈 상태 카드가 호스트를 선택하도록 안내합니다. 호스트 선택기는 감지된 플랫폼이 탭과 일치하는 호스트만 나열합니다 — Linux 탭에는 Linux 호스트, FreeBSD 탭에는 FreeBSD 호스트 — 잘못 구성된 쌍을 방지합니다.",
    "zh_CN": "如果活动标签尚未配置平台，空状态卡片会提示您选择主机。主机选择器仅列出检测到的平台与标签匹配的主机 — Linux 标签上仅列 Linux 主机，FreeBSD 标签上仅列 FreeBSD 主机 — 以防止配置错误的配对。",
    "zh_TW": "若使用中的分頁尚未設定平台，空白狀態卡片會提示您選擇主機。主機選擇器僅列出偵測到的平台與分頁相符的主機 — Linux 分頁僅列 Linux 主機，FreeBSD 分頁僅列 FreeBSD 主機 — 以防止組態錯誤的配對。",
    "ar": "إذا لم يكن لعلامة التبويب النشطة أي تكوين منصة بعد، تطلب منك بطاقة الحالة الفارغة اختيار مضيف. يسرد منتقي المضيف فقط المضيفين الذين تتطابق منصتهم المكتشفة مع علامة التبويب — مضيفو Linux على علامة تبويب Linux، ومضيفو FreeBSD على علامة تبويب FreeBSD — لمنع الاقترانات المهيأة بشكل خاطئ.",
    "hi": "यदि सक्रिय टैब में अभी तक कोई प्लेटफ़ॉर्म कॉन्फ़िगरेशन नहीं है, तो एक खाली-स्थिति कार्ड आपको होस्ट चुनने के लिए कहता है। होस्ट पिकर केवल उन होस्टों को सूचीबद्ध करता है जिनका पहचाना गया प्लेटफ़ॉर्म टैब से मेल खाता है — Linux टैब पर Linux होस्ट, FreeBSD टैब पर FreeBSD होस्ट — गलत-कॉन्फ़िगर्ड जोड़ियों को रोकने के लिए।",
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
    out["docs.proplus.mirror.platforms.title"] = TITLE_BY_LOCALE[locale]
    out["docs.proplus.mirror.platforms.intro"] = INTRO_BY_LOCALE[locale]
    out["docs.proplus.mirror.platforms.empty"] = EMPTY_BY_LOCALE[locale]
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
