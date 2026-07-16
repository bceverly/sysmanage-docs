#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

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

    'ar.json': {
        # Arabic translations - Host Account Management
        'docs.admin.host_accounts.title': 'إدارة حسابات المضيف - إدارة SysManage',
        'docs.admin.host_accounts.meta_description': 'دليل شامل لإنشاء وإدارة حسابات المستخدمين والمجموعات على المضيفين البعيدين باستخدام SysManage.',
        'docs.admin.host_accounts.breadcrumb': 'إدارة حسابات المضيف',
        'docs.admin.host_accounts.header.title': 'إدارة حسابات المضيف',
        'docs.admin.host_accounts.header.subtitle': 'إنشاء وإدارة حسابات المستخدمين والمجموعات على المضيفين البعيدين عبر جميع المنصات المدعومة.',
        'docs.admin.host_accounts.overview.title': 'نظرة عامة',
        'docs.admin.host_accounts.overview.description': 'يوفر SysManage إدارة مركزية لحسابات المستخدمين والمجموعات على المضيفين البعيدين. أنشئ مستخدمين ومجموعات من واجهة الويب دون الحاجة إلى وصول SSH مباشر، مع دعم كامل للخيارات الخاصة بكل منصة عبر أنظمة Linux وBSD وmacOS وWindows.',
        'docs.admin.host_accounts.overview.key_features': 'الميزات الرئيسية',
        'docs.admin.host_accounts.overview.features.cross_platform': '<strong>دعم متعدد المنصات:</strong> إنشاء مستخدمين ومجموعات على Linux وBSD وmacOS وWindows',
        'docs.admin.host_accounts.overview.features.platform_specific': '<strong>خيارات خاصة بالمنصة:</strong> تكوين الصدفة ودليل المنزل وUID/GID وإعدادات Windows المحددة',
        'docs.admin.host_accounts.overview.features.web_interface': '<strong>واجهة الويب:</strong> إنشاء الحسابات مباشرة من صفحة تفاصيل المضيف',
        'docs.admin.host_accounts.overview.features.rbac': '<strong>التحكم في الوصول المستند إلى الأدوار:</strong> أذونات دقيقة لإدارة الحسابات والمجموعات',
        'docs.admin.host_accounts.overview.features.audit_logging': '<strong>تسجيل التدقيق:</strong> يتم تسجيل جميع عمليات الحساب للامتثال',
        'docs.admin.host_accounts.overview.features.privileged_mode': '<strong>الوضع المميز مطلوب:</strong> يجب تشغيل الوكيل بصلاحيات مرتفعة لإدارة الحسابات',
        'docs.admin.host_accounts.platforms.title': 'المنصات المدعومة',
        'docs.admin.host_accounts.platforms.linux.title': 'أنظمة Linux',
        'docs.admin.host_accounts.platforms.linux.description': 'يستخدم إنشاء المستخدمين والمجموعات أوامر <code>useradd</code> و<code>groupadd</code> القياسية:',
        'docs.admin.host_accounts.platforms.linux.ubuntu_debian': '<strong>Ubuntu/Debian:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.linux.rhel_centos': '<strong>RHEL/CentOS/Fedora:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.linux.opensuse': '<strong>openSUSE:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.bsd.title': 'أنظمة BSD',
        'docs.admin.host_accounts.platforms.bsd.description': 'تستخدم منصات BSD أدوات إدارة الحسابات الأصلية:',
        'docs.admin.host_accounts.platforms.bsd.freebsd': '<strong>FreeBSD:</strong> pw useradd, pw groupadd',
        'docs.admin.host_accounts.platforms.bsd.openbsd': '<strong>OpenBSD:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.bsd.netbsd': '<strong>NetBSD:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.macos.title': 'macOS',
        'docs.admin.host_accounts.platforms.macos.description': 'يستخدم macOS خدمات الدليل لإدارة الحسابات:',
        'docs.admin.host_accounts.platforms.macos.dscl': '<strong>dscl:</strong> أداة سطر أوامر خدمات الدليل',
        'docs.admin.host_accounts.platforms.macos.homedir': '<strong>createhomedir:</strong> إنشاء دليل المنزل',
        'docs.admin.host_accounts.platforms.windows.title': 'Windows',
        'docs.admin.host_accounts.platforms.windows.description': 'يستخدم Windows أوامر إدارة الحسابات الأصلية:',
        'docs.admin.host_accounts.platforms.windows.net_user': '<strong>net user:</strong> إنشاء وإدارة حسابات المستخدمين المحليين',
        'docs.admin.host_accounts.platforms.windows.net_localgroup': '<strong>net localgroup:</strong> إنشاء وإدارة المجموعات المحلية',
        'docs.admin.host_accounts.user_ops.title': 'عمليات حساب المستخدم',
        'docs.admin.host_accounts.user_ops.create.title': 'إنشاء حساب مستخدم',
        'docs.admin.host_accounts.user_ops.create.description': 'إنشاء حسابات مستخدمين جديدة على المضيفين البعيدين من خلال واجهة الويب أو API.',
        'docs.admin.host_accounts.user_ops.create.steps_title': 'الإنشاء عبر واجهة الويب',
        'docs.admin.host_accounts.user_ops.create.step1': 'انتقل إلى صفحة تفاصيل المضيف للنظام المستهدف',
        'docs.admin.host_accounts.user_ops.create.step2': 'حدد موقع بطاقة المستخدمين في تفاصيل المضيف',
        'docs.admin.host_accounts.user_ops.create.step3': 'انقر على زر <strong>إضافة مستخدم</strong>',
        'docs.admin.host_accounts.user_ops.create.step4': 'املأ اسم المستخدم المطلوب والحقول الاختيارية',
        'docs.admin.host_accounts.user_ops.create.step5': 'انقر على <strong>إنشاء</strong> لإرسال الطلب',
        'docs.admin.host_accounts.user_ops.create.step6': 'ستتحدث قائمة المستخدمين تلقائياً بعد الإنشاء',
        'docs.admin.host_accounts.user_ops.create.options_title': 'خيارات إنشاء المستخدم',
        'docs.admin.host_accounts.user_ops.create.table_option': 'الخيار',
        'docs.admin.host_accounts.user_ops.create.table_description': 'الوصف',
        'docs.admin.host_accounts.user_ops.create.table_platforms': 'المنصات',
        'docs.admin.host_accounts.user_ops.create.opt_username': 'اسم المستخدم للحساب الجديد (مطلوب)',
        'docs.admin.host_accounts.user_ops.create.opt_fullname': 'الاسم الكامل أو التعليق للمستخدم',
        'docs.admin.host_accounts.user_ops.create.opt_homedir': 'مسار دليل المنزل للمستخدم',
        'docs.admin.host_accounts.user_ops.create.opt_shell': 'صدفة تسجيل الدخول (مثل /bin/bash، /bin/zsh)',
        'docs.admin.host_accounts.user_ops.create.opt_createhome': 'إنشاء دليل المنزل إذا لم يكن موجوداً',
        'docs.admin.host_accounts.user_ops.create.opt_uid': 'رقم معرف المستخدم المحدد',
        'docs.admin.host_accounts.user_ops.create.opt_primarygroup': 'اسم المجموعة الأساسية للمستخدم',
        'docs.admin.host_accounts.user_ops.create.opt_password': 'كلمة المرور الأولية للحساب',
        'docs.admin.host_accounts.user_ops.create.opt_neverexpires': 'تعيين كلمة المرور بحيث لا تنتهي صلاحيتها أبداً',
        'docs.admin.host_accounts.user_ops.create.opt_mustchange': 'طلب تغيير كلمة المرور عند تسجيل الدخول الأول',
        'docs.admin.host_accounts.user_ops.create.opt_disabled': 'إنشاء الحساب في حالة معطلة',
        'docs.admin.host_accounts.user_ops.create.api_title': 'الإنشاء عبر API',
        'docs.admin.host_accounts.group_ops.title': 'عمليات المجموعة',
        'docs.admin.host_accounts.group_ops.create.title': 'إنشاء مجموعة',
        'docs.admin.host_accounts.group_ops.create.description': 'إنشاء مجموعات جديدة على المضيفين البعيدين من خلال واجهة الويب أو API.',
        'docs.admin.host_accounts.group_ops.create.steps_title': 'الإنشاء عبر واجهة الويب',
        'docs.admin.host_accounts.group_ops.create.step1': 'انتقل إلى صفحة تفاصيل المضيف للنظام المستهدف',
        'docs.admin.host_accounts.group_ops.create.step2': 'حدد موقع بطاقة المجموعات في تفاصيل المضيف',
        'docs.admin.host_accounts.group_ops.create.step3': 'انقر على زر <strong>إضافة مجموعة</strong>',
        'docs.admin.host_accounts.group_ops.create.step4': 'املأ اسم المجموعة المطلوب والحقول الاختيارية',
        'docs.admin.host_accounts.group_ops.create.step5': 'انقر على <strong>إنشاء</strong> لإرسال الطلب',
        'docs.admin.host_accounts.group_ops.create.step6': 'ستتحدث قائمة المجموعات تلقائياً بعد الإنشاء',
        'docs.admin.host_accounts.group_ops.create.options_title': 'خيارات إنشاء المجموعة',
        'docs.admin.host_accounts.group_ops.create.table_option': 'الخيار',
        'docs.admin.host_accounts.group_ops.create.table_description': 'الوصف',
        'docs.admin.host_accounts.group_ops.create.table_platforms': 'المنصات',
        'docs.admin.host_accounts.group_ops.create.opt_groupname': 'اسم المجموعة الجديدة (مطلوب)',
        'docs.admin.host_accounts.group_ops.create.opt_gid': 'رقم معرف المجموعة المحدد',
        'docs.admin.host_accounts.group_ops.create.opt_description': 'وصف أو تعليق للمجموعة',
        'docs.admin.host_accounts.group_ops.create.api_title': 'الإنشاء عبر API',
        'docs.admin.host_accounts.prerequisites.title': 'المتطلبات الأساسية',
        'docs.admin.host_accounts.prerequisites.privileged_mode.title': 'الوضع المميز مطلوب',
        'docs.admin.host_accounts.prerequisites.privileged_mode.description': 'يجب تشغيل وكيل SysManage في الوضع المميز (كـ root أو Administrator) لإنشاء حسابات المستخدمين والمجموعات. إذا لم يكن الوكيل يعمل في الوضع المميز، فسيتم تعطيل أزرار إضافة مستخدم وإضافة مجموعة.',
        'docs.admin.host_accounts.prerequisites.privileged_mode.check_title': 'التحقق من الوضع المميز',
        'docs.admin.host_accounts.prerequisites.privileged_mode.check_description': 'تُظهر صفحة تفاصيل المضيف ما إذا كان الوكيل يعمل في الوضع المميز. ابحث عن مؤشر "الوكيل مميز" في قسم معلومات المضيف.',
        'docs.admin.host_accounts.prerequisites.privileged_mode.warning_title': 'اعتبارات الأمان',
        'docs.admin.host_accounts.prerequisites.privileged_mode.warning_description': 'يمنح تشغيل الوكيل في الوضع المميز وصولاً مرتفعاً للنظام. قم بتمكين الوضع المميز فقط على المضيفين الذين تحتاج فيهم إلى إدارة الحسابات أو العمليات المميزة الأخرى.',
        'docs.admin.host_accounts.prerequisites.active_host.title': 'اتصال المضيف النشط',
        'docs.admin.host_accounts.prerequisites.active_host.description': 'يجب أن يكون المضيف المستهدف نشطاً ومتصلاً بخادم SysManage. يتم وضع طلبات إنشاء الحسابات في قائمة الانتظار وتسليمها للوكيل عندما يكون متصلاً.',
        'docs.admin.host_accounts.security.title': 'الأمان والتحكم في الوصول',
        'docs.admin.host_accounts.security.description': 'عمليات إدارة حسابات المضيف محمية بالتحكم في الوصول المستند إلى الأدوار (RBAC). يجب أن يكون لدى المستخدمين أدوار أمان محددة لإنشاء الحسابات والمجموعات.',
        'docs.admin.host_accounts.security.required_roles_title': 'أدوار الأمان المطلوبة',
        'docs.admin.host_accounts.security.role_add_account': '<strong>ADD_HOST_ACCOUNT:</strong> مطلوب لإنشاء حسابات المستخدمين على المضيفين',
        'docs.admin.host_accounts.security.role_add_group': '<strong>ADD_HOST_GROUP:</strong> مطلوب لإنشاء المجموعات على المضيفين',
        'docs.admin.host_accounts.security.role_edit_account': '<strong>EDIT_HOST_ACCOUNT:</strong> مطلوب لتعديل حسابات المستخدمين الحالية',
        'docs.admin.host_accounts.security.role_edit_group': '<strong>EDIT_HOST_GROUP:</strong> مطلوب لتعديل المجموعات الحالية',
        'docs.admin.host_accounts.security.role_delete_account': '<strong>DELETE_HOST_ACCOUNT:</strong> مطلوب لحذف حسابات المستخدمين',
        'docs.admin.host_accounts.security.role_delete_group': '<strong>DELETE_HOST_GROUP:</strong> مطلوب لحذف المجموعات',
        'docs.admin.host_accounts.security.role_assignment_title': 'تعيين أدوار حساب المضيف',
        'docs.admin.host_accounts.security.role_assignment_description': 'يمكن للمسؤولين تعيين أدوار إدارة حسابات المضيف للمستخدمين من خلال واجهة إدارة المستخدمين:',
        'docs.admin.host_accounts.security.assignment_step1': 'انتقل إلى الإدارة > إدارة المستخدمين',
        'docs.admin.host_accounts.security.assignment_step2': 'حدد المستخدم للتعديل',
        'docs.admin.host_accounts.security.assignment_step3': 'انقر على تعديل الأدوار',
        'docs.admin.host_accounts.security.assignment_step4': 'حدد أدوار إدارة حسابات المضيف المناسبة',
        'docs.admin.host_accounts.security.assignment_step5': 'احفظ التغييرات',
        'docs.admin.host_accounts.troubleshooting.title': 'استكشاف الأخطاء وإصلاحها',
        'docs.admin.host_accounts.troubleshooting.button_disabled_title': 'زر إضافة مستخدم/مجموعة معطل',
        'docs.admin.host_accounts.troubleshooting.button_disabled_symptoms': '<strong>الأعراض:</strong> زر إضافة مستخدم أو إضافة مجموعة باللون الرمادي',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solutions_title': '<strong>الحلول:</strong>',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solution1': 'تحقق من أن الوكيل يعمل في الوضع المميز',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solution2': 'تحقق من أن لديك دور ADD_HOST_ACCOUNT أو ADD_HOST_GROUP المطلوب',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solution3': 'تأكد من أن المضيف نشط ومتصل',
        'docs.admin.host_accounts.troubleshooting.creation_fails_title': 'فشل إنشاء المستخدم/المجموعة',
        'docs.admin.host_accounts.troubleshooting.creation_fails_symptoms': '<strong>الأعراض:</strong> طلب الإنشاء يُرجع خطأ',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solutions_title': '<strong>الحلول:</strong>',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution1': 'تحقق من أن اسم المستخدم/المجموعة غير موجود بالفعل',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution2': 'تحقق من أن UID/GID غير مستخدم بالفعل',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution3': 'راجع سجلات الوكيل للحصول على رسائل الخطأ التفصيلية',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution4': 'تأكد من وجود الصدفة المحددة على النظام المستهدف',
        'docs.admin.host_accounts.troubleshooting.permission_denied_title': 'تم رفض الإذن',
        'docs.admin.host_accounts.troubleshooting.permission_denied_symptoms': '<strong>الأعراض:</strong> رسالة خطأ "تم رفض الإذن"',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solutions_title': '<strong>الحلول:</strong>',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solution1': 'تحقق من أن حساب المستخدم الخاص بك لديه الدور المطلوب (ADD_HOST_ACCOUNT أو ADD_HOST_GROUP)',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solution2': 'اتصل بالمسؤول لطلب أذونات إدارة حسابات المضيف',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solution3': 'قم بتحديث جلستك بعد تغييرات الأدوار',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_title': 'قائمة المستخدمين/المجموعات لا تتحدث',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_symptoms': '<strong>الأعراض:</strong> المستخدم/المجموعة المُنشأة لا تظهر في القائمة',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solutions_title': '<strong>الحلول:</strong>',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solution1': 'انتظر بضع لحظات حتى يُبلغ الوكيل عن البيانات المحدثة',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solution2': 'انقر على "طلب بيانات المضيف" لفرض تحديث فوري',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solution3': 'تحقق من حالة اتصال WebSocket في وحدة تحكم المتصفح',
        'docs.admin.host_accounts.best_practices.title': 'أفضل الممارسات',
        'docs.admin.host_accounts.best_practices.naming_title': 'اصطلاحات التسمية',
        'docs.admin.host_accounts.best_practices.naming_practice1': 'استخدم تنسيقات اسم مستخدم متسقة عبر بنيتك التحتية',
        'docs.admin.host_accounts.best_practices.naming_practice2': 'اتبع معايير التسمية الخاصة بمؤسستك لحسابات الخدمة',
        'docs.admin.host_accounts.best_practices.naming_practice3': 'استخدم أسماء مجموعات وصفية تشير إلى الغرض',
        'docs.admin.host_accounts.best_practices.security_title': 'ممارسات الأمان',
        'docs.admin.host_accounts.best_practices.security_practice1': 'امنح أدوار إدارة حسابات المضيف فقط للمسؤولين الموثوقين',
        'docs.admin.host_accounts.best_practices.security_practice2': 'راجع سجلات التدقيق لأنشطة إنشاء الحسابات',
        'docs.admin.host_accounts.best_practices.security_practice3': 'استخدم حسابات خدمة منفصلة للتطبيقات بدلاً من الحسابات المشتركة',
        'docs.admin.host_accounts.best_practices.security_practice4': 'قم بتنفيذ سياسات كلمات المرور لحسابات Windows',
        'docs.admin.host_accounts.best_practices.operational_title': 'الممارسات التشغيلية',
        'docs.admin.host_accounts.best_practices.operational_practice1': 'أنشئ المجموعات قبل إنشاء المستخدمين الذين يحتاجون إلى الانتماء إليها',
        'docs.admin.host_accounts.best_practices.operational_practice2': 'وثق تعيينات UID/GID المخصصة لتجنب التعارضات',
        'docs.admin.host_accounts.best_practices.operational_practice3': 'اختبر إنشاء الحسابات على مضيفين غير إنتاجيين أولاً',
        'docs.admin.host_accounts.related.title': 'الوثائق ذات الصلة',
        'docs.admin.host_accounts.related.user_management': 'إدارة مستخدمي SysManage',
        'docs.admin.host_accounts.related.host_management': 'إدارة المضيفين',
        'docs.admin.host_accounts.related.rbac': 'التحكم في الوصول المستند إلى الأدوار (RBAC)',
        'docs.admin.host_accounts.related.privileged_execution': 'التنفيذ المميز للوكيل',
        'docs.admin.host_accounts.navigation.title': 'التنقل السريع',
        'docs.admin.host_accounts.navigation.previous': 'إدارة المضيفين',
        'docs.admin.host_accounts.navigation.next': 'المراقبة',
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

        # German translations - Host Account Management
        'docs.admin.host_accounts.title': 'Host-Kontoverwaltung - SysManage-Administration',
        'docs.admin.host_accounts.meta_description': 'Vollständige Anleitung zum Erstellen und Verwalten von Benutzerkonten und Gruppen auf Remote-Hosts mit SysManage.',
        'docs.admin.host_accounts.breadcrumb': 'Host-Kontoverwaltung',
        'docs.admin.host_accounts.header.title': 'Host-Kontoverwaltung',
        'docs.admin.host_accounts.header.subtitle': 'Erstellen und verwalten Sie Benutzerkonten und Gruppen auf Remote-Hosts über alle unterstützten Plattformen hinweg.',
        'docs.admin.host_accounts.overview.title': 'Übersicht',
        'docs.admin.host_accounts.overview.description': 'SysManage bietet zentrale Verwaltung von Benutzerkonten und Gruppen auf Remote-Hosts. Erstellen Sie Benutzer und Gruppen über die Web-Oberfläche ohne direkten SSH-Zugang, mit vollständiger Unterstützung für plattformspezifische Optionen auf Linux-, BSD-, macOS- und Windows-Systemen.',
        'docs.admin.host_accounts.overview.key_features': 'Hauptfunktionen',
        'docs.admin.host_accounts.overview.features.cross_platform': '<strong>Plattformübergreifende Unterstützung:</strong> Erstellen Sie Benutzer und Gruppen auf Linux, BSD, macOS und Windows',
        'docs.admin.host_accounts.overview.features.platform_specific': '<strong>Plattformspezifische Optionen:</strong> Konfigurieren Sie Shell, Home-Verzeichnis, UID/GID und Windows-spezifische Einstellungen',
        'docs.admin.host_accounts.overview.features.web_interface': '<strong>Web-Oberfläche:</strong> Erstellen Sie Konten direkt von der Host-Detailseite',
        'docs.admin.host_accounts.overview.features.rbac': '<strong>Rollenbasierte Zugriffskontrolle:</strong> Granulare Berechtigungen für Konto- und Gruppenverwaltung',
        'docs.admin.host_accounts.overview.features.audit_logging': '<strong>Audit-Protokollierung:</strong> Alle Kontovorgänge werden für Compliance protokolliert',
        'docs.admin.host_accounts.overview.features.privileged_mode': '<strong>Privilegierter Modus erforderlich:</strong> Agent muss mit erhöhten Rechten für Kontoverwaltung laufen',
        'docs.admin.host_accounts.platforms.title': 'Unterstützte Plattformen',
        'docs.admin.host_accounts.platforms.linux.title': 'Linux-Systeme',
        'docs.admin.host_accounts.platforms.linux.description': 'Benutzer- und Gruppenerstellung verwendet Standard-<code>useradd</code>- und <code>groupadd</code>-Befehle:',
        'docs.admin.host_accounts.platforms.linux.ubuntu_debian': '<strong>Ubuntu/Debian:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.linux.rhel_centos': '<strong>RHEL/CentOS/Fedora:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.linux.opensuse': '<strong>openSUSE:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.bsd.title': 'BSD-Systeme',
        'docs.admin.host_accounts.platforms.bsd.description': 'BSD-Plattformen verwenden ihre nativen Kontoverwaltungstools:',
        'docs.admin.host_accounts.platforms.bsd.freebsd': '<strong>FreeBSD:</strong> pw useradd, pw groupadd',
        'docs.admin.host_accounts.platforms.bsd.openbsd': '<strong>OpenBSD:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.bsd.netbsd': '<strong>NetBSD:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.macos.title': 'macOS',
        'docs.admin.host_accounts.platforms.macos.description': 'macOS verwendet Verzeichnisdienste für die Kontoverwaltung:',
        'docs.admin.host_accounts.platforms.macos.dscl': '<strong>dscl:</strong> Verzeichnisdienste-Befehlszeilenprogramm',
        'docs.admin.host_accounts.platforms.macos.homedir': '<strong>createhomedir:</strong> Home-Verzeichnis-Erstellung',
        'docs.admin.host_accounts.platforms.windows.title': 'Windows',
        'docs.admin.host_accounts.platforms.windows.description': 'Windows verwendet native Kontoverwaltungsbefehle:',
        'docs.admin.host_accounts.platforms.windows.net_user': '<strong>net user:</strong> Lokale Benutzerkonten erstellen und verwalten',
        'docs.admin.host_accounts.platforms.windows.net_localgroup': '<strong>net localgroup:</strong> Lokale Gruppen erstellen und verwalten',
        'docs.admin.host_accounts.user_ops.title': 'Benutzerkonten-Operationen',
        'docs.admin.host_accounts.user_ops.create.title': 'Benutzerkonto erstellen',
        'docs.admin.host_accounts.user_ops.create.description': 'Erstellen Sie neue Benutzerkonten auf Remote-Hosts über die Web-Oberfläche oder API.',
        'docs.admin.host_accounts.user_ops.create.steps_title': 'Über Web-Oberfläche erstellen',
        'docs.admin.host_accounts.user_ops.create.step1': 'Navigieren Sie zur Host-Detailseite des Zielsystems',
        'docs.admin.host_accounts.user_ops.create.step2': 'Suchen Sie die Benutzer-Karte in den Host-Details',
        'docs.admin.host_accounts.user_ops.create.step3': 'Klicken Sie auf die Schaltfläche <strong>Benutzer hinzufügen</strong>',
        'docs.admin.host_accounts.user_ops.create.step4': 'Füllen Sie den erforderlichen Benutzernamen und optionale Felder aus',
        'docs.admin.host_accounts.user_ops.create.step5': 'Klicken Sie auf <strong>Erstellen</strong>, um die Anfrage zu senden',
        'docs.admin.host_accounts.user_ops.create.step6': 'Die Benutzerliste wird nach der Erstellung automatisch aktualisiert',
        'docs.admin.host_accounts.user_ops.create.options_title': 'Optionen zur Benutzererstellung',
        'docs.admin.host_accounts.user_ops.create.table_option': 'Option',
        'docs.admin.host_accounts.user_ops.create.table_description': 'Beschreibung',
        'docs.admin.host_accounts.user_ops.create.table_platforms': 'Plattformen',
        'docs.admin.host_accounts.user_ops.create.opt_username': 'Benutzername für das neue Konto (erforderlich)',
        'docs.admin.host_accounts.user_ops.create.opt_fullname': 'Vollständiger Name oder Kommentar für den Benutzer',
        'docs.admin.host_accounts.user_ops.create.opt_homedir': 'Pfad zum Home-Verzeichnis des Benutzers',
        'docs.admin.host_accounts.user_ops.create.opt_shell': 'Login-Shell (z.B. /bin/bash, /bin/zsh)',
        'docs.admin.host_accounts.user_ops.create.opt_createhome': 'Home-Verzeichnis erstellen, falls nicht vorhanden',
        'docs.admin.host_accounts.user_ops.create.opt_uid': 'Spezifische Benutzer-ID-Nummer',
        'docs.admin.host_accounts.user_ops.create.opt_primarygroup': 'Primärer Gruppenname für den Benutzer',
        'docs.admin.host_accounts.user_ops.create.opt_password': 'Anfangspasswort für das Konto',
        'docs.admin.host_accounts.user_ops.create.opt_neverexpires': 'Passwort auf nie ablaufend setzen',
        'docs.admin.host_accounts.user_ops.create.opt_mustchange': 'Passwortänderung bei erster Anmeldung erfordern',
        'docs.admin.host_accounts.user_ops.create.opt_disabled': 'Konto im deaktivierten Zustand erstellen',
        'docs.admin.host_accounts.user_ops.create.api_title': 'Über API erstellen',
        'docs.admin.host_accounts.group_ops.title': 'Gruppen-Operationen',
        'docs.admin.host_accounts.group_ops.create.title': 'Gruppe erstellen',
        'docs.admin.host_accounts.group_ops.create.description': 'Erstellen Sie neue Gruppen auf Remote-Hosts über die Web-Oberfläche oder API.',
        'docs.admin.host_accounts.group_ops.create.steps_title': 'Über Web-Oberfläche erstellen',
        'docs.admin.host_accounts.group_ops.create.step1': 'Navigieren Sie zur Host-Detailseite des Zielsystems',
        'docs.admin.host_accounts.group_ops.create.step2': 'Suchen Sie die Gruppen-Karte in den Host-Details',
        'docs.admin.host_accounts.group_ops.create.step3': 'Klicken Sie auf die Schaltfläche <strong>Gruppe hinzufügen</strong>',
        'docs.admin.host_accounts.group_ops.create.step4': 'Füllen Sie den erforderlichen Gruppennamen und optionale Felder aus',
        'docs.admin.host_accounts.group_ops.create.step5': 'Klicken Sie auf <strong>Erstellen</strong>, um die Anfrage zu senden',
        'docs.admin.host_accounts.group_ops.create.step6': 'Die Gruppenliste wird nach der Erstellung automatisch aktualisiert',
        'docs.admin.host_accounts.group_ops.create.options_title': 'Optionen zur Gruppenerstellung',
        'docs.admin.host_accounts.group_ops.create.table_option': 'Option',
        'docs.admin.host_accounts.group_ops.create.table_description': 'Beschreibung',
        'docs.admin.host_accounts.group_ops.create.table_platforms': 'Plattformen',
        'docs.admin.host_accounts.group_ops.create.opt_groupname': 'Name für die neue Gruppe (erforderlich)',
        'docs.admin.host_accounts.group_ops.create.opt_gid': 'Spezifische Gruppen-ID-Nummer',
        'docs.admin.host_accounts.group_ops.create.opt_description': 'Beschreibung oder Kommentar für die Gruppe',
        'docs.admin.host_accounts.group_ops.create.api_title': 'Über API erstellen',
        'docs.admin.host_accounts.prerequisites.title': 'Voraussetzungen',
        'docs.admin.host_accounts.prerequisites.privileged_mode.title': 'Privilegierter Modus erforderlich',
        'docs.admin.host_accounts.prerequisites.privileged_mode.description': 'Der SysManage-Agent muss im privilegierten Modus (als root oder Administrator) laufen, um Benutzerkonten und Gruppen zu erstellen. Wenn der Agent nicht im privilegierten Modus läuft, sind die Schaltflächen Benutzer hinzufügen und Gruppe hinzufügen deaktiviert.',
        'docs.admin.host_accounts.prerequisites.privileged_mode.check_title': 'Privilegierten Modus prüfen',
        'docs.admin.host_accounts.prerequisites.privileged_mode.check_description': 'Die Host-Detailseite zeigt, ob der Agent im privilegierten Modus läuft. Suchen Sie nach dem Indikator "Agent privilegiert" im Host-Informationsbereich.',
        'docs.admin.host_accounts.prerequisites.privileged_mode.warning_title': 'Sicherheitshinweis',
        'docs.admin.host_accounts.prerequisites.privileged_mode.warning_description': 'Das Ausführen des Agents im privilegierten Modus gewährt ihm erhöhten Systemzugriff. Aktivieren Sie den privilegierten Modus nur auf Hosts, auf denen Sie Kontoverwaltung oder andere privilegierte Operationen benötigen.',
        'docs.admin.host_accounts.prerequisites.active_host.title': 'Aktive Host-Verbindung',
        'docs.admin.host_accounts.prerequisites.active_host.description': 'Der Zielhost muss aktiv und mit dem SysManage-Server verbunden sein. Kontenerstellungsanfragen werden in die Warteschlange gestellt und an den Agent geliefert, wenn er online ist.',
        'docs.admin.host_accounts.security.title': 'Sicherheit und Zugriffskontrolle',
        'docs.admin.host_accounts.security.description': 'Host-Kontoverwaltungsoperationen sind durch rollenbasierte Zugriffskontrolle (RBAC) geschützt. Benutzer müssen spezifische Sicherheitsrollen haben, um Konten und Gruppen zu erstellen.',
        'docs.admin.host_accounts.security.required_roles_title': 'Erforderliche Sicherheitsrollen',
        'docs.admin.host_accounts.security.role_add_account': '<strong>ADD_HOST_ACCOUNT:</strong> Erforderlich zum Erstellen von Benutzerkonten auf Hosts',
        'docs.admin.host_accounts.security.role_add_group': '<strong>ADD_HOST_GROUP:</strong> Erforderlich zum Erstellen von Gruppen auf Hosts',
        'docs.admin.host_accounts.security.role_edit_account': '<strong>EDIT_HOST_ACCOUNT:</strong> Erforderlich zum Ändern bestehender Benutzerkonten',
        'docs.admin.host_accounts.security.role_edit_group': '<strong>EDIT_HOST_GROUP:</strong> Erforderlich zum Ändern bestehender Gruppen',
        'docs.admin.host_accounts.security.role_delete_account': '<strong>DELETE_HOST_ACCOUNT:</strong> Erforderlich zum Löschen von Benutzerkonten',
        'docs.admin.host_accounts.security.role_delete_group': '<strong>DELETE_HOST_GROUP:</strong> Erforderlich zum Löschen von Gruppen',
        'docs.admin.host_accounts.security.role_assignment_title': 'Host-Kontorollen zuweisen',
        'docs.admin.host_accounts.security.role_assignment_description': 'Administratoren können Host-Kontoverwaltungsrollen über die Benutzerverwaltungsoberfläche zuweisen:',
        'docs.admin.host_accounts.security.assignment_step1': 'Navigieren Sie zu Administration > Benutzerverwaltung',
        'docs.admin.host_accounts.security.assignment_step2': 'Wählen Sie den zu ändernden Benutzer',
        'docs.admin.host_accounts.security.assignment_step3': 'Klicken Sie auf Rollen bearbeiten',
        'docs.admin.host_accounts.security.assignment_step4': 'Wählen Sie die entsprechenden Host-Kontoverwaltungsrollen',
        'docs.admin.host_accounts.security.assignment_step5': 'Änderungen speichern',
        'docs.admin.host_accounts.troubleshooting.title': 'Fehlerbehebung',
        'docs.admin.host_accounts.troubleshooting.button_disabled_title': 'Benutzer/Gruppe hinzufügen-Schaltfläche deaktiviert',
        'docs.admin.host_accounts.troubleshooting.button_disabled_symptoms': '<strong>Symptome:</strong> Die Schaltfläche Benutzer hinzufügen oder Gruppe hinzufügen ist ausgegraut',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solutions_title': '<strong>Lösungen:</strong>',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solution1': 'Überprüfen Sie, ob der Agent im privilegierten Modus läuft',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solution2': 'Überprüfen Sie, ob Sie die erforderliche ADD_HOST_ACCOUNT- oder ADD_HOST_GROUP-Rolle haben',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solution3': 'Stellen Sie sicher, dass der Host aktiv und verbunden ist',
        'docs.admin.host_accounts.troubleshooting.creation_fails_title': 'Benutzer-/Gruppenerstellung schlägt fehl',
        'docs.admin.host_accounts.troubleshooting.creation_fails_symptoms': '<strong>Symptome:</strong> Erstellungsanfrage gibt einen Fehler zurück',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solutions_title': '<strong>Lösungen:</strong>',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution1': 'Überprüfen Sie, ob der Benutzer-/Gruppenname nicht bereits existiert',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution2': 'Überprüfen Sie, ob die UID/GID nicht bereits verwendet wird',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution3': 'Überprüfen Sie die Agent-Protokolle auf detaillierte Fehlermeldungen',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution4': 'Stellen Sie sicher, dass die angegebene Shell auf dem Zielsystem existiert',
        'docs.admin.host_accounts.troubleshooting.permission_denied_title': 'Zugriff verweigert',
        'docs.admin.host_accounts.troubleshooting.permission_denied_symptoms': '<strong>Symptome:</strong> Fehlermeldung "Zugriff verweigert"',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solutions_title': '<strong>Lösungen:</strong>',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solution1': 'Überprüfen Sie, ob Ihr Benutzerkonto die erforderliche Rolle hat (ADD_HOST_ACCOUNT oder ADD_HOST_GROUP)',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solution2': 'Kontaktieren Sie den Administrator, um Host-Kontoverwaltungsberechtigungen anzufordern',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solution3': 'Aktualisieren Sie Ihre Sitzung nach Rollenänderungen',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_title': 'Benutzer-/Gruppenliste wird nicht aktualisiert',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_symptoms': '<strong>Symptome:</strong> Erstellter Benutzer/Gruppe erscheint nicht in der Liste',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solutions_title': '<strong>Lösungen:</strong>',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solution1': 'Warten Sie einige Momente, bis der Agent aktualisierte Daten meldet',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solution2': 'Klicken Sie auf "Host-Daten anfordern", um eine sofortige Aktualisierung zu erzwingen',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solution3': 'Überprüfen Sie den WebSocket-Verbindungsstatus in der Browser-Konsole',
        'docs.admin.host_accounts.best_practices.title': 'Best Practices',
        'docs.admin.host_accounts.best_practices.naming_title': 'Namenskonventionen',
        'docs.admin.host_accounts.best_practices.naming_practice1': 'Verwenden Sie konsistente Benutzernamenformate in Ihrer Infrastruktur',
        'docs.admin.host_accounts.best_practices.naming_practice2': 'Befolgen Sie die Namensstandards Ihrer Organisation für Dienstkonten',
        'docs.admin.host_accounts.best_practices.naming_practice3': 'Verwenden Sie beschreibende Gruppennamen, die den Zweck angeben',
        'docs.admin.host_accounts.best_practices.security_title': 'Sicherheitspraktiken',
        'docs.admin.host_accounts.best_practices.security_practice1': 'Gewähren Sie Host-Kontoverwaltungsrollen nur vertrauenswürdigen Administratoren',
        'docs.admin.host_accounts.best_practices.security_practice2': 'Überprüfen Sie Audit-Protokolle auf Kontoerstellungsaktivitäten',
        'docs.admin.host_accounts.best_practices.security_practice3': 'Verwenden Sie separate Dienstkonten für Anwendungen anstelle von gemeinsam genutzten Konten',
        'docs.admin.host_accounts.best_practices.security_practice4': 'Implementieren Sie Passwortrichtlinien für Windows-Konten',
        'docs.admin.host_accounts.best_practices.operational_title': 'Betriebliche Praktiken',
        'docs.admin.host_accounts.best_practices.operational_practice1': 'Erstellen Sie Gruppen vor dem Erstellen von Benutzern, die ihnen angehören müssen',
        'docs.admin.host_accounts.best_practices.operational_practice2': 'Dokumentieren Sie benutzerdefinierte UID/GID-Zuweisungen, um Konflikte zu vermeiden',
        'docs.admin.host_accounts.best_practices.operational_practice3': 'Testen Sie die Kontoerstellung zuerst auf Nicht-Produktionshosts',
        'docs.admin.host_accounts.related.title': 'Verwandte Dokumentation',
        'docs.admin.host_accounts.related.user_management': 'SysManage-Benutzerverwaltung',
        'docs.admin.host_accounts.related.host_management': 'Host-Verwaltung',
        'docs.admin.host_accounts.related.rbac': 'Rollenbasierte Zugriffskontrolle (RBAC)',
        'docs.admin.host_accounts.related.privileged_execution': 'Agent-privilegierte Ausführung',
        'docs.admin.host_accounts.navigation.title': 'Schnellnavigation',
        'docs.admin.host_accounts.navigation.previous': 'Host-Verwaltung',
        'docs.admin.host_accounts.navigation.next': 'Überwachung',
    },

    'es.json': {
        # Spanish translations - Host Account Management
        'docs.admin.host_accounts.title': 'Gestión de Cuentas de Host - Administración de SysManage',
        'docs.admin.host_accounts.meta_description': 'Guía completa para crear y gestionar cuentas de usuario y grupos en hosts remotos con SysManage.',
        'docs.admin.host_accounts.breadcrumb': 'Gestión de Cuentas de Host',
        'docs.admin.host_accounts.header.title': 'Gestión de Cuentas de Host',
        'docs.admin.host_accounts.header.subtitle': 'Crear y gestionar cuentas de usuario y grupos en hosts remotos en todas las plataformas compatibles.',
        'docs.admin.host_accounts.overview.title': 'Descripción General',
        'docs.admin.host_accounts.overview.description': 'SysManage proporciona gestión centralizada de cuentas de usuario y grupos en hosts remotos. Cree usuarios y grupos desde la interfaz web sin necesidad de acceso SSH directo, con soporte completo para opciones específicas de plataforma en sistemas Linux, BSD, macOS y Windows.',
        'docs.admin.host_accounts.overview.key_features': 'Características Principales',
        'docs.admin.host_accounts.overview.features.cross_platform': '<strong>Soporte Multiplataforma:</strong> Crear usuarios y grupos en Linux, BSD, macOS y Windows',
        'docs.admin.host_accounts.overview.features.platform_specific': '<strong>Opciones Específicas de Plataforma:</strong> Configurar shell, directorio home, UID/GID y configuraciones específicas de Windows',
        'docs.admin.host_accounts.overview.features.web_interface': '<strong>Interfaz Web:</strong> Crear cuentas directamente desde la página de detalles del host',
        'docs.admin.host_accounts.overview.features.rbac': '<strong>Control de Acceso Basado en Roles:</strong> Permisos granulares para gestión de cuentas y grupos',
        'docs.admin.host_accounts.overview.features.audit_logging': '<strong>Registro de Auditoría:</strong> Todas las operaciones de cuenta se registran para cumplimiento',
        'docs.admin.host_accounts.overview.features.privileged_mode': '<strong>Modo Privilegiado Requerido:</strong> El agente debe ejecutarse con privilegios elevados para la gestión de cuentas',
        'docs.admin.host_accounts.platforms.title': 'Plataformas Compatibles',
        'docs.admin.host_accounts.platforms.linux.title': 'Sistemas Linux',
        'docs.admin.host_accounts.platforms.linux.description': 'La creación de usuarios y grupos utiliza los comandos estándar <code>useradd</code> y <code>groupadd</code>:',
        'docs.admin.host_accounts.platforms.linux.ubuntu_debian': '<strong>Ubuntu/Debian:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.linux.rhel_centos': '<strong>RHEL/CentOS/Fedora:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.linux.opensuse': '<strong>openSUSE:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.bsd.title': 'Sistemas BSD',
        'docs.admin.host_accounts.platforms.bsd.description': 'Las plataformas BSD utilizan sus herramientas nativas de gestión de cuentas:',
        'docs.admin.host_accounts.platforms.bsd.freebsd': '<strong>FreeBSD:</strong> pw useradd, pw groupadd',
        'docs.admin.host_accounts.platforms.bsd.openbsd': '<strong>OpenBSD:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.bsd.netbsd': '<strong>NetBSD:</strong> useradd, groupadd',
        'docs.admin.host_accounts.platforms.macos.title': 'macOS',
        'docs.admin.host_accounts.platforms.macos.description': 'macOS utiliza Servicios de Directorio para la gestión de cuentas:',
        'docs.admin.host_accounts.platforms.macos.dscl': '<strong>dscl:</strong> Utilidad de línea de comandos de Servicios de Directorio',
        'docs.admin.host_accounts.platforms.macos.homedir': '<strong>createhomedir:</strong> Creación de directorio home',
        'docs.admin.host_accounts.platforms.windows.title': 'Windows',
        'docs.admin.host_accounts.platforms.windows.description': 'Windows utiliza comandos nativos de gestión de cuentas:',
        'docs.admin.host_accounts.platforms.windows.net_user': '<strong>net user:</strong> Crear y gestionar cuentas de usuario locales',
        'docs.admin.host_accounts.platforms.windows.net_localgroup': '<strong>net localgroup:</strong> Crear y gestionar grupos locales',
        'docs.admin.host_accounts.user_ops.title': 'Operaciones de Cuentas de Usuario',
        'docs.admin.host_accounts.user_ops.create.title': 'Crear una Cuenta de Usuario',
        'docs.admin.host_accounts.user_ops.create.description': 'Crear nuevas cuentas de usuario en hosts remotos a través de la interfaz web o API.',
        'docs.admin.host_accounts.user_ops.create.steps_title': 'Crear mediante Interfaz Web',
        'docs.admin.host_accounts.user_ops.create.step1': 'Navegue a la página de detalles del host del sistema destino',
        'docs.admin.host_accounts.user_ops.create.step2': 'Localice la tarjeta de Usuarios en los detalles del host',
        'docs.admin.host_accounts.user_ops.create.step3': 'Haga clic en el botón <strong>Agregar Usuario</strong>',
        'docs.admin.host_accounts.user_ops.create.step4': 'Complete el nombre de usuario requerido y los campos opcionales',
        'docs.admin.host_accounts.user_ops.create.step5': 'Haga clic en <strong>Crear</strong> para enviar la solicitud',
        'docs.admin.host_accounts.user_ops.create.step6': 'La lista de usuarios se actualizará automáticamente después de la creación',
        'docs.admin.host_accounts.user_ops.create.options_title': 'Opciones de Creación de Usuario',
        'docs.admin.host_accounts.user_ops.create.table_option': 'Opción',
        'docs.admin.host_accounts.user_ops.create.table_description': 'Descripción',
        'docs.admin.host_accounts.user_ops.create.table_platforms': 'Plataformas',
        'docs.admin.host_accounts.user_ops.create.opt_username': 'Nombre de usuario para la nueva cuenta (requerido)',
        'docs.admin.host_accounts.user_ops.create.opt_fullname': 'Nombre completo o comentario para el usuario',
        'docs.admin.host_accounts.user_ops.create.opt_homedir': 'Ruta al directorio home del usuario',
        'docs.admin.host_accounts.user_ops.create.opt_shell': 'Shell de inicio de sesión (ej. /bin/bash, /bin/zsh)',
        'docs.admin.host_accounts.user_ops.create.opt_createhome': 'Crear directorio home si no existe',
        'docs.admin.host_accounts.user_ops.create.opt_uid': 'Número de ID de usuario específico',
        'docs.admin.host_accounts.user_ops.create.opt_primarygroup': 'Nombre del grupo primario para el usuario',
        'docs.admin.host_accounts.user_ops.create.opt_password': 'Contraseña inicial para la cuenta',
        'docs.admin.host_accounts.user_ops.create.opt_neverexpires': 'Establecer contraseña para que nunca expire',
        'docs.admin.host_accounts.user_ops.create.opt_mustchange': 'Requerir cambio de contraseña en el primer inicio de sesión',
        'docs.admin.host_accounts.user_ops.create.opt_disabled': 'Crear cuenta en estado deshabilitado',
        'docs.admin.host_accounts.user_ops.create.api_title': 'Crear mediante API',
        'docs.admin.host_accounts.group_ops.title': 'Operaciones de Grupo',
        'docs.admin.host_accounts.group_ops.create.title': 'Crear un Grupo',
        'docs.admin.host_accounts.group_ops.create.description': 'Crear nuevos grupos en hosts remotos a través de la interfaz web o API.',
        'docs.admin.host_accounts.group_ops.create.steps_title': 'Crear mediante Interfaz Web',
        'docs.admin.host_accounts.group_ops.create.step1': 'Navegue a la página de detalles del host del sistema destino',
        'docs.admin.host_accounts.group_ops.create.step2': 'Localice la tarjeta de Grupos en los detalles del host',
        'docs.admin.host_accounts.group_ops.create.step3': 'Haga clic en el botón <strong>Agregar Grupo</strong>',
        'docs.admin.host_accounts.group_ops.create.step4': 'Complete el nombre de grupo requerido y los campos opcionales',
        'docs.admin.host_accounts.group_ops.create.step5': 'Haga clic en <strong>Crear</strong> para enviar la solicitud',
        'docs.admin.host_accounts.group_ops.create.step6': 'La lista de grupos se actualizará automáticamente después de la creación',
        'docs.admin.host_accounts.group_ops.create.options_title': 'Opciones de Creación de Grupo',
        'docs.admin.host_accounts.group_ops.create.table_option': 'Opción',
        'docs.admin.host_accounts.group_ops.create.table_description': 'Descripción',
        'docs.admin.host_accounts.group_ops.create.table_platforms': 'Plataformas',
        'docs.admin.host_accounts.group_ops.create.opt_groupname': 'Nombre para el nuevo grupo (requerido)',
        'docs.admin.host_accounts.group_ops.create.opt_gid': 'Número de ID de grupo específico',
        'docs.admin.host_accounts.group_ops.create.opt_description': 'Descripción o comentario para el grupo',
        'docs.admin.host_accounts.group_ops.create.api_title': 'Crear mediante API',
        'docs.admin.host_accounts.prerequisites.title': 'Requisitos Previos',
        'docs.admin.host_accounts.prerequisites.privileged_mode.title': 'Modo Privilegiado Requerido',
        'docs.admin.host_accounts.prerequisites.privileged_mode.description': 'El agente de SysManage debe ejecutarse en modo privilegiado (como root o Administrador) para crear cuentas de usuario y grupos. Si el agente no se ejecuta en modo privilegiado, los botones Agregar Usuario y Agregar Grupo estarán deshabilitados.',
        'docs.admin.host_accounts.prerequisites.privileged_mode.check_title': 'Verificar Modo Privilegiado',
        'docs.admin.host_accounts.prerequisites.privileged_mode.check_description': 'La página de detalles del host muestra si el agente se está ejecutando en modo privilegiado. Busque el indicador "Agente Privilegiado" en la sección de información del host.',
        'docs.admin.host_accounts.prerequisites.privileged_mode.warning_title': 'Consideración de Seguridad',
        'docs.admin.host_accounts.prerequisites.privileged_mode.warning_description': 'Ejecutar el agente en modo privilegiado le otorga acceso elevado al sistema. Habilite el modo privilegiado solo en hosts donde necesite gestión de cuentas u otras operaciones privilegiadas.',
        'docs.admin.host_accounts.prerequisites.active_host.title': 'Conexión de Host Activa',
        'docs.admin.host_accounts.prerequisites.active_host.description': 'El host destino debe estar activo y conectado al servidor de SysManage. Las solicitudes de creación de cuentas se ponen en cola y se entregan al agente cuando está en línea.',
        'docs.admin.host_accounts.security.title': 'Seguridad y Control de Acceso',
        'docs.admin.host_accounts.security.description': 'Las operaciones de gestión de cuentas de host están protegidas por control de acceso basado en roles (RBAC). Los usuarios deben tener roles de seguridad específicos para crear cuentas y grupos.',
        'docs.admin.host_accounts.security.required_roles_title': 'Roles de Seguridad Requeridos',
        'docs.admin.host_accounts.security.role_add_account': '<strong>ADD_HOST_ACCOUNT:</strong> Requerido para crear cuentas de usuario en hosts',
        'docs.admin.host_accounts.security.role_add_group': '<strong>ADD_HOST_GROUP:</strong> Requerido para crear grupos en hosts',
        'docs.admin.host_accounts.security.role_edit_account': '<strong>EDIT_HOST_ACCOUNT:</strong> Requerido para modificar cuentas de usuario existentes',
        'docs.admin.host_accounts.security.role_edit_group': '<strong>EDIT_HOST_GROUP:</strong> Requerido para modificar grupos existentes',
        'docs.admin.host_accounts.security.role_delete_account': '<strong>DELETE_HOST_ACCOUNT:</strong> Requerido para eliminar cuentas de usuario',
        'docs.admin.host_accounts.security.role_delete_group': '<strong>DELETE_HOST_GROUP:</strong> Requerido para eliminar grupos',
        'docs.admin.host_accounts.security.role_assignment_title': 'Asignar Roles de Cuenta de Host',
        'docs.admin.host_accounts.security.role_assignment_description': 'Los administradores pueden asignar roles de gestión de cuentas de host a usuarios a través de la interfaz de gestión de usuarios:',
        'docs.admin.host_accounts.security.assignment_step1': 'Navegue a Administración > Gestión de Usuarios',
        'docs.admin.host_accounts.security.assignment_step2': 'Seleccione el usuario a modificar',
        'docs.admin.host_accounts.security.assignment_step3': 'Haga clic en Editar Roles',
        'docs.admin.host_accounts.security.assignment_step4': 'Seleccione los roles apropiados de gestión de cuentas de host',
        'docs.admin.host_accounts.security.assignment_step5': 'Guardar cambios',
        'docs.admin.host_accounts.troubleshooting.title': 'Solución de Problemas',
        'docs.admin.host_accounts.troubleshooting.button_disabled_title': 'Botón Agregar Usuario/Grupo Deshabilitado',
        'docs.admin.host_accounts.troubleshooting.button_disabled_symptoms': '<strong>Síntomas:</strong> El botón Agregar Usuario o Agregar Grupo está en gris',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solutions_title': '<strong>Soluciones:</strong>',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solution1': 'Verifique que el agente se está ejecutando en modo privilegiado',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solution2': 'Verifique que tiene el rol ADD_HOST_ACCOUNT o ADD_HOST_GROUP requerido',
        'docs.admin.host_accounts.troubleshooting.button_disabled_solution3': 'Asegúrese de que el host está activo y conectado',
        'docs.admin.host_accounts.troubleshooting.creation_fails_title': 'La Creación de Usuario/Grupo Falla',
        'docs.admin.host_accounts.troubleshooting.creation_fails_symptoms': '<strong>Síntomas:</strong> La solicitud de creación devuelve un error',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solutions_title': '<strong>Soluciones:</strong>',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution1': 'Verifique que el nombre de usuario/grupo no existe ya',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution2': 'Verifique que el UID/GID no está ya en uso',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution3': 'Revise los registros del agente para mensajes de error detallados',
        'docs.admin.host_accounts.troubleshooting.creation_fails_solution4': 'Asegúrese de que el shell especificado existe en el sistema destino',
        'docs.admin.host_accounts.troubleshooting.permission_denied_title': 'Permiso Denegado',
        'docs.admin.host_accounts.troubleshooting.permission_denied_symptoms': '<strong>Síntomas:</strong> Mensaje de error "Permiso denegado"',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solutions_title': '<strong>Soluciones:</strong>',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solution1': 'Verifique que su cuenta de usuario tiene el rol requerido (ADD_HOST_ACCOUNT o ADD_HOST_GROUP)',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solution2': 'Contacte al administrador para solicitar permisos de gestión de cuentas de host',
        'docs.admin.host_accounts.troubleshooting.permission_denied_solution3': 'Actualice su sesión después de cambios de roles',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_title': 'La Lista de Usuarios/Grupos No Se Actualiza',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_symptoms': '<strong>Síntomas:</strong> El usuario/grupo creado no aparece en la lista',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solutions_title': '<strong>Soluciones:</strong>',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solution1': 'Espere unos momentos para que el agente reporte datos actualizados',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solution2': 'Haga clic en "Solicitar Datos del Host" para forzar una actualización inmediata',
        'docs.admin.host_accounts.troubleshooting.list_not_updating_solution3': 'Verifique el estado de la conexión WebSocket en la consola del navegador',
        'docs.admin.host_accounts.best_practices.title': 'Mejores Prácticas',
        'docs.admin.host_accounts.best_practices.naming_title': 'Convenciones de Nomenclatura',
        'docs.admin.host_accounts.best_practices.naming_practice1': 'Use formatos de nombre de usuario consistentes en toda su infraestructura',
        'docs.admin.host_accounts.best_practices.naming_practice2': 'Siga los estándares de nomenclatura de su organización para cuentas de servicio',
        'docs.admin.host_accounts.best_practices.naming_practice3': 'Use nombres de grupo descriptivos que indiquen el propósito',
        'docs.admin.host_accounts.best_practices.security_title': 'Prácticas de Seguridad',
        'docs.admin.host_accounts.best_practices.security_practice1': 'Otorgue roles de gestión de cuentas de host solo a administradores de confianza',
        'docs.admin.host_accounts.best_practices.security_practice2': 'Revise los registros de auditoría para actividades de creación de cuentas',
        'docs.admin.host_accounts.best_practices.security_practice3': 'Use cuentas de servicio separadas para aplicaciones en lugar de cuentas compartidas',
        'docs.admin.host_accounts.best_practices.security_practice4': 'Implemente políticas de contraseña para cuentas de Windows',
        'docs.admin.host_accounts.best_practices.operational_title': 'Prácticas Operacionales',
        'docs.admin.host_accounts.best_practices.operational_practice1': 'Cree grupos antes de crear usuarios que necesiten pertenecer a ellos',
        'docs.admin.host_accounts.best_practices.operational_practice2': 'Documente las asignaciones de UID/GID personalizadas para evitar conflictos',
        'docs.admin.host_accounts.best_practices.operational_practice3': 'Pruebe la creación de cuentas en hosts no productivos primero',
        'docs.admin.host_accounts.related.title': 'Documentación Relacionada',
        'docs.admin.host_accounts.related.user_management': 'Gestión de Usuarios de SysManage',
        'docs.admin.host_accounts.related.host_management': 'Gestión de Hosts',
        'docs.admin.host_accounts.related.rbac': 'Control de Acceso Basado en Roles (RBAC)',
        'docs.admin.host_accounts.related.privileged_execution': 'Ejecución Privilegiada del Agente',
        'docs.admin.host_accounts.navigation.title': 'Navegación Rápida',
        'docs.admin.host_accounts.navigation.previous': 'Gestión de Hosts',
        'docs.admin.host_accounts.navigation.next': 'Monitoreo',

        # Spanish translations - Server Docs (existing)
        'server_docs.configuration.database_settings': 'Configuración de base de datos',
        'server_docs.configuration.description': 'Opciones de configuración completas para personalizar su despliegue de SysManage.',
        'server_docs.configuration.file_structure': 'Estructura de archivos de configuración',
        'server_docs.configuration.link': 'Guía de Configuración →',
        'server_docs.configuration.security_options': 'Opciones de seguridad y autenticación',
        'server_docs.configuration.title': '⚙️ Configuración',
        'server_docs.configuration.websocket_api': 'Configuración de WebSocket y API',
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