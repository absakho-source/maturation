"""
Générateur PDF pour les fiches d'évaluation DGPPE
Format conforme à FicheEvaluationDGPPE.vue
Génère un PDF multi-pages avec toutes les sections, scores, appréciations et recommandations
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

    def __init__(self, fiche_data, project_data, output_path):
        self.fiche = fiche_data
        self.project = project_data
        self.output_path = output_path

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
        self._setup_custom_styles()
        self.story = []

        # Couleur verte DGPPE
        self.dgppe_green = HexColor('#2d7a2d')

    def _setup_custom_styles(self):
        """Configuration des styles personnalisés"""
        # Style pour l'en-tête République
        self.styles.add(ParagraphStyle(
            name='RepublicHeader',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.dgppe_green,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=2
        ))

        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=self.dgppe_green,
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
            alignment=TA_LEFT,
            spaceBefore=15,
            spaceAfter=10,
            backColor=self.dgppe_green,
            borderPadding=8
        ))

        # Style pour les critères
        self.styles.add(ParagraphStyle(
            name='CriteriaTitle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.dgppe_green,
            fontName='Helvetica-Bold',
            spaceBefore=8,
            spaceAfter=5
        ))

        # Style pour le texte normal
        self.styles.add(ParagraphStyle(
            name='BodyText',
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
        # Chercher le logo
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                'frontend', 'public', 'logo-dgppe.png')

        # En-tête avec logo et texte
        header_text = Paragraph("""
        <b>RÉPUBLIQUE DU SÉNÉGAL</b><br/>
        <b>Ministère de l'Économie, du Plan et de la Coopération</b><br/>
        <b>Direction Générale de la Planification des Politiques Économiques</b><br/>
        <b>Plateforme de Maturation des Projets et Programmes Publics</b>
        """, self.styles['RepublicHeader'])

        # Logo si disponible
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*cm, height=2*cm)
                header_table = Table([[header_text, logo]], colWidths=[14*cm, 3*cm])
            except:
                header_table = Table([[header_text, '']], colWidths=[14*cm, 3*cm])
        else:
            header_table = Table([[header_text, '']], colWidths=[14*cm, 3*cm])

        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1.5, self.dgppe_green),
            ('BACKGROUND', (0, 0), (-1, -1), Color(0.95, 0.98, 0.95)),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
        ]))

        self.story.append(header_table)
        self.story.append(Spacer(1, 15))

        # Titre principal
        title = Paragraph("FICHE D'ÉVALUATION DE PROJET", self.styles['MainTitle'])
        self.story.append(title)

        # Référence et numéro
        ref_text = f"<b>Référence:</b> {self.fiche.get('reference_fiche', 'N/A')}"
        if self.project.get('numero_projet'):
            ref_text += f" | <b>Numéro de projet:</b> {self.project['numero_projet']}"

        ref_para = Paragraph(ref_text, self.styles['BodyText'])
        self.story.append(ref_para)
        self.story.append(Spacer(1, 20))

    def _create_section_I(self):
        """Section I - PRÉSENTATION DU PROJET"""
        # Titre de section
        section_title = Paragraph("I - PRÉSENTATION DU PROJET", self.styles['SectionHeader'])
        self.story.append(section_title)
        self.story.append(Spacer(1, 10))

        # Grille d'informations
        data = []

        # Ligne 1: Coût et Origine
        row1 = [
            Paragraph("<b>COÛT DU PROJET</b>", self.styles['Label']),
            Paragraph(self.fiche.get('cout_projet', 'N/A'), self.styles['BodyText']),
            Paragraph("<b>ORIGINE DU PROJET</b>", self.styles['Label']),
            Paragraph(self.fiche.get('origine_projet', 'N/A'), self.styles['BodyText'])
        ]
        data.append(row1)

        # Ligne 2: Typologie et Changement climatique
        row2 = [
            Paragraph("<b>TYPOLOGIE DU PROJET</b>", self.styles['Label']),
            Paragraph(self.fiche.get('typologie_projet', 'N/A'), self.styles['BodyText']),
            Paragraph("<b>CHANGEMENT CLIMATIQUE</b>", self.styles['Label']),
            Paragraph(self.fiche.get('changement_climatique', 'N/A'), self.styles['BodyText'])
        ]
        data.append(row2)

        # Ligne 3: Sous-secteur et Organisme
        row3 = [
            Paragraph("<b>SOUS SECTEUR</b>", self.styles['Label']),
            Paragraph(self.fiche.get('sous_secteur', 'N/A'), self.styles['BodyText']),
            Paragraph("<b>ORGANISME DE TUTELLE</b>", self.styles['Label']),
            Paragraph(self.fiche.get('organisme_tutelle', 'N/A'), self.styles['BodyText'])
        ]
        data.append(row3)

        # Ligne 4: SND et Objectifs stratégiques
        row4 = [
            Paragraph("<b>SND 2025-2029</b>", self.styles['Label']),
            Paragraph(self.fiche.get('snd_2025_2029', 'N/A'), self.styles['BodyText']),
            Paragraph("<b>OBJECTIFS STRATÉGIQUES</b>", self.styles['Label']),
            Paragraph(self.fiche.get('objectifs_strategiques', 'N/A'), self.styles['BodyText'])
        ]
        data.append(row4)

        # Ligne 5: Durées
        duree_text = f"Analyse: {self.fiche.get('duree_analyse', 'N/A')} | " + \
                     f"Réalisation: {self.fiche.get('realisation', 'N/A')} | " + \
                     f"Exploitation: {self.fiche.get('exploitation', 'N/A')}"
        row5 = [
            Paragraph("<b>DURÉES</b>", self.styles['Label']),
            Paragraph(duree_text, self.styles['BodyText']),
            '', ''
        ]
        data.append(row5)

        # Ligne 6: Localisation
        row6 = [
            Paragraph("<b>LOCALISATION</b>", self.styles['Label']),
            Paragraph(self.fiche.get('localisation', 'N/A'), self.styles['BodyText']),
            '', ''
        ]
        data.append(row6)

        table = Table(data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), Color(0.9, 0.95, 0.9)),
            ('BACKGROUND', (2, 0), (2, -1), Color(0.9, 0.95, 0.9)),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('SPAN', (1, 4), (3, 4)),  # Durées
            ('SPAN', (1, 5), (3, 5)),  # Localisation
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 10))

        # Champs textuels
        if self.fiche.get('parties_prenantes'):
            self.story.append(Paragraph("<b>PARTIES PRENANTES</b>", self.styles['Label']))
            self.story.append(Paragraph(self.fiche['parties_prenantes'], self.styles['BodyText']))
            self.story.append(Spacer(1, 8))

        if self.fiche.get('autres_projets_connexes'):
            self.story.append(Paragraph("<b>AUTRES PROJETS/PROG. CONNEXES</b>", self.styles['Label']))
            self.story.append(Paragraph(self.fiche['autres_projets_connexes'], self.styles['BodyText']))
            self.story.append(Spacer(1, 8))

        if self.fiche.get('objectif_projet'):
            self.story.append(Paragraph("<b>OBJECTIF DU PROJET</b>", self.styles['Label']))
            self.story.append(Paragraph(self.fiche['objectif_projet'], self.styles['BodyText']))
            self.story.append(Spacer(1, 8))

        if self.fiche.get('activites_principales'):
            self.story.append(Paragraph("<b>ACTIVITÉS PRINCIPALES</b>", self.styles['Label']))
            self.story.append(Paragraph(self.fiche['activites_principales'], self.styles['BodyText']))
            self.story.append(Spacer(1, 8))

        if self.fiche.get('resultats_attendus'):
            self.story.append(Paragraph("<b>RÉSULTATS/IMPACTS ATTENDUS</b>", self.styles['Label']))
            self.story.append(Paragraph(self.fiche['resultats_attendus'], self.styles['BodyText']))
            self.story.append(Spacer(1, 15))

    def _create_criterion_block(self, title, score_key, score_max, appreciation_key, recommendation_key):
        """Crée un bloc pour un critère avec score, appréciation et recommandations"""
        score = self.fiche.get(score_key, 0)
        appreciation = self.fiche.get(appreciation_key, '')
        recommendation = self.fiche.get(recommendation_key, '')

        # Titre du critère avec score
        criterion_title = Paragraph(
            f"<b>{title}</b> - Score: {score}/{score_max}",
            self.styles['CriteriaTitle']
        )
        self.story.append(criterion_title)

        # Barre de score visuelle
        self._create_score_bar(score, score_max)

        # Appréciation
        if appreciation:
            self.story.append(Paragraph("<b>Appréciation:</b>", self.styles['Label']))
            self.story.append(Paragraph(appreciation, self.styles['BodyText']))
            self.story.append(Spacer(1, 5))

        # Recommandations
        if recommendation:
            self.story.append(Paragraph("<b>Recommandations:</b>", self.styles['Label']))
            self.story.append(Paragraph(recommendation, self.styles['BodyText']))

        self.story.append(Spacer(1, 10))

    def _create_score_bar(self, score, max_score):
        """Crée une barre de score visuelle"""
        percentage = (score / max_score * 100) if max_score > 0 else 0

        # Déterminer la couleur
        if percentage >= 80:
            color = Color(0.2, 0.8, 0.2)  # Vert
        elif percentage >= 60:
            color = Color(1.0, 0.8, 0.0)  # Orange
        else:
            color = Color(0.9, 0.2, 0.2)  # Rouge

        # Créer la barre
        filled_width = percentage / 10  # 10 segments
        data = [['']]

        table = Table(data, colWidths=[17*cm], rowHeights=[0.4*cm])
        table.setStyle(TableStyle([
            ('BOX', (0, 0), (0, 0), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, 0), Color(0.95, 0.95, 0.95)),
        ]))

        # Ajouter une barre colorée (simplifiée)
        score_text = Paragraph(
            f"<font color='green'>{score}/{max_score} ({percentage:.0f}%)</font>",
            self.styles['BodyText']
        )
        self.story.append(score_text)
        self.story.append(Spacer(1, 5))

    def _create_section_II(self):
        """Section II - RÉSULTATS DE L'ÉVALUATION"""
        # Titre de section
        section_title = Paragraph("II - RÉSULTATS DE L'ÉVALUATION", self.styles['SectionHeader'])
        self.story.append(section_title)
        self.story.append(Spacer(1, 10))

        # PERTINENCE (/5)
        self._create_criterion_block(
            "PERTINENCE",
            "pertinence_score", 5,
            "pertinence_appreciation",
            "pertinence_recommandations"
        )

        # ALIGNEMENT (/10)
        self._create_criterion_block(
            "ALIGNEMENT À LA DOCTRINE DE TRANSFORMATION SYSTÉMIQUE",
            "alignement_score", 10,
            "alignement_appreciation",
            "alignement_recommandations"
        )

        # PERTINENCE DES ACTIVITÉS (/15)
        self._create_criterion_block(
            "PERTINENCE DES ACTIVITÉS EN FONCTION DES COÛTS, PART DE FONCTIONNEMENT",
            "pertinence_activites_score", 15,
            "pertinence_activites_appreciation",
            "pertinence_activites_recommandations"
        )

        # ÉQUITÉ (/15)
        self._create_criterion_block(
            "ÉQUITÉ (SOCIALE-TERRITORIALE-GENRE)",
            "equite_score", 15,
            "equite_appreciation",
            "equite_recommandations"
        )

        # Score total
        score_total = self.fiche.get('score_total', 0)
        appreciation_globale = self._get_appreciation_text(score_total)

        self.story.append(Spacer(1, 15))
        total_para = Paragraph(
            f"<b>TOTAL SCORE = {score_total}/100</b><br/>"
            f"<b>Appréciation: {appreciation_globale}</b>",
            self.styles['MainTitle']
        )
        self.story.append(total_para)
        self.story.append(Spacer(1, 15))

    def _get_appreciation_text(self, score):
        """Retourne l'appréciation selon le score"""
        if score >= 85:
            return "Excellent"
        elif score >= 75:
            return "Très bien"
        elif score >= 65:
            return "Bien"
        elif score >= 50:
            return "Passable"
        else:
            return "Insuffisant"

    def _create_section_III(self):
        """Section III - CONCLUSION"""
        # Titre de section
        section_title = Paragraph("III - CONCLUSION", self.styles['SectionHeader'])
        self.story.append(section_title)
        self.story.append(Spacer(1, 10))

        # Avis final
        avis_final = self.fiche.get('avis_final', '')
        avis_text = self._get_avis_text(avis_final)
        avis_color = self._get_avis_color(avis_final)

        avis_style = ParagraphStyle(
            name='AvisFinalStyle',
            parent=self.styles['Label'],
            fontSize=11,
            textColor=avis_color
        )

        self.story.append(Paragraph("<b>AVIS FINAL</b>", self.styles['Label']))
        self.story.append(Paragraph(avis_text, avis_style))
        self.story.append(Spacer(1, 10))

        # Proposition
        if self.fiche.get('proposition'):
            self.story.append(Paragraph("<b>PROPOSITION</b>", self.styles['Label']))
            self.story.append(Paragraph(self.fiche['proposition'], self.styles['BodyText']))
            self.story.append(Spacer(1, 10))

        # Recommandations générales
        if self.fiche.get('recommandations_generales'):
            self.story.append(Paragraph("<b>RECOMMANDATIONS</b>", self.styles['Label']))
            self.story.append(Paragraph(self.fiche['recommandations_generales'], self.styles['BodyText']))
            self.story.append(Spacer(1, 10))

        # Impact sur l'emploi
        if self.fiche.get('impact_sur_emploi'):
            self.story.append(Paragraph("<b>IMPACT SUR L'EMPLOI</b>", self.styles['Label']))
            self.story.append(Paragraph(self.fiche['impact_sur_emploi'], self.styles['BodyText']))
            self.story.append(Spacer(1, 15))

    def _get_avis_text(self, avis):
        """Convertir le code d'avis en texte"""
        avis_map = {
            'favorable': 'AVIS FAVORABLE (80 points et plus)',
            'favorable_sous_reserves': 'AVIS FAVORABLE SOUS RÉSERVES (70-79 points)',
            'defavorable': 'AVIS DÉFAVORABLE (0-69 points)'
        }
        return avis_map.get(avis, 'Non défini')

    def _get_avis_color(self, avis):
        """Couleur selon l'avis"""
        color_map = {
            'favorable': HexColor('#2d7a2d'),
            'favorable_sous_reserves': HexColor('#d97706'),
            'defavorable': HexColor('#dc2626')
        }
        return color_map.get(avis, colors.black)

    def _create_section_IV(self):
        """Section IV - DOCUMENTS ANNEXES"""
        # Titre de section
        section_title = Paragraph("IV - DOCUMENTS ANNEXES", self.styles['SectionHeader'])
        self.story.append(section_title)
        self.story.append(Spacer(1, 10))

        # Évaluateur et signature
        evaluateur = self.fiche.get('evaluateur_nom', 'N/A')
        date_eval = self._format_date(self.fiche.get('date_evaluation'))

        data = [
            [Paragraph("<b>ÉVALUATEUR</b>", self.styles['Label']), Paragraph(evaluateur, self.styles['BodyText'])],
            [Paragraph("<b>DATE</b>", self.styles['Label']), Paragraph(date_eval, self.styles['BodyText'])],
            [Paragraph("<b>SIGNATURE</b>", self.styles['Label']), ''],
        ]

        table = Table(data, colWidths=[4*cm, 13*cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), Color(0.9, 0.95, 0.9)),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        self.story.append(table)

    def _format_date(self, date_str):
        """Formatage des dates"""
        if not date_str:
            return datetime.now().strftime("%d/%m/%Y")

        try:
            if isinstance(date_str, str):
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        return date_obj.strftime("%d/%m/%Y")
                    except ValueError:
                        continue
            return str(date_str)
        except:
            return datetime.now().strftime("%d/%m/%Y")

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
