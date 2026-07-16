# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Phase 10.4.3 i18n: per-PM tab labels + revised intro/snaps text.

The earlier 10.4.2 keys (`docs.proplus.mirror.platforms.intro` etc)
referenced two tabs (Linux, FreeBSD).  10.4.3 retunes that to four
tabs keyed on the package manager, so the intro paragraph rewrites
and a new "snaps" paragraph lands.  Tab labels themselves are short
proper nouns so they share the EN string across most locales except
where a non-Latin script is the convention.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

EN = {
    "docs.proplus.mirror.platforms.title": "Per-platform tab strip (Phase 10.4.3)",
    "docs.proplus.mirror.platforms.intro": "The Settings → Repository Mirroring page is laid out as a tab strip with one tab per package manager. Today the four tabs are <strong>Ubuntu/Debian</strong> (apt), <strong>RHEL/Fedora</strong> (dnf — covers RHEL, Fedora, Oracle Linux, Rocky, Alma, CentOS Stream), <strong>openSUSE/SLES</strong> (zypper), and <strong>FreeBSD</strong> (pkg). Each tab represents one mirror host running one PM, so the Add Mirror dialog inherits its package manager from the active tab and the host picker filters to OS-family matches (Linux hosts on apt/dnf/zypper tabs, FreeBSD hosts on the pkg tab).",
    "docs.proplus.mirror.platforms.snaps": "<strong>Snaps:</strong> not supported. Mirroring snap packages requires Canonical's commercial Snap Store Proxy product (separate auth + HTTP API, not file-level), which is out of scope for this engine. OpenBSD, NetBSD, macOS, and Windows are deferred until their own tooling probes and install plans are written.",
    # Tab labels in the frontend (mirror.platform.*).  These are
    # generally proper-noun-ish ("Ubuntu/Debian", "FreeBSD") so most
    # locales keep them verbatim.
    "mirror.platform.apt": "Ubuntu/Debian",
    "mirror.platform.dnf": "RHEL/Fedora",
    "mirror.platform.zypper": "openSUSE/SLES",
    "mirror.platform.pkg": "FreeBSD",
}

# Native translations for the section title + intro/snaps where the
# rendered prose benefits from translation.  Distro brand names stay
# untouched in every locale (proper nouns).
TITLE_BY_LOCALE = {
    "de": "Tab-Leiste pro Paketmanager (Phase 10.4.3)",
    "es": "Pestañas por gestor de paquetes (Fase 10.4.3)",
    "fr": "Onglets par gestionnaire de paquets (Phase 10.4.3)",
    "it": "Schede per gestore di pacchetti (Fase 10.4.3)",
    "pt": "Abas por gerenciador de pacotes (Fase 10.4.3)",
    "nl": "Tabbladen per pakketbeheerder (Fase 10.4.3)",
    "ru": "Вкладки по менеджерам пакетов (Этап 10.4.3)",
    "ja": "パッケージマネージャー別タブ（フェーズ 10.4.3）",
    "ko": "패키지 관리자별 탭 (10.4.3 단계)",
    "zh_CN": "按包管理器分页（阶段 10.4.3）",
    "zh_TW": "依套件管理員分頁（階段 10.4.3）",
    "ar": "علامات تبويب لكل مدير حزم (المرحلة 10.4.3)",
    "hi": "पैकेज प्रबंधक-वार टैब (चरण 10.4.3)",
}

INTRO_BY_LOCALE = {
    "de": "Die Seite Einstellungen → Repository-Spiegelung ist als Tab-Leiste mit einer Registerkarte pro Paketmanager aufgebaut. Heute gibt es vier Registerkarten: <strong>Ubuntu/Debian</strong> (apt), <strong>RHEL/Fedora</strong> (dnf — deckt RHEL, Fedora, Oracle Linux, Rocky, Alma, CentOS Stream ab), <strong>openSUSE/SLES</strong> (zypper) und <strong>FreeBSD</strong> (pkg). Jede Registerkarte steht für einen Mirror-Host mit einem PM; der Dialog zum Hinzufügen eines Mirrors übernimmt den Paketmanager von der aktiven Registerkarte und der Host-Picker filtert nach übereinstimmender OS-Familie.",
    "es": "La página Configuración → Espejado de repositorios se presenta como una barra de pestañas con una pestaña por gestor de paquetes. Hoy hay cuatro pestañas: <strong>Ubuntu/Debian</strong> (apt), <strong>RHEL/Fedora</strong> (dnf — cubre RHEL, Fedora, Oracle Linux, Rocky, Alma, CentOS Stream), <strong>openSUSE/SLES</strong> (zypper) y <strong>FreeBSD</strong> (pkg). Cada pestaña representa un host de espejo ejecutando un PM, por lo que el diálogo Agregar Espejo hereda su gestor de paquetes de la pestaña activa.",
    "fr": "La page Paramètres → Mise en miroir des dépôts est présentée comme une barre d'onglets avec un onglet par gestionnaire de paquets. Aujourd'hui les quatre onglets sont <strong>Ubuntu/Debian</strong> (apt), <strong>RHEL/Fedora</strong> (dnf — couvre RHEL, Fedora, Oracle Linux, Rocky, Alma, CentOS Stream), <strong>openSUSE/SLES</strong> (zypper) et <strong>FreeBSD</strong> (pkg). Chaque onglet représente un hôte miroir exécutant un PM ; la boîte de dialogue Ajouter un miroir hérite donc de son gestionnaire de paquets de l'onglet actif.",
    "it": "La pagina Impostazioni → Mirroring repository è organizzata come una barra di schede con una scheda per gestore di pacchetti. Oggi le quattro schede sono <strong>Ubuntu/Debian</strong> (apt), <strong>RHEL/Fedora</strong> (dnf — copre RHEL, Fedora, Oracle Linux, Rocky, Alma, CentOS Stream), <strong>openSUSE/SLES</strong> (zypper) e <strong>FreeBSD</strong> (pkg). Ogni scheda rappresenta un host mirror che esegue un PM, quindi il dialogo Aggiungi mirror eredita il gestore di pacchetti dalla scheda attiva.",
    "pt": "A página Configurações → Espelhamento de repositórios é apresentada como uma barra de abas com uma aba por gerenciador de pacotes. Hoje as quatro abas são <strong>Ubuntu/Debian</strong> (apt), <strong>RHEL/Fedora</strong> (dnf — cobre RHEL, Fedora, Oracle Linux, Rocky, Alma, CentOS Stream), <strong>openSUSE/SLES</strong> (zypper) e <strong>FreeBSD</strong> (pkg). Cada aba representa um host de espelho executando um PM, então o diálogo Adicionar Espelho herda seu gerenciador de pacotes da aba ativa.",
    "nl": "De pagina Instellingen → Repository-mirroring is opgezet als een tabbalk met één tabblad per pakketbeheerder. Vandaag zijn de vier tabbladen <strong>Ubuntu/Debian</strong> (apt), <strong>RHEL/Fedora</strong> (dnf — dekt RHEL, Fedora, Oracle Linux, Rocky, Alma, CentOS Stream), <strong>openSUSE/SLES</strong> (zypper) en <strong>FreeBSD</strong> (pkg). Elk tabblad vertegenwoordigt één mirror-host met één PM, dus het dialoogvenster Mirror toevoegen erft zijn pakketbeheerder van het actieve tabblad.",
    "ru": "Страница «Настройки → Зеркалирование репозиториев» оформлена как панель вкладок с одной вкладкой на каждый менеджер пакетов. Сегодня четыре вкладки: <strong>Ubuntu/Debian</strong> (apt), <strong>RHEL/Fedora</strong> (dnf — охватывает RHEL, Fedora, Oracle Linux, Rocky, Alma, CentOS Stream), <strong>openSUSE/SLES</strong> (zypper) и <strong>FreeBSD</strong> (pkg). Каждая вкладка представляет один зеркальный узел с одним PM, поэтому диалог «Добавить зеркало» наследует менеджер пакетов от активной вкладки.",
    "ja": "設定 → リポジトリミラーリングページは、パッケージマネージャーごとに 1 つのタブを持つタブストリップとして構成されています。現在、4 つのタブがあります: <strong>Ubuntu/Debian</strong> (apt)、<strong>RHEL/Fedora</strong> (dnf — RHEL、Fedora、Oracle Linux、Rocky、Alma、CentOS Stream をカバー)、<strong>openSUSE/SLES</strong> (zypper)、および <strong>FreeBSD</strong> (pkg)。各タブは 1 つの PM を実行する 1 つのミラーホストを表し、ミラー追加ダイアログはアクティブなタブからパッケージマネージャーを継承します。",
    "ko": "설정 → 저장소 미러링 페이지는 패키지 관리자별로 탭 하나가 있는 탭 스트립으로 구성됩니다. 현재 네 개의 탭이 있습니다: <strong>Ubuntu/Debian</strong> (apt), <strong>RHEL/Fedora</strong> (dnf — RHEL, Fedora, Oracle Linux, Rocky, Alma, CentOS Stream 지원), <strong>openSUSE/SLES</strong> (zypper), 및 <strong>FreeBSD</strong> (pkg). 각 탭은 하나의 PM을 실행하는 하나의 미러 호스트를 나타내므로 미러 추가 대화 상자는 활성 탭에서 패키지 관리자를 상속합니다.",
    "zh_CN": "设置 → 仓库镜像页面以标签栏形式展示，每个包管理器对应一个标签。目前有四个标签：<strong>Ubuntu/Debian</strong>（apt）、<strong>RHEL/Fedora</strong>（dnf — 覆盖 RHEL、Fedora、Oracle Linux、Rocky、Alma、CentOS Stream）、<strong>openSUSE/SLES</strong>（zypper）和 <strong>FreeBSD</strong>（pkg）。每个标签代表运行一个 PM 的一个镜像主机，因此添加镜像对话框从活动标签继承其包管理器。",
    "zh_TW": "設定 → 儲存庫鏡像頁面以分頁列形式呈現，每個套件管理員對應一個分頁。目前有四個分頁：<strong>Ubuntu/Debian</strong>（apt）、<strong>RHEL/Fedora</strong>（dnf — 涵蓋 RHEL、Fedora、Oracle Linux、Rocky、Alma、CentOS Stream）、<strong>openSUSE/SLES</strong>（zypper）與 <strong>FreeBSD</strong>（pkg）。每個分頁代表執行一個 PM 的一個鏡像主機，因此新增鏡像對話框會從使用中分頁繼承其套件管理員。",
    "ar": "صفحة الإعدادات ← نسخ المستودعات معروضة كشريط علامات تبويب بعلامة تبويب لكل مدير حزم. اليوم هناك أربع علامات تبويب: <strong>Ubuntu/Debian</strong> (apt)، <strong>RHEL/Fedora</strong> (dnf — يغطي RHEL وFedora وOracle Linux وRocky وAlma وCentOS Stream)، <strong>openSUSE/SLES</strong> (zypper)، و<strong>FreeBSD</strong> (pkg). تمثل كل علامة تبويب مضيف مرآة واحدًا يقوم بتشغيل مدير حزم واحد، لذا يرث مربع حوار إضافة مرآة مدير حزمه من علامة التبويب النشطة.",
    "hi": "सेटिंग्स → रिपॉजिटरी मिररिंग पृष्ठ एक टैब स्ट्रिप के रूप में व्यवस्थित है, जिसमें प्रत्येक पैकेज प्रबंधक के लिए एक टैब है। वर्तमान में चार टैब हैं: <strong>Ubuntu/Debian</strong> (apt), <strong>RHEL/Fedora</strong> (dnf — RHEL, Fedora, Oracle Linux, Rocky, Alma, CentOS Stream को कवर करता है), <strong>openSUSE/SLES</strong> (zypper), और <strong>FreeBSD</strong> (pkg)। प्रत्येक टैब एक PM चलाने वाले एक मिरर होस्ट का प्रतिनिधित्व करता है, इसलिए मिरर जोड़ें संवाद सक्रिय टैब से अपना पैकेज प्रबंधक प्राप्त करता है।",
}

SNAPS_BY_LOCALE = {
    "de": "<strong>Snaps:</strong> nicht unterstützt. Das Spiegeln von Snap-Paketen erfordert das kommerzielle Snap Store Proxy-Produkt von Canonical (separate Authentifizierung + HTTP-API, nicht auf Dateiebene), was außerhalb des Anwendungsbereichs dieser Engine liegt. OpenBSD, NetBSD, macOS und Windows sind zurückgestellt, bis ihre eigenen Tool-Sonden und Installationspläne geschrieben sind.",
    "es": "<strong>Snaps:</strong> no compatible. El espejado de paquetes snap requiere el producto comercial Snap Store Proxy de Canonical (autenticación + API HTTP separadas, no a nivel de archivo), que queda fuera del alcance de este motor. OpenBSD, NetBSD, macOS y Windows quedan pospuestos hasta que se escriban sus propias sondas de herramientas y planes de instalación.",
    "fr": "<strong>Snaps :</strong> non pris en charge. La mise en miroir des paquets snap nécessite le produit commercial Snap Store Proxy de Canonical (authentification + API HTTP séparées, pas au niveau fichier), qui est hors de portée de ce moteur. OpenBSD, NetBSD, macOS et Windows sont reportés jusqu'à ce que leurs sondes d'outils et plans d'installation soient écrits.",
    "it": "<strong>Snap:</strong> non supportati. Il mirroring dei pacchetti snap richiede il prodotto commerciale Snap Store Proxy di Canonical (autenticazione + API HTTP separate, non a livello di file), fuori dallo scope di questo motore. OpenBSD, NetBSD, macOS e Windows sono rimandati finché non vengono scritte le rispettive sonde e piani di installazione.",
    "pt": "<strong>Snaps:</strong> não suportado. O espelhamento de pacotes snap requer o produto comercial Snap Store Proxy da Canonical (autenticação + API HTTP separadas, não em nível de arquivo), fora do escopo deste motor. OpenBSD, NetBSD, macOS e Windows ficam adiados até que suas próprias sondas e planos de instalação sejam escritos.",
    "nl": "<strong>Snaps:</strong> niet ondersteund. Het mirroren van snap-pakketten vereist Canonical's commerciële Snap Store Proxy-product (afzonderlijke authenticatie + HTTP API, niet op bestandsniveau), wat buiten de scope van deze engine valt. OpenBSD, NetBSD, macOS en Windows zijn uitgesteld tot hun eigen tooling-probes en installatieplannen zijn geschreven.",
    "ru": "<strong>Snap-пакеты:</strong> не поддерживаются. Зеркалирование snap-пакетов требует коммерческого продукта Canonical Snap Store Proxy (отдельная аутентификация + HTTP API, не на уровне файлов), что выходит за рамки этого движка. OpenBSD, NetBSD, macOS и Windows отложены до написания собственных проб инструментов и планов установки.",
    "ja": "<strong>Snap:</strong> サポートされていません。snap パッケージのミラーリングには、Canonical の商用 Snap Store Proxy 製品（個別の認証 + HTTP API、ファイルレベルではない）が必要であり、このエンジンの範囲外です。OpenBSD、NetBSD、macOS、Windows は、それぞれのツールプローブとインストールプランが書かれるまで延期されています。",
    "ko": "<strong>Snap:</strong> 지원되지 않습니다. snap 패키지 미러링에는 Canonical의 상용 Snap Store Proxy 제품이 필요하며(별도 인증 + HTTP API, 파일 수준 아님), 이는 이 엔진의 범위를 벗어납니다. OpenBSD, NetBSD, macOS, Windows는 각자의 도구 프로브와 설치 플랜이 작성될 때까지 연기되었습니다.",
    "zh_CN": "<strong>Snap：</strong>不支持。镜像 snap 包需要 Canonical 的商业 Snap Store Proxy 产品（单独的认证 + HTTP API，非文件级），超出了此引擎的范围。OpenBSD、NetBSD、macOS 和 Windows 推迟到其各自的工具探测和安装计划编写完成后再支持。",
    "zh_TW": "<strong>Snap：</strong>不支援。鏡像 snap 套件需要 Canonical 的商業 Snap Store Proxy 產品（獨立驗證 + HTTP API，非檔案層級），超出此引擎的範圍。OpenBSD、NetBSD、macOS 與 Windows 延後至各自的工具探測與安裝計畫撰寫完成後再支援。",
    "ar": "<strong>Snap:</strong> غير مدعوم. يتطلب نسخ حزم snap منتج Snap Store Proxy التجاري من Canonical (مصادقة منفصلة + واجهة HTTP API، وليس على مستوى الملف)، وهو خارج نطاق هذا المحرك. تم تأجيل OpenBSD وNetBSD وmacOS وWindows حتى كتابة مسبارات الأدوات وخطط التثبيت الخاصة بها.",
    "hi": "<strong>Snap:</strong> समर्थित नहीं। snap पैकेजों की मिररिंग के लिए Canonical के व्यावसायिक Snap Store Proxy उत्पाद की आवश्यकता होती है (अलग-अलग प्रमाणीकरण + HTTP API, फ़ाइल स्तर नहीं), जो इस इंजन के दायरे से बाहर है। OpenBSD, NetBSD, macOS, और Windows को उनके स्वयं के टूल प्रोब और इंस्टॉल प्लान लिखे जाने तक स्थगित कर दिया गया है।",
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
    out["docs.proplus.mirror.platforms.snaps"] = SNAPS_BY_LOCALE[locale]
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
        print(f"  {locale}: 7 keys written")


if __name__ == "__main__":
    main()
