# myInvo v1.4.1 - Logiciel de Facturation et Devis

## 📋 Description

**myInvo** est un logiciel professionnel de facturation et de devis développé en Python avec PyQt6. Conçu pour les entreprises et les freelances, il offre une interface moderne et intuitive pour la gestion complète des documents commerciaux.

## ✨ Fonctionnalités principales

### 💼 Gestion des documents
- **Devis** : Création et gestion de devis professionnels
- **Factures** : Génération de factures conformes
- **Numérotation automatique** : Système de numérotation intelligent
- **Gestion des dates** : Interface calendrier intégrée

### 👥 Gestion clients
- **Fiche client complète** : Nom, prénom, entreprise, adresse
- **Coordonnées** : Email, téléphone, code postal
- **Sauvegarde automatique** : Historique des clients

### 📦 Gestion des articles
- **Catalogue d'articles** : Désignation, quantité, prix unitaire
- **TVA configurable** : Taux de TVA personnalisables
- **Calculs automatiques** : Total HT, TVA, TTC en temps réel
- **Suppression sécurisée** : Confirmation avant suppression

### 🏢 Configuration entreprise
- **Informations complètes** : Nom, adresse, SIRET, TVA intracommunautaire
- **Logo personnalisé** : Intégration de logo d'entreprise
- **Coordonnées** : Téléphone, email professionnel

### 📄 Génération PDF
- **PDF professionnel** : Mise en page automatique et élégante
- **Sauvegarde flexible** : Choix du dossier et du nom de fichier
- **Archivage JSON** : Sauvegarde des données pour réouverture
- **Filigrane version d'essai** : Système de licence intégré

## 🔐 Système de licence sécurisé

### Types de licences
- **Trial** : Version d'évaluation (30 jours)
- **Standard** : Version complète (1 an)
- **Premium** : Version permanente (illimitée)

### Sécurité renforcée v1.4.1
- **Validation stricte** des informations utilisateur
- **Chiffrement AES-256** du registre des licences
- **Clés auto-suffisantes** avec validation cryptographique
- **Protection anti-contournement** multicouche
- **Empêche l'activation** avec des informations incorrectes

## 🔄 Système de mise à jour

### Méthodes de mise à jour
1. **Interface intégrée** : Menu "Aide" → "Mise à jour..."
2. **Installateur Inno Setup** : Packages professionnels

### Fonctionnalités avancées
- **Sélection de fichiers** : Parcourir et choisir la mise à jour
- **Détection intelligente** : Installateurs vs exécutables
- **Lancement automatique** : Sans conflit avec l'application
- **Sauvegarde** : Backup automatique avant mise à jour
- **Vérification d'intégrité** : Contrôle SHA-256

## 📊 Fonctionnalités techniques

### Architecture
- **Framework** : PyQt6 pour l'interface graphique
- **Base de données** : JSON pour la persistance
- **PDF** : ReportLab pour la génération
- **Chiffrement** : Cryptography (Fernet AES)

### Gestion des versions
- **Versionnement automatique** : Lecture depuis `version_info.txt`
- **Affichage cohérent** : Titre, logs, à propos synchronisés
- **Informations détaillées** : Version, date, description

### Logging et diagnostics
- **Journalisation complète** : Toutes les actions utilisateur
- **Rapports d'erreur** : Diagnostics automatiques
- **Niveaux de log** : INFO, WARNING, ERROR avec fichiers séparés
- **Journal d'événements** : Accessible depuis l'interface

### Préférences utilisateur
- **TVA par défaut** : Configuration personnalisable
- **Confirmations** : Activation/désactivation des alertes
- **Auto-sauvegarde** : Sauvegarde automatique optionnelle

## 📁 Structure des fichiers

```
myInvo/
├── main.py                # Application principale
├── models.py              # Modèles de données
├── pdf_generator.py       # Générateur PDF
├── version_info.txt       # Informations de version
├── compilation/spec/myInvo.spec           # Configuration PyInstaller
├── compilation/iss/myInvo_installer.iss   # Installateur complet
├── compilation/iss/update_installer.iss   # Installateur de mise à jour
├── requirements.txt       # Dépendances Python
├── README.txt             # Guide d'utilisation
├── dist/                 # Application compilée
├── installer/            # Installateurs générés
├── config/               # Configuration utilisateur
├── devis/                # Dossier des devis
├── factures/             # Dossier des factures
├── archives/             # Archives JSON
└── logs/                 # Journaux d'événements
```

## 🚀 Installation

### Prérequis
- **Windows 10/11** (64-bit recommandé)
- **Python 3.8+** (pour le développement)
- **Inno Setup** (pour la compilation des installateurs)

### Installation utilisateur final
1. Télécharger `myInvo-1.4.1.exe`
2. Exécuter l'installateur
3. Suivre l'assistant d'installation
4. Activer avec votre clé de licence

### Installation développeur
```bash
git clone [repository]
cd myInvo
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## 🛠️ Compilation

### Application
```bash
pyinstaller .\compilation\spec\myInvo.spec --noconfirm
```

### Installateurs
```bash
# Installateur complet
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" .\compilation\iss\myInvo_installer.iss

# Installateur de mise à jour
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" .\compilation\iss\update_installer.iss
```

## 📝 Changelog v1.4.1

### 🔒 Sécurité
- **Validation renforcée** des informations utilisateur avec les clés
- **Empêche l'activation** de clés avec des informations incorrectes
- **Protection anti-manipulation** du système de licence

### 🔄 Mise à jour
- **Interface intégrée** pour la sélection de mises à jour avec parcours de fichiers
- **Correction du conflit** installateur/application avec lancement différé
- **Détection intelligente** du type de fichier (installateur vs exécutable)
- **Lancement automatique** des installateurs après fermeture propre de l'application
- **Système offline complet** avec 4 méthodes (Interface, Python, Batch, Inno Setup)

### ⚙️ Technique
- **Gestion automatique des versions** depuis version_info.txt
- **Logging amélioré** avec closeEvent et gestion propre de la fermeture
- **Interface utilisateur** plus intuitive pour les mises à jour avec sélection de fichiers
- **Lancement différé sécurisé** : Évite les conflits entre application et installateurs
- **Robustesse** accrue du système de validation des licences

## 📞 Support

### Contact
- **Développeur** : Julien Gataleta
- **Copyright** : ©2025 Les Créa Design

### Documentation
- **Guide d'utilisation** : `README.txt` (inclus)
- **Licence** : `LICENCE` (inclus)
- **Journaux** : Menu "Aide" → "Journal d'événements"

---

**myInvo v1.4.1** - Solution complète et sécurisée pour votre facturation professionnelle ! 🚀