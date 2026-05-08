"""Phase 10.4.4 i18n: known-version dropdown + default package mirrors card.

Scope:
  - 2 new docs sections (Version dropdown + known-version catalog;
    Default Package Mirrors).  Each gets a title, intro, and several
    body paragraphs with inline <code> snippets.
  - The PM-specific bullet list under defaults.applymech (apt/dnf/
    zypper/pkg) — body stays English everywhere because every line
    is dominated by file paths and shell commands.

Pattern: titles + sentence-form prose translated for major locales;
heavily-technical body (paths, commands, API surface) stays English.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

EN = {
    "docs.proplus.mirror.versions.title": "Version dropdown + known-version catalog (Phase 10.4.4)",
    "docs.proplus.mirror.versions.intro": "The Add Mirror dialog's version field is sourced from a pre-populated <code>mirror_known_version</code> catalog instead of free-text. Selecting a row auto-fills the upstream URL and the per-PM identifier (suite for apt, repoid for dnf, repo_alias for zypper, release for pkg) so an operator can't fat-finger <code>noblee</code> and silently produce a broken mirror. The catalog ships seeded with the canonical Ubuntu/Debian/RHEL-family/openSUSE/FreeBSD versions; future versions land via dedicated migrations rather than auto-discovery, keeping the supported set reviewable in code.",
    "docs.proplus.mirror.versions.crossfamily": "One physical host can mirror multiple OS families that share a package manager. RHEL/Rocky/Alma/Fedora all use <code>dnf</code> with different upstream URLs, so they appear as separate <code>mirror_repository</code> rows under the same RHEL/Fedora tab — each row carries its own <code>known_version_id</code> referencing a different catalog entry. The Default Package Mirrors card has independent rows for each, so an admin can assign different defaults to RHEL 9 hosts vs Rocky 9 hosts even when both pull from the same physical mirror server.",
    "docs.proplus.mirror.defaults.title": "Default Package Mirrors (Phase 10.4.4)",
    "docs.proplus.mirror.defaults.intro": 'Settings → Host Defaults gains a "Default Package Mirrors" card that drives an apply/revert workflow against active hosts. One row per (platform, version_key, os_family) tuple drawn from the catalog; each row\'s dropdown lists the eligible mirrors (right PM + at least one successful sync) plus a "Cloud (upstream default)" option.',
    "docs.proplus.mirror.defaults.flow": 'Saving a non-cloud choice queues an apply plan to every active host whose <code>platform_release</code> matches the catalog row\'s regex — simultaneous rollout, no staggered windows. Choosing "Cloud" queues a revert plan to the same matching hosts. New host registrations and approvals invoke the same hook automatically, so a freshly-enrolled host of a covered family gets pointed at the mirror without operator action.',
    "docs.proplus.mirror.defaults.hardblock": "The API hard-blocks (HTTP 409) any attempt to assign a mirror that hasn't completed a successful sync. This prevents pointing live clients at an empty or partially-built mirror tree where <code>apt update</code> would fail. Re-attempt once the mirror's <code>last_sync_status</code> reaches <code>SUCCESS</code>.",
    "docs.proplus.mirror.defaults.applymech": "The apply mechanism is additive only. Each PM gets a single override file the agent drops into a directory the package manager scans alongside operator-edited config:",
    "docs.proplus.mirror.defaults.apt": "<strong>apt:</strong> <code>/etc/apt/sources.list.d/zzz-sysmanage-mirror.list</code> + <code>apt-get update</code>",
    "docs.proplus.mirror.defaults.dnf": "<strong>dnf:</strong> <code>/etc/yum.repos.d/zzz-sysmanage-&lt;repoid&gt;.repo</code> with the same <code>[section]</code> header as the upstream — dnf reads files in lex order and the last definition wins, so our <code>zzz-</code> prefix overrides whatever shipped + <code>dnf clean all</code>",
    "docs.proplus.mirror.defaults.zypper": "<strong>zypper:</strong> <code>/etc/zypp/repos.d/zzz-sysmanage-&lt;alias&gt;.repo</code> + <code>zypper refresh</code>",
    "docs.proplus.mirror.defaults.pkg": "<strong>pkg:</strong> <code>/usr/local/etc/pkg/repos/sysmanage-mirror.conf</code> overriding the FreeBSD repo + <code>pkg update -f</code>",
    "docs.proplus.mirror.defaults.revert": "Revert is symmetric: each plan deletes the override file and refreshes the package manager's metadata cache. Operator-edited config (the original <code>sources.list</code>, vendor-shipped <code>.repo</code> files) is never modified, so a manual edit between apply and revert is preserved.",
    "docs.proplus.mirror.defaults.api": "API surface: <code>GET /api/mirror-known-versions</code> for the catalog dropdown, <code>GET /api/host-defaults/mirrors</code> for the assignment table, <code>PUT /api/host-defaults/mirrors/{platform}/{version_key}/{os_family}</code> with <code>{mirror_id}</code> body to assign or <code>{mirror_id: null}</code> to revert to cloud.",
    # Frontend i18n keys (mirror.field.* + hostDefaults.mirror.*)
    "mirror.field.version": "Version",
    "mirror.field.upstreamHelp": "Auto-filled from the version above; override only if you have a region-specific mirror to point at.",
    "hostDefaults.mirror.title": "Default Package Mirrors",
    "hostDefaults.mirror.subtitle": "For each supported (platform, version) pair, pick which mirror new and existing hosts of that family use as their default. Cloud means hosts hit the public upstream directly. Only mirrors that have completed a successful sync are eligible.",
    "hostDefaults.mirror.col.platform": "Platform",
    "hostDefaults.mirror.col.version": "Version",
    "hostDefaults.mirror.col.osFamily": "OS Family",
    "hostDefaults.mirror.col.mirror": "Default Mirror",
    "hostDefaults.mirror.cloud": "Cloud (upstream default)",
    "hostDefaults.mirror.noEligible": "No synced mirrors available",
    "hostDefaults.mirror.saveSuccess": "Saved. {{count}} host(s) will be reconfigured.",
}

VERSIONS_TITLE_BY_LOCALE = {
    "de": "Versions-Dropdown + bekannte-Versionen-Katalog (Phase 10.4.4)",
    "es": "Menú desplegable de versiones + catálogo de versiones conocidas (Fase 10.4.4)",
    "fr": "Liste déroulante des versions + catalogue de versions connues (Phase 10.4.4)",
    "it": "Menu a discesa delle versioni + catalogo delle versioni note (Fase 10.4.4)",
    "pt": "Menu suspenso de versões + catálogo de versões conhecidas (Fase 10.4.4)",
    "nl": "Versie-vervolgkeuzelijst + catalogus van bekende versies (Fase 10.4.4)",
    "ru": "Раскрывающийся список версий + каталог известных версий (Этап 10.4.4)",
    "ja": "バージョンドロップダウン + 既知バージョンカタログ（フェーズ 10.4.4）",
    "ko": "버전 드롭다운 + 알려진 버전 카탈로그 (10.4.4 단계)",
    "zh_CN": "版本下拉菜单 + 已知版本目录（阶段 10.4.4）",
    "zh_TW": "版本下拉選單 + 已知版本目錄（階段 10.4.4）",
    "ar": "قائمة منسدلة للإصدارات + كتالوج الإصدارات المعروفة (المرحلة 10.4.4)",
    "hi": "संस्करण ड्रॉपडाउन + ज्ञात-संस्करण कैटलॉग (चरण 10.4.4)",
}

DEFAULTS_TITLE_BY_LOCALE = {
    "de": "Standard-Paket-Spiegel (Phase 10.4.4)",
    "es": "Espejos de paquetes predeterminados (Fase 10.4.4)",
    "fr": "Miroirs de paquets par défaut (Phase 10.4.4)",
    "it": "Mirror dei pacchetti predefiniti (Fase 10.4.4)",
    "pt": "Espelhos de pacotes padrão (Fase 10.4.4)",
    "nl": "Standaard-pakketspiegels (Fase 10.4.4)",
    "ru": "Зеркала пакетов по умолчанию (Этап 10.4.4)",
    "ja": "デフォルトパッケージミラー（フェーズ 10.4.4）",
    "ko": "기본 패키지 미러 (10.4.4 단계)",
    "zh_CN": "默认软件包镜像（阶段 10.4.4）",
    "zh_TW": "預設套件鏡像（階段 10.4.4）",
    "ar": "مرايا الحزم الافتراضية (المرحلة 10.4.4)",
    "hi": "डिफ़ॉल्ट पैकेज मिरर (चरण 10.4.4)",
}

# Frontend i18n — the card title/subtitle/columns shown to operators.
HD_TITLE_BY_LOCALE = {
    "de": "Standard-Paket-Spiegel",
    "es": "Espejos de paquetes predeterminados",
    "fr": "Miroirs de paquets par défaut",
    "it": "Mirror dei pacchetti predefiniti",
    "pt": "Espelhos de pacotes padrão",
    "nl": "Standaard-pakketspiegels",
    "ru": "Зеркала пакетов по умолчанию",
    "ja": "デフォルトパッケージミラー",
    "ko": "기본 패키지 미러",
    "zh_CN": "默认软件包镜像",
    "zh_TW": "預設套件鏡像",
    "ar": "مرايا الحزم الافتراضية",
    "hi": "डिफ़ॉल्ट पैकेज मिरर",
}

HD_SUBTITLE_BY_LOCALE = {
    "de": "Wählen Sie für jedes unterstützte (Plattform, Version)-Paar aus, welchen Spiegel neue und vorhandene Hosts dieser Familie als Standard verwenden. Cloud bedeutet, dass Hosts direkt das öffentliche Upstream ansprechen. Nur Spiegel, die eine erfolgreiche Synchronisation abgeschlossen haben, sind verfügbar.",
    "es": "Para cada par (plataforma, versión) compatible, elija qué espejo usan los hosts nuevos y existentes de esa familia como predeterminado. Cloud significa que los hosts contactan directamente el upstream público. Solo están disponibles los espejos que han completado una sincronización exitosa.",
    "fr": "Pour chaque paire (plateforme, version) prise en charge, choisissez le miroir que les nouveaux hôtes et les hôtes existants de cette famille utilisent par défaut. Cloud signifie que les hôtes contactent directement l'upstream public. Seuls les miroirs ayant terminé une synchronisation réussie sont éligibles.",
    "it": "Per ogni coppia (piattaforma, versione) supportata, scegli quale mirror gli host nuovi ed esistenti di quella famiglia usano come predefinito. Cloud significa che gli host raggiungono direttamente l'upstream pubblico. Sono ammessi solo mirror che hanno completato una sincronizzazione riuscita.",
    "pt": "Para cada par (plataforma, versão) suportado, escolha qual espelho os hosts novos e existentes dessa família usam como padrão. Cloud significa que os hosts acessam diretamente o upstream público. Apenas espelhos que concluíram uma sincronização bem-sucedida são elegíveis.",
    "nl": "Kies voor elk ondersteund (platform, versie)-paar welke spiegel nieuwe en bestaande hosts van die familie als standaard gebruiken. Cloud betekent dat hosts rechtstreeks naar de publieke upstream gaan. Alleen spiegels die een succesvolle synchronisatie hebben voltooid komen in aanmerking.",
    "ru": "Для каждой поддерживаемой пары (платформа, версия) выберите, какое зеркало новые и существующие хосты этого семейства используют по умолчанию. Cloud означает, что хосты обращаются напрямую к публичному upstream. Доступны только зеркала, успешно завершившие хотя бы одну синхронизацию.",
    "ja": "サポートされている各（プラットフォーム、バージョン）ペアについて、その系統の新規および既存のホストがデフォルトとして使用するミラーを選択します。Cloud は、ホストが公開アップストリームに直接アクセスすることを意味します。正常にシンクが完了したミラーのみ選択できます。",
    "ko": "지원되는 각 (플랫폼, 버전) 쌍에 대해 해당 계열의 새 호스트와 기존 호스트가 기본값으로 사용할 미러를 선택하십시오. Cloud는 호스트가 공개 upstream에 직접 접속함을 의미합니다. 동기화에 성공한 미러만 선택할 수 있습니다.",
    "zh_CN": "为每个受支持的（平台，版本）对，选择该系列的新主机和现有主机用作默认值的镜像。Cloud 表示主机直接访问公共上游。只有完成过成功同步的镜像才可用。",
    "zh_TW": "為每個支援的（平台、版本）配對，選擇該系列的新主機與現有主機使用的預設鏡像。Cloud 表示主機直接連線公開上游。只有完成過成功同步的鏡像才可選。",
    "ar": "لكل زوج (منصة، إصدار) مدعوم، اختر المرآة التي يستخدمها المضيفون الجدد والحاليون من تلك العائلة كافتراضية. Cloud يعني أن المضيفين يتصلون مباشرة بالمصدر الأصلي العام. المرايا التي أكملت مزامنة ناجحة فقط مؤهلة.",
    "hi": "प्रत्येक समर्थित (प्लेटफ़ॉर्म, संस्करण) जोड़े के लिए, चुनें कि उस परिवार के नए और मौजूदा होस्ट किस मिरर को डिफ़ॉल्ट के रूप में उपयोग करते हैं। Cloud का अर्थ है कि होस्ट सीधे सार्वजनिक upstream से संपर्क करते हैं। केवल वे मिरर ही पात्र हैं जिन्होंने एक सफल सिंक पूरी कर ली है।",
}

CLOUD_BY_LOCALE = {
    "de": "Cloud (Upstream-Standard)",
    "es": "Cloud (predeterminado upstream)",
    "fr": "Cloud (par défaut upstream)",
    "it": "Cloud (predefinito upstream)",
    "pt": "Cloud (padrão upstream)",
    "nl": "Cloud (upstream-standaard)",
    "ru": "Cloud (upstream по умолчанию)",
    "ja": "Cloud（アップストリームデフォルト）",
    "ko": "Cloud (업스트림 기본값)",
    "zh_CN": "Cloud（上游默认）",
    "zh_TW": "Cloud（上游預設）",
    "ar": "Cloud (الافتراضي من المصدر)",
    "hi": "Cloud (अपस्ट्रीम डिफ़ॉल्ट)",
}

NO_ELIGIBLE_BY_LOCALE = {
    "de": "Keine synchronisierten Spiegel verfügbar",
    "es": "No hay espejos sincronizados disponibles",
    "fr": "Aucun miroir synchronisé disponible",
    "it": "Nessun mirror sincronizzato disponibile",
    "pt": "Nenhum espelho sincronizado disponível",
    "nl": "Geen gesynchroniseerde spiegels beschikbaar",
    "ru": "Нет синхронизированных зеркал",
    "ja": "シンク済みミラーがありません",
    "ko": "동기화된 미러를 사용할 수 없음",
    "zh_CN": "没有可用的已同步镜像",
    "zh_TW": "沒有可用的已同步鏡像",
    "ar": "لا توجد مرايا متزامنة متاحة",
    "hi": "कोई सिंक किया गया मिरर उपलब्ध नहीं",
}

SAVE_SUCCESS_BY_LOCALE = {
    "de": "Gespeichert. {{count}} Host(s) werden neu konfiguriert.",
    "es": "Guardado. Se reconfigurarán {{count}} host(s).",
    "fr": "Enregistré. {{count}} hôte(s) seront reconfigurés.",
    "it": "Salvato. {{count}} host verranno riconfigurati.",
    "pt": "Salvo. {{count}} host(s) serão reconfigurados.",
    "nl": "Opgeslagen. {{count}} host(s) worden opnieuw geconfigureerd.",
    "ru": "Сохранено. {{count}} хост(ов) будут перенастроены.",
    "ja": "保存しました。{{count}} 個のホストが再構成されます。",
    "ko": "저장되었습니다. {{count}}개 호스트가 재구성됩니다.",
    "zh_CN": "已保存。{{count}} 个主机将被重新配置。",
    "zh_TW": "已儲存。{{count}} 個主機將被重新設定。",
    "ar": "تم الحفظ. ستتم إعادة تكوين {{count}} مضيف.",
    "hi": "सहेजा गया। {{count}} होस्ट पुन: कॉन्फ़िगर किए जाएंगे।",
}

VERSION_LABEL_BY_LOCALE = {
    "de": "Version",
    "es": "Versión",
    "fr": "Version",
    "it": "Versione",
    "pt": "Versão",
    "nl": "Versie",
    "ru": "Версия",
    "ja": "バージョン",
    "ko": "버전",
    "zh_CN": "版本",
    "zh_TW": "版本",
    "ar": "الإصدار",
    "hi": "संस्करण",
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
    out["docs.proplus.mirror.versions.title"] = VERSIONS_TITLE_BY_LOCALE[locale]
    out["docs.proplus.mirror.defaults.title"] = DEFAULTS_TITLE_BY_LOCALE[locale]
    out["mirror.field.version"] = VERSION_LABEL_BY_LOCALE[locale]
    out["hostDefaults.mirror.title"] = HD_TITLE_BY_LOCALE[locale]
    out["hostDefaults.mirror.subtitle"] = HD_SUBTITLE_BY_LOCALE[locale]
    out["hostDefaults.mirror.cloud"] = CLOUD_BY_LOCALE[locale]
    out["hostDefaults.mirror.noEligible"] = NO_ELIGIBLE_BY_LOCALE[locale]
    out["hostDefaults.mirror.saveSuccess"] = SAVE_SUCCESS_BY_LOCALE[locale]
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
