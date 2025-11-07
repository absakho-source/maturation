"""
Module de génération PDF pour les fiches d'évaluation
Génère un PDF professionnel avec en-tête DGPPE et mise en forme standardisée
"""

import os
import qrcode
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color, black, blue, green, red, orange
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, Frame, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors

class FicheEvaluationPDF:
    def __init__(self, fiche_data, project_data, output_path):
        self.fiche = fiche_data
        self.project = project_data
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2*cm
        )
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.story = []
    
    def _setup_custom_styles(self):
        """Configuration des styles personnalisés"""
        # Style pour l'en-tête
        self.styles.add(ParagraphStyle(
            name='Header',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=blue,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='SubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=blue,
            spaceBefore=15,
            spaceAfter=10
        ))
        
        # Style pour les sections
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=blue,
            spaceBefore=12,
            spaceAfter=8,
            borderWidth=1,
            borderColor=blue,
            borderPadding=5,
            backColor=Color(0.9, 0.95, 1.0)
        ))
        
        # Style pour les critères
        self.styles.add(ParagraphStyle(
            name='Criteria',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=5,
            spaceAfter=5,
            leftIndent=20
        ))
        
        # Style pour les valeurs importantes
        self.styles.add(ParagraphStyle(
            name='Important',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=blue,
            fontName='Helvetica-Bold'
        ))
        
        # Style pour les commentaires
        self.styles.add(ParagraphStyle(
            name='Comment',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceBefore=5,
            spaceAfter=5,
            leftIndent=10,
            rightIndent=10,
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=8,
            backColor=Color(0.98, 0.98, 0.98)
        ))
    
    def _create_header(self):
        """Création de l'en-tête avec logo DGPPE"""
        # Chemin vers le logo DGPPE
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                'frontend', 'src', 'assets', 'logo-dgppe.png')
        
        # Vérifier si le logo existe, sinon utiliser le chemin public
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                    'frontend', 'public', 'logo-dgppe.png')
        
        # En-tête principal avec le texte officiel complet
        header_text = """<b>RÉPUBLIQUE DU SÉNÉGAL</b><br/>
<b>Ministère de l'Économie, du Plan et de la Coopération</b><br/>
<b>Direction Générale de la Planification des Politiques Économiques</b><br/>
<b>Plateforme de Maturation des Projets Publics</b>"""
        
        # Créer l'image du logo si elle existe
        logo_element = None
        if os.path.exists(logo_path):
            try:
                logo_element = Image(logo_path, width=1.5*inch, height=1.5*inch)
            except Exception as e:
                print(f"Erreur lors du chargement du logo: {e}")
                logo_element = Paragraph("<b>LOGO<br/>DGPPE</b>", self.styles['Normal'])
        else:
            logo_element = Paragraph("<b>LOGO<br/>DGPPE</b>", self.styles['Normal'])
        
        # Tableau d'en-tête avec logo et texte
        header_data = [
            [Paragraph(header_text, self.styles['Normal']), logo_element]
        ]
        
        header_table = Table(header_data, colWidths=[4.5*inch, 1.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 0), (0, 0), 11),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 1, colors.blue),
            ('BACKGROUND', (0, 0), (-1, -1), Color(0.95, 0.98, 1.0)),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8)
        ]))
        
        self.story.append(header_table)
        self.story.append(Spacer(1, 20))
        
        # Titre principal
        title = Paragraph("FICHE D'ÉVALUATION DE PROJET", self.styles['Header'])
        self.story.append(title)
        
        # Sous-titre avec référence
        ref_text = f"Référence: <b>{self.fiche.get('reference_fiche', 'N/A')}</b>"
        ref_para = Paragraph(ref_text, self.styles['Important'])
        self.story.append(ref_para)
        self.story.append(Spacer(1, 20))
    
    def _create_project_info(self):
        """Section des informations générales du projet"""
        self.story.append(Paragraph("1. INFORMATIONS GÉNÉRALES", self.styles['SectionTitle']))
        
        info_data = [
            ["Numéro du projet:", self.project.get('numero_projet', 'En attente')],
            ["Titre du projet:", self.project.get('titre', 'N/A')],
            ["Soumissionnaire:", self.project.get('auteur_nom', 'N/A')],
            ["Pôle territorial:", self.project.get('poles', 'N/A')],
            ["Secteur d'activité:", self.project.get('secteur', 'N/A')],
            ["Coût estimatif:", f"{self.project.get('cout_estimatif', 0):,.0f} FCFA"],
            ["Date de soumission:", self._format_date(self.project.get('date_soumission'))]
        ]
        
        info_table = Table(info_data, colWidths=[2.5*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), Color(0.9, 0.9, 0.9))
        ]))
        
        self.story.append(info_table)
        self.story.append(Spacer(1, 20))
    
    def _create_evaluator_info(self):
        """Section des informations de l'évaluateur"""
        self.story.append(Paragraph("2. ÉVALUATEUR", self.styles['SectionTitle']))
        
        eval_data = [
            ["Nom de l'évaluateur:", self.fiche.get('evaluateur_nom', 'N/A')],
            ["Date d'évaluation:", self._format_date(self.fiche.get('date_evaluation'))],
            ["Référence de la fiche:", self.fiche.get('reference_fiche', 'N/A')]
        ]
        
        eval_table = Table(eval_data, colWidths=[2.5*inch, 3.5*inch])
        eval_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), Color(0.9, 0.9, 0.9))
        ]))
        
        self.story.append(eval_table)
        self.story.append(Spacer(1, 20))
    
    def _create_evaluation_criteria(self):
        """Section des critères d'évaluation détaillés"""
        self.story.append(Paragraph("3. CRITÈRES D'ÉVALUATION", self.styles['SectionTitle']))
        
        # A. Pertinence et alignement stratégique
        self._create_criteria_section(
            "A. PERTINENCE ET ALIGNEMENT STRATÉGIQUE (20 points)",
            [
                ("3.1. Alignement avec les priorités nationales", self.fiche.get('alignement_national', 0), 5),
                ("3.2. Pertinence territoriale", self.fiche.get('pertinence_territoriale', 0), 5),
                ("3.3. Innovation et valeur ajoutée", self.fiche.get('innovation_valeur', 0), 5),
                ("3.4. Urgence et priorité", self.fiche.get('urgence_priorite', 0), 5)
            ]
        )
        
        # B. Faisabilité technique
        self._create_criteria_section(
            "B. FAISABILITÉ TECHNIQUE (20 points)",
            [
                ("3.5. Solidité technique", self.fiche.get('solidite_technique', 0), 10),
                ("3.6. Capacités de mise en œuvre", self.fiche.get('capacites_mise_oeuvre', 0), 5),
                ("3.7. Gestion des risques", self.fiche.get('gestion_risques', 0), 5)
            ]
        )
        
        # C. Viabilité financière
        self._create_criteria_section(
            "C. VIABILITÉ FINANCIÈRE (20 points)",
            [
                ("3.8. Réalisme du budget", self.fiche.get('realisme_budget', 0), 10),
                ("3.9. Rapport coût/bénéfice", self.fiche.get('rapport_cout_benefice', 0), 5),
                ("3.10. Durabilité financière", self.fiche.get('durabilite_financiere', 0), 5)
            ]
        )
        
        # D. Impact et bénéfices
        self._create_criteria_section(
            "D. IMPACT ET BÉNÉFICES (20 points)",
            [
                ("3.11. Impact social", self.fiche.get('impact_social', 0), 5),
                ("3.12. Impact économique", self.fiche.get('impact_economique', 0), 5),
                ("3.13. Impact environnemental", self.fiche.get('impact_environnemental', 0), 5),
                ("3.14. Effet multiplicateur", self.fiche.get('effet_multiplicateur', 0), 5)
            ]
        )
        
        # E. Gestion et gouvernance
        self._create_criteria_section(
            "E. GESTION ET GOUVERNANCE (20 points)",
            [
                ("3.15. Organisation du projet", self.fiche.get('organisation_projet', 0), 5),
                ("3.16. Planification", self.fiche.get('planification', 0), 5),
                ("3.17. Suivi-évaluation", self.fiche.get('suivi_evaluation', 0), 5),
                ("3.18. Transparence et redevabilité", self.fiche.get('transparence_redevabilite', 0), 5)
            ]
        )
    
    def _create_criteria_section(self, title, criteria_list):
        """Création d'une section de critères"""
        # Titre de la section
        section_para = Paragraph(title, self.styles['SubHeader'])
        self.story.append(section_para)
        
        # Tableau des critères
        criteria_data = [["Critère", "Score obtenu", "Score maximum", "Pourcentage"]]
        
        total_obtenu = 0
        total_maximum = 0
        
        for critere, score, max_score in criteria_list:
            pourcentage = f"{(score/max_score)*100:.1f}%" if max_score > 0 else "0%"
            criteria_data.append([critere, str(score), str(max_score), pourcentage])
            total_obtenu += score
            total_maximum += max_score
        
        # Ligne de total
        total_pourcentage = f"{(total_obtenu/total_maximum)*100:.1f}%" if total_maximum > 0 else "0%"
        criteria_data.append([
            f"<b>SOUS-TOTAL {title[0]}</b>", 
            f"<b>{total_obtenu}</b>", 
            f"<b>{total_maximum}</b>", 
            f"<b>{total_pourcentage}</b>"
        ])
        
        criteria_table = Table(criteria_data, colWidths=[3*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        criteria_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), Color(0.8, 0.8, 0.8)),
            ('BACKGROUND', (0, -1), (-1, -1), Color(0.9, 0.95, 1.0)),
            # Coloration selon le score
            *self._get_score_colors(criteria_data[1:-1], total_maximum)
        ]))
        
        self.story.append(criteria_table)
        self.story.append(Spacer(1, 15))
    
    def _get_score_colors(self, criteria_data, total_maximum):
        """Retourne les couleurs selon les scores"""
        colors_list = []
        for i, (_, score_str, max_str, _) in enumerate(criteria_data, 1):
            try:
                score = int(score_str)
                max_score = int(max_str)
                percentage = (score / max_score) * 100 if max_score > 0 else 0
                
                if percentage >= 80:
                    color = Color(0.8, 1.0, 0.8)  # Vert clair
                elif percentage >= 60:
                    color = Color(1.0, 1.0, 0.8)  # Jaune clair
                else:
                    color = Color(1.0, 0.9, 0.9)  # Rouge clair
                
                colors_list.append(('BACKGROUND', (1, i), (3, i), color))
            except ValueError:
                continue
        
        return colors_list
    
    def _create_detailed_evaluation(self):
        """Section de l'évaluation détaillée"""
        self.story.append(Paragraph("4. ÉVALUATION DÉTAILLÉE", self.styles['SectionTitle']))
        
        # Points forts
        if self.fiche.get('points_forts'):
            self.story.append(Paragraph("<b>Points forts identifiés :</b>", self.styles['Normal']))
            points_forts = Paragraph(self.fiche['points_forts'], self.styles['Comment'])
            self.story.append(points_forts)
            self.story.append(Spacer(1, 10))
        
        # Points faibles
        if self.fiche.get('points_faibles'):
            self.story.append(Paragraph("<b>Points faibles et risques :</b>", self.styles['Normal']))
            points_faibles = Paragraph(self.fiche['points_faibles'], self.styles['Comment'])
            self.story.append(points_faibles)
            self.story.append(Spacer(1, 10))
        
        # Recommandations
        if self.fiche.get('recommandations'):
            self.story.append(Paragraph("<b>Recommandations d'amélioration :</b>", self.styles['Normal']))
            recommandations = Paragraph(self.fiche['recommandations'], self.styles['Comment'])
            self.story.append(recommandations)
            self.story.append(Spacer(1, 10))
        
        # Conditions particulières
        if self.fiche.get('conditions_particulieres'):
            self.story.append(Paragraph("<b>Conditions particulières :</b>", self.styles['Normal']))
            conditions = Paragraph(self.fiche['conditions_particulieres'], self.styles['Comment'])
            self.story.append(conditions)
            self.story.append(Spacer(1, 20))
    
    def _create_synthesis(self):
        """Section de synthèse"""
        self.story.append(Paragraph("5. SYNTHÈSE", self.styles['SectionTitle']))
        
        # Score total avec barre de progression visuelle
        score_total = self.fiche.get('score_total', 0)
        score_para = Paragraph(f"<b>Score total : {score_total}/100 points</b>", self.styles['Important'])
        self.story.append(score_para)
        
        # Création d'une barre de progression
        self._create_score_bar(score_total)
        
        # Appréciation globale
        appreciation = self._get_appreciation_text(self.fiche.get('appreciation_globale', ''))
        appreciation_para = Paragraph(f"<b>Appréciation globale :</b> {appreciation}", self.styles['Normal'])
        self.story.append(appreciation_para)
        self.story.append(Spacer(1, 10))
        
        # Avis final
        avis = self._get_avis_text(self.fiche.get('avis_final', ''))
        avis_color = self._get_avis_color(self.fiche.get('avis_final', ''))
        avis_style = ParagraphStyle(
            name='AvisFinal',
            parent=self.styles['Important'],
            textColor=avis_color,
            fontSize=12
        )
        avis_para = Paragraph(f"<b>AVIS FINAL :</b> {avis}", avis_style)
        self.story.append(avis_para)
        self.story.append(Spacer(1, 15))
        
        # Commentaires finaux
        if self.fiche.get('commentaires_finaux'):
            self.story.append(Paragraph("<b>Commentaires finaux :</b>", self.styles['Normal']))
            commentaires = Paragraph(self.fiche['commentaires_finaux'], self.styles['Comment'])
            self.story.append(commentaires)
    
    def _create_score_bar(self, score):
        """Création d'une barre de progression pour le score"""
        # Données pour la barre de score
        bar_data = [[""] * 10]  # 10 segments de 10 points chacun
        
        bar_table = Table(bar_data, colWidths=[0.6*inch] * 10, rowHeights=[0.3*inch])
        
        # Style de base
        bar_style = [
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER')
        ]
        
        # Coloration selon le score
        for i in range(10):
            threshold = (i + 1) * 10
            if score >= threshold:
                if threshold <= 40:
                    color = Color(1.0, 0.6, 0.6)  # Rouge
                elif threshold <= 70:
                    color = Color(1.0, 1.0, 0.6)  # Jaune
                else:
                    color = Color(0.6, 1.0, 0.6)  # Vert
                bar_style.append(('BACKGROUND', (i, 0), (i, 0), color))
        
        bar_table.setStyle(TableStyle(bar_style))
        self.story.append(bar_table)
        self.story.append(Spacer(1, 15))
    
    def _create_signature_section(self):
        """Section de signature et validation"""
        self.story.append(Paragraph("6. SIGNATURE ET VALIDATION", self.styles['SectionTitle']))
        
        # QR Code pour vérification
        qr_code = self._generate_qr_code()
        
        signature_data = [
            ["Évaluateur :", self.fiche.get('evaluateur_nom', 'N/A'), "QR Code de vérification"],
            ["Date :", self._format_date(self.fiche.get('date_evaluation')), ""],
            ["Signature :", "\n\n\n", ""],
            ["Cachet DGPPE :", "\n\n\n", ""]
        ]
        
        signature_table = Table(signature_data, colWidths=[1.5*inch, 2.5*inch, 2*inch])
        signature_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('SPAN', (2, 1), (2, -1)),
        ]))
        
        self.story.append(signature_table)
        
        # Note sur la vérification
        verification_note = Paragraph(
            "<i>Ce document peut être vérifié en scannant le QR code ci-dessus ou en contactant la DGPPE.</i>",
            self.styles['Normal']
        )
        self.story.append(Spacer(1, 10))
        self.story.append(verification_note)
    
    def _generate_qr_code(self):
        """Génération d'un QR code pour la vérification"""
        # Données pour le QR code
        qr_data = {
            'reference': self.fiche.get('reference_fiche', ''),
            'project_id': self.project.get('id', ''),
            'evaluateur': self.fiche.get('evaluateur_nom', ''),
            'score': self.fiche.get('score_total', 0),
            'avis': self.fiche.get('avis_final', ''),
            'verification_url': 'https://dgppe.gouv.sn/verify'
        }
        
        qr_text = f"DGPPE-EVAL:{qr_data['reference']}:{qr_data['score']}"
        
        qr = qrcode.QRCode(version=1, box_size=3, border=1)
        qr.add_data(qr_text)
        qr.make(fit=True)
        
        # Conversion en image pour ReportLab
        qr_img = qr.make_image(fill_color="black", back_color="white")
        return qr_img
    
    def _format_date(self, date_str):
        """Formatage des dates"""
        if not date_str:
            return datetime.now().strftime("%d/%m/%Y")
        
        try:
            if isinstance(date_str, str):
                # Essayer différents formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        return date_obj.strftime("%d/%m/%Y")
                    except ValueError:
                        continue
            return str(date_str)
        except:
            return datetime.now().strftime("%d/%m/%Y")
    
    def _get_appreciation_text(self, appreciation):
        """Conversion de l'appréciation en texte"""
        appreciation_map = {
            'excellent': 'Excellent (90-100 points) - Projet remarquable, prêt pour validation',
            'tres_bien': 'Très bien (80-89 points) - Projet de qualité, recommandé avec réserves mineures',
            'bien': 'Bien (70-79 points) - Projet acceptable, nécessite des améliorations',
            'passable': 'Passable (60-69 points) - Projet acceptable avec réserves importantes',
            'insuffisant': 'Insuffisant (< 60 points) - Projet non recommandé en l\'état'
        }
        return appreciation_map.get(appreciation, 'Non défini')
    
    def _get_avis_text(self, avis):
        """Conversion de l'avis en texte"""
        avis_map = {
            'favorable': 'FAVORABLE - Le projet est recommandé pour validation',
            'favorable_sous_conditions': 'FAVORABLE SOUS CONDITIONS - Le projet est recommandé sous réserve des améliorations suggérées',
            'defavorable': 'DÉFAVORABLE - Le projet n\'est pas recommandé pour validation'
        }
        return avis_map.get(avis, 'Non défini')
    
    def _get_avis_color(self, avis):
        """Couleur selon l'avis"""
        color_map = {
            'favorable': green,
            'favorable_sous_conditions': orange,
            'defavorable': red
        }
        return color_map.get(avis, black)
    
    def generate(self):
        """Génération du PDF complet"""
        # Construction du document
        self._create_header()
        self._create_project_info()
        self._create_evaluator_info()
        self._create_evaluation_criteria()
        self._create_detailed_evaluation()
        self._create_synthesis()
        self._create_signature_section()
        
        # Génération du PDF
        self.doc.build(self.story)
        return self.output_path

def generer_fiche_evaluation_pdf(fiche_data, project_data, output_directory):
    """
    Fonction principale pour générer une fiche d'évaluation en PDF
    
    Args:
        fiche_data (dict): Données de la fiche d'évaluation
        project_data (dict): Données du projet
        output_directory (str): Répertoire de sortie
    
    Returns:
        str: Chemin vers le fichier PDF généré
    """
    # Création du nom de fichier
    reference = fiche_data.get('reference_fiche', f"EVAL-{project_data.get('id', 'XXX')}")
    filename = f"{reference}.pdf"
    output_path = os.path.join(output_directory, filename)
    
    # Création du répertoire si nécessaire
    os.makedirs(output_directory, exist_ok=True)
    
    # Génération du PDF
    pdf_generator = FicheEvaluationPDF(fiche_data, project_data, output_path)
    pdf_generator.generate()
    
    return output_path