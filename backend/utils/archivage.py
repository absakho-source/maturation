"""
Utilitaires pour l'archivage des fiches d'évaluation
"""

from datetime import datetime
from models import db, FicheEvaluationArchive


def archiver_fiche(fiche, raison, archive_par):
    """
    Archive une fiche d'évaluation avant modification ou réassignation

    Args:
        fiche: Instance FicheEvaluation à archiver
        raison: Raison de l'archivage (ex: "modification_secretariat", "reassignation_avant_hierarchie", etc.)
        archive_par: Nom d'utilisateur de la personne qui déclenche l'archivage

    Returns:
        FicheEvaluationArchive: L'objet archive créé, ou None en cas d'erreur
    """
    if not fiche:
        print("⚠️ Aucune fiche fournie pour archivage")
        return None

    try:
        # Compter les versions existantes pour ce projet
        versions_existantes = FicheEvaluationArchive.query.filter_by(
            project_id=fiche.project_id
        ).count()

        # Créer l'archive avec copie de tous les champs
        archive = FicheEvaluationArchive(
            fiche_id_originale=fiche.id,
            project_id=fiche.project_id,
            raison_archivage=raison,
            archive_par=archive_par,
            version=versions_existantes + 1,

            # Copie de tous les champs de la fiche
            evaluateur_nom=fiche.evaluateur_nom,
            date_evaluation=fiche.date_evaluation,
            date_modification=fiche.date_modification,

            # Section I - Présentation du projet (pré-rempli)
            numero_projet=fiche.numero_projet,
            titre_projet=fiche.titre_projet,
            porteur_projet=fiche.porteur_projet,
            structure_appartenance=fiche.structure_appartenance,
            type_structure=fiche.type_structure,
            nom_collectivite=fiche.nom_collectivite,
            adresse_structure=fiche.adresse_structure,
            email_porteur=fiche.email_porteur,
            telephone_porteur=fiche.telephone_porteur,
            zone_intervention=fiche.zone_intervention,
            cout_total=fiche.cout_total,
            financement_sollicite=fiche.financement_sollicite,
            contribution_structure=fiche.contribution_structure,
            autres_financements=fiche.autres_financements,
            autres_financements_details=fiche.autres_financements_details,

            # Section II - Pertinence et cohérence (35 points)
            conformite_priorites_plasepri=fiche.conformite_priorites_plasepri,
            conformite_priorites_plasepri_score=fiche.conformite_priorites_plasepri_score,
            conformite_priorites_plasepri_justification=fiche.conformite_priorites_plasepri_justification,

            coherence_pld=fiche.coherence_pld,
            coherence_pld_score=fiche.coherence_pld_score,
            coherence_pld_justification=fiche.coherence_pld_justification,

            adequation_besoins=fiche.adequation_besoins,
            adequation_besoins_score=fiche.adequation_besoins_score,
            adequation_besoins_justification=fiche.adequation_besoins_justification,

            coherence_cout=fiche.coherence_cout,
            coherence_cout_score=fiche.coherence_cout_score,
            coherence_cout_justification=fiche.coherence_cout_justification,

            pertinence_coherence_total=fiche.pertinence_coherence_total,

            # Section III - Faisabilité (20 points)
            faisabilite_technique=fiche.faisabilite_technique,
            faisabilite_technique_score=fiche.faisabilite_technique_score,
            faisabilite_technique_justification=fiche.faisabilite_technique_justification,

            capacite_maitrise_ouvrage=fiche.capacite_maitrise_ouvrage,
            capacite_maitrise_ouvrage_score=fiche.capacite_maitrise_ouvrage_score,
            capacite_maitrise_ouvrage_justification=fiche.capacite_maitrise_ouvrage_justification,

            faisabilite_financiere=fiche.faisabilite_financiere,
            faisabilite_financiere_score=fiche.faisabilite_financiere_score,
            faisabilite_financiere_justification=fiche.faisabilite_financiere_justification,

            respect_reglementations=fiche.respect_reglementations,
            respect_reglementations_score=fiche.respect_reglementations_score,
            respect_reglementations_justification=fiche.respect_reglementations_justification,

            faisabilite_total=fiche.faisabilite_total,

            # Section IV - Impacts et durabilité (20 points)
            impacts_economiques=fiche.impacts_economiques,
            impacts_economiques_score=fiche.impacts_economiques_score,
            impacts_economiques_justification=fiche.impacts_economiques_justification,

            impacts_sociaux=fiche.impacts_sociaux,
            impacts_sociaux_score=fiche.impacts_sociaux_score,
            impacts_sociaux_justification=fiche.impacts_sociaux_justification,

            impacts_environnementaux=fiche.impacts_environnementaux,
            impacts_environnementaux_score=fiche.impacts_environnementaux_score,
            impacts_environnementaux_justification=fiche.impacts_environnementaux_justification,

            durabilite=fiche.durabilite,
            durabilite_score=fiche.durabilite_score,
            durabilite_justification=fiche.durabilite_justification,

            impacts_durabilite_total=fiche.impacts_durabilite_total,

            # Section V - Gouvernance et transparence (15 points)
            implication_parties_prenantes=fiche.implication_parties_prenantes,
            implication_parties_prenantes_score=fiche.implication_parties_prenantes_score,
            implication_parties_prenantes_justification=fiche.implication_parties_prenantes_justification,

            mecanismes_suivi=fiche.mecanismes_suivi,
            mecanismes_suivi_score=fiche.mecanismes_suivi_score,
            mecanismes_suivi_justification=fiche.mecanismes_suivi_justification,

            transparence_gestion=fiche.transparence_gestion,
            transparence_gestion_score=fiche.transparence_gestion_score,
            transparence_gestion_justification=fiche.transparence_gestion_justification,

            gouvernance_total=fiche.gouvernance_total,

            # Section VI - Innovation et reproductibilité (10 points)
            caractere_innovant=fiche.caractere_innovant,
            caractere_innovant_score=fiche.caractere_innovant_score,
            caractere_innovant_justification=fiche.caractere_innovant_justification,

            potentiel_replicabilite=fiche.potentiel_replicabilite,
            potentiel_replicabilite_score=fiche.potentiel_replicabilite_score,
            potentiel_replicabilite_justification=fiche.potentiel_replicabilite_justification,

            innovation_total=fiche.innovation_total,

            # Scores totaux et proposition
            score_total=fiche.score_total,
            appreciation_globale=fiche.appreciation_globale,
            points_forts=fiche.points_forts,
            points_amelioration=fiche.points_amelioration,
            recommandations=fiche.recommandations,
            proposition=fiche.proposition,
            conditions_reserves=fiche.conditions_reserves,

            # PDF et statut
            fichier_pdf=fiche.fichier_pdf,
            statut=fiche.statut
        )

        # Ajouter à la session et flusher pour obtenir l'ID
        db.session.add(archive)
        db.session.flush()

        print(f"✅ Fiche archivée avec succès (ID: {archive.id}, Version: {archive.version}, Raison: {raison})")
        return archive

    except Exception as e:
        print(f"❌ Erreur lors de l'archivage de la fiche: {e}")
        import traceback
        traceback.print_exc()
        return None
