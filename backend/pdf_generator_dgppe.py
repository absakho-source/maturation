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

    def _get_value(self, key, default='N/A'):
        """
        Récupère une valeur depuis la fiche, avec fallback sur le projet si vide.
        Utile pour les champs de présentation qui peuvent être dans l'un ou l'autre.
        """
        # D'abord essayer depuis la fiche
        value = self.fiche.get(key, '')
        if value and str(value).strip():
            return str(value).strip()

        # Sinon essayer depuis le projet
        value = self.project.get(key, '')
        if value and str(value).strip():
            return str(value).strip()

        return default

    @staticmethod
    def format_text_with_linebreaks(text):
        """Convertir les retours à la ligne en balises <br/> pour ReportLab"""
        if not text:
            return text
        # Échapper les caractères HTML spéciaux sauf <br/>
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Remplacer les \n par <br/>
        text = text.replace('\n', '<br/>')
        # Rétablir <br/>
        text = text.replace('&lt;br/&gt;', '<br/>')
        return text

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

        # Style pour les en-têtes de tableau (texte blanc sur fond sombre)
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=colors.white,
            alignment=TA_CENTER
        ))

    def _create_header(self):
        """Création de l'en-tête officiel avec PLASMAP et logo DGPPE"""
        # Charger le logo DGPPE
        logo_path = os.path.join(os.path.dirname(__file__), 'static', 'logo-dgppe.png')
        logo = None
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*cm, height=2*cm)
            except Exception as e:
                print(f"Erreur chargement logo: {e}")
                logo = None

        # Style pour le ministère (plus petit)
        ministry_style = ParagraphStyle(
            name='MinistryStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            textColor=HexColor('#1a4d7a'),
            alignment=TA_CENTER,
            leading=12
        )

        # Style pour la DGPPE
        dgppe_style = ParagraphStyle(
            name='DGPPEStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold',
            textColor=HexColor('#1a4d7a'),
            alignment=TA_CENTER,
            leading=12
        )

        # Style pour PLASMAP (acronyme mis en valeur)
        plasmap_style = ParagraphStyle(
            name='PLASMAPStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName='Helvetica-Bold',
            textColor=HexColor('#27ae60'),
            alignment=TA_CENTER,
            leading=18
        )

        # Style pour le nom complet de PLASMAP
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
                textColor=HexColor('#1a4d7a'),
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

        # Séparateur décoratif
        separator = Paragraph("───────────────", ParagraphStyle(
            name='SepStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=HexColor('#27ae60'),
            alignment=TA_CENTER
        ))

        plasmap = Paragraph("<b>PLASMAP</b>", plasmap_style)
        plasmap_full = Paragraph(
            "<b>PL</b>ateforme de <b>S</b>uivi de la <b>MA</b>turation des <b>P</b>rojets",
            plasmap_full_style
        )

        # Créer le contenu central (texte)
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

        # Créer le tableau principal avec logo à gauche et contenu central
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

        # Encadrer tout l'en-tête dans un cadre avec fond
        outer_table = Table([[header_table]], colWidths=[17.5*cm])
        outer_table.setStyle(TableStyle([
            ('BOX', (0, 0), (0, 0), 2, HexColor('#1a4d7a')),
            ('BACKGROUND', (0, 0), (0, 0), HexColor('#f8f9fa')),
            ('TOPPADDING', (0, 0), (0, 0), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 10),
            ('LEFTPADDING', (0, 0), (0, 0), 8),
            ('RIGHTPADDING', (0, 0), (0, 0), 8),
        ]))

        self.story.append(outer_table)
        self.story.append(Spacer(1, 15))

        # Titre principal: FICHE D'ÉVALUATION
        title = Paragraph("FICHE D'ÉVALUATION", self.styles['MainTitle'])
        self.story.append(title)

        # Date et version sur la même ligne
        date_generation = datetime.now().strftime("%d/%m/%Y à %H:%M")

        # Construire le texte avec version si disponible
        if self.version_affichage:
            date_version_text = f"<i>Générée le {date_generation} - {self.version_affichage}</i>"
        else:
            date_version_text = f"<i>Générée le {date_generation}</i>"

        date_para = Paragraph(
            date_version_text,
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
        description = self.project.get('description', '') or self.fiche.get('description', '')
        if not description or not description.strip():
            description = 'Non renseignée'
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

        # Origine et dimensions transversales (depuis fiche d'abord, puis projet)
        origine_data = self.fiche.get('origine_projet', {}) or self.project.get('origine_projet', {})

        # Si origine_projet est une chaîne, la convertir en dict
        if isinstance(origine_data, str):
            origine_data = {
                'maturation': origine_data == 'maturation',
                'offre_spontanee': origine_data == 'offre_spontanee',
                'autres': origine_data == 'autres'
            }

        # Construire les textes avec cases cochées (utiliser [X] et [ ] pour compatibilité)
        origine_items = []
        if origine_data.get('maturation'): origine_items.append('<b>[X]</b> MATURATION')
        else: origine_items.append('[ ] MATURATION')
        if origine_data.get('offre_spontanee'): origine_items.append('<b>[X]</b> OFFRE SPONTANÉE')
        else: origine_items.append('[ ] OFFRE SPONTANÉE')
        if origine_data.get('autres'): origine_items.append('<b>[X]</b> AUTRES')
        else: origine_items.append('[ ] AUTRES')

        # Dimensions transversales (depuis fiche d'abord, puis projet)
        cc_adaptation = self.fiche.get('cc_adaptation', False) or self.project.get('cc_adaptation', False)
        cc_attenuation = self.fiche.get('cc_attenuation', False) or self.project.get('cc_attenuation', False)
        genre = self.fiche.get('genre', False) or self.project.get('genre', False)

        # Construire le texte des dimensions transversales
        dimensions_items = []

        # Changement climatique
        cc_label = "<b>CHANGEMENT CLIMATIQUE:</b> "
        cc_parts = []
        if cc_adaptation:
            cc_parts.append('<b>[X]</b> Adaptation')
        else:
            cc_parts.append('[ ] Adaptation')
        if cc_attenuation:
            cc_parts.append('<b>[X]</b> Atténuation')
        else:
            cc_parts.append('[ ] Atténuation')

        cc_text = cc_label + ' &nbsp; '.join(cc_parts)

        # Genre
        if genre:
            genre_text = "<b>GENRE:</b> <b>[X]</b> Oui"
        else:
            genre_text = "<b>GENRE:</b> [ ] Oui"

        data = [
            [
                Paragraph("<b>ORIGINE DU PROJET:</b>", self.styles['Label']),
                Paragraph(' &nbsp;&nbsp; '.join(origine_items), self.styles['DGPPEBodyText'])
            ],
            [
                Paragraph("<b>DIMENSIONS TRANSVERSALES:</b>", self.styles['Label']),
                Paragraph(f"{cc_text}<br/>{genre_text}", self.styles['DGPPEBodyText'])
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
        self.story.append(Spacer(1, 10))

        # Nouveau: Tableaux de présentation détaillée (depuis fiche avec fallback sur projet)
        # Tableau 1: ARTICULATION / AXES / OBJECTIFS STRATÉGIQUES / ODD
        data_tab1 = [
            [
                Paragraph("<b>ARTICULATION</b>", self.styles['TableHeader']),
                Paragraph("<b>AXE(S)</b>", self.styles['TableHeader']),
                Paragraph("<b>OBJECTIF(S) STRATÉGIQUE(S)</b>", self.styles['TableHeader']),
                Paragraph("<b>ODD</b>", self.styles['TableHeader'])
            ],
            [
                Paragraph(self._get_value('articulation', '-'), self.styles['DGPPEBodyText']),
                Paragraph(self._get_value('axes', '-'), self.styles['DGPPEBodyText']),
                Paragraph(self._get_value('objectifs_strategiques', '-'), self.styles['DGPPEBodyText']),
                Paragraph(self._get_value('odd', '-'), self.styles['DGPPEBodyText'])
            ]
        ]

        table1 = Table(data_tab1, colWidths=[4.25*cm, 4.25*cm, 4.25*cm, 4.25*cm])
        table1.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), self.dgppe_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        self.story.append(table1)
        self.story.append(Spacer(1, 10))

        # Tableau 2: DURÉES
        data_tab2 = [
            [
                Paragraph("<b>DURÉE D'ANALYSE</b>", self.styles['TableHeader']),
                Paragraph("<b>RÉALISATION</b>", self.styles['TableHeader']),
                Paragraph("<b>EXPLOITATION</b>", self.styles['TableHeader'])
            ],
            [
                Paragraph(self._get_value('duree_analyse', '-'), self.styles['DGPPEBodyText']),
                Paragraph(self._get_value('realisation', '-'), self.styles['DGPPEBodyText']),
                Paragraph(self._get_value('exploitation', '-'), self.styles['DGPPEBodyText'])
            ]
        ]

        table2 = Table(data_tab2, colWidths=[5.67*cm, 5.67*cm, 5.67*cm])
        table2.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), self.dgppe_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        self.story.append(table2)
        self.story.append(Spacer(1, 10))

        # Tableau 3: LOCALISATION / PARTIES PRENANTES / AUTRES PROJETS
        # Pour localisation, utiliser poles du projet comme fallback
        localisation = self._get_value('localisation', '')
        if not localisation or localisation == '-':
            localisation = self.project.get('poles', '-') or '-'

        data_tab3 = [
            [
                Paragraph("<b>LOCALISATION</b>", self.styles['TableHeader']),
                Paragraph("<b>PARTIES PRENANTES</b>", self.styles['TableHeader']),
                Paragraph("<b>AUTRES PROJETS/PROG. CONNEXES</b>", self.styles['TableHeader'])
            ],
            [
                Paragraph(localisation, self.styles['DGPPEBodyText']),
                Paragraph(self._get_value('parties_prenantes', '-'), self.styles['DGPPEBodyText']),
                Paragraph(self._get_value('autres_projets_connexes', '-'), self.styles['DGPPEBodyText'])
            ]
        ]

        table3 = Table(data_tab3, colWidths=[5.67*cm, 5.67*cm, 5.67*cm])
        table3.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), self.dgppe_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        self.story.append(table3)
        self.story.append(Spacer(1, 10))

        # Tableau 4: OBJECTIF / ACTIVITÉS / RÉSULTATS
        # Utiliser la description du projet comme fallback pour objectif_projet
        objectif = self._get_value('objectif_projet', '')
        if not objectif or objectif == '-':
            objectif = self.project.get('description', '-') or '-'

        data_tab4 = [
            [
                Paragraph("<b>OBJECTIF DU PROJET</b>", self.styles['TableHeader']),
                Paragraph("<b>ACTIVITÉS PRINCIPALES</b>", self.styles['TableHeader']),
                Paragraph("<b>EXTRANTS / RÉSULTATS / IMPACTS ATTENDUS</b>", self.styles['TableHeader'])
            ],
            [
                Paragraph(objectif, self.styles['DGPPEBodyText']),
                Paragraph(self._get_value('activites_principales', '-'), self.styles['DGPPEBodyText']),
                Paragraph(self._get_value('resultats_attendus', '-'), self.styles['DGPPEBodyText'])
            ]
        ]

        table4 = Table(data_tab4, colWidths=[5.67*cm, 5.67*cm, 5.67*cm])
        table4.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), self.dgppe_blue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        self.story.append(table4)
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

        # Liste des 12 critères (total 100 points)
        # Note: impact_emploi retiré car pas dans le formulaire frontend
        criteria_list = [
            ('PERTINENCE', 'pertinence', 10),
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
            ('IMPACTS ENVIRONNEMENTAUX', 'impact_environnemental', 5)
        ]

        # Créer le tableau des critères
        data = []

        # En-tête avec texte blanc sur fond sombre
        header_row = [
            Paragraph("<b>CRITÈRES</b>", self.styles['TableHeader']),
            Paragraph("<b>VALEUR ET/OU<br/>DESCRIPTION</b>", self.styles['TableHeader']),
            Paragraph("<b>SCORE</b>", self.styles['TableHeader']),
            Paragraph("<b>RECOMMANDATIONS</b>", self.styles['TableHeader'])
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

            # Formater les textes pour préserver les retours à la ligne
            description_formatted = self.format_text_with_linebreaks(description) if description else '-'
            recommandations_formatted = self.format_text_with_linebreaks(recommandations) if recommandations else '-'

            # Formater le score pour afficher les décimales si nécessaire
            score_formatted = f"{score:.1f}" if isinstance(score, float) and score % 1 != 0 else str(int(score)) if isinstance(score, (int, float)) else str(score)
            max_score_formatted = f"{max_score:.1f}" if isinstance(max_score, float) and max_score % 1 != 0 else str(int(max_score)) if isinstance(max_score, (int, float)) else str(max_score)

            row = [
                Paragraph(f"<b>{title}</b><br/><font size=8>({max_score_formatted} points)</font>", self.styles['DGPPEBodyText']),
                Paragraph(description_formatted, self.styles['DGPPEBodyText']),
                Paragraph(f"<b>{score_formatted}/{max_score_formatted}</b>", ParagraphStyle(
                    name=f'Score{key}',
                    parent=self.styles['DGPPEBodyText'],
                    alignment=TA_CENTER,
                    fontSize=10
                )),
                Paragraph(recommandations_formatted, self.styles['DGPPEBodyText'])
            ]
            data.append(row)

        # Ligne de total avec formatage des décimales
        total_score_formatted = f"{total_score:.1f}" if isinstance(total_score, float) and total_score % 1 != 0 else str(int(total_score)) if isinstance(total_score, (int, float)) else str(total_score)

        total_row = [
            Paragraph("<b>SCORE TOTAL =</b>", self.styles['Label']),
            '',
            Paragraph(f"<b>{total_score_formatted}/100</b>", ParagraphStyle(
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
            # Formater le texte pour préserver les retours à la ligne
            recommandations_formatted = self.format_text_with_linebreaks(recommandations)
            data = [[
                Paragraph("<b>RECOMMANDATIONS:</b>", self.styles['Label']),
                Paragraph(recommandations_formatted, self.styles['DGPPEBodyText'])
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

        # Ajouter le nom de l'évaluateur après les recommandations
        evaluateur_nom = self.fiche.get('evaluateur_nom', '')
        if evaluateur_nom:
            self.story.append(Spacer(1, 10))
            evaluateur_data = [[
                Paragraph("<b>ÉVALUATEUR:</b>", self.styles['Label']),
                Paragraph(evaluateur_nom, self.styles['DGPPEBodyText'])
            ]]

            evaluateur_table = Table(evaluateur_data, colWidths=[4*cm, 13*cm])
            evaluateur_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (0, 0), Color(0.95, 0.95, 0.95)),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ]))

            self.story.append(evaluateur_table)

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
