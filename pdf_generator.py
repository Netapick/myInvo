"""
Générateur de PDF pour les devis et factures
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.graphics import renderPDF
from datetime import datetime
from models import Devis, Facture, Document
from svglib.svglib import svg2rlg
import os


class PDFGenerator:
    """Génère des PDF pour les devis et factures"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configure les styles personnalisés"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=13,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT,
            fontSize=10
        ))
    
    def generer_pdf(self, document: Document, fichier_sortie: str, type_doc: str = "Devis", is_trial: bool = False):
        """
        Génère un PDF pour un document
        
        Args:
            document: Instance de Devis ou Facture
            fichier_sortie: Chemin du fichier PDF à générer
            type_doc: "Devis" ou "Facture"
            is_trial: True si version d'essai (ajoute un filigrane)
        """
        doc = SimpleDocTemplate(
            fichier_sortie,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        
        # En-tête du document
        story.extend(self._creer_entete(document, type_doc))
        
        # Informations client et entreprise
        story.extend(self._creer_infos_parties(document))
        
        # Tableau des articles
        story.extend(self._creer_tableau_articles(document))
        
        # Totaux
        story.extend(self._creer_totaux(document))
        
        # Informations spécifiques selon le type
        if isinstance(document, Devis):
            story.extend(self._creer_infos_devis(document))
        elif isinstance(document, Facture):
            story.extend(self._creer_infos_facture(document))
        
        # Conditions et notes
        if document.conditions:
            story.append(Spacer(1, 5*mm))
            story.append(Paragraph("<b>Conditions:</b>", self.styles['CustomHeading']))
            story.append(Paragraph(document.conditions, self.styles['Normal']))
        
        if document.notes:
            story.append(Spacer(1, 5*mm))
            story.append(Paragraph("<b>Notes:</b>", self.styles['CustomHeading']))
            story.append(Paragraph(document.notes, self.styles['Normal']))
        
        # Ajouter filigrane si version d'essai
        if is_trial:
            watermark = Paragraph(
                "<font color='#cccccc' size='10'>⚠️ VERSION D'ESSAI - myInvo - Achetez une licence pour supprimer ce filigrane</font>", 
                self.styles['Normal']
            )
            story.insert(0, watermark)
            story.insert(1, Spacer(1, 5))
        
        # Construction du PDF
        doc.build(story)
    
    def _creer_entete(self, document: Document, type_doc: str):
        """Crée l'en-tête du document avec logo centré verticalement par rapport au titre"""
        elements = []

        # --- Chargement du logo ---
        logo_obj = None
        if document.entreprise.logo and os.path.exists(document.entreprise.logo):
            try:
                if document.entreprise.logo.lower().endswith(".svg"):
                    drawing = svg2rlg(document.entreprise.logo)
                    scale_factor = min(70*mm / drawing.width, 70*mm / drawing.height)
                    drawing.width *= scale_factor
                    drawing.height *= scale_factor
                    drawing.scale(scale_factor, scale_factor)
                    logo_obj = drawing
                else:
                    logo_obj = Image(document.entreprise.logo, width=70*mm, height=70*mm)
            except:
                logo_obj = None

        # --- Titre ---
        title = Paragraph(f"<b>{type_doc.upper()}</b>", self.styles['CustomTitle'])

        # --- Ligne tableau LOGO + TITRE (centré) ---
        if logo_obj:
            header_table = Table(
                [
                    [logo_obj, title]
                ],
                colWidths=[30*mm, 110*mm],
                rowHeights=[25*mm]
            )

            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            
            header_table.hAlign = 'LEFT'

            elements.append(header_table)
            elements.append(Spacer(1, 8*mm))

        else:
            # Aucun logo → afficher uniquement le titre
            elements.append(title)
            elements.append(Spacer(1, 8*mm))

        # --- Numéro + Date ---
        info_data = [
            [
                Paragraph(f"<b>Numéro:</b> {document.numero}", self.styles['Normal']),
                Paragraph(f"<b>Date:</b> {document.date.strftime('%d/%m/%Y')}", self.styles['RightAlign'])
            ]
        ]

        info_table = Table(info_data, colWidths=[85*mm, 85*mm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#e8f4f8")),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
        ]))

        elements.append(info_table)
        elements.append(Spacer(1, 8*mm))

        return elements

    
    def _creer_infos_parties(self, document: Document):
        """Crée le tableau avec les infos entreprise et client"""
        elements = []
        
        # Informations entreprise
        info_entreprise = [
            f"<b>{document.entreprise.nom}</b>",
            document.entreprise.adresse,
            f"{document.entreprise.code_postal} {document.entreprise.ville}",
        ]
        if document.entreprise.siret:
            info_entreprise.append(f"SIRET: {document.entreprise.siret}")
        if document.entreprise.tva_intracommunautaire:
            info_entreprise.append(f"TVA: {document.entreprise.tva_intracommunautaire}")
        if document.entreprise.telephone:
            info_entreprise.append(f"Tél: {document.entreprise.telephone}")
        if document.entreprise.email:
            info_entreprise.append(f"Email: {document.entreprise.email}")
        
        # Informations client
        info_client = [
            f"<b>{document.client.get_nom_complet()}</b>",
        ]
        if document.client.entreprise:
            info_client.append(document.client.entreprise)
        info_client.append(document.client.adresse)
        info_client.append(f"{document.client.code_postal} {document.client.ville}")
        if document.client.email:
            info_client.append(f"Email: {document.client.email}")
        if document.client.telephone:
            info_client.append(f"Tél: {document.client.telephone}")
        
        # Création du tableau
        data = [
            [
                Paragraph("<br/>".join(info_entreprise), self.styles['Normal']),
                Paragraph("<br/>".join(info_client), self.styles['Normal'])
            ]
        ]
        
        table = Table(data, colWidths=[85*mm, 85*mm])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#1a5490')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f7fb')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 8*mm))
        
        return elements
    
    def _creer_tableau_articles(self, document: Document):
        """Crée le tableau des articles"""
        elements = []
        
        data = [['Désignation', 'Qté', 'Prix U. HT', 'TVA', 'Total HT']]
        
        # Articles
        for article in document.articles:
            data.append([
                Paragraph(article.designation, self.styles['Normal']),
                str(article.quantite),
                f"{article.prix_unitaire:.2f} €",
                f"{article.tva:.1f}%",
                f"{article.get_montant_ht():.2f} €"
            ])
        
        table = Table(data, colWidths=[80*mm, 20*mm, 25*mm, 20*mm, 25*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7f7f7')]),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 5*mm))
        
        return elements
    
    def _creer_totaux(self, document: Document):
        """Crée le tableau des totaux"""
        elements = []
        
        # Détail TVA
        tva_par_taux = document.get_tva_par_taux()
        
        data = []
        data.append(['Total HT:', f"{document.get_total_ht():.2f} €"])
        
        for taux, montants in sorted(tva_par_taux.items()):
            data.append([
                f"TVA {taux:.1f}% sur {montants['base']:.2f} €:",
                f"{montants['montant']:.2f} €"
            ])
        
        data.append(['<b>Total TTC:</b>', f"<b>{document.get_total_ttc():.2f} €</b>"])
        
        # Transformation en Paragraphs pour le style
        styled_data = []
        for row in data:
            styled_data.append([
                Paragraph(row[0], self.styles['RightAlign']),
                Paragraph(row[1], self.styles['RightAlign'])
            ])
        
        table = Table(styled_data, colWidths=[120*mm, 50*mm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1a5490')),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#cccccc')),
            ('FONTSIZE', (0, -1), (-1, -1), 13),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f4f8')),
            ('TOPPADDING', (0, -1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -2), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -2), 5),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _creer_infos_devis(self, devis: Devis):
        """Ajoute les informations spécifiques au devis"""
        elements = []
        elements.append(Spacer(1, 10*mm))
        elements.append(Paragraph(
            f"<b>Validité du devis:</b> {devis.validite_jours} jours (jusqu'au {devis.get_date_validite().strftime('%d/%m/%Y')})",
            self.styles['Normal']
        ))
        return elements
    
    def _creer_infos_facture(self, facture: Facture):
        """Ajoute les informations spécifiques à la facture"""
        elements = []
        elements.append(Spacer(1, 10*mm))
        
        if facture.reference_devis:
            elements.append(Paragraph(
                f"<b>Référence devis:</b> {facture.reference_devis}",
                self.styles['Normal']
            ))
                
        return elements
