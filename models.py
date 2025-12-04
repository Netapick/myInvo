"""
Modèles de données pour le système de facturation et devis
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from decimal import Decimal


@dataclass
class Client:
    """Représente un client"""
    nom: str
    prenom: str = ""
    entreprise: str = ""
    adresse: str = ""
    code_postal: str = ""
    ville: str = ""
    email: str = ""
    telephone: str = ""
    
    def get_nom_complet(self) -> str:
        """Retourne le nom complet du client"""
        if self.entreprise:
            return self.entreprise
        return f"{self.prenom} {self.nom}".strip()


@dataclass
class Article:
    """Représente un article ou service"""
    designation: str
    quantite: float
    prix_unitaire: Decimal
    tva: Decimal = Decimal("20.0")  # TVA par défaut à 20%
    
    def get_montant_ht(self) -> Decimal:
        """Calcule le montant HT de l'article"""
        return Decimal(str(self.quantite)) * self.prix_unitaire
    
    def get_montant_tva(self) -> Decimal:
        """Calcule le montant de TVA"""
        return self.get_montant_ht() * (self.tva / Decimal("100"))
    
    def get_montant_ttc(self) -> Decimal:
        """Calcule le montant TTC"""
        return self.get_montant_ht() + self.get_montant_tva()


@dataclass
class Entreprise:
    """Informations de l'entreprise émettrice"""
    nom: str
    adresse: str
    code_postal: str
    ville: str
    siret: str = ""
    tva_intracommunautaire: str = ""
    telephone: str = ""
    email: str = ""
    logo: str = ""


@dataclass
class Document:
    """Classe de base pour les devis et factures"""
    numero: str
    date: datetime
    client: Client
    articles: List[Article]
    entreprise: Entreprise
    conditions: str = ""
    notes: str = ""
    
    def get_total_ht(self) -> Decimal:
        """Calcule le total HT"""
        return sum((article.get_montant_ht() for article in self.articles), Decimal("0"))
    
    def get_total_tva(self) -> Decimal:
        """Calcule le total TVA"""
        return sum((article.get_montant_tva() for article in self.articles), Decimal("0"))
    
    def get_total_ttc(self) -> Decimal:
        """Calcule le total TTC"""
        return self.get_total_ht() + self.get_total_tva()
    
    def get_tva_par_taux(self) -> dict:
        """Retourne un dictionnaire des montants de TVA par taux"""
        tva_dict = {}
        for article in self.articles:
            taux = article.tva
            if taux not in tva_dict:
                tva_dict[taux] = {"base": Decimal("0"), "montant": Decimal("0")}
            tva_dict[taux]["base"] += article.get_montant_ht()
            tva_dict[taux]["montant"] += article.get_montant_tva()
        return tva_dict


@dataclass
class Devis(Document):
    """Représente un devis"""
    validite_jours: int = 30  # Validité du devis en jours
    
    def get_date_validite(self) -> datetime:
        """Retourne la date de validité du devis"""
        from datetime import timedelta
        return self.date + timedelta(days=self.validite_jours)


@dataclass
class Facture(Document):
    """Représente une facture"""
    date_echeance: datetime = None
    reference_devis: str = ""
    payee: bool = False
    
    def __post_init__(self):
        """Initialise la date d'échéance si non fournie"""
        if self.date_echeance is None:
            from datetime import timedelta
            self.date_echeance = self.date + timedelta(days=30)
