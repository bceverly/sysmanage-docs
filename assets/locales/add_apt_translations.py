#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Add APT installation translations to all locale files."""

import json
import os
from pathlib import Path

# Translation mappings for all supported languages
TRANSLATIONS = {
    "es": {  # Spanish
        "title": "📦 Método 1: Repositorio APT (Ubuntu/Debian - Recomendado)",
        "supported": "Plataformas soportadas:",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS y posteriores",
        "platforms_debian_11": "Debian 11 y posteriores",
        "platforms_note": "El paquete incluye todas las dependencias de Python en un virtualenv autónomo, por lo que funciona en cualquier versión de Ubuntu/Debian con Python 3.10 o superior.",
        "quick_start": "Instalación Rápida",
        "benefits_title": "✨ Beneficios de la Instalación APT",
        "automatic": "Actualizaciones Automáticas:",
        "automatic_desc": "Obtenga nuevas versiones a través de apt upgrade estándar",
        "dependencies": "Gestión de Dependencias:",
        "dependencies_desc": "Todas las dependencias de Python incluidas en el paquete",
        "systemd": "Integración con Systemd:",
        "systemd_desc": "Servicio configurado y habilitado automáticamente",
        "user": "Usuario y Permisos:",
        "user_desc": "Usuario del sistema y sudoers configurados automáticamente",
        "directories": "Estructura de Directorios:",
        "directories_desc": "Directorios de configuración, registros y datos creados automáticamente",
        "whats_installed": "📂 Qué se Instala",
        "component": "Componente",
        "location": "Ubicación",
        "application": "Aplicación",
        "config_dir": "Directorio de Configuración",
        "main_config": "Archivo de Configuración Principal",
        "database": "Base de Datos",
        "logs": "Registros",
        "systemd_service": "Servicio Systemd",
        "sudoers": "Archivo Sudoers",
        "version_management": "🔄 Gestión de Versiones",
        "uninstall": "🗑️ Desinstalación",
        "security_note": "🔒 Nota de Seguridad",
        "security_text": "El repositorio actualmente usa [trusted=yes] porque los paquetes no están firmados con GPG. Para entornos de producción, la firma GPG se agregará en una versión futura. Los paquetes se sirven a través de HTTPS desde GitHub Pages, proporcionando seguridad a nivel de transporte."
    },
    "fr": {  # French
        "title": "📦 Méthode 1 : Dépôt APT (Ubuntu/Debian - Recommandé)",
        "supported": "Plateformes prises en charge :",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS et plus récent",
        "platforms_debian_11": "Debian 11 et plus récent",
        "platforms_note": "Le paquet inclut toutes les dépendances Python dans un virtualenv autonome, il fonctionne donc sur n'importe quelle version d'Ubuntu/Debian avec Python 3.10 ou supérieur.",
        "quick_start": "Installation Rapide",
        "benefits_title": "✨ Avantages de l'Installation APT",
        "automatic": "Mises à Jour Automatiques :",
        "automatic_desc": "Obtenez de nouvelles versions via apt upgrade standard",
        "dependencies": "Gestion des Dépendances :",
        "dependencies_desc": "Toutes les dépendances Python incluses dans le paquet",
        "systemd": "Intégration Systemd :",
        "systemd_desc": "Service automatiquement configuré et activé",
        "user": "Utilisateur et Permissions :",
        "user_desc": "Utilisateur système et sudoers configurés automatiquement",
        "directories": "Structure des Répertoires :",
        "directories_desc": "Répertoires de configuration, journaux et données créés automatiquement",
        "whats_installed": "📂 Ce qui est Installé",
        "component": "Composant",
        "location": "Emplacement",
        "application": "Application",
        "config_dir": "Répertoire de Configuration",
        "main_config": "Fichier de Configuration Principal",
        "database": "Base de Données",
        "logs": "Journaux",
        "systemd_service": "Service Systemd",
        "sudoers": "Fichier Sudoers",
        "version_management": "🔄 Gestion des Versions",
        "uninstall": "🗑️ Désinstallation",
        "security_note": "🔒 Note de Sécurité",
        "security_text": "Le dépôt utilise actuellement [trusted=yes] car les paquets ne sont pas signés GPG. Pour les environnements de production, la signature GPG sera ajoutée dans une version future. Les paquets sont servis via HTTPS depuis GitHub Pages, fournissant une sécurité au niveau du transport."
    },
    "de": {  # German
        "title": "📦 Methode 1: APT-Repository (Ubuntu/Debian - Empfohlen)",
        "supported": "Unterstützte Plattformen:",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS und neuer",
        "platforms_debian_11": "Debian 11 und neuer",
        "platforms_note": "Das Paket enthält alle Python-Abhängigkeiten in einer eigenständigen virtualenv, daher funktioniert es auf jeder Ubuntu/Debian-Version mit Python 3.10 oder höher.",
        "quick_start": "Schnellinstallation",
        "benefits_title": "✨ Vorteile der APT-Installation",
        "automatic": "Automatische Updates:",
        "automatic_desc": "Neue Versionen über standard apt upgrade erhalten",
        "dependencies": "Abhängigkeitsverwaltung:",
        "dependencies_desc": "Alle Python-Abhängigkeiten im Paket enthalten",
        "systemd": "Systemd-Integration:",
        "systemd_desc": "Service automatisch konfiguriert und aktiviert",
        "user": "Benutzer und Berechtigungen:",
        "user_desc": "Systembenutzer und sudoers automatisch konfiguriert",
        "directories": "Verzeichnisstruktur:",
        "directories_desc": "Konfigurations-, Protokoll- und Datenverzeichnisse automatisch erstellt",
        "whats_installed": "📂 Was wird Installiert",
        "component": "Komponente",
        "location": "Standort",
        "application": "Anwendung",
        "config_dir": "Konfigurationsverzeichnis",
        "main_config": "Hauptkonfigurationsdatei",
        "database": "Datenbank",
        "logs": "Protokolle",
        "systemd_service": "Systemd-Dienst",
        "sudoers": "Sudoers-Datei",
        "version_management": "🔄 Versionsverwaltung",
        "uninstall": "🗑️ Deinstallation",
        "security_note": "🔒 Sicherheitshinweis",
        "security_text": "Das Repository verwendet derzeit [trusted=yes], da Pakete nicht GPG-signiert sind. Für Produktionsumgebungen wird die GPG-Signierung in einer zukünftigen Version hinzugefügt. Die Pakete werden über HTTPS von GitHub Pages bereitgestellt und bieten Sicherheit auf Transportebene."
    },
    "it": {  # Italian
        "title": "📦 Metodo 1: Repository APT (Ubuntu/Debian - Consigliato)",
        "supported": "Piattaforme supportate:",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS e successive",
        "platforms_debian_11": "Debian 11 e successive",
        "platforms_note": "Il pacchetto include tutte le dipendenze Python in un virtualenv autonomo, quindi funziona su qualsiasi versione di Ubuntu/Debian con Python 3.10 o superiore.",
        "quick_start": "Installazione Rapida",
        "benefits_title": "✨ Vantaggi dell'Installazione APT",
        "automatic": "Aggiornamenti Automatici:",
        "automatic_desc": "Ottieni nuove versioni tramite apt upgrade standard",
        "dependencies": "Gestione delle Dipendenze:",
        "dependencies_desc": "Tutte le dipendenze Python incluse nel pacchetto",
        "systemd": "Integrazione Systemd:",
        "systemd_desc": "Servizio configurato e abilitato automaticamente",
        "user": "Utente e Permessi:",
        "user_desc": "Utente di sistema e sudoers configurati automaticamente",
        "directories": "Struttura delle Directory:",
        "directories_desc": "Directory di configurazione, log e dati create automaticamente",
        "whats_installed": "📂 Cosa viene Installato",
        "component": "Componente",
        "location": "Posizione",
        "application": "Applicazione",
        "config_dir": "Directory di Configurazione",
        "main_config": "File di Configurazione Principale",
        "database": "Database",
        "logs": "Log",
        "systemd_service": "Servizio Systemd",
        "sudoers": "File Sudoers",
        "version_management": "🔄 Gestione delle Versioni",
        "uninstall": "🗑️ Disinstallazione",
        "security_note": "🔒 Nota sulla Sicurezza",
        "security_text": "Il repository utilizza attualmente [trusted=yes] perché i pacchetti non sono firmati GPG. Per ambienti di produzione, la firma GPG verrà aggiunta in una versione futura. I pacchetti sono serviti tramite HTTPS da GitHub Pages, fornendo sicurezza a livello di trasporto."
    },
    "pt": {  # Portuguese
        "title": "📦 Método 1: Repositório APT (Ubuntu/Debian - Recomendado)",
        "supported": "Plataformas suportadas:",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS e mais recente",
        "platforms_debian_11": "Debian 11 e mais recente",
        "platforms_note": "O pacote inclui todas as dependências Python em um virtualenv autônomo, portanto funciona em qualquer versão do Ubuntu/Debian com Python 3.10 ou superior.",
        "quick_start": "Instalação Rápida",
        "benefits_title": "✨ Benefícios da Instalação APT",
        "automatic": "Atualizações Automáticas:",
        "automatic_desc": "Obtenha novas versões via apt upgrade padrão",
        "dependencies": "Gerenciamento de Dependências:",
        "dependencies_desc": "Todas as dependências Python incluídas no pacote",
        "systemd": "Integração Systemd:",
        "systemd_desc": "Serviço configurado e habilitado automaticamente",
        "user": "Usuário e Permissões:",
        "user_desc": "Usuário do sistema e sudoers configurados automaticamente",
        "directories": "Estrutura de Diretórios:",
        "directories_desc": "Diretórios de configuração, logs e dados criados automaticamente",
        "whats_installed": "📂 O que é Instalado",
        "component": "Componente",
        "location": "Localização",
        "application": "Aplicação",
        "config_dir": "Diretório de Configuração",
        "main_config": "Arquivo de Configuração Principal",
        "database": "Banco de Dados",
        "logs": "Logs",
        "systemd_service": "Serviço Systemd",
        "sudoers": "Arquivo Sudoers",
        "version_management": "🔄 Gerenciamento de Versões",
        "uninstall": "🗑️ Desinstalação",
        "security_note": "🔒 Nota de Segurança",
        "security_text": "O repositório atualmente usa [trusted=yes] porque os pacotes não são assinados com GPG. Para ambientes de produção, a assinatura GPG será adicionada em uma versão futura. Os pacotes são servidos via HTTPS do GitHub Pages, fornecendo segurança no nível de transporte."
    },
    "nl": {  # Dutch
        "title": "📦 Methode 1: APT Repository (Ubuntu/Debian - Aanbevolen)",
        "supported": "Ondersteunde platforms:",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS en nieuwer",
        "platforms_debian_11": "Debian 11 en nieuwer",
        "platforms_note": "Het pakket bevat alle Python-afhankelijkheden in een zelfstandige virtualenv, dus het werkt op elke Ubuntu/Debian-versie met Python 3.10 of hoger.",
        "quick_start": "Snelle Installatie",
        "benefits_title": "✨ Voordelen van APT-installatie",
        "automatic": "Automatische Updates:",
        "automatic_desc": "Nieuwe versies verkrijgen via standaard apt upgrade",
        "dependencies": "Beheer van Afhankelijkheden:",
        "dependencies_desc": "Alle Python-afhankelijkheden inbegrepen in pakket",
        "systemd": "Systemd-integratie:",
        "systemd_desc": "Service automatisch geconfigureerd en ingeschakeld",
        "user": "Gebruiker en Machtigingen:",
        "user_desc": "Systeemgebruiker en sudoers automatisch geconfigureerd",
        "directories": "Mappenstructuur:",
        "directories_desc": "Configuratie-, log- en datamappen automatisch aangemaakt",
        "whats_installed": "📂 Wat wordt Geïnstalleerd",
        "component": "Component",
        "location": "Locatie",
        "application": "Applicatie",
        "config_dir": "Configuratiemap",
        "main_config": "Hoofdconfiguratiebestand",
        "database": "Database",
        "logs": "Logbestanden",
        "systemd_service": "Systemd-service",
        "sudoers": "Sudoers-bestand",
        "version_management": "🔄 Versiebeheer",
        "uninstall": "🗑️ Deïnstallatie",
        "security_note": "🔒 Beveiligingsopmerking",
        "security_text": "De repository gebruikt momenteel [trusted=yes] omdat pakketten niet GPG-ondertekend zijn. Voor productieomgevingen zal GPG-ondertekening worden toegevoegd in een toekomstige release. De pakketten worden aangeboden via HTTPS van GitHub Pages, wat transportniveau beveiliging biedt."
    },
    "ja": {  # Japanese
        "title": "📦 方法1: APTリポジトリ (Ubuntu/Debian - 推奨)",
        "supported": "サポートされているプラットフォーム:",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS 以降",
        "platforms_debian_11": "Debian 11 以降",
        "platforms_note": "パッケージには自己完結型の virtualenv にすべての Python 依存関係が含まれているため、Python 3.10 以上を備えた任意の Ubuntu/Debian バージョンで動作します。",
        "quick_start": "クイックインストール",
        "benefits_title": "✨ APT インストールのメリット",
        "automatic": "自動更新:",
        "automatic_desc": "標準の apt upgrade で新しいバージョンを取得",
        "dependencies": "依存関係管理:",
        "dependencies_desc": "すべての Python 依存関係がパッケージに含まれています",
        "systemd": "Systemd 統合:",
        "systemd_desc": "サービスが自動的に構成され、有効化されます",
        "user": "ユーザーと権限:",
        "user_desc": "システムユーザーと sudoers が自動的に構成されます",
        "directories": "ディレクトリ構造:",
        "directories_desc": "設定、ログ、データのディレクトリが自動的に作成されます",
        "whats_installed": "📂 インストールされるもの",
        "component": "コンポーネント",
        "location": "場所",
        "application": "アプリケーション",
        "config_dir": "構成ディレクトリ",
        "main_config": "メイン構成ファイル",
        "database": "データベース",
        "logs": "ログ",
        "systemd_service": "Systemd サービス",
        "sudoers": "Sudoers ファイル",
        "version_management": "🔄 バージョン管理",
        "uninstall": "🗑️ アンインストール",
        "security_note": "🔒 セキュリティに関する注意",
        "security_text": "パッケージが GPG 署名されていないため、リポジトリは現在 [trusted=yes] を使用しています。本番環境では、将来のリリースで GPG 署名が追加されます。パッケージは GitHub Pages から HTTPS 経由で提供され、トランスポートレベルのセキュリティを提供します。"
    },
    "zh_CN": {  # Chinese Simplified
        "title": "📦 方法1: APT仓库 (Ubuntu/Debian - 推荐)",
        "supported": "支持的平台：",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS 及更高版本",
        "platforms_debian_11": "Debian 11 及更高版本",
        "platforms_note": "该软件包在自包含的 virtualenv 中包含所有 Python 依赖项，因此可在任何具有 Python 3.10 或更高版本的 Ubuntu/Debian 版本上运行。",
        "quick_start": "快速安装",
        "benefits_title": "✨ APT 安装的好处",
        "automatic": "自动更新：",
        "automatic_desc": "通过标准 apt upgrade 获取新版本",
        "dependencies": "依赖管理：",
        "dependencies_desc": "软件包中包含所有 Python 依赖项",
        "systemd": "Systemd 集成：",
        "systemd_desc": "服务自动配置和启用",
        "user": "用户和权限：",
        "user_desc": "系统用户和 sudoers 自动配置",
        "directories": "目录结构：",
        "directories_desc": "配置、日志和数据目录自动创建",
        "whats_installed": "📂 安装内容",
        "component": "组件",
        "location": "位置",
        "application": "应用程序",
        "config_dir": "配置目录",
        "main_config": "主配置文件",
        "database": "数据库",
        "logs": "日志",
        "systemd_service": "Systemd 服务",
        "sudoers": "Sudoers 文件",
        "version_management": "🔄 版本管理",
        "uninstall": "🗑️ 卸载",
        "security_note": "🔒 安全说明",
        "security_text": "由于软件包未进行 GPG 签名，仓库当前使用 [trusted=yes]。对于生产环境，将在未来版本中添加 GPG 签名。软件包通过 HTTPS 从 GitHub Pages 提供，提供传输级别的安全性。"
    },
    "zh_TW": {  # Chinese Traditional
        "title": "📦 方法1: APT儲存庫 (Ubuntu/Debian - 推薦)",
        "supported": "支援的平台：",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS 及更高版本",
        "platforms_debian_11": "Debian 11 及更高版本",
        "platforms_note": "該套件在自包含的 virtualenv 中包含所有 Python 相依性，因此可在任何具有 Python 3.10 或更高版本的 Ubuntu/Debian 版本上運行。",
        "quick_start": "快速安裝",
        "benefits_title": "✨ APT 安裝的好處",
        "automatic": "自動更新：",
        "automatic_desc": "透過標準 apt upgrade 取得新版本",
        "dependencies": "相依性管理：",
        "dependencies_desc": "套件中包含所有 Python 相依性",
        "systemd": "Systemd 整合：",
        "systemd_desc": "服務自動設定和啟用",
        "user": "使用者和權限：",
        "user_desc": "系統使用者和 sudoers 自動設定",
        "directories": "目錄結構：",
        "directories_desc": "設定、日誌和資料目錄自動建立",
        "whats_installed": "📂 安裝內容",
        "component": "元件",
        "location": "位置",
        "application": "應用程式",
        "config_dir": "設定目錄",
        "main_config": "主設定檔",
        "database": "資料庫",
        "logs": "日誌",
        "systemd_service": "Systemd 服務",
        "sudoers": "Sudoers 檔案",
        "version_management": "🔄 版本管理",
        "uninstall": "🗑️ 解除安裝",
        "security_note": "🔒 安全說明",
        "security_text": "由於套件未進行 GPG 簽署，儲存庫目前使用 [trusted=yes]。對於生產環境，將在未來版本中新增 GPG 簽署。套件透過 HTTPS 從 GitHub Pages 提供，提供傳輸層級的安全性。"
    },
    "ko": {  # Korean
        "title": "📦 방법 1: APT 저장소 (Ubuntu/Debian - 권장)",
        "supported": "지원되는 플랫폼:",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS 이상",
        "platforms_debian_11": "Debian 11 이상",
        "platforms_note": "패키지에는 독립적인 virtualenv에 모든 Python 종속성이 포함되어 있으므로 Python 3.10 이상이 있는 모든 Ubuntu/Debian 버전에서 작동합니다.",
        "quick_start": "빠른 설치",
        "benefits_title": "✨ APT 설치의 장점",
        "automatic": "자동 업데이트:",
        "automatic_desc": "표준 apt upgrade를 통해 새 버전 가져오기",
        "dependencies": "종속성 관리:",
        "dependencies_desc": "패키지에 모든 Python 종속성 포함",
        "systemd": "Systemd 통합:",
        "systemd_desc": "서비스가 자동으로 구성되고 활성화됨",
        "user": "사용자 및 권한:",
        "user_desc": "시스템 사용자 및 sudoers가 자동으로 구성됨",
        "directories": "디렉토리 구조:",
        "directories_desc": "구성, 로그 및 데이터 디렉토리가 자동으로 생성됨",
        "whats_installed": "📂 설치되는 항목",
        "component": "구성 요소",
        "location": "위치",
        "application": "애플리케이션",
        "config_dir": "구성 디렉토리",
        "main_config": "주 구성 파일",
        "database": "데이터베이스",
        "logs": "로그",
        "systemd_service": "Systemd 서비스",
        "sudoers": "Sudoers 파일",
        "version_management": "🔄 버전 관리",
        "uninstall": "🗑️ 제거",
        "security_note": "🔒 보안 참고 사항",
        "security_text": "패키지가 GPG 서명되지 않았기 때문에 저장소는 현재 [trusted=yes]를 사용합니다. 프로덕션 환경의 경우 향후 릴리스에서 GPG 서명이 추가될 예정입니다. 패키지는 GitHub Pages에서 HTTPS를 통해 제공되어 전송 수준 보안을 제공합니다."
    },
    "ru": {  # Russian
        "title": "📦 Метод 1: Репозиторий APT (Ubuntu/Debian - Рекомендуется)",
        "supported": "Поддерживаемые платформы:",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS и новее",
        "platforms_debian_11": "Debian 11 и новее",
        "platforms_note": "Пакет включает все зависимости Python в автономном virtualenv, поэтому он работает на любой версии Ubuntu/Debian с Python 3.10 или выше.",
        "quick_start": "Быстрая установка",
        "benefits_title": "✨ Преимущества установки APT",
        "automatic": "Автоматические обновления:",
        "automatic_desc": "Получайте новые версии через стандартный apt upgrade",
        "dependencies": "Управление зависимостями:",
        "dependencies_desc": "Все зависимости Python включены в пакет",
        "systemd": "Интеграция с Systemd:",
        "systemd_desc": "Служба автоматически настраивается и включается",
        "user": "Пользователь и права:",
        "user_desc": "Системный пользователь и sudoers настраиваются автоматически",
        "directories": "Структура каталогов:",
        "directories_desc": "Каталоги конфигурации, журналов и данных создаются автоматически",
        "whats_installed": "📂 Что устанавливается",
        "component": "Компонент",
        "location": "Расположение",
        "application": "Приложение",
        "config_dir": "Каталог конфигурации",
        "main_config": "Основной файл конфигурации",
        "database": "База данных",
        "logs": "Журналы",
        "systemd_service": "Служба Systemd",
        "sudoers": "Файл Sudoers",
        "version_management": "🔄 Управление версиями",
        "uninstall": "🗑️ Удаление",
        "security_note": "🔒 Примечание по безопасности",
        "security_text": "Репозиторий в настоящее время использует [trusted=yes], поскольку пакеты не подписаны GPG. Для производственных сред подпись GPG будет добавлена в будущем выпуске. Пакеты предоставляются через HTTPS с GitHub Pages, обеспечивая безопасность на транспортном уровне."
    },
    "ar": {  # Arabic
        "title": "📦 الطريقة 1: مستودع APT (Ubuntu/Debian - موصى به)",
        "supported": "المنصات المدعومة:",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS والإصدارات الأحدث",
        "platforms_debian_11": "Debian 11 والإصدارات الأحدث",
        "platforms_note": "تتضمن الحزمة جميع تبعيات Python في virtualenv مستقل، لذا فهي تعمل على أي إصدار من Ubuntu/Debian مع Python 3.10 أو أعلى.",
        "quick_start": "التثبيت السريع",
        "benefits_title": "✨ فوائد تثبيت APT",
        "automatic": "التحديثات التلقائية:",
        "automatic_desc": "احصل على إصدارات جديدة عبر apt upgrade القياسي",
        "dependencies": "إدارة التبعيات:",
        "dependencies_desc": "جميع تبعيات Python مضمنة في الحزمة",
        "systemd": "تكامل Systemd:",
        "systemd_desc": "الخدمة مكونة ومفعلة تلقائيًا",
        "user": "المستخدم والأذونات:",
        "user_desc": "مستخدم النظام و sudoers مكونة تلقائيًا",
        "directories": "هيكل الدلائل:",
        "directories_desc": "يتم إنشاء دلائل التكوين والسجلات والبيانات تلقائيًا",
        "whats_installed": "📂 ما يتم تثبيته",
        "component": "المكون",
        "location": "الموقع",
        "application": "التطبيق",
        "config_dir": "دليل التكوين",
        "main_config": "ملف التكوين الرئيسي",
        "database": "قاعدة البيانات",
        "logs": "السجلات",
        "systemd_service": "خدمة Systemd",
        "sudoers": "ملف Sudoers",
        "version_management": "🔄 إدارة الإصدارات",
        "uninstall": "🗑️ إلغاء التثبيت",
        "security_note": "🔒 ملاحظة أمنية",
        "security_text": "يستخدم المستودع حاليًا [trusted=yes] لأن الحزم غير موقعة بـ GPG. بالنسبة لبيئات الإنتاج، ستتم إضافة توقيع GPG في إصدار مستقبلي. يتم تقديم الحزم عبر HTTPS من GitHub Pages، مما يوفر أمانًا على مستوى النقل."
    },
    "hi": {  # Hindi
        "title": "📦 विधि 1: APT रिपॉजिटरी (Ubuntu/Debian - अनुशंसित)",
        "supported": "समर्थित प्लेटफ़ॉर्म:",
        "platforms_ubuntu_2204": "Ubuntu 22.04 LTS और नया",
        "platforms_debian_11": "Debian 11 और नया",
        "platforms_note": "पैकेज में एक स्व-निहित virtualenv में सभी Python निर्भरताएं शामिल हैं, इसलिए यह Python 3.10 या उच्चतर के साथ किसी भी Ubuntu/Debian संस्करण पर काम करता है।",
        "quick_start": "त्वरित स्थापना",
        "benefits_title": "✨ APT स्थापना के लाभ",
        "automatic": "स्वचालित अपडेट:",
        "automatic_desc": "मानक apt upgrade के माध्यम से नए संस्करण प्राप्त करें",
        "dependencies": "निर्भरता प्रबंधन:",
        "dependencies_desc": "पैकेज में सभी Python निर्भरताएं शामिल हैं",
        "systemd": "Systemd एकीकरण:",
        "systemd_desc": "सेवा स्वचालित रूप से कॉन्फ़िगर और सक्षम की गई",
        "user": "उपयोगकर्ता और अनुमतियां:",
        "user_desc": "सिस्टम उपयोगकर्ता और sudoers स्वचालित रूप से कॉन्फ़िगर किए गए",
        "directories": "निर्देशिका संरचना:",
        "directories_desc": "कॉन्फ़िगरेशन, लॉग और डेटा निर्देशिकाएं स्वचालित रूप से बनाई गईं",
        "whats_installed": "📂 क्या स्थापित होता है",
        "component": "घटक",
        "location": "स्थान",
        "application": "एप्लिकेशन",
        "config_dir": "कॉन्फ़िगरेशन निर्देशिका",
        "main_config": "मुख्य कॉन्फ़िगरेशन फ़ाइल",
        "database": "डेटाबेस",
        "logs": "लॉग",
        "systemd_service": "Systemd सेवा",
        "sudoers": "Sudoers फ़ाइल",
        "version_management": "🔄 संस्करण प्रबंधन",
        "uninstall": "🗑️ स्थापना रद्द करें",
        "security_note": "🔒 सुरक्षा नोट",
        "security_text": "रिपॉजिटरी वर्तमान में [trusted=yes] का उपयोग करती है क्योंकि पैकेज GPG-हस्ताक्षरित नहीं हैं। उत्पादन वातावरण के लिए, भविष्य के रिलीज़ में GPG हस्ताक्षरण जोड़ा जाएगा। पैकेज GitHub Pages से HTTPS के माध्यम से परोसे जाते हैं, जो परिवहन स्तर की सुरक्षा प्रदान करते हैं।"
    }
}

def add_translations_to_file(lang_code, translations):
    """Add APT translations to a specific language file."""
    locale_dir = Path(__file__).parent
    file_path = locale_dir / f"{lang_code}.json"

    # Read existing translations
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Navigate to agent_installation.installation and add apt translations
    if 'agent_installation' not in data:
        print(f"Warning: agent_installation not found in {lang_code}.json")
        return

    if 'installation' not in data['agent_installation']:
        print(f"Warning: installation section not found in {lang_code}.json")
        return

    # Add apt translations
    data['agent_installation']['installation']['apt'] = translations

    # Update method titles if they exist
    if 'method1' in data['agent_installation']['installation']:
        if lang_code == 'es':
            data['agent_installation']['installation']['method1']['title'] = "Método 2: Desde el Código Fuente"
            data['agent_installation']['installation']['method2']['title'] = "Método 3: Instalación Directa"
        elif lang_code == 'fr':
            data['agent_installation']['installation']['method1']['title'] = "Méthode 2 : Depuis le Code Source"
            data['agent_installation']['installation']['method2']['title'] = "Méthode 3 : Installation Directe"
        elif lang_code == 'de':
            data['agent_installation']['installation']['method1']['title'] = "Methode 2: Aus dem Quellcode"
            data['agent_installation']['installation']['method2']['title'] = "Methode 3: Direkte Installation"
        elif lang_code == 'it':
            data['agent_installation']['installation']['method1']['title'] = "Metodo 2: Dal Codice Sorgente"
            data['agent_installation']['installation']['method2']['title'] = "Metodo 3: Installazione Diretta"
        elif lang_code == 'pt':
            data['agent_installation']['installation']['method1']['title'] = "Método 2: Do Código Fonte"
            data['agent_installation']['installation']['method2']['title'] = "Método 3: Instalação Direta"
        elif lang_code == 'nl':
            data['agent_installation']['installation']['method1']['title'] = "Methode 2: Vanuit de Broncode"
            data['agent_installation']['installation']['method2']['title'] = "Methode 3: Directe Installatie"
        elif lang_code == 'ja':
            data['agent_installation']['installation']['method1']['title'] = "方法2: ソースから"
            data['agent_installation']['installation']['method2']['title'] = "方法3: 直接インストール"
        elif lang_code == 'zh_CN':
            data['agent_installation']['installation']['method1']['title'] = "方法2: 从源代码"
            data['agent_installation']['installation']['method2']['title'] = "方法3: 直接安装"
        elif lang_code == 'zh_TW':
            data['agent_installation']['installation']['method1']['title'] = "方法2: 從原始碼"
            data['agent_installation']['installation']['method2']['title'] = "方法3: 直接安裝"
        elif lang_code == 'ko':
            data['agent_installation']['installation']['method1']['title'] = "방법 2: 소스에서"
            data['agent_installation']['installation']['method2']['title'] = "방법 3: 직접 설치"
        elif lang_code == 'ru':
            data['agent_installation']['installation']['method1']['title'] = "Метод 2: Из исходного кода"
            data['agent_installation']['installation']['method2']['title'] = "Метод 3: Прямая установка"
        elif lang_code == 'ar':
            data['agent_installation']['installation']['method1']['title'] = "الطريقة 2: من الكود المصدري"
            data['agent_installation']['installation']['method2']['title'] = "الطريقة 3: التثبيت المباشر"
        elif lang_code == 'hi':
            data['agent_installation']['installation']['method1']['title'] = "विधि 2: स्रोत से"
            data['agent_installation']['installation']['method2']['title'] = "विधि 3: प्रत्यक्ष स्थापना"

    # Write back with proper formatting
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Updated {lang_code}.json")

def main():
    """Add APT translations to all language files."""
    print("Adding APT installation translations to all locale files...\n")

    for lang_code, translations in TRANSLATIONS.items():
        add_translations_to_file(lang_code, translations)

    print("\n✅ All translations added successfully!")
    print("\nTranslations added for languages:")
    for lang_code in TRANSLATIONS.keys():
        print(f"  - {lang_code}")

if __name__ == '__main__':
    main()
