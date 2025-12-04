# Changelog - myInvo

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère à [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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