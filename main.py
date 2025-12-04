"""
Interface principale du logiciel de facturation et devis - Version PyQt6
"""
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QTabWidget, QGroupBox,
                             QLabel, QLineEdit, QPushButton, QRadioButton, 
                             QTreeWidget, QTreeWidgetItem, QTextEdit,
                             QMenuBar, QMenu, QMessageBox, QFileDialog,
                             QButtonGroup, QFormLayout, QScrollArea,
                             QComboBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap, QPainter, QBrush, QColor, QPen
from datetime import datetime
from decimal import Decimal
import json
import os
import logging
import traceback
from datetime import datetime as dt
from models import Client, Article, Devis, Facture, Entreprise
from pdf_generator import PDFGenerator
from keygen.license_manager import LicenseManager, LicenseDialog, show_trial_info
import re


class ApplicationFacturation(QMainWindow):
    """myInvo - Application principale de gestion de facturation et devis"""
    
    @staticmethod
    def get_version_info():
        """Lit les informations de version depuis version_info.txt"""
        try:
            # Essayer de lire depuis version_info.txt
            version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "version_info.txt")
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extraire la version avec regex
                version_match = re.search(r"StringStruct\(u'ProductVersion', u'([0-9.]+)'", content)
                date_match = re.search(r"date=(\(\d+, \d+\))", content)
                
                if version_match:
                    version = version_match.group(1).rsplit('.', 1)[0]  # Enlever le dernier .0
                    return {
                        'version': version,
                        'date': '04/12/2025'  # Date fixe ou calculée
                    }
        except Exception:
            pass
            
        # Valeurs par défaut si échec
        return {
            'version': '1.4.0',
            'date': '04/12/2025'
        }
    
    def __init__(self):
        super().__init__()
        version_info = self.get_version_info()
        self.setWindowTitle(f"myInvo v{version_info['version']} - Logiciel de Facturation et Devis")
        self.setGeometry(100, 100, 1200, 800)
        
        # Créer et définir l'icône de l'application
        self.setWindowIcon(self.create_app_icon())
        
        self.pdf_generator = PDFGenerator()
        self.articles_list = []
        
        # Définir le répertoire de travail selon le mode d'exécution
        self.setup_working_directory()
        
        # Créer tous les dossiers nécessaires s'ils n'existent pas
        folders_to_create = ["config", "devis", "factures", "archives", "logs"]
        for folder in folders_to_create:
            folder_path = os.path.join(self.working_dir, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
        
        # Configurer le système de logging
        self.setup_logging()
        
        # Initialiser le gestionnaire de licence
        self.license_manager = LicenseManager(self.working_dir)
        
        # Vérifier s'il y a une clé d'installation depuis l'installateur (différé pour optimiser le démarrage)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, self.check_installer_key)
        
        self.config_file = os.path.join(self.working_dir, "config", "config_entreprise.json")
        self.preferences_file = os.path.join(self.working_dir, "config", "preferences_utilisateur.json")
        
        # Charger la configuration de l'entreprise
        self.entreprise = self.charger_config_entreprise()
        
        # Charger les préférences utilisateur
        self.preferences = self.charger_preferences()
        
        self.setup_ui()
        self.setup_menu()
        
        # Logger le démarrage de l'application
        version_info = self.get_version_info()
        self.logger.info(f"=== Démarrage de myInvo v{version_info['version']} ===")
        self.logger.info(f"Système: {os.name} - Python: {sys.version}")
        self.logger.info(f"Répertoire de travail: {self.working_dir}")
        
        # Déferrer la vérification de licence après l'affichage de l'interface 
        # pour améliorer les performances de démarrage
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.check_license)  # Vérifier dans 100ms
    
    def setup_working_directory(self):
        """Configure le répertoire de travail selon le mode d'exécution"""
        if getattr(sys, 'frozen', False):
            # Application compilée avec PyInstaller
            # Utiliser le dossier d'installation comme racine
            self.working_dir = os.path.dirname(sys.executable)
        else:
            # Mode développement - utiliser le dossier courant
            self.working_dir = os.getcwd()
    
    def check_installer_key(self):
        """Vérifie s'il y a une clé d'installation depuis l'installateur"""
        temp_key_file = os.path.join(self.working_dir, "config", "install_key_temp.txt")
        
        if os.path.exists(temp_key_file):
            try:
                with open(temp_key_file, 'r', encoding='utf-8') as f:
                    install_key = f.read().strip()
                
                # Valider et enregistrer la clé
                if install_key:
                    validation_result = self.license_manager.validate_key(install_key)
                    if validation_result.get('valid', False):
                        self.license_manager.save_install_key(validation_result)
                        self.log_info(f"Clé d'installation activée automatiquement: {validation_result.get('key_type', 'unknown')}")
                        QMessageBox.information(self, "Activation réussie", 
                            f"Clé d'installation activée avec succès!\n"
                            f"Type: {validation_result.get('key_type', 'standard')}\n"
                            f"Utilisateur: {validation_result.get('user_name', 'N/A')}")
                    else:
                        self.log_error(f"Clé d'installation invalide depuis l'installateur: {validation_result.get('error', 'unknown')}")
                
                # Supprimer le fichier temporaire
                os.remove(temp_key_file)
                
            except Exception as e:
                self.log_error(f"Erreur lors de la vérification de la clé d'installation: {str(e)}")
    
    def setup_menu(self):
        """Configure le menu principal"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")
        
        ouvrir_action = QAction("Ouvrir une archive", self)
        ouvrir_action.triggered.connect(self.ouvrir_document)
        file_menu.addAction(ouvrir_action)
              
        quitter_action = QAction("Quitter", self)
        quitter_action.triggered.connect(self.close)
        file_menu.addAction(quitter_action)
        
        # Menu Paramètres
        config_menu = menubar.addMenu("Paramètres")
        
        entreprise_action = QAction("Informations Entreprise", self)
        entreprise_action.triggered.connect(self.configurer_entreprise)
        config_menu.addAction(entreprise_action)
                
        preferences_action = QAction("Préférences", self)
        preferences_action.triggered.connect(self.configurer_preferences)
        config_menu.addAction(preferences_action)
        
        config_menu.addSeparator()
        
        licence_action = QAction("Gestion de licence", self)
        licence_action.triggered.connect(self.gerer_licence)
        config_menu.addAction(licence_action)
        
        # Menu Aide
        aide_menu = menubar.addMenu("Aide")
        
        guide_action = QAction("Guide d'utilisation", self)
        guide_action.triggered.connect(self.ouvrir_guide)
        aide_menu.addAction(guide_action)
        
        licence_action = QAction("Licence", self)
        licence_action.triggered.connect(self.ouvrir_licence)
        aide_menu.addAction(licence_action)
        
        aide_menu.addSeparator()
        
        rapport_action = QAction("Journal d'événements", self)
        rapport_action.triggered.connect(self.ouvrir_rapports)
        aide_menu.addAction(rapport_action)
        
        update_action = QAction("Mise à jour...", self)
        update_action.triggered.connect(self.verifier_mise_a_jour)
        aide_menu.addAction(update_action)
        
        aide_menu.addSeparator()
        
        apropos_action = QAction("À propos", self)
        apropos_action.triggered.connect(self.afficher_apropos)
        aide_menu.addAction(apropos_action)
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Type de document
        self.setup_type_document(main_layout)
        
        # Informations du document
        self.setup_info_document(main_layout)
        
        # Informations client
        self.setup_info_client(main_layout)
        
        # Articles
        self.setup_articles(main_layout)
        
        # Totaux
        self.setup_totaux(main_layout)
        
        # Boutons d'action
        self.setup_buttons(main_layout)
        
        # Appliquer la TVA par défaut depuis les préférences
        self.article_tva.setText(self.preferences.get("tva_defaut", "20.0"))
    
    def setup_type_document(self, parent_layout):
        """Configuration du sélecteur de type de document"""
        group_box = QGroupBox("Type de document")
        layout = QHBoxLayout(group_box)
        
        self.type_doc_group = QButtonGroup()
        
        self.radio_devis = QRadioButton("Devis")
        self.radio_facture = QRadioButton("Facture")
        self.radio_devis.setChecked(True)  # Devis par défaut
        
        self.type_doc_group.addButton(self.radio_devis, 0)
        self.type_doc_group.addButton(self.radio_facture, 1)
        
        layout.addWidget(self.radio_devis)
        layout.addWidget(self.radio_facture)
        layout.addStretch()
        
        parent_layout.addWidget(group_box)
    
    def setup_info_document(self, parent_layout):
        """Configuration des informations du document"""
        group_box = QGroupBox("Informations du document")
        layout = QGridLayout(group_box)
        
        # Numéro
        layout.addWidget(QLabel("Numéro:"), 0, 0)
        self.numero_entry = QLineEdit()
        self.numero_entry.setText(self.generer_numero_document())
        layout.addWidget(self.numero_entry, 0, 1)
        
        # Date
        layout.addWidget(QLabel("Date:"), 0, 2)
        self.date_entry = QLineEdit()
        self.date_entry.setText(datetime.now().strftime("%d/%m/%Y"))
        layout.addWidget(self.date_entry, 0, 3)
        
        # Configuration des colonnes pour l'étirement
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        
        parent_layout.addWidget(group_box)
    
    def setup_info_client(self, parent_layout):
        """Configuration des informations client"""
        group_box = QGroupBox("Informations Client")
        layout = QGridLayout(group_box)
        
        # Ligne 1
        layout.addWidget(QLabel("Entreprise:"), 0, 0)
        self.client_entreprise = QLineEdit()
        layout.addWidget(self.client_entreprise, 0, 1)
        
        layout.addWidget(QLabel("Nom:"), 0, 2)
        self.client_nom = QLineEdit()
        layout.addWidget(self.client_nom, 0, 3)
        
        # Ligne 2
        layout.addWidget(QLabel("Prénom:"), 1, 0)
        self.client_prenom = QLineEdit()
        layout.addWidget(self.client_prenom, 1, 1)
        
        layout.addWidget(QLabel("Email:"), 1, 2)
        self.client_email = QLineEdit()
        layout.addWidget(self.client_email, 1, 3)
        
        # Ligne 3
        layout.addWidget(QLabel("Adresse:"), 2, 0)
        self.client_adresse = QLineEdit()
        layout.addWidget(self.client_adresse, 2, 1)
        
        layout.addWidget(QLabel("Téléphone:"), 2, 2)
        self.client_tel = QLineEdit()
        layout.addWidget(self.client_tel, 2, 3)
        
        # Ligne 4
        layout.addWidget(QLabel("Code Postal:"), 3, 0)
        self.client_cp = QLineEdit()
        layout.addWidget(self.client_cp, 3, 1)
        
        layout.addWidget(QLabel("Ville:"), 3, 2)
        self.client_ville = QLineEdit()
        layout.addWidget(self.client_ville, 3, 3)
        
        # Configuration des colonnes pour l'étirement
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(3, 1)
        
        parent_layout.addWidget(group_box)
    
    def setup_articles(self, parent_layout):
        """Configuration de la section articles"""
        group_box = QGroupBox("Articles / Prestations")
        layout = QVBoxLayout(group_box)
        
        # Formulaire d'ajout d'article
        form_layout = QHBoxLayout()
        
        form_layout.addWidget(QLabel("Désignation:"))
        self.article_designation = QLineEdit()
        self.article_designation.setMinimumWidth(250)
        form_layout.addWidget(self.article_designation)
        
        form_layout.addWidget(QLabel("Qté:"))
        self.article_qte = QLineEdit()
        self.article_qte.setMaximumWidth(80)
        form_layout.addWidget(self.article_qte)
        
        form_layout.addWidget(QLabel("Prix U. HT:"))
        self.article_prix = QLineEdit()
        self.article_prix.setMaximumWidth(100)
        form_layout.addWidget(self.article_prix)
        
        form_layout.addWidget(QLabel("TVA %:"))
        self.article_tva = QLineEdit()
        # La valeur sera définie après le chargement des préférences
        self.article_tva.setMaximumWidth(80)
        form_layout.addWidget(self.article_tva)
        
        btn_ajouter = QPushButton("Ajouter")
        btn_ajouter.clicked.connect(self.ajouter_article)
        form_layout.addWidget(btn_ajouter)
        
        form_layout.addStretch()
        
        layout.addLayout(form_layout)
        
        # Liste des articles (TreeWidget)
        self.articles_tree = QTreeWidget()
        self.articles_tree.setHeaderLabels(["Désignation", "Quantité", "Prix U. HT", "TVA %", "Total HT"])
        self.articles_tree.setColumnWidth(0, 300)
        self.articles_tree.setColumnWidth(1, 80)
        self.articles_tree.setColumnWidth(2, 100)
        self.articles_tree.setColumnWidth(3, 80)
        self.articles_tree.setColumnWidth(4, 100)
        
        layout.addWidget(self.articles_tree)
        
        # Bouton supprimer
        btn_supprimer = QPushButton("Supprimer l'article sélectionné")
        btn_supprimer.clicked.connect(self.supprimer_article)
        layout.addWidget(btn_supprimer)
        
        parent_layout.addWidget(group_box)
    
    def setup_totaux(self, parent_layout):
        """Configuration de la section totaux"""
        group_box = QGroupBox("Totaux")
        layout = QVBoxLayout(group_box)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        font = QFont()
        font.setPointSize(11)
        
        self.label_total_ht = QLabel("Total HT: 0.00 €")
        self.label_total_ht.setFont(font)
        self.label_total_ht.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.label_total_ht)
        
        self.label_total_tva = QLabel("Total TVA: 0.00 €")
        self.label_total_tva.setFont(font)
        self.label_total_tva.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.label_total_tva)
        
        font_bold = QFont()
        font_bold.setPointSize(12)
        font_bold.setBold(True)
        
        self.label_total_ttc = QLabel("Total TTC: 0.00 €")
        self.label_total_ttc.setFont(font_bold)
        self.label_total_ttc.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.label_total_ttc)
        
        parent_layout.addWidget(group_box)
    
    def setup_buttons(self, parent_layout):
        """Configuration des boutons d'action"""
        layout = QHBoxLayout()
        layout.addStretch()
        
        btn_reinitialiser = QPushButton("Réinitialiser")
        btn_reinitialiser.clicked.connect(self.reinitialiser)
        layout.addWidget(btn_reinitialiser)
        
        btn_generer = QPushButton("Générer PDF")
        btn_generer.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        btn_generer.clicked.connect(self.generer_pdf)
        layout.addWidget(btn_generer)
        
        parent_layout.addLayout(layout)
    
    def generer_numero_document(self):
        """Génère un numéro de document automatique"""
        return f"{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
    
    def charger_config_entreprise(self):
        """Charge la configuration de l'entreprise depuis le fichier JSON"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return Entreprise(**data)
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.log_error("Erreur lors du chargement de la configuration entreprise", e)
                else:
                    print(f"Erreur lors du chargement de la configuration: {e}")
        
        # Configuration par défaut si le fichier n'existe pas
        return Entreprise(
            nom="Votre Entreprise",
            adresse="123 Rue Example",
            code_postal="75000",
            ville="Paris",
            siret="123 456 789 00010",
            tva_intracommunautaire="FR12345678901",
            telephone="01 23 45 67 89",
            email="contact@entreprise.fr"
        )
    
    def sauvegarder_config_entreprise(self):
        """Sauvegarde la configuration de l'entreprise dans un fichier JSON"""
        try:
            data = {
                "nom": self.entreprise.nom,
                "adresse": self.entreprise.adresse,
                "code_postal": self.entreprise.code_postal,
                "ville": self.entreprise.ville,
                "siret": self.entreprise.siret,
                "tva_intracommunautaire": self.entreprise.tva_intracommunautaire,
                "telephone": self.entreprise.telephone,
                "email": self.entreprise.email,
                "logo": self.entreprise.logo
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.log_info("Configuration entreprise sauvegardée avec succès")
            return True
        except Exception as e:
            self.log_error("Erreur lors de la sauvegarde de la configuration entreprise", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def ajouter_article(self):
        """Ajoute un article à la liste"""
        try:
            designation = self.article_designation.text().strip()
            if not designation:
                QMessageBox.warning(self, "Attention", "Veuillez saisir une désignation")
                return
            
            qte_str = self.article_qte.text().strip()
            if not qte_str:
                QMessageBox.warning(self, "Attention", "Veuillez saisir une quantité")
                return
            
            prix_str = self.article_prix.text().strip()
            if not prix_str:
                QMessageBox.warning(self, "Attention", "Veuillez saisir un prix")
                return
            
            quantite = float(qte_str.replace(',', '.'))
            prix = Decimal(prix_str.replace(',', '.'))
            tva = Decimal(self.article_tva.text().replace(',', '.'))
            
            article = Article(
                designation=designation,
                quantite=quantite,
                prix_unitaire=prix,
                tva=tva
            )
            
            self.articles_list.append(article)
            
            # Ajouter à la TreeWidget
            item = QTreeWidgetItem([
                designation,
                str(quantite),
                f"{prix:.2f} €",
                f"{tva:.1f}%",
                f"{article.get_montant_ht():.2f} €"
            ])
            self.articles_tree.addTopLevelItem(item)
            
            # Réinitialiser les champs
            self.article_designation.clear()
            self.article_qte.clear()
            self.article_prix.clear()
            # Utiliser la TVA par défaut des préférences
            self.article_tva.setText(self.preferences.get("tva_defaut", "20.0"))
            
            self.mettre_a_jour_totaux()
            self.log_info(f"Article ajouté: {designation} - Qte: {quantite} - Prix: {prix}€ - TVA: {tva}%")
            self.log_info(f"Nombre total d'articles: {len(self.articles_list)}")
            
        except ValueError as e:
            self.log_error("Erreur de saisie lors de l'ajout d'article", e)
            QMessageBox.critical(self, "Erreur", f"Erreur de saisie: {e}")
    
    def supprimer_article(self):
        """Supprime l'article sélectionné"""
        current_item = self.articles_tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner un article")
            return
        
        # Vérifier la préférence de confirmation
        if self.preferences.get("confirmer_suppression", True):
            reply = QMessageBox.question(self, "Confirmation", 
                                       "Voulez-vous vraiment supprimer cet article ?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        index = self.articles_tree.indexOfTopLevelItem(current_item)
        article_supprime = self.articles_list[index]
        self.log_info(f"Article supprimé: {article_supprime.designation} - Index: {index}")
        
        self.articles_tree.takeTopLevelItem(index)
        del self.articles_list[index]
        
        self.log_info(f"Nombre d'articles restants: {len(self.articles_list)}")
        self.mettre_a_jour_totaux()
    
    def mettre_a_jour_totaux(self):
        """Met à jour l'affichage des totaux"""
        total_ht = sum(article.get_montant_ht() for article in self.articles_list)
        total_tva = sum(article.get_montant_tva() for article in self.articles_list)
        total_ttc = total_ht + total_tva
        
        self.label_total_ht.setText(f"Total HT: {total_ht:.2f} €")
        self.label_total_tva.setText(f"Total TVA: {total_tva:.2f} €")
        self.label_total_ttc.setText(f"Total TTC: {total_ttc:.2f} €")
        
        self.log_info(f"Totaux mis à jour - HT: {total_ht:.2f}€, TVA: {total_tva:.2f}€, TTC: {total_ttc:.2f}€")
    
    def creer_client(self):
        """Crée un objet Client à partir des champs du formulaire"""
        return Client(
            nom=self.client_nom.text().strip(),
            prenom=self.client_prenom.text().strip(),
            entreprise=self.client_entreprise.text().strip(),
            adresse=self.client_adresse.text().strip(),
            code_postal=self.client_cp.text().strip(),
            ville=self.client_ville.text().strip(),
            email=self.client_email.text().strip(),
            telephone=self.client_tel.text().strip()
        )
    
    def generer_pdf(self):
        """Génère le PDF du document"""
        self.log_info("Début de génération PDF")
        
        if not self.articles_list:
            self.log_warning("Tentative de génération PDF sans articles")
            QMessageBox.warning(self, "Attention", "Veuillez ajouter au moins un article")
            return
        
        # Vérifier l'activation et l'expiration pour la génération PDF
        install_info = self.license_manager.get_install_info()
        
        if not self.license_manager.is_activated():
            if install_info and self.license_manager.is_key_expired(install_info):
                # Clé expirée - bloquer complètement
                key_type = install_info.get('key_type', 'standard')
                
                QMessageBox.critical(self, "Licence expirée", 
                    f"Votre licence {key_type} a expiré.\n\n"
                    "La génération de PDF est bloquée.\n"
                    "Veuillez renouveler votre licence ou passer à la version Premium.")
                return
            else:
                # Version d'essai ou pas de licence
                reply = QMessageBox.question(self, "Version d'essai", 
                    "Vous utilisez la version d'essai de myInvo.\n"
                    "Voulez-vous continuer ? (Filigrane ajouté au PDF)",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply != QMessageBox.StandardButton.Yes:
                    return
        else:
            # Clé valide - vérifier si proche de l'expiration
            days_remaining = self.license_manager.get_days_remaining()
            if days_remaining != -1 and days_remaining <= 7:  # Avertir 7 jours avant expiration
                QMessageBox.information(self, "Attention", 
                    f"Votre licence expire dans {days_remaining} jour(s).\n"
                    "Pensez à la renouveler pour continuer à utiliser toutes les fonctionnalités.")
        
        client = self.creer_client()
        if not client.get_nom_complet():
            QMessageBox.warning(self, "Attention", "Veuillez renseigner au moins le nom du client ou l'entreprise")
            return
        
        try:
            # Parser la date
            date_str = self.date_entry.text()
            date = datetime.strptime(date_str, "%d/%m/%Y")
            
            numero = self.numero_entry.text().strip()
            if not numero:
                numero = self.generer_numero_document()
            
            # Créer le document
            if self.radio_devis.isChecked():
                document = Devis(
                    numero=numero,
                    date=date,
                    client=client,
                    articles=self.articles_list.copy(),
                    entreprise=self.entreprise,
                    validite_jours=30
                )
                type_label = "Devis"
            else:
                document = Facture(
                    numero=numero,
                    date=date,
                    client=client,
                    articles=self.articles_list.copy(),
                    entreprise=self.entreprise
                )
                type_label = "Facture"
            
            # Demander le nom du fichier avec le bon dossier par défaut
            dossier_defaut = os.path.join(self.working_dir, "devis" if type_label == "Devis" else "factures")
            chemin_defaut = os.path.join(dossier_defaut, f"{type_label}_{numero}.pdf")
            
            fichier, _ = QFileDialog.getSaveFileName(
                self,
                "Sauvegarder le PDF",
                chemin_defaut,
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if fichier:
                # Créer les dossiers nécessaires
                self.creer_dossiers_archive()
                
                # Sauvegarder le document en JSON
                json_filename = self.sauvegarder_document(document, type_label)
                
                # Générer le PDF
                is_trial = not self.license_manager.is_activated()
                self.pdf_generator.generer_pdf(document, fichier, type_label, is_trial)
                self.log_info(f"{type_label} généré avec succès: {fichier}")
                QMessageBox.information(self, "Succès", 
                    f"{type_label} généré(e) avec succès!\nPDF: {fichier}\nArchive: {json_filename}")
        
        except ValueError as e:
            self.log_error("Erreur de format de date lors de la génération PDF", e)
            QMessageBox.critical(self, "Erreur", f"Erreur de format de date. Utilisez JJ/MM/AAAA\n{e}")
        except Exception as e:
            self.log_error("Erreur lors de la génération du PDF", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération du PDF:\n{e}")
    
    def reinitialiser(self):
        """Réinitialise le formulaire"""
        reply = QMessageBox.question(self, "Confirmation", 
                                   "Voulez-vous vraiment réinitialiser le formulaire?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.log_info("Réinitialisation du formulaire demandée par l'utilisateur")
            
            self.numero_entry.setText(self.generer_numero_document())
            self.date_entry.setText(datetime.now().strftime("%d/%m/%Y"))
            
            self.client_entreprise.clear()
            self.client_nom.clear()
            self.client_prenom.clear()
            self.client_adresse.clear()
            self.client_cp.clear()
            self.client_ville.clear()
            self.client_email.clear()
            self.client_tel.clear()
            
            nb_articles = len(self.articles_list)
            self.articles_tree.clear()
            self.articles_list.clear()
            self.mettre_a_jour_totaux()
            
            self.log_info(f"Formulaire réinitialisé - {nb_articles} articles supprimés")
    
    def configurer_entreprise(self):
        """Ouvre une fenêtre pour configurer les informations de l'entreprise"""
        self.log_info("Ouverture de la configuration entreprise")
        dialog = ConfigurationEntrepriseDialog(self.entreprise, self)
        if dialog.exec():
            self.log_info(f"Configuration entreprise modifiée - Nom: {dialog.get_entreprise().nom}")
            self.entreprise = dialog.get_entreprise()
            self.sauvegarder_config_entreprise()
            QMessageBox.information(self, "Succès", "Informations de l'entreprise mises à jour et sauvegardées")
        else:
            self.log_info("Configuration entreprise annulée")
    
    def creer_dossiers_archive(self):
        """Crée la structure de dossiers pour l'archivage"""
        dossiers = ['archives', 'factures', 'devis']
        for dossier in dossiers:
            dossier_path = os.path.join(self.working_dir, dossier)
            if not os.path.exists(dossier_path):
                os.makedirs(dossier_path)
    
    def sauvegarder_document(self, document, type_doc):
        """Sauvegarde un document en JSON dans le dossier archives"""
        self.creer_dossiers_archive()
        
        # Préparer les données pour JSON
        data = {
            'numero': document.numero,
            'date': document.date.isoformat(),
            'entreprise': {
                'nom': document.entreprise.nom,
                'adresse': document.entreprise.adresse,
                'code_postal': document.entreprise.code_postal,
                'ville': document.entreprise.ville,
                'siret': document.entreprise.siret,
                'tva_intracommunautaire': document.entreprise.tva_intracommunautaire,
                'telephone': document.entreprise.telephone,
                'email': document.entreprise.email,
                'logo': document.entreprise.logo
            },
            'client': {
                'nom': document.client.nom,
                'prenom': document.client.prenom,
                'entreprise': document.client.entreprise,
                'adresse': document.client.adresse,
                'code_postal': document.client.code_postal,
                'ville': document.client.ville,
                'email': document.client.email,
                'telephone': document.client.telephone
            },
            'articles': [
                {
                    'designation': art.designation,
                    'quantite': float(art.quantite),
                    'prix_unitaire': float(art.prix_unitaire),
                    'tva': float(art.tva)
                } for art in document.articles
            ],
            'conditions': document.conditions,
            'notes': document.notes,
            'type': type_doc.lower()
        }
        
        # Ajouter les champs spécifiques
        if isinstance(document, Devis):
            data['validite_jours'] = document.validite_jours
        elif isinstance(document, Facture):
            data['date_echeance'] = document.date_echeance.isoformat()
            data['reference_devis'] = document.reference_devis
            data['payee'] = document.payee
        
        # Sauvegarder
        filename = os.path.join(self.working_dir, "archives", f"{type_doc.lower()}_{document.numero}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return filename
    
    def charger_document(self, filename):
        """Charge un document depuis un fichier JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstituer l'entreprise
            entreprise_data = data['entreprise']
            entreprise = Entreprise(**entreprise_data)
            
            # Reconstituer le client
            client_data = data['client']
            client = Client(**client_data)
            
            # Reconstituer les articles
            articles = []
            for art_data in data['articles']:
                article = Article(
                    designation=art_data['designation'],
                    quantite=Decimal(str(art_data['quantite'])),
                    prix_unitaire=Decimal(str(art_data['prix_unitaire'])),
                    tva=Decimal(str(art_data['tva']))
                )
                articles.append(article)
            
            # Créer le document approprié
            if data['type'] == 'devis':
                document = Devis(
                    numero=data['numero'],
                    date=datetime.fromisoformat(data['date']),
                    client=client,
                    articles=articles,
                    entreprise=entreprise,
                    conditions=data['conditions'],
                    notes=data['notes'],
                    validite_jours=data['validite_jours']
                )
            else:  # facture
                document = Facture(
                    numero=data['numero'],
                    date=datetime.fromisoformat(data['date']),
                    client=client,
                    articles=articles,
                    entreprise=entreprise,
                    conditions=data['conditions'],
                    notes=data['notes'],
                    date_echeance=datetime.fromisoformat(data['date_echeance']),
                    reference_devis=data.get('reference_devis', ''),
                    payee=data.get('payee', False)
                )
            
            return document, data['type']
            
        except Exception as e:
            self.log_error(f"Erreur lors du chargement du document {filename}", e)
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement: {e}")
            return None, None
    
    def ouvrir_document(self):
        """Ouvre une boîte de dialogue pour charger un document"""
        self.log_info("Ouverture de la boîte de dialogue pour charger un document")
        archives_dir = os.path.join(self.working_dir, "archives")
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un document",
            archives_dir,
            "Documents JSON (*.json);;All Files (*)"
        )
        
        if fichier:
            self.log_info(f"Tentative de chargement du fichier: {fichier}")
            document, type_doc = self.charger_document(fichier)
            if document:
                # Charger les données dans l'interface
                self.charger_document_dans_interface(document, type_doc)
        else:
            self.log_info("Chargement de document annulé")
    
    def charger_document_dans_interface(self, document, type_doc):
        """Charge un document dans l'interface utilisateur"""
        # Effacer les données actuelles
        self.articles_list.clear()
        self.articles_tree.clear()
        
        # Charger les informations client
        self.client_nom.setText(document.client.nom)
        self.client_prenom.setText(document.client.prenom)
        self.client_entreprise.setText(document.client.entreprise)
        self.client_adresse.setText(document.client.adresse)
        self.client_cp.setText(document.client.code_postal)
        self.client_ville.setText(document.client.ville)
        self.client_email.setText(document.client.email)
        self.client_tel.setText(document.client.telephone)
        
        # Charger les articles
        for article in document.articles:
            self.articles_list.append(article)
            item = QTreeWidgetItem([
                article.designation,
                str(article.quantite),
                f"{article.prix_unitaire:.2f} €",
                f"{article.tva:.1f}%",
                f"{article.get_montant_ht():.2f} €"
            ])
            self.articles_tree.addTopLevelItem(item)
        
        # Charger les autres informations
        self.numero_entry.setText(document.numero)
        
        # Sélectionner le type de document
        if type_doc == 'devis':
            self.radio_devis.setChecked(True)
        else:
            self.radio_facture.setChecked(True)
        
        self.mettre_a_jour_totaux()
        self.log_info(f"{type_doc.capitalize()} chargé dans l'interface - Numéro: {document.numero}, Articles: {len(document.articles)}")
        QMessageBox.information(self, "Succès", f"{type_doc.capitalize()} chargé avec succès")
    
    def charger_preferences(self):
        """Charge les préférences utilisateur depuis le fichier JSON"""
        if os.path.exists(self.preferences_file):
            try:
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                if hasattr(self, 'logger'):
                    self.log_error("Erreur lors du chargement des préférences", e)
                else:
                    print(f"Erreur lors du chargement des préférences: {e}")
        
        # Préférences par défaut
        return {
            "auto_sauvegarde": True,
            "confirmer_suppression": True,
            "tva_defaut": "20.0"
        }
    
    def sauvegarder_preferences(self):
        """Sauvegarde les préférences utilisateur dans un fichier JSON"""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde des préférences: {e}")
            return False
    

    def configurer_preferences(self):
        """Ouvre une fenêtre pour configurer les préférences utilisateur"""
        self.log_info("Ouverture de la configuration des préférences")
        dialog = PreferencesDialog(self.preferences, self)
        if dialog.exec():
            new_prefs = dialog.get_preferences()
            self.log_info(f"Préférences modifiées - TVA défaut: {new_prefs.get('tva_defaut')}%")
            self.preferences = new_prefs
            self.sauvegarder_preferences()
            # Appliquer la TVA par défaut
            self.article_tva.setText(self.preferences.get("tva_defaut", "20.0"))
            QMessageBox.information(self, "Succès", "Préférences mises à jour avec succès")
        else:
            self.log_info("Configuration des préférences annulée")
    
    def afficher_apropos(self):
        """Affiche la boîte de dialogue À propos"""
        install_info = self.license_manager.get_install_info()
        license_status = "Version d'essai"
        
        if install_info and install_info.get('valid'):
            description = install_info.get('description')
            if description:
                license_status = f"{description}"
            else:
                license_status = "Licence valide"
        
        version_info = self.get_version_info()
        apropos_text = f"""
<h2>myInvo</h2>
<p><b>Version:</b> {version_info['version']}</p>
<p><b>Date:</b> {version_info['date']}</p>
<p><b>Auteur:</b> Julien Gataleta</p>
<p><b>Copyright:</b> ©2025 Julien Gataleta</p>
<p><b>Licence:</b> {license_status}</p>
        """
        
        QMessageBox.about(self, "À propos de myInvo", apropos_text)
    
    def ouvrir_guide(self):
        """Ouvre le guide d'utilisation (README.txt)"""
        import subprocess
        import platform
        
        if getattr(sys, 'frozen', False):
            # Application compilée - utiliser sys._MEIPASS pour les ressources intégrées
            if hasattr(sys, '_MEIPASS'):
                readme_path = os.path.join(sys._MEIPASS, "README.txt")
            else:
                readme_path = os.path.join(os.path.dirname(sys.executable), "README.txt")
        else:
            # Mode développement
            readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.txt")
        
        try:
            if platform.system() == "Windows":
                os.startfile(readme_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", readme_path])
            else:  # Linux
                subprocess.run(["xdg-open", readme_path])
        except Exception as e:
            QMessageBox.information(self, "Guide d'utilisation", 
                f"Impossible d'ouvrir le guide automatiquement.\n"
                f"Veuillez ouvrir manuellement le fichier README.txt\n"
                f"Erreur: {e}")
    
    def ouvrir_licence(self):
        """Ouvre le fichier de licence (LICENCE)"""
        import subprocess
        import platform
        
        if getattr(sys, 'frozen', False):
            # Application compilée - utiliser sys._MEIPASS pour les ressources intégrées
            if hasattr(sys, '_MEIPASS'):
                licence_path = os.path.join(sys._MEIPASS, "LICENCE")
            else:
                licence_path = os.path.join(os.path.dirname(sys.executable), "LICENCE")
        else:
            # Mode développement
            licence_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LICENCE")
        
        try:
            if platform.system() == "Windows":
                os.startfile(licence_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", licence_path])
            else:  # Linux
                subprocess.run(["xdg-open", licence_path])
        except Exception as e:
            QMessageBox.information(self, "Licence", 
                f"Impossible d'ouvrir la licence automatiquement.\n"
                f"Veuillez ouvrir manuellement le fichier LICENCE\n"
                f"Erreur: {e}")
    
    def create_app_icon(self):
        """Crée l'icône de l'application directement en mémoire"""
        # Créer un pixmap de 32x32 pixels
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Dessiner un cercle de fond bleu
        painter.setBrush(QBrush(QColor(0, 120, 212)))  # Bleu Microsoft
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawEllipse(1, 1, 30, 30)
        
        # Dessiner le texte "mI" pour myInvo
        painter.setPen(QPen(QColor(255, 255, 255)))
        font = QFont("Consolas", 12, QFont.Weight.Bold)  # Police monospace avec sérifs pour le I
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "mI")
        
        painter.end()
        
        return QIcon(pixmap)
    
    def setup_logging(self):
        """Configure le système de logging pour les rapports de crash"""
        # Créer le logger principal
        self.logger = logging.getLogger('myInvo')
        self.logger.setLevel(logging.DEBUG)
        
        # Éviter la duplication des logs
        if self.logger.handlers:
            return
        
        # Format des messages de log
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler pour fichier principal (INFO et plus)
        log_file = os.path.join(self.working_dir, 'logs', f'myinvo_{dt.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler pour fichier d'erreurs (ERROR et plus)
        error_file = os.path.join(self.working_dir, 'logs', f'myinvo_errors_{dt.now().strftime("%Y%m%d")}.log')
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # Handler pour la console (développement)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
    
    def log_error(self, message, exception=None):
        """Enregistre une erreur avec tous les détails"""
        error_msg = f"ERREUR: {message}"
        if exception:
            error_msg += f" - Exception: {str(exception)}"
            error_msg += f"\nTraceback:\n{traceback.format_exc()}"
        
        self.logger.error(error_msg)
        
        # Créer un rapport de crash détaillé
        self.create_crash_report(message, exception)
    
    def log_warning(self, message):
        """Enregistre un avertissement"""
        self.logger.warning(f"ATTENTION: {message}")
    
    def log_info(self, message):
        """Enregistre une information"""
        self.logger.info(f"INFO: {message}")
    
    def create_crash_report(self, message, exception=None):
        """Crée un rapport de crash détaillé"""
        try:
            timestamp = dt.now().strftime("%Y%m%d_%H%M%S")
            crash_file = os.path.join(self.working_dir, 'logs', f'crash_report_{timestamp}.txt')
            
            with open(crash_file, 'w', encoding='utf-8') as f:
                f.write("=== RAPPORT DE CRASH - myInvo v1.0 ===\n")
                f.write(f"Date: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Système: {os.name}\n")
                f.write(f"Python: {sys.version}\n")
                f.write(f"PyQt6: {sys.modules.get('PyQt6', 'Non disponible')}\n\n")
                
                f.write(f"Message d'erreur: {message}\n\n")
                
                if exception:
                    f.write(f"Type d'exception: {type(exception).__name__}\n")
                    f.write(f"Détails: {str(exception)}\n\n")
                    f.write("Traceback complet:\n")
                    f.write(traceback.format_exc())
                    f.write("\n")
                
                # Informations sur l'état de l'application
                f.write("=== ÉTAT DE L'APPLICATION ===\n")
                f.write(f"Nombre d'articles: {len(self.articles_list)}\n")
                f.write(f"Type de document: {'Devis' if self.radio_devis.isChecked() else 'Facture'}\n")
                f.write(f"Configuration entreprise: {self.config_file}\n")
                f.write(f"Préférences: {self.preferences_file}\n\n")
                
                # Informations système
                f.write("=== INFORMATIONS SYSTÈME ===\n")
                try:
                    import psutil
                    f.write(f"RAM disponible: {psutil.virtual_memory().available / (1024**3):.1f} GB\n")
                    f.write(f"Espace disque: {psutil.disk_usage('.').free / (1024**3):.1f} GB\n")
                except (ImportError, ModuleNotFoundError, AttributeError):
                    f.write("Module psutil non disponible (informations système limitées)\n")
                except Exception as psutil_error:
                    f.write(f"Erreur lors de la récupération des informations système: {psutil_error}\n")
                
                f.write(f"Répertoire de travail: {os.getcwd()}\n")
                f.write(f"Fichiers dans le répertoire: {len(os.listdir('.'))}\n")
        
        except Exception as e:
            self.logger.error(f"Impossible de créer le rapport de crash: {e}")
    
    def ouvrir_rapports(self):
        """Ouvre le dossier des rapports de diagnostic"""
        import subprocess
        import platform
        
        logs_path = os.path.join(self.working_dir, "logs")
        
        try:
            if platform.system() == "Windows":
                os.startfile(logs_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", logs_path])
            else:  # Linux
                subprocess.run(["xdg-open", logs_path])
            
            self.log_info("Dossier du journal d'événements ouvert")
        except Exception as e:
            self.log_error("Impossible d'ouvrir le dossier des rapports", e)
            QMessageBox.information(self, "Journal d'événements", 
                f"Impossible d'ouvrir le dossier automatiquement.\n"
                f"Dossier: {logs_path}\n"
                f"Erreur: {e}")
    
    def handle_exception(self, func):
        """Décorateur pour gérer les exceptions dans les méthodes"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.log_error(f"Erreur dans {func.__name__}", e)
                QMessageBox.critical(self, "Erreur", 
                    f"Une erreur s'est produite dans {func.__name__}.\n"
                    f"Détails: {str(e)}\n\n"
                    f"Un rapport d'erreur a été créé dans le dossier 'logs'.")
                return None
        return wrapper
    
    def check_license(self):
        """Vérifie la licence au démarrage"""
        install_info = self.license_manager.get_install_info()
        
        if not self.license_manager.is_activated():
            if install_info and self.license_manager.is_key_expired(install_info):
                # Clé expirée
                key_type = install_info.get('key_type', 'standard')
                self.log_warning(f"Clé {key_type} expirée")
                self.setWindowTitle(f"myInvo - Licence {key_type} expirée")
                
                QMessageBox.warning(self, "Licence expirée", 
                    f"Votre licence {key_type} a expiré.\n\n"
                    "Certaines fonctionnalités sont bloquées.\n"
                    "Allez dans Paramètres > Gestion de licence pour renouveler.")
            else:
                # Version d'essai ou pas de licence
                self.log_warning("Application démarrée sans clé d'activation valide")
                self.setWindowTitle("myInvo - Version d'essai")
                
                # Afficher une info sur la version d'essai seulement la première fois
                if not install_info or not install_info.get('trial_shown'):
                    QMessageBox.information(self, "Version d'essai", 
                        "Vous utilisez la version d'essai de myInvo.\n\n"
                        "Certaines fonctionnalités sont limitées.\n"
                        "Allez dans Paramètres > Gestion de licence pour activer votre licence.")
        else:
            install_info = self.license_manager.get_install_info()
            self.log_info(f"Clé d'activation valide - Utilisateur: {install_info.get('user_name', 'Non spécifié')}")
            
            # Déterminer le type de version basé sur la clé
            key_type = install_info.get('key_type', 'standard')
            if key_type == 'trial':
                version_name = "Version d'essai"
            elif key_type == 'premium':
                version_name = "Version Premium"
            else:  # standard
                version_name = "Version Standard"
            
            # Ajouter le nom d'entreprise s'il existe
            company = install_info.get('company', '').strip()
            if company:
                self.setWindowTitle(f"myInvo - {version_name} - {company}")
            else:
                self.setWindowTitle(f"myInvo - {version_name}")
    
    def gerer_licence(self):
        """Ouvre le dialog de gestion de licence"""
        self.log_info("Ouverture de la gestion de licence")
        dialog = LicenseDialog(self.license_manager, self)
        if dialog.exec():
            # Recharger les informations de licence
            self.check_license()
            self.log_info("Licence mise à jour avec succès")
        else:
            self.log_info("Gestion de licence annulée")
    
    def verifier_mise_a_jour(self):
        """Permet à l'utilisateur de sélectionner un fichier de mise à jour"""
        self.log_info("Mise à jour demandée par l'utilisateur")
        
        try:
            # Ouvrir un dialogue pour sélectionner le fichier de mise à jour
            fichier_update, _ = QFileDialog.getOpenFileName(
                self,
                "Sélectionner le fichier de mise à jour",
                self.working_dir,
                "Exécutables (*.exe);;Installateurs (*.msi *.exe);;Tous les fichiers (*.*)"
            )
            
            if not fichier_update:
                self.log_info("Sélection de mise à jour annulée")
                return
            
            self.log_info(f"Fichier de mise à jour sélectionné: {fichier_update}")
            
            # Vérifier le type de fichier
            if fichier_update.lower().endswith('.exe'):
                filename = os.path.basename(fichier_update)
                
                # Si c'est un installateur (contient "setup", "install", "update")
                if any(word in filename.lower() for word in ['setup', 'install', 'update']):
                    reply = QMessageBox.question(self, "Installateur détecté", 
                        f"Fichier sélectionné : {filename}\n\n"
                        "Ce fichier semble être un installateur.\n"
                        "Voulez-vous l'exécuter maintenant ?\n\n"
                        "⚠️ L'application sera fermée avant l'installation.",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            # Programmer le lancement de l'installateur après fermeture de l'app
                            self.fichier_update_a_lancer = fichier_update
                            
                            QMessageBox.information(self, "Mise à jour", 
                                "L'application va se fermer pour permettre l'installation.\n"
                                "L'installateur sera lancé automatiquement.")
                            self.log_info(f"Programmation du lancement de l'installateur: {fichier_update}")
                            
                            # Fermer l'application - l'installateur sera lancé dans closeEvent
                            self.close()
                            
                        except Exception as e:
                            self.log_error("Erreur lors de la programmation de l'installateur", e)
                            QMessageBox.critical(self, "Erreur", 
                                f"Impossible de programmer l'installateur :\n{e}")
                
                else:
                    # C'est probablement un nouvel exécutable
                    reply = QMessageBox.question(self, "Nouveau fichier exécutable", 
                        f"Fichier sélectionné : {filename}\n\n"
                        "Voulez-vous copier ce fichier comme mise à jour ?\n"
                        "Il sera placé dans le dossier de l'application sous le nom 'myInvo_new.exe'",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            import shutil
                            destination = os.path.join(self.working_dir, "myInvo_new.exe")
                            shutil.copy2(fichier_update, destination)
                            
                            QMessageBox.information(self, "Fichier copié", 
                                f"Le fichier a été copié sous le nom 'myInvo_new.exe'.\n\n"
                                "Pour appliquer la mise à jour :\n"
                                "1. Fermez myInvo\n"
                                "2. Remplacez myInvo.exe par myInvo_new.exe\n"
                                "3. Ou utilisez le script updater.py")
                            self.log_info(f"Fichier de mise à jour copié: {destination}")
                            
                        except Exception as e:
                            self.log_error("Erreur lors de la copie du fichier", e)
                            QMessageBox.critical(self, "Erreur", 
                                f"Impossible de copier le fichier :\n{e}")
            else:
                QMessageBox.warning(self, "Type de fichier non supporté", 
                    "Veuillez sélectionner un fichier .exe (exécutable ou installateur)")
                    
        except Exception as e:
            self.log_error("Erreur lors de la sélection de mise à jour", e)
            QMessageBox.critical(self, "Erreur", 
                f"Erreur lors de la sélection de la mise à jour :\n{e}")
    
    def closeEvent(self, event):
        """Gestionnaire d'événement de fermeture de l'application"""
        try:
            # Si un fichier de mise à jour doit être lancé après fermeture
            if hasattr(self, 'fichier_update_a_lancer'):
                import subprocess
                import os
                
                fichier = self.fichier_update_a_lancer
                if os.path.exists(fichier):
                    # Lancer l'installateur après un délai pour s'assurer que l'app est fermée
                    try:
                        # Utiliser subprocess.Popen avec démarrage différé
                        subprocess.Popen([
                            'cmd', '/c', 'timeout', '/t', '2', '&&', f'"{fichier}"'
                        ], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        
                        self.log_info(f"Installateur programmé pour démarrage: {fichier}")
                    except Exception as e:
                        self.log_error("Erreur lors du lancement différé de l'installateur", e)
                        # Fallback: lancer directement
                        subprocess.Popen([fichier])
            
            # Logger la fermeture
            if hasattr(self, 'logger'):
                self.log_info("=== Fermeture de myInvo ===")
            
            # Accepter l'événement de fermeture
            event.accept()
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.log_error("Erreur lors de la fermeture de l'application", e)
            event.accept()  # Fermer quand même l'application


class ConfigurationEntrepriseDialog(QWidget):
    """Dialog pour configurer les informations de l'entreprise"""
    
    def __init__(self, entreprise, parent=None):
        super().__init__(parent, Qt.WindowType.Dialog)
        self.setWindowTitle("Configuration de l'entreprise")
        self.setFixedSize(500, 450)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.entreprise = entreprise
        self.result_code = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface du dialog"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Formulaire
        form_layout = QFormLayout()
        
        self.entries = {}
        
        fields = [
            ("Nom:", "nom"),
            ("Adresse:", "adresse"),
            ("Code Postal:", "code_postal"),
            ("Ville:", "ville"),
            ("SIRET:", "siret"),
            ("TVA Intracom.:", "tva_intracommunautaire"),
            ("Téléphone:", "telephone"),
            ("Email:", "email"),
        ]
        
        for label, attr in fields:
            entry = QLineEdit()
            entry.setText(getattr(self.entreprise, attr))
            self.entries[attr] = entry
            form_layout.addRow(label, entry)
        
        # Logo avec bouton parcourir
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        
        self.logo_entry = QLineEdit()
        self.logo_entry.setText(self.entreprise.logo)
        self.entries["logo"] = self.logo_entry
        logo_layout.addWidget(self.logo_entry)
        
        btn_parcourir = QPushButton("Parcourir")
        btn_parcourir.clicked.connect(self.parcourir_logo)
        logo_layout.addWidget(btn_parcourir)
        
        form_layout.addRow("Logo:", logo_widget)
        
        layout.addLayout(form_layout)
        
        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_annuler = QPushButton("Annuler")
        btn_annuler.clicked.connect(self.reject)
        button_layout.addWidget(btn_annuler)
        
        btn_sauvegarder = QPushButton("Sauvegarder")
        btn_sauvegarder.clicked.connect(self.accept)
        btn_sauvegarder.setDefault(True)
        button_layout.addWidget(btn_sauvegarder)
        
        layout.addLayout(button_layout)
    
    def parcourir_logo(self):
        """Ouvre le dialog de sélection de logo"""
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un logo",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg);;All Files (*)"
        )
        if fichier:
            self.logo_entry.setText(fichier)
    
    def accept(self):
        """Valide et ferme le dialog"""
        for attr, entry in self.entries.items():
            setattr(self.entreprise, attr, entry.text())
        self.result_code = 1
        self.close()
    
    def reject(self):
        """Annule et ferme le dialog"""
        self.result_code = 0
        self.close()
    
    def exec(self):
        """Affiche le dialog de manière modale"""
        self.show()
        # Simuler un dialog modal
        loop = QApplication.instance().processEvents
        while self.isVisible():
            loop()
        return self.result_code
    
    def get_entreprise(self):
        """Retourne l'objet entreprise modifié"""
        return self.entreprise


class PreferencesDialog(QWidget):
    """Dialog pour configurer les préférences utilisateur"""
    
    def __init__(self, preferences, parent=None):
        super().__init__(parent, Qt.WindowType.Dialog)
        self.setWindowTitle("Préférences")
        self.setFixedSize(400, 300)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.preferences = preferences.copy()
        self.result_code = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface du dialog"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Auto-sauvegarde
        self.auto_sauvegarde_check = QCheckBox()
        self.auto_sauvegarde_check.setChecked(self.preferences.get("auto_sauvegarde", True))
        form_layout.addRow("Auto-sauvegarde:", self.auto_sauvegarde_check)
        
        # Confirmer suppression
        self.confirmer_suppression_check = QCheckBox()
        self.confirmer_suppression_check.setChecked(self.preferences.get("confirmer_suppression", True))
        form_layout.addRow("Confirmer suppressions:", self.confirmer_suppression_check)
        
        # TVA par défaut
        self.tva_defaut_entry = QLineEdit()
        self.tva_defaut_entry.setText(self.preferences.get("tva_defaut", "20.0"))
        form_layout.addRow("TVA par défaut (%):", self.tva_defaut_entry)
        
        layout.addLayout(form_layout)
        
        # Boutons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        btn_annuler = QPushButton("Annuler")
        btn_annuler.clicked.connect(self.reject)
        button_layout.addWidget(btn_annuler)
        
        btn_sauvegarder = QPushButton("Sauvegarder")
        btn_sauvegarder.clicked.connect(self.accept)
        btn_sauvegarder.setDefault(True)
        button_layout.addWidget(btn_sauvegarder)
        
        layout.addLayout(button_layout)
    
    def accept(self):
        """Valide et ferme le dialog"""
        self.preferences["auto_sauvegarde"] = self.auto_sauvegarde_check.isChecked()
        self.preferences["confirmer_suppression"] = self.confirmer_suppression_check.isChecked()
        self.preferences["tva_defaut"] = self.tva_defaut_entry.text()
        
        self.result_code = 1
        self.close()
    
    def reject(self):
        """Annule et ferme le dialog"""
        self.result_code = 0
        self.close()
    
    def exec(self):
        """Affiche le dialog de manière modale"""
        self.show()
        # Simuler un dialog modal
        loop = QApplication.instance().processEvents
        while self.isVisible():
            loop()
        return self.result_code
    
    def get_preferences(self):
        """Retourne les préférences modifiées"""
        return self.preferences


def main():
    """Point d'entrée de l'application"""
    app = QApplication(sys.argv)
    
    # Style moderne
    app.setStyle('Fusion')
    
    # L'icône sera définie dans le constructeur de la classe
    
    window = ApplicationFacturation()
    window.show()
    
    try:
        sys.exit(app.exec())
    except Exception as e:
        if hasattr(window, 'logger'):
            window.log_error("Erreur critique lors de la fermeture de l'application", e)
        raise


if __name__ == "__main__":
    main()