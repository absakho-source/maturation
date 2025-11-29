"""
Générateur PDF pour les fiches d'évaluation DGPPE
Format conforme à EvaluationDetaillee.vue
Génère un PDF multi-pages avec toutes les sections, scores et recommandations
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors

class FicheEvaluationDGPPEPDF:
    """Classe pour générer le PDF de la fiche d'évaluation DGPPE"""

    def __init__(self, fiche_data, project_data, output_path, version_affichage=None):
        self.fiche = fiche_data
        self.project = project_data
        self.output_path = output_path
        self.version_affichage = version_affichage

        # Configuration du document A4 avec marges
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        self.styles = getSampleStyleSheet()

        # Couleurs DGPPE
        self.dgppe_green = HexColor('#2d7a2d')
        self.dgppe_blue = HexColor('#3498db')

        self._setup_custom_styles()
        self.story = []

    def _setup_custom_styles(self):
        """Configuration des styles personnalisés"""
        # Style pour l'en-tête République
        self.styles.add(ParagraphStyle(
            name='RepublicHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=2,
            leading=12
        ))

        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceBefore=10,
            spaceAfter=15
        ))

        # Style pour les titres de section (I, II, III, IV)
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceBefore=15,
            spaceAfter=10
        ))

        # Style pour le texte normal
        self.styles.add(ParagraphStyle(
            name='DGPPEBodyText',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_JUSTIFY,
            spaceBefore=3,
            spaceAfter=3
        ))

        # Style pour les labels
        self.styles.add(ParagraphStyle(
            name='Label',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=colors.black
        ))

    def _create_header(self):
        """Création de l'en-tête officiel"""
        # En-tête texte centré
        header_text = Paragraph(
            "<b>MINISTÈRE DE L'ÉCONOMIE, DU PLAN ET DE LA COOPÉRATION</b><br/>"
            "<b>DIRECTION GÉNÉRALE DE LA PLANIFICATION ET DES POLITIQUES ÉCONOMIQUES</b><br/>"
            "<b>PLATEFORME DE SUIVI DE LA MATURATION DES PROJETS</b>",
            self.styles['RepublicHeader']
        )

        # Créer un tableau pour l'en-tête avec bordure
        header_table = Table([[header_text]], colWidths=[17*cm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ('BOX', (0, 0), (0, 0), 1.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, 0), Color(0.95, 0.98, 0.95)),
            ('TOPPADDING', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 10)
        ]))

        self.story.append(header_table)
        self.story.append(Spacer(1, 15))

        # Titre principal
        title = Paragraph("FICHE D'ÉVALUATION", self.styles['MainTitle'])
        self.story.append(title)

        # Date et heure de génération
        date_generation = datetime.now().strftime("%d/%m/%Y à %H:%M:%S")
        date_para = Paragraph(
            f"<i>Générée le {date_generation}</i>",
            ParagraphStyle(
                name='DateGeneration',
                parent=self.styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=HexColor('#6c757d'),
                spaceBefore=5,
                spaceAfter=5
            )
        )
        self.story.append(date_para)

        # Version du formulaire (si disponible)
        if self.version_affichage:
            version_para = Paragraph(
                f"<i>{self.version_affichage}</i>",
                ParagraphStyle(
                    name='VersionInfo',
                    parent=self.styles['Normal'],
                    fontSize=9,
                    alignment=TA_CENTER,
                    textColor=HexColor('#6c757d')
                )
            )
            self.story.append(version_para)
            self.story.append(Spacer(1, 15))
        else:
            self.story.append(Spacer(1, 20))

    def _create_section_I(self):
        """Section I - PRÉSENTATION DU PROJET"""
        # Titre de section avec fond bleu
        section_title_table = Table(
            [[Paragraph("I - PRÉSENTATION DU PROJET", self.styles['SectionHeader'])]],
            colWidths=[17*cm]
        )
        section_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.dgppe_blue),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 10)
        ]))
        self.story.append(section_title_table)
        self.story.append(Spacer(1, 10))

        # Intitulé du projet (centré)
        intitule = self.project.get('titre', 'N/A')
        intitule_para = Paragraph(
            f"<b>INTITULÉ DU PROJET: {intitule}</b>",
            ParagraphStyle(
                name='IntituleCentered',
                parent=self.styles['Label'],
                fontSize=11,
                alignment=TA_CENTER
            )
        )
        self.story.append(intitule_para)
        self.story.append(Spacer(1, 10))

        # Grille d'informations (2 colonnes)
        data = []

        # Ligne 1: Secteur et Pôles
        data.append([
            Paragraph("<b>SECTEUR DE PLANIFICATION:</b>", self.styles['Label']),
            Paragraph(str(self.project.get('secteur', 'N/A')), self.styles['DGPPEBodyText']),
            Paragraph("<b>PÔLES TERRITORIAUX:</b>", self.styles['Label']),
            Paragraph(str(self.project.get('poles', 'N/A')), self.styles['DGPPEBodyText'])
        ])

        # Ligne 2: Coût et Organisme (organisé de tutelle centré)
        cout_text = self._format_currency(self.project.get('cout_estimatif', 0))
        data.append([
            Paragraph("<b>COÛT DU PROJET:</b>", self.styles['Label']),
            Paragraph(cout_text, self.styles['DGPPEBodyText']),
            '', ''
        ])

        # Ligne 3: Organisme de tutelle (centré, pleine largeur)
        organisme = self.project.get('organisme_tutelle', "MINISTÈRE DE L'ÉCONOMIE, DU PLAN ET DE LA COOPÉRATION")
        data.append([
            Paragraph("<b>ORGANISME DE TUTELLE:</b>", self.styles['Label']),
            Paragraph(organisme, ParagraphStyle(
                name='OrganismeCentered',
                parent=self.styles['DGPPEBodyText'],
                alignment=TA_CENTER
            )),
            '', ''
        ])

        # Ligne 4: Description (pleine largeur)
        description = self.project.get('description', 'N/A')
        data.append([
            Paragraph("<b>DESCRIPTION DU PROJET:</b>", self.styles['Label']),
            Paragraph(description, self.styles['DGPPEBodyText']),
            '', ''
        ])

        table = Table(data, colWidths=[4*cm, 4.5*cm, 4*cm, 4.5*cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), Color(0.95, 0.95, 0.95)),
            ('BACKGROUND', (2, 0), (2, 0), Color(0.95, 0.95, 0.95)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('SPAN', (1, 1), (3, 1)),  # Coût
            ('SPAN', (1, 2), (3, 2)),  # Organisme
            ('SPAN', (1, 3), (3, 3)),  # Description
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 15))

    def _create_section_II(self):
        """Section II - CLASSIFICATION DU PROJET"""
        # Titre de section avec fond bleu
        section_title_table = Table(
            [[Paragraph("II - CLASSIFICATION DU PROJET", self.styles['SectionHeader'])]],
            colWidths=[17*cm]
        )
        section_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.dgppe_blue),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 10)
        ]))
        self.story.append(section_title_table)
        self.story.append(Spacer(1, 10))

        # Origine et typologie (depuis project_data, pas fiche_data)
        origine_data = self.project.get('origine_projet', {})
        typologie_data = self.project.get('typologie_projet', {})

        # Construire les textes avec cases cochées (utiliser [X] et [ ] pour compatibilité)
        origine_items = []
        if origine_data.get('maturation'): origine_items.append('<b>[X]</b> MATURATION')
        else: origine_items.append('[ ] MATURATION')
        if origine_data.get('offre_spontanee'): origine_items.append('<b>[X]</b> OFFRE SPONTANÉE')
        else: origine_items.append('[ ] OFFRE SPONTANÉE')
        if origine_data.get('autres'): origine_items.append('<b>[X]</b> AUTRES')
        else: origine_items.append('[ ] AUTRES')

        typologie_items = []
        if typologie_data.get('productif'): typologie_items.append('<b>[X]</b> PRODUCTIF')
        else: typologie_items.append('[ ] PRODUCTIF')
        if typologie_data.get('appui_production'): typologie_items.append('<b>[X]</b> APPUI À LA PRODUCTION')
        else: typologie_items.append('[ ] APPUI À LA PRODUCTION')
        if typologie_data.get('social'): typologie_items.append('<b>[X]</b> SOCIAL')
        else: typologie_items.append('[ ] SOCIAL')
        if typologie_data.get('environnemental'): typologie_items.append('<b>[X]</b> ENVIRONNEMENTAL')
        else: typologie_items.append('[ ] ENVIRONNEMENTAL')

        data = [
            [
                Paragraph("<b>ORIGINE DU PROJET:</b>", self.styles['Label']),
                Paragraph(' &nbsp;&nbsp; '.join(origine_items), self.styles['DGPPEBodyText'])
            ],
            [
                Paragraph("<b>TYPOLOGIE DU PROJET:</b>", self.styles['Label']),
                Paragraph(' &nbsp;&nbsp; '.join(typologie_items), self.styles['DGPPEBodyText'])
            ]
        ]

        table = Table(data, colWidths=[5*cm, 12*cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), Color(0.95, 0.95, 0.95)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 15))

    def _create_section_III(self):
        """Section III - RÉSULTATS DE L'ÉVALUATION"""
        # Titre de section avec fond bleu
        section_title_table = Table(
            [[Paragraph("III - RÉSULTATS DE L'ÉVALUATION", self.styles['SectionHeader'])]],
            colWidths=[17*cm]
        )
        section_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.dgppe_blue),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 10)
        ]))
        self.story.append(section_title_table)
        self.story.append(Spacer(1, 10))

        # En-tête du tableau des critères
        criteres = self.fiche.get('criteres', {})

        # Liste complète des 13 critères
        criteria_list = [
            ('PERTINENCE', 'pertinence', 5),
            ('ALIGNEMENT À LA DOCTRINE DE TRANSFORMATION SYSTÉMIQUE', 'alignement', 10),
            ('PERTINENCE DES ACTIVITÉS ET BIEN FONDÉ DES COÛTS/PART DE FONCTIONNEMENT', 'activites_couts', 15),
            ('ÉQUITÉ (SOCIALE-TERRITORIALE-GENRE)', 'equite', 15),
            ('VIABILITÉ/RENTABILITÉ FINANCIÈRE', 'viabilite', 5),
            ('RENTABILITÉ SOCIO-ÉCONOMIQUE (ACA/MPR)', 'rentabilite', 5),
            ('BÉNÉFICES STRATÉGIQUES (SÉCURITÉ-RÉSILIENCE-INNOVATION-COMPÉTITIVITÉ-CONTENU LOCAL, ETC.)', 'benefices_strategiques', 10),
            ('PÉRENNITÉ ET DURABILITÉ DES EFFETS ET IMPACTS DU PROJET', 'perennite', 5),
            ('AVANTAGES ET COÛTS INTANGIBLES', 'avantages_intangibles', 10),
            ('FAISABILITÉ DU PROJET / RISQUES POTENTIELS', 'faisabilite', 5),
            ('POTENTIALITÉ OU OPPORTUNITÉ DU PROJET À ÊTRE RÉALISÉ EN PPP', 'ppp', 5),
            ('IMPACTS ENVIRONNEMENTAUX', 'impact_environnemental', 5),
            ('IMPACT SUR L\'EMPLOI', 'impact_emploi', 5)
        ]

        # Créer le tableau des critères
        data = []

        # En-tête
        header_row = [
            Paragraph("<b>CRITÈRES</b>", self.styles['Label']),
            Paragraph("<b>VALEUR ET/OU DESCRIPTION</b>", self.styles['Label']),
            Paragraph("<b>SCORE</b>", self.styles['Label']),
            Paragraph("<b>RECOMMANDATIONS</b>", self.styles['Label'])
        ]
        data.append(header_row)

        # Score total pour le calcul
        total_score = 0

        # Lignes de critères
        for title, key, max_score in criteria_list:
            critere_data = criteres.get(key, {})
            score = critere_data.get('score', 0)
            description = critere_data.get('description', '')
            recommandations = critere_data.get('recommandations', '')

            total_score += score

            row = [
                Paragraph(f"<b>{title}</b><br/><font size=8>({max_score} points)</font>", self.styles['DGPPEBodyText']),
                Paragraph(description if description else '-', self.styles['DGPPEBodyText']),
                Paragraph(f"<b>{score}/{max_score}</b>", ParagraphStyle(
                    name=f'Score{key}',
                    parent=self.styles['DGPPEBodyText'],
                    alignment=TA_CENTER,
                    fontSize=10
                )),
                Paragraph(recommandations if recommandations else '-', self.styles['DGPPEBodyText'])
            ]
            data.append(row)

        # Ligne de total
        total_row = [
            Paragraph("<b>SCORE TOTAL =</b>", self.styles['Label']),
            '',
            Paragraph(f"<b>{total_score}/100</b>", ParagraphStyle(
                name='TotalScore',
                parent=self.styles['Label'],
                alignment=TA_CENTER,
                fontSize=12,
                textColor=self._get_score_color(total_score)
            )),
            ''
        ]
        data.append(total_row)

        table = Table(data, colWidths=[4.5*cm, 5*cm, 2*cm, 5.5*cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), Color(0.2, 0.3, 0.4)),  # En-tête sombre
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (0, -2), Color(0.97, 0.97, 0.97)),  # Critères
            ('BACKGROUND', (0, -1), (-1, -1), Color(0.9, 0.97, 0.9)),  # Total
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 15))

    def _get_score_color(self, score):
        """Retourne la couleur selon le score"""
        if score >= 80:
            return HexColor('#2d7a2d')  # Vert (Favorable)
        elif score >= 70:
            return HexColor('#d97706')  # Orange (Conditionnel)
        else:
            return HexColor('#dc2626')  # Rouge (Défavorable)

    def _create_section_IV(self):
        """Section IV - CONCLUSION"""
        # Titre de section avec fond bleu
        section_title_table = Table(
            [[Paragraph("IV - CONCLUSION", self.styles['SectionHeader'])]],
            colWidths=[17*cm]
        )
        section_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.dgppe_blue),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 10)
        ]))
        self.story.append(section_title_table)
        self.story.append(Spacer(1, 10))

        # Calculer le score total pour déterminer la proposition
        criteres = self.fiche.get('criteres', {})
        total_score = sum((criteres.get(key, {}).get('score') or 0) for key in [
            'pertinence', 'alignement', 'activites_couts', 'equite', 'viabilite',
            'rentabilite', 'benefices_strategiques', 'perennite', 'avantages_intangibles',
            'faisabilite', 'ppp', 'impact_environnemental', 'impact_emploi'
        ])

        # Déterminer la proposition automatique
        if total_score >= 80:
            proposition_text = "Favorable"
            proposition_color = HexColor('#2d7a2d')
            proposition_bg = Color(0.91, 0.96, 0.91)
        elif total_score >= 70:
            proposition_text = "Favorable sous condition"
            proposition_color = HexColor('#d97706')
            proposition_bg = Color(1.0, 0.97, 0.93)
        else:
            proposition_text = "Défavorable"
            proposition_color = HexColor('#dc2626')
            proposition_bg = Color(1.0, 0.93, 0.93)

        # Proposition
        data = [[
            Paragraph("<b>PROPOSITION:</b>", self.styles['Label']),
            Paragraph(f"<b>{proposition_text}</b>", ParagraphStyle(
                name='PropositionText',
                parent=self.styles['Label'],
                fontSize=11,
                textColor=proposition_color,
                alignment=TA_CENTER
            ))
        ]]

        table = Table(data, colWidths=[4*cm, 13*cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, 0), Color(0.95, 0.95, 0.95)),
            ('BACKGROUND', (1, 0), (1, 0), proposition_bg),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 10))

        # Note explicative
        note_text = (
            "<i><font size=8>"
            "Proposition automatique basée sur le score total:<br/>"
            "• 0-69 points = Défavorable<br/>"
            "• 70-79 points = Favorable sous condition<br/>"
            "• 80-100 points = Favorable"
            "</font></i>"
        )
        self.story.append(Paragraph(note_text, self.styles['DGPPEBodyText']))
        self.story.append(Spacer(1, 10))

        # Recommandations
        recommandations = self.fiche.get('recommandations', '')
        if recommandations:
            data = [[
                Paragraph("<b>RECOMMANDATIONS:</b>", self.styles['Label']),
                Paragraph(recommandations, self.styles['DGPPEBodyText'])
            ]]

            table = Table(data, colWidths=[4*cm, 13*cm])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (0, 0), Color(0.95, 0.95, 0.95)),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))

            self.story.append(table)

        self.story.append(Spacer(1, 20))

    def _format_currency(self, amount):
        """Formatage des montants"""
        if not amount:
            return '0 FCFA'
        try:
            return f"{int(amount):,} FCFA".replace(',', ' ')
        except:
            return str(amount)

    def _format_date(self, date_obj):
        """Formatage des dates"""
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except:
                return date_obj

        if isinstance(date_obj, datetime):
            return date_obj.strftime("%d/%m/%Y")

        return str(date_obj)

    def generate(self):
        """Génération du PDF complet"""
        self._create_header()
        self._create_section_I()
        self._create_section_II()
        self._create_section_III()
        self._create_section_IV()

        # Générer le PDF
        self.doc.build(self.story)
        return self.output_path


def generer_fiche_evaluation_dgppe_pdf(fiche_data, project_data, output_directory):
    """
    Fonction principale pour générer une fiche d'évaluation DGPPE en PDF

    Args:
        fiche_data (dict): Données de la fiche d'évaluation
        project_data (dict): Données du projet
        output_directory (str): Répertoire de sortie

    Returns:
        str: Chemin vers le fichier PDF généré
    """
    # Création du nom de fichier
    reference = fiche_data.get('reference_fiche', f"FICHE-{project_data.get('id', 'XXX')}")
    filename = f"{reference}.pdf"
    output_path = os.path.join(output_directory, filename)

    # Création du répertoire si nécessaire
    os.makedirs(output_directory, exist_ok=True)

    # Génération du PDF
    pdf_generator = FicheEvaluationDGPPEPDF(fiche_data, project_data, output_path)
    pdf_generator.generate()

    return output_path
