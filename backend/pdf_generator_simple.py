"""
Module de génération PDF simplifié pour les fiches d'évaluation
Format identique à celui affiché à l'écran
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

def generer_fiche_evaluation_pdf(fiche_data, project_data, output_directory):
    """
    Génère un PDF de fiche d'évaluation au format identique à l'écran

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

    # Configuration du document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Styles personnalisés
    styles.add(ParagraphStyle(
        name='HeaderMinistere',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=2
    ))

    styles.add(ParagraphStyle(
        name='TitleMain',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        textColor=HexColor('#2c3e50'),
        spaceAfter=20,
        spaceBefore=10
    ))

    styles.add(ParagraphStyle(
        name='SectionTitle',
        parent=styles['Heading2'],
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=10,
        spaceBefore=10
    ))

    story = []

    # Logo DGPPE
    logo_path = os.path.join(os.path.dirname(__file__), 'logo-dgppe.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=2*cm, height=2*cm)
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 10))

    # En-tête DGPPE
    story.append(Paragraph("RÉPUBLIQUE DU SÉNÉGAL", styles['HeaderMinistere']))
    story.append(Paragraph("MINISTÈRE DE L'ÉCONOMIE, DU PLAN ET DE LA COOPÉRATION", styles['HeaderMinistere']))
    story.append(Paragraph("DIRECTION GÉNÉRALE DE LA PLANIFICATION DES POLITIQUES ÉCONOMIQUES", styles['HeaderMinistere']))
    story.append(Paragraph("PLATEFORME DE MATURATION DES PROJETS ET PROGRAMMES PUBLICS", styles['HeaderMinistere']))
    story.append(Spacer(1, 20))

    # Titre principal
    story.append(Paragraph("FICHE D'ÉVALUATION", styles['TitleMain']))

    # Numéro de projet uniquement
    if project_data.get('numero_projet'):
        numero_projet_style = ParagraphStyle(
            name='NumeroProjet',
            parent=styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            textColor=HexColor('#2c3e50')
        )
        numero_projet_text = f"Numéro de projet: {project_data['numero_projet']}"
        story.append(Paragraph(numero_projet_text, numero_projet_style))

    story.append(Spacer(1, 10))

    # Section I - PRÉSENTATION DU PROJET
    section1_title = Paragraph("I - PRÉSENTATION DU PROJET", styles['SectionTitle'])
    section1_table = Table([[section1_title]], colWidths=[17*cm])
    section1_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#3498db')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(section1_table)
    story.append(Spacer(1, 10))

    # Informations du projet
    criteres = fiche_data.get('criteres', {})

    info_data = [
        ["INTITULÉ DU PROJET:", project_data.get('titre', 'N/A')],
        ["SECTEUR DE PLANIFICATION:", project_data.get('secteur', 'N/A')],
        ["PÔLES TERRITORIAUX:", project_data.get('poles', 'N/A')],
        ["COÛT DU PROJET:", f"{project_data.get('cout_estimatif', 0):,.0f} FCFA"],
        ["DESCRIPTION DU PROJET:", project_data.get('description', 'N/A')]
    ]

    info_table = Table(info_data, colWidths=[5*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # Section II - RÉSULTATS DE L'ÉVALUATION
    section2_title = Paragraph("II - RÉSULTATS DE L'ÉVALUATION", styles['SectionTitle'])
    section2_table = Table([[section2_title]], colWidths=[17*cm])
    section2_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#3498db')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(section2_table)
    story.append(Spacer(1, 10))

    # Style pour les textes
    detail_style = ParagraphStyle(
        name='DetailText',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_LEFT
    )

    critere_title_style = ParagraphStyle(
        name='CritereTitle',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        leading=11,
        alignment=TA_LEFT
    )

    # Liste des critères avec leurs scores max et clés
    criteres_list = [
        ("PERTINENCE", 'pertinence', 5),
        ("ALIGNEMENT À LA DOCTRINE DE TRANSFORMATION SYSTÉMIQUE", 'alignement', 10),
        ("PERTINENCE DES ACTIVITÉS ET BIEN FONDÉ DES COÛTS", 'activites_couts', 15),
        ("ÉQUITÉ (SOCIALE-TERRITORIALE-GENRE)", 'equite', 15),
        ("VIABILITÉ/RENTABILITÉ FINANCIÈRE", 'viabilite', 5),
        ("RENTABILITÉ SOCIO-ÉCONOMIQUE (ACA/MPR)", 'rentabilite', 5),
        ("BÉNÉFICES STRATÉGIQUES (SÉCURITÉ-RÉSILIENCE-INNOVATION-COMPÉTITIVITÉ-CONTENU LOCAL, ETC.)", 'benefices_strategiques', 10),
        ("PÉRENNITÉ ET DURABILITÉ DES EFFETS ET IMPACTS DU PROJET", 'perennite', 5),
        ("AVANTAGES ET COÛTS INTANGIBLES", 'avantages_intangibles', 10),
        ("FAISABILITÉ DU PROJET / RISQUES POTENTIELS", 'faisabilite', 5),
        ("POTENTIALITÉ OU OPPORTUNITÉ DU PROJET À ÊTRE RÉALISÉ EN PPP", 'ppp', 5),
        ("IMPACTS ENVIRONNEMENTAUX", 'impact_environnemental', 5),
        ("IMPACT SUR L'EMPLOI", 'impact_emploi', 5),
    ]

    # Afficher chaque critère avec score et commentaire ensemble
    for critere_nom, critere_key, max_score in criteres_list:
        critere_data = criteres.get(critere_key, {})
        score = critere_data.get('score', 0)
        description = critere_data.get('description', 'Aucun commentaire')

        # Tableau pour chaque critère (3 lignes: titre+score, description, commentaire)
        critere_table_data = [
            [Paragraph(f"<b>{critere_nom}</b>", critere_title_style),
             Paragraph(f"<b>{score}/{max_score}</b>", critere_title_style)],
            [Paragraph(f"<i>Commentaire:</i> {description or 'Aucun commentaire'}", detail_style), ""]
        ]

        critere_table = Table(critere_table_data, colWidths=[14*cm, 3*cm])
        critere_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#e8f4f8')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('SPAN', (0, 1), (1, 1)),  # Fusionner les colonnes pour le commentaire
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(critere_table)
        story.append(Spacer(1, 8))

    # Total des scores
    score_total = fiche_data.get('score_total', 0)
    total_data = [["TOTAL SCORE", f"{score_total}/100"]]
    total_table = Table(total_data, colWidths=[14*cm, 3*cm])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 15))

    # Section III - CONCLUSION
    section3_title = Paragraph("III - CONCLUSION", styles['SectionTitle'])
    section3_table = Table([[section3_title]], colWidths=[17*cm])
    section3_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#3498db')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(section3_table)
    story.append(Spacer(1, 10))

    # Proposition et recommandations avec Paragraph pour gérer les textes longs
    proposition_text = fiche_data.get('proposition', 'N/A')
    recommandations_text = fiche_data.get('recommandations', 'N/A')

    conclusion_data = [
        ["PROPOSITION:", Paragraph(proposition_text or 'N/A', detail_style)],
        ["RECOMMANDATIONS:", Paragraph(recommandations_text or 'N/A', detail_style)]
    ]

    conclusion_table = Table(conclusion_data, colWidths=[5*cm, 12*cm])
    conclusion_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(conclusion_table)
    story.append(Spacer(1, 20))

    # Évaluateur
    evaluateur_data = [
        ["ÉVALUATEUR:", fiche_data.get('evaluateur_nom', 'N/A')],
        ["DATE:", _format_date(fiche_data.get('date_evaluation'))]
    ]

    evaluateur_table = Table(evaluateur_data, colWidths=[5*cm, 12*cm])
    evaluateur_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#e3f2fd')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(evaluateur_table)

    # Génération du PDF
    doc.build(story)
    return output_path

def _format_date(date_str):
    """Formatage des dates avec heure"""
    if not date_str:
        return datetime.now().strftime("%d/%m/%Y %H:%M")

    try:
        if isinstance(date_str, str):
            # Essayer différents formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    continue
        return str(date_str)
    except:
        return datetime.now().strftime("%d/%m/%Y")
