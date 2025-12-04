# Changelog - myInvo

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2025-12-04

### 🛡️ Système Anti-Piratage GitHub Centralisé
- **NOUVEAU** : Suivi centralisé des activations via API GitHub privé
- **Prévention globale** : Détection cross-installations sur toutes les machines
- **Registre GitHub** : Double fichiers `activations/keys.json` + `activations/local_tracking.json`
- **Suivi anonyme** : Hash des clés et données utilisateur pour confidentialité
- **Fallback local** : Fonctionnement même si GitHub indisponible
- **Tracking temps réel** : Enregistrement immédiat de chaque activation

### 🔐 Registre Local Chiffré AES-256
- **Protection renforcée** : Registre local chiffré avec PBKDF2 + AES-256
- **Empreinte machine** : Liaison définitive clé ↔ machine via hardware fingerprint
- **Une clé = Une machine** : Impossibilité absolue de réutiliser sur autre PC
- **Révocation administrative** : Mot de passe admin pour libérer les clés
- **Chiffrement intégral** : Toutes les données sensibles protégées

### 🖥️ Interface d'Administration PyQt6
- **Interface complète** : Gestion visuelle de toutes les clés activées
- **Surveillance temps réel** : Statut local + GitHub pour chaque clé
- **Vérification croisée** : Consultation simultanée des deux systèmes
- **Administration sécurisée** : Révocation avec authentification
- **Export professionnel** : Génération de rapports d'usage
- **Tests connectivité** : Vérification GitHub en un clic

### 🔑 Générateur de Clés Unifié
- **Intégration complète** : Fonctions client intégrées dans keygen.py
- **Génération lot** : Création de 5 clés prédéfinies pour distribution
- **Sauvegarde automatique** : Formats TXT et JSON pour clients
- **Validation immédiate** : Test des clés générées en temps réel
- **Interface interactive** : Menu dédié pour génération client
- **Instructions incluses** : Fichiers avec guide d'activation

### ⚡ Optimisations Build & Distribution
- **PyInstaller optimisé** : Suppression modules non utilisés du .spec
- **Installateur v1.5.0** : Inno Setup avec nouvelles fonctionnalités
- **Documentation intégrée** : GITHUB_TRACKING.md et REGISTRE_CLES.md
- **Mise à jour automatique** : Scripts de mise à jour vers v1.5.0
- **Taille réduite** : Optimisation des dépendances empaquetées

### 🌐 Intégration API GitHub
- **Connexion sécurisée** : Authentification token personnel GitHub
- **Repository privé** : Stockage sécurisé des données de suivi
- **API REST complète** : Upload/Download automatique des activations
- **Gestion erreurs** : Retry automatique et fallback intelligent
- **Threading optimisé** : Opérations non-bloquantes pour l'interface

### 🔧 Architecture Technique
- **Modules unifiés** : Suppression client_keygen.py obsolète
- **Classes centralisées** : GitHubKeyTracker, LocalKeyTracker, KeyRegistry
- **Configuration centralisée** : Token et paramètres dans un seul endroit
- **Logging amélioré** : Traçabilité complète des opérations
- **Gestion d'état** : Synchronisation locale ↔ GitHub automatique

### 📊 Surveillance et Analytics
- **Détection piratage** : Algorithmes de détection d'usage anormal
- **Statistiques d'usage** : Nombre d'activations, machines, dates
- **Rapports détaillés** : Export des données pour analyse
- **Alertes automatiques** : Détection tentatives d'activation multiples
- **Dashboard admin** : Vue d'ensemble de toutes les licences

### 🔒 Sécurité Renforcée
- **Double protection** : Local (AES) + Cloud (GitHub privé)
- **Données anonymisées** : Seuls les hash stockés sur GitHub
- **Token rotation** : Possibilité de changer les clés d'accès
- **Audit trail** : Traçabilité complète de toutes les opérations
- **Protection RGPD** : Pas de données personnelles sur GitHub

## [1.4.2] - 2025-12-04

### 🔑 Système de Licence Corrigé
- **CORRECTION CRITIQUE** : Résolution du bug "Clé invalide (checksum incorrect)"
- **Synchronisation algorithmes** : Harmonisation entre génération et validation des clés
- **Validation informations utilisateur** : Correction du problème "informations saisies ne correspondent pas"
- **Compatibilité rétroactive** : Support maintenu pour les clés existantes
- **Identifiants uniques** : Ajout de `secrets.token_hex(4)` et hash temporel pour garantir l'unicité
- **Anti-duplication** : Historique des clés générées pour détecter et éviter les doublons

### 🚀 Performance Optimisée
- **Démarrage ultra-rapide** : Cache intelligent dans le système de licence (90% d'amélioration)
- **Vérifications différées** : License check en QTimer.singleShot(100ms) pour interface plus réactive  
- **Élimination des fenêtres terminal** : Remplacement de tous les subprocess par ctypes Windows API
- **Cache Machine ID** : Mise en cache de l'identifiant machine pour éviter les recalculs
- **Cache activation** : Statut d'activation en cache pendant 60 secondes

### 🔒 Sécurité Anti-Piratage Renforcée
- **REGISTRE CENTRALISÉ** : Système empêchant l'activation d'une clé sur plusieurs machines
- **Protection cross-installation** : Une clé = Une seule machine à vie
- **Empreinte machine unique** : Identification basée sur hardware + système
- **Machine-binding robuste** : Chaque clé reste unique même avec mêmes informations utilisateur
- **Validation cohérente** : Algorithmes de génération et validation parfaitement synchronisés
- **Chiffrement AES renforcé** : Registre des clés protégé par PBKDF2 + AES-256
- **Contrôles d'intégrité** : Validation croisée pour détecter la copie de fichiers
- **SECRET_KEY unifié** : Synchronisation des clés secrètes entre tous les modules

### ⚙️ Optimisations Techniques  
- **ctypes remplace subprocess** : Appels Windows API directs pour attributs de fichiers
- **Cache temporisé** : Système de cache intelligent avec expiration automatique
- **Imports optimisés** : Ajout des nouveaux modules au .spec PyInstaller
- **Memory management** : Réutilisation des calculs coûteux via mise en cache
- **Code nettoyé** : Suppression du système de compatibilité legacy complexe

### �️ Outils d'Administration
- **Interface graphique admin** : Gestion complète du registre des clés (`admin_keys.py`)
- **Surveillance des activations** : Liste de toutes les clés enregistrées avec détails
- **Révocation de clés** : Possibilité de libérer une clé avec mot de passe admin
- **Export des données** : Génération de rapports d'utilisation
- **Vérification de statut** : Contrôle en temps réel du statut des clés

### 🐛 Corrections Majeures
- **"Clé invalide (checksum incorrect)" RÉSOLU** : Incohérence entre génération et validation corrigée
- **"Informations ne correspondent pas" RÉSOLU** : Hash utilisateur/entreprise maintenant compatible
- **PIRATAGE IMPOSSIBLE** : Une clé ne peut plus être activée sur plusieurs machines
- **Duplication de clés éliminée** : Impossible de générer deux clés identiques
- **Lenteur démarrage corrigée** : Différé des opérations coûteuses après affichage interface
- **Fenêtres terminal supprimées** : Plus d'ouverture de cmd.exe/powershell lors du démarrage
- **Validation cross-platform** : Fonctionne correctement sur tous les PC

## [1.4.1] - 2025-12-04

### 🔒 Sécurité
- **Validation renforcée des licences** : Le système vérifie maintenant strictement que les informations utilisateur correspondent à la clé
- **Prévention d'activation frauduleuse** : Empêche l'activation de clés valides avec des informations utilisateur incorrectes
- **Contrôle d'intégrité** des informations de licence lors du chargement
- **Validation préalable** lors de la sauvegarde des clés d'installation

### 🔄 Mise à jour
- **Menu "Mise à jour..." intégré** : Nouvelle option dans le menu "Aide" pour gérer les mises à jour
- **Sélection de fichiers intuitive** : Interface de parcours de fichiers pour choisir les mises à jour
- **Détection intelligente** : Distinction automatique entre installateurs et exécutables
- **Correction du conflit d'installation** : L'application se ferme proprement avant le lancement des installateurs
- **Lancement différé sécurisé** : Système de délai pour éviter les conflits de processus
- **Système offline complet** : Mise à jour sans connexion internet requise

### ⚙️ Technique
- **Gestion automatique des versions** : Lecture depuis version_info.txt pour affichage cohérent
- **Méthode closeEvent()** : Gestion propre de la fermeture avec lancement différé d'installateurs
- **Logging amélioré** : Enregistrement de toutes les actions de mise à jour et de licence
- **Architecture modulaire** : Séparation claire entre validation et activation des licences

### 🐛 Corrections
- **Conflit installateur/application** : Les installateurs ne se lancent plus pendant que l'application est ouverte
- **Validation des informations utilisateur** : `info_verified = False` bloque maintenant l'activation
- **Cohérence des versions** : Tous les fichiers utilisent la même source de version

## [1.4.0] - 2025-12-03

### ✨ Nouveautés
- **Système de licence sécurisé** : Implémentation complète avec chiffrement AES-256
- **Générateur de clés intégré** : Keygen avec support Trial, Standard et Premium
- **Registre de licences chiffré** : Protection avancée des données de licence
- **Interface de gestion de licence** : Dialog d'activation et de validation

### 🔐 Licence
- **Support multi-types** : Trial (30j), Standard (1an), Premium (permanent)
- **Clés auto-suffisantes** : Validation cryptographique sans serveur externe
- **Protection anti-manipulation** : Système de checksum et hash sécurisé
- **Activation unique** : Chaque clé ne peut être utilisée qu'une seule fois

### 📄 Interface utilisateur
- **Interface keygen améliorée** : Espacement optimisé et champs plus larges
- **Validation en temps réel** : Vérification immédiate des clés saisies
- **Messages d'erreur détaillés** : Feedback précis pour l'utilisateur
- **Dialog d'activation** : Interface moderne et intuitive

### 🛠️ Système de mise à jour
- **Installateur de mise à jour Inno Setup** : Package professionnel
- **Vérification d'intégrité** : Contrôle SHA-256 des fichiers

### 🔧 Technique
- **Correction bug troncature** : Les noms d'utilisateurs ne sont plus tronqués
- **Validation cryptographique** : Algorithmes renforcés pour la sécurité
- **Gestion d'erreurs robuste** : Meilleure handling des cas d'échec

## [1.3.0] - 2025-12-03

### ✨ Fonctionnalités
- **Gestion des préférences utilisateur** : Configuration personnalisable de l'application
- **TVA par défaut configurable** : Paramètre sauvegardé et réutilisé automatiquement
- **Confirmations optionnelles** : Possibilité de désactiver les confirmations de suppression
- **Persistance des paramètres** : Sauvegarde automatique des préférences

### 🏢 Configuration entreprise
- **Informations complètes** : SIRET, TVA intracommunautaire, coordonnées
- **Logo d'entreprise** : Support des images pour personnalisation
- **Sauvegarde sécurisée** : Protection des données entreprise

### 📊 Interface
- **Dialog de préférences** : Interface moderne pour la configuration
- **Validation des saisies** : Contrôles automatiques des données
- **Messages d'information** : Feedback utilisateur amélioré

### 📄 Génération PDF
- **Amélioration mise en page** : Design professionnel et moderne
- **Gestion des logos** : Intégration automatique du logo entreprise
- **Calculs automatisés** : Total HT, TVA, TTC en temps réel
- **Sauvegarde flexible** : Choix du dossier et du nom de fichier

### 💾 Archivage
- **Sauvegarde JSON** : Format structuré pour la persistance
- **Réouverture des documents** : Chargement complet depuis les archives
- **Organisation des dossiers** : Structure automatique devis/factures/archives

### 🔍 Fonctionnalités
- **Numérotation automatique** : Génération intelligente des numéros
- **Validation des saisies** : Contrôles de cohérence des données
- **Gestion d'erreurs** : Messages explicites et solutions proposées

## [1.1.0] - 2025-12-01

### 👥 Gestion clients
- **Fiche client complète** : Nom, prénom, entreprise, adresse complète
- **Coordonnées étendues** : Email, téléphone, code postal, ville
- **Validation des champs** : Contrôles de saisie et formatage

### 📦 Gestion articles
- **Catalogue d'articles** : Désignation, quantité, prix unitaire, TVA
- **Interface TreeWidget** : Affichage professionnel et organisé
- **Calculs en temps réel** : Mise à jour automatique des totaux
- **Suppression sécurisée** : Confirmation avant suppression d'articles

### 🎨 Interface utilisateur
- **Design moderne** : Style Fusion avec palette de couleurs cohérente
- **Organisation en groupes** : Sections logiques pour une meilleure UX
- **Icône personnalisée** : Logo myInvo intégré à l'application

## [1.0.0] - 2025-12-01

### 🚀 Version initiale
- **Application PyQt6** : Interface graphique moderne et responsive
- **Types de documents** : Support devis et factures
- **Informations de base** : Numéro, date, client, articles
- **Génération PDF basique** : Export des documents au format PDF
- **Architecture modulaire** : Séparation modèles, vues et générateur PDF

### 🏗️ Infrastructure
- **Modèles de données** : Classes Client, Article, Devis, Facture, Entreprise
- **Générateur PDF** : Utilisation de ReportLab pour la création de documents
- **Système de logging** : Enregistrement des événements et erreurs
- **Configuration PyInstaller** : Compilation en exécutable standalone

---

## Légende des symboles

- ✨ **Nouvelles fonctionnalités**
- 🔒 **Sécurité**
- 🔄 **Mise à jour / Migration**
- ⚙️ **Technique / Architecture**
- 🐛 **Corrections de bugs**
- 📄 **Documentation**
- 🎨 **Interface utilisateur**
- 🏢 **Fonctionnalités entreprise**
- 📊 **Données / Analytics**
- 💾 **Stockage / Persistance**
- 👥 **Gestion utilisateurs**
- 📦 **Gestion contenu**
- 🔧 **Outils / Utilitaires**
- 🚀 **Performance**
- 📞 **Support / Maintenance**

---

**Développé par Julien Gataleta - Les Créa Design**  
**Copyright ©2025 - Tous droits réservés**