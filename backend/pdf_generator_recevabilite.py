"""
Générateur PDF pour la Matrice d'Évaluation de la Recevabilité
Format conforme à MatriceEvaluationPrealable.vue
"""

import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors


class FicheRecevabilitePDF:
    """Classe pour générer le PDF de la fiche de recevabilité"""

    def __init__(self, project_data, matrice_data, decision, output_path):
        self.project = project_data
        self.matrice = matrice_data if isinstance(matrice_data, dict) else json.loads(matrice_data or '{}')
        self.decision = decision
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

        # Couleurs
        self.dgppe_blue = HexColor('#1a4d7a')
        self.dgppe_green = HexColor('#27ae60')
        self.color_success = HexColor('#10b981')
        self.color_warning = HexColor('#f59e0b')
        self.color_danger = HexColor('#ef4444')

        self._setup_custom_styles()
        self.story = []

    def _setup_custom_styles(self):
        """Configuration des styles personnalisés"""
        # Titre principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=self.dgppe_blue,
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))

        # Titre de section
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            alignment=TA_CENTER
        ))

        # Label
        self.styles.add(ParagraphStyle(
            name='Label',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=HexColor('#1e293b')
        ))

        # Texte normal
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            textColor=HexColor('#374151'),
            leading=14
        ))

        # En-tête tableau
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            alignment=TA_CENTER
        ))

    def _create_header(self):
        """Création de l'en-tête officiel avec PLASMAP"""
        # Charger le logo DGPPE
        logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo-dgppe.png')
        logo = None
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*cm, height=2*cm)
            except Exception:
                logo = None

        # Styles pour l'en-tête
        ministry_style = ParagraphStyle(
            name='MinistryStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            textColor=self.dgppe_blue,
            alignment=TA_CENTER,
            leading=12
        )

        dgppe_style = ParagraphStyle(
            name='DGPPEStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=self.dgppe_blue,
            alignment=TA_CENTER,
            leading=12
        )

        plasmap_style = ParagraphStyle(
            name='PLASMAPStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=self.dgppe_green,
            alignment=TA_CENTER,
            leading=18
        )

        plasmap_full_style = ParagraphStyle(
            name='PLASMAPFullStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Helvetica-Oblique',
            textColor=HexColor('#555555'),
            alignment=TA_CENTER,
            leading=10
        )

        # Textes de l'en-tête
        republique = Paragraph(
            "RÉPUBLIQUE DU SÉNÉGAL",
            ParagraphStyle(
                name='RepubliqueStyle',
                parent=self.styles['Normal'],
                fontSize=10,
                fontName='Helvetica-Bold',
                textColor=self.dgppe_blue,
                alignment=TA_CENTER
            )
        )

        devise = Paragraph(
            "<i>Un Peuple - Un But - Une Foi</i>",
            ParagraphStyle(
                name='DeviseStyle',
                parent=self.styles['Normal'],
                fontSize=8,
                fontName='Helvetica-Oblique',
                textColor=HexColor('#666666'),
                alignment=TA_CENTER
            )
        )

        ministere = Paragraph("MINISTÈRE DE L'ÉCONOMIE, DU PLAN ET DE LA COOPÉRATION", ministry_style)
        dgppe = Paragraph("DIRECTION GÉNÉRALE DE LA PLANIFICATION<br/>ET DES POLITIQUES ÉCONOMIQUES", dgppe_style)

        separator = Paragraph("───────────────", ParagraphStyle(
            name='SepStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=self.dgppe_green,
            alignment=TA_CENTER
        ))

        plasmap = Paragraph("<b>PLASMAP</b>", plasmap_style)
        plasmap_full = Paragraph(
            "<b>PL</b>ateforme de <b>S</b>uivi de la <b>MA</b>turation des <b>P</b>rojets",
            plasmap_full_style
        )

        # Créer le contenu central
        central_content = Table([
            [republique],
            [devise],
            [Spacer(1, 3)],
            [ministere],
            [dgppe],
            [Spacer(1, 2)],
            [separator],
            [plasmap],
            [plasmap_full]
        ], colWidths=[12*cm])
        central_content.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (0, -1), 1),
            ('BOTTOMPADDING', (0, 0), (0, -1), 1),
        ]))

        # Créer le tableau principal avec logo
        if logo:
            header_data = [[logo, central_content, '']]
            header_table = Table(header_data, colWidths=[2.5*cm, 12*cm, 2.5*cm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
        else:
            header_data = [[central_content]]
            header_table = Table(header_data, colWidths=[17*cm])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ]))

        # Encadrer l'en-tête
        outer_table = Table([[header_table]], colWidths=[17.5*cm])
        outer_table.setStyle(TableStyle([
            ('BOX', (0, 0), (0, 0), 2, self.dgppe_blue),
            ('BACKGROUND', (0, 0), (0, 0), HexColor('#f8f9fa')),
            ('TOPPADDING', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 10),
            ('LEFTPADDING', (0, 0), (0, 0), 8),
            ('RIGHTPADDING', (0, 0), (0, 0), 8),
        ]))

        self.story.append(outer_table)
        self.story.append(Spacer(1, 15))

        # Titre principal
        title = Paragraph("MATRICE D'ÉVALUATION DE LA RECEVABILITÉ", self.styles['MainTitle'])
        self.story.append(title)

        # Date de génération
        date_generation = datetime.now().strftime("%d/%m/%Y à %H:%M")
        date_para = Paragraph(
            f"<i>Générée le {date_generation}</i>",
            ParagraphStyle(
                name='DateGeneration',
                parent=self.styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=HexColor('#6c757d'),
                spaceBefore=5,
                spaceAfter=15
            )
        )
        self.story.append(date_para)

    def _create_project_info(self):
        """Section informations du projet"""
        # Titre de section
        section_title_table = Table(
            [[Paragraph("INFORMATIONS DU PROJET", self.styles['SectionHeader'])]],
            colWidths=[17*cm]
        )
        section_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.dgppe_blue),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (0, 0), 8),
            ('BOTTOMPADDING', (0, 0), (0, 0), 8)
        ]))
        self.story.append(section_title_table)
        self.story.append(Spacer(1, 10))

        # Informations du projet
        data = [
            [
                Paragraph("<b>NUMÉRO:</b>", self.styles['Label']),
                Paragraph(str(self.project.get('numero_projet', 'N/A')), self.styles['BodyText']),
                Paragraph("<b>DATE SOUMISSION:</b>", self.styles['Label']),
                Paragraph(self._format_date(self.project.get('date_soumission')), self.styles['BodyText'])
            ],
            [
                Paragraph("<b>INTITULÉ:</b>", self.styles['Label']),
                Paragraph(str(self.project.get('titre', 'N/A')), self.styles['BodyText']),
                '', ''
            ],
            [
                Paragraph("<b>SECTEUR:</b>", self.styles['Label']),
                Paragraph(str(self.project.get('secteur', 'N/A')), self.styles['BodyText']),
                Paragraph("<b>PÔLES:</b>", self.styles['Label']),
                Paragraph(str(self.project.get('poles', 'N/A')), self.styles['BodyText'])
            ],
            [
                Paragraph("<b>STRUCTURE:</b>", self.styles['Label']),
                Paragraph(str(self.project.get('structure_soumissionnaire', 'N/A')), self.styles['BodyText']),
                '', ''
            ]
        ]

        table = Table(data, colWidths=[4*cm, 4.5*cm, 4*cm, 4.5*cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), Color(0.95, 0.95, 0.95)),
            ('BACKGROUND', (2, 0), (2, -1), Color(0.95, 0.95, 0.95)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('SPAN', (1, 1), (3, 1)),  # Intitulé
            ('SPAN', (1, 3), (3, 3)),  # Structure
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 15))

    def _create_documents_table(self):
        """Tableau des documents vérifiés"""
        # Titre de section
        section_title_table = Table(
            [[Paragraph("VÉRIFICATION DES DOCUMENTS", self.styles['SectionHeader'])]],
            colWidths=[17*cm]
        )
        section_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.dgppe_blue),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (0, 0), 8),
            ('BOTTOMPADDING', (0, 0), (0, 0), 8)
        ]))
        self.story.append(section_title_table)
        self.story.append(Spacer(1, 10))

        # En-tête du tableau
        header_row = [
            Paragraph("<b>Documents à fournir</b>", self.styles['TableHeader']),
            Paragraph("<b>Requis</b>", self.styles['TableHeader']),
            Paragraph("<b>Transmis</b>", self.styles['TableHeader']),
            Paragraph("<b>Statut</b>", self.styles['TableHeader'])
        ]

        data = [header_row]

        # Lignes des documents
        documents = self.matrice.get('documents', [])
        for doc in documents:
            nom = doc.get('nom', 'Document inconnu')
            requis = doc.get('requis', False)
            transmis = doc.get('transmis', False)

            # Déterminer le statut
            if not requis:
                statut = "Non requis"
                statut_color = HexColor('#64748b')
                statut_bg = HexColor('#f1f5f9')
            elif transmis:
                statut = "✓ Conforme"
                statut_color = HexColor('#065f46')
                statut_bg = HexColor('#d1fae5')
            else:
                statut = "⚠ Manquant"
                statut_color = HexColor('#991b1b')
                statut_bg = HexColor('#fee2e2')

            row = [
                Paragraph(nom, self.styles['BodyText']),
                Paragraph("OUI" if requis else "NON", ParagraphStyle(
                    name='CenterText',
                    parent=self.styles['BodyText'],
                    alignment=TA_CENTER
                )),
                Paragraph("OUI" if transmis else "NON", ParagraphStyle(
                    name='CenterText',
                    parent=self.styles['BodyText'],
                    alignment=TA_CENTER
                )),
                Paragraph(f"<font color='{statut_color}'>{statut}</font>", ParagraphStyle(
                    name='StatutText',
                    parent=self.styles['BodyText'],
                    alignment=TA_CENTER,
                    fontSize=9
                ))
            ]
            data.append(row)

        table = Table(data, colWidths=[8*cm, 2.5*cm, 2.5*cm, 4*cm])

        # Style du tableau
        style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0ea5e9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]

        # Colorer les lignes selon le statut
        for i, doc in enumerate(documents, start=1):
            if doc.get('requis') and not doc.get('transmis'):
                style.append(('BACKGROUND', (0, i), (-1, i), HexColor('#fef2f2')))

        table.setStyle(TableStyle(style))
        self.story.append(table)
        self.story.append(Spacer(1, 15))

    def _create_summary(self):
        """Résumé de l'évaluation"""
        # Titre de section
        section_title_table = Table(
            [[Paragraph("RÉSUMÉ DE L'ÉVALUATION", self.styles['SectionHeader'])]],
            colWidths=[17*cm]
        )
        section_title_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), self.dgppe_blue),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (0, 0), 8),
            ('BOTTOMPADDING', (0, 0), (0, 0), 8)
        ]))
        self.story.append(section_title_table)
        self.story.append(Spacer(1, 10))

        # Calculer les statistiques
        documents = self.matrice.get('documents', [])
        docs_requis = len([d for d in documents if d.get('requis')])
        docs_transmis = len([d for d in documents if d.get('requis') and d.get('transmis')])
        docs_manquants = docs_requis - docs_transmis

        # Statistiques
        stats_data = [
            [
                Paragraph("<b>Documents requis:</b>", self.styles['Label']),
                Paragraph(str(docs_requis), self.styles['BodyText']),
                Paragraph("<b>Documents transmis:</b>", self.styles['Label']),
                Paragraph(str(docs_transmis), self.styles['BodyText'])
            ],
            [
                Paragraph("<b>Documents manquants:</b>", self.styles['Label']),
                Paragraph(str(docs_manquants), ParagraphStyle(
                    name='ManquantsText',
                    parent=self.styles['BodyText'],
                    textColor=self.color_danger if docs_manquants > 0 else self.color_success
                )),
                Paragraph("<b>Date d'évaluation:</b>", self.styles['Label']),
                Paragraph(self._format_date(self.matrice.get('date_evaluation')), self.styles['BodyText'])
            ]
        ]

        stats_table = Table(stats_data, colWidths=[4.5*cm, 4*cm, 4.5*cm, 4*cm])
        stats_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), Color(0.95, 0.95, 0.95)),
            ('BACKGROUND', (2, 0), (2, -1), Color(0.95, 0.95, 0.95)),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        self.story.append(stats_table)
        self.story.append(Spacer(1, 15))

        # Décision
        decision_text, decision_color, decision_bg = self._get_decision_display()

        decision_table = Table([
            [Paragraph(f"<b>DÉCISION: {decision_text}</b>", ParagraphStyle(
                name='DecisionText',
                parent=self.styles['BodyText'],
                fontSize=12,
                fontName='Helvetica-Bold',
                textColor=decision_color,
                alignment=TA_CENTER
            ))]
        ], colWidths=[17*cm])
        decision_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), decision_bg),
            ('BOX', (0, 0), (0, 0), 2, decision_color),
            ('TOPPADDING', (0, 0), (0, 0), 12),
            ('BOTTOMPADDING', (0, 0), (0, 0), 12),
        ]))

        self.story.append(decision_table)
        self.story.append(Spacer(1, 15))

        # Commentaires
        commentaires = self.matrice.get('commentaires_globaux', '')
        if commentaires:
            comment_title = Paragraph("<b>Commentaires et suite à donner:</b>", self.styles['Label'])
            self.story.append(comment_title)
            self.story.append(Spacer(1, 5))

            comment_table = Table([
                [Paragraph(commentaires, self.styles['BodyText'])]
            ], colWidths=[17*cm])
            comment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), HexColor('#f8fafc')),
                ('BOX', (0, 0), (0, 0), 1, colors.grey),
                ('TOPPADDING', (0, 0), (0, 0), 10),
                ('BOTTOMPADDING', (0, 0), (0, 0), 10),
                ('LEFTPADDING', (0, 0), (0, 0), 10),
                ('RIGHTPADDING', (0, 0), (0, 0), 10),
            ]))
            self.story.append(comment_table)
            self.story.append(Spacer(1, 15))

        # Évaluateur
        evaluateur = self.matrice.get('evaluateur', 'N/A')
        evaluateur_para = Paragraph(
            f"<i>Évaluation réalisée par: {evaluateur}</i>",
            ParagraphStyle(
                name='EvaluateurText',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=HexColor('#6c757d'),
                alignment=TA_CENTER
            )
        )
        self.story.append(evaluateur_para)

    def _get_decision_display(self):
        """Retourne le texte, la couleur et le fond de la décision"""
        if self.decision == 'dossier_evaluable':
            return "DOSSIER ÉVALUABLE", HexColor('#065f46'), HexColor('#d1fae5')
        elif self.decision == 'complements_requis':
            return "COMPLÉMENTS REQUIS", HexColor('#92400e'), HexColor('#fef3c7')
        elif self.decision == 'dossier_rejete':
            return "DOSSIER REJETÉ", HexColor('#991b1b'), HexColor('#fee2e2')
        else:
            return "EN ATTENTE", HexColor('#475569'), HexColor('#f1f5f9')

    def _format_date(self, date_str):
        """Formate une date ISO en format français"""
        if not date_str:
            return 'N/A'
        try:
            if isinstance(date_str, str):
                # Gérer différents formats
                if 'T' in date_str:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
                return dt.strftime('%d/%m/%Y')
            return str(date_str)
        except Exception:
            return str(date_str)

    def generate(self):
        """Génère le PDF complet"""
        self._create_header()
        self._create_project_info()
        self._create_documents_table()
        self._create_summary()

        self.doc.build(self.story)
        return self.output_path


def generer_fiche_recevabilite_pdf(project_data, matrice_data, decision, output_directory):
    """
    Fonction utilitaire pour générer le PDF de recevabilité

    Args:
        project_data: dict avec les infos du projet
        matrice_data: dict ou JSON string avec la matrice d'évaluation
        decision: str ('dossier_evaluable', 'complements_requis', 'dossier_rejete')
        output_directory: répertoire de sortie

    Returns:
        str: chemin du fichier PDF généré
    """
    os.makedirs(output_directory, exist_ok=True)

    # Nom du fichier
    numero_projet = project_data.get('numero_projet', f"PROJ-{project_data.get('id', 'X')}")
    filename = f"recevabilite_{numero_projet}.pdf"
    output_path = os.path.join(output_directory, filename)

    # Générer le PDF
    pdf = FicheRecevabilitePDF(project_data, matrice_data, decision, output_path)
    return pdf.generate()
