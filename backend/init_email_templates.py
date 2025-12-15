#!/usr/bin/env python3
"""
Script d'initialisation des templates d'emails par défaut
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
from db import db
from models import EmailTemplate
import json

def init_templates():
    """Initialise les templates d'emails par défaut"""

    templates = [
        {
            'template_key': 'projet_assigne',
            'nom': 'Projet assigné à un évaluateur',
            'description': 'Email envoyé au soumissionnaire quand son projet est assigné à un évaluateur',
            'sujet': '[DGPPE] Votre projet a été assigné pour évaluation',
            'contenu_html': '''
                <p>Bonjour {user_name},</p>
                <p>Nous vous informons que votre projet <strong>"{project_titre}"</strong> (N° {numero_projet}) a été assigné à un évaluateur.</p>
                <p>L'évaluation de votre dossier va commencer prochainement.</p>
            ''',
            'variables_disponibles': json.dumps([
                {'var': '{user_name}', 'description': 'Nom du soumissionnaire'},
                {'var': '{project_titre}', 'description': 'Titre du projet'},
                {'var': '{numero_projet}', 'description': 'Numéro du projet'}
            ])
        },
        {
            'template_key': 'projet_en_evaluation',
            'nom': 'Projet en cours d\'évaluation',
            'description': 'Email envoyé au soumissionnaire quand l\'évaluation de son projet démarre',
            'sujet': '[DGPPE] Évaluation de votre projet en cours',
            'contenu_html': '''
                <p>Bonjour {user_name},</p>
                <p>Votre projet <strong>"{project_titre}"</strong> (N° {numero_projet}) est actuellement en cours d'évaluation.</p>
                <p>Vous serez informé dès que l'évaluation sera terminée.</p>
            ''',
            'variables_disponibles': json.dumps([
                {'var': '{user_name}', 'description': 'Nom du soumissionnaire'},
                {'var': '{project_titre}', 'description': 'Titre du projet'},
                {'var': '{numero_projet}', 'description': 'Numéro du projet'}
            ])
        },
        {
            'template_key': 'complements_demandes',
            'nom': 'Compléments d\'information requis',
            'description': 'Email envoyé quand des compléments sont demandés au soumissionnaire',
            'sujet': '[DGPPE] Compléments d\'information requis pour votre projet',
            'contenu_html': '''
                <p>Bonjour {user_name},</p>
                <p>Suite à l'examen de votre projet <strong>"{project_titre}"</strong> (N° {numero_projet}), des compléments d'information sont nécessaires.</p>
                <p><strong>Message du secrétariat :</strong></p>
                <blockquote style="border-left: 4px solid #f59e0b; padding-left: 16px; margin: 16px 0; color: #92400e; background: #fef3c7; padding: 12px 16px; border-radius: 4px;">
                    {message_complements}
                </blockquote>
                <p>Veuillez vous connecter à la plateforme pour fournir les informations demandées.</p>
            ''',
            'variables_disponibles': json.dumps([
                {'var': '{user_name}', 'description': 'Nom du soumissionnaire'},
                {'var': '{project_titre}', 'description': 'Titre du projet'},
                {'var': '{numero_projet}', 'description': 'Numéro du projet'},
                {'var': '{message_complements}', 'description': 'Message du secrétariat'}
            ])
        },
        {
            'template_key': 'projet_evalue',
            'nom': 'Évaluation terminée',
            'description': 'Email envoyé quand l\'évaluation du projet est terminée',
            'sujet': '[DGPPE] Évaluation de votre projet terminée',
            'contenu_html': '''
                <p>Bonjour {user_name},</p>
                <p>L'évaluation de votre projet <strong>"{project_titre}"</strong> (N° {numero_projet}) est terminée.</p>
                <p>Le dossier est en cours de validation par le Secrétariat SCT.</p>
                <p>Vous serez informé de la suite du processus prochainement.</p>
            ''',
            'variables_disponibles': json.dumps([
                {'var': '{user_name}', 'description': 'Nom du soumissionnaire'},
                {'var': '{project_titre}', 'description': 'Titre du projet'},
                {'var': '{numero_projet}', 'description': 'Numéro du projet'}
            ])
        },
        {
            'template_key': 'avis_favorable',
            'nom': 'Avis favorable',
            'description': 'Email envoyé quand le projet reçoit un avis favorable',
            'sujet': '[DGPPE] ✅ Avis favorable pour votre projet',
            'contenu_html': '''
                <p>Bonjour {user_name},</p>
                <p>Nous avons le plaisir de vous informer que votre projet <strong>"{project_titre}"</strong> (N° {numero_projet}) a reçu un <strong style="color: #10b981;">avis favorable</strong>.</p>
                <p>La fiche d'évaluation détaillée est maintenant disponible sur la plateforme.</p>
            ''',
            'variables_disponibles': json.dumps([
                {'var': '{user_name}', 'description': 'Nom du soumissionnaire'},
                {'var': '{project_titre}', 'description': 'Titre du projet'},
                {'var': '{numero_projet}', 'description': 'Numéro du projet'}
            ])
        },
        {
            'template_key': 'avis_favorable_conditions',
            'nom': 'Avis favorable sous conditions',
            'description': 'Email envoyé quand le projet reçoit un avis favorable sous conditions',
            'sujet': '[DGPPE] Avis favorable sous conditions pour votre projet',
            'contenu_html': '''
                <p>Bonjour {user_name},</p>
                <p>Votre projet <strong>"{project_titre}"</strong> (N° {numero_projet}) a reçu un <strong style="color: #f59e0b;">avis favorable sous conditions</strong>.</p>
                <p>Veuillez consulter la fiche d'évaluation sur la plateforme pour connaître les conditions à remplir.</p>
            ''',
            'variables_disponibles': json.dumps([
                {'var': '{user_name}', 'description': 'Nom du soumissionnaire'},
                {'var': '{project_titre}', 'description': 'Titre du projet'},
                {'var': '{numero_projet}', 'description': 'Numéro du projet'}
            ])
        },
        {
            'template_key': 'avis_defavorable',
            'nom': 'Avis défavorable',
            'description': 'Email envoyé quand le projet reçoit un avis défavorable',
            'sujet': '[DGPPE] Avis défavorable pour votre projet',
            'contenu_html': '''
                <p>Bonjour {user_name},</p>
                <p>Nous vous informons que votre projet <strong>"{project_titre}"</strong> (N° {numero_projet}) a reçu un <strong style="color: #ef4444;">avis défavorable</strong>.</p>
                <p>La fiche d'évaluation détaillée expliquant les raisons de cet avis est disponible sur la plateforme.</p>
            ''',
            'variables_disponibles': json.dumps([
                {'var': '{user_name}', 'description': 'Nom du soumissionnaire'},
                {'var': '{project_titre}', 'description': 'Titre du projet'},
                {'var': '{numero_projet}', 'description': 'Numéro du projet'}
            ])
        },
        {
            'template_key': 'evaluateur_assignation',
            'nom': 'Assignation à un évaluateur',
            'description': 'Email envoyé à l\'évaluateur quand un projet lui est assigné',
            'sujet': '[DGPPE] Nouveau projet assigné - {project_titre}',
            'contenu_html': '''
                <p>Bonjour {evaluateur_nom},</p>
                <p>Un nouveau projet vous a été assigné pour évaluation.</p>
                <p><strong>Projet :</strong> {project_titre}</p>
                <p><strong>Numéro :</strong> {numero_projet}</p>
                <p><strong>Soumissionnaire :</strong> {auteur_nom}</p>
                <p>Veuillez vous connecter à la plateforme pour consulter le dossier complet et procéder à l'évaluation.</p>
            ''',
            'variables_disponibles': json.dumps([
                {'var': '{evaluateur_nom}', 'description': 'Nom de l\'évaluateur'},
                {'var': '{project_titre}', 'description': 'Titre du projet'},
                {'var': '{numero_projet}', 'description': 'Numéro du projet'},
                {'var': '{auteur_nom}', 'description': 'Nom du soumissionnaire'}
            ])
        },
        {
            'template_key': 'nouveau_message',
            'nom': 'Nouveau message sur le projet',
            'description': 'Email envoyé quand un nouveau message est posté sur le projet',
            'sujet': '[DGPPE] Nouveau message - {project_titre}',
            'contenu_html': '''
                <p>Bonjour {user_name},</p>
                <p>Un nouveau message a été posté sur votre projet <strong>"{project_titre}"</strong> (N° {numero_projet}).</p>
                <p><strong>Message de :</strong> {message_auteur}</p>
                <p>Connectez-vous à la plateforme pour consulter ce message et y répondre si nécessaire.</p>
            ''',
            'variables_disponibles': json.dumps([
                {'var': '{user_name}', 'description': 'Nom du destinataire'},
                {'var': '{project_titre}', 'description': 'Titre du projet'},
                {'var': '{numero_projet}', 'description': 'Numéro du projet'},
                {'var': '{message_auteur}', 'description': 'Auteur du message'}
            ])
        }
    ]

    with app.app_context():
        # Créer les tables si elles n'existent pas
        db.create_all()

        for template_data in templates:
            # Vérifier si le template existe déjà
            existing = EmailTemplate.query.filter_by(template_key=template_data['template_key']).first()

            if existing:
                print(f"⚠️  Template '{template_data['template_key']}' existe déjà, on le met à jour")
                # Mettre à jour seulement si c'est la première fois (pas de modifie_par)
                if not existing.modifie_par:
                    existing.nom = template_data['nom']
                    existing.description = template_data['description']
                    existing.sujet = template_data['sujet']
                    existing.contenu_html = template_data['contenu_html']
                    existing.variables_disponibles = template_data['variables_disponibles']
            else:
                print(f"✅ Création du template '{template_data['template_key']}'")
                new_template = EmailTemplate(**template_data)
                db.session.add(new_template)

        db.session.commit()
        print(f"\n✅ {len(templates)} templates initialisés avec succès!")

if __name__ == '__main__':
    print("🔧 Initialisation des templates d'emails...")
    init_templates()
