<!-- filepath: /Users/abou/Documents/DGPPE/2025/Plateforme de soumission/maturation/frontend/src/views/ProjectDetail.vue -->
<template>
  <PageWrapper>
    <div class="project-detail-container" v-if="project">
      <div class="detail-header">
        <button @click="$router.back()" class="btn-back">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Retour
        </button>
        <span class="badge" :class="getStatusBadgeClass()">{{ getStatusBadgeText() }}</span>
      </div>

      <div class="detail-content">
        <h1>{{ project.titre }}</h1>

        <!-- Avertissement si le compte soumissionnaire n'est pas vérifié -->
        <div v-if="project.soumissionnaire_statut_compte === 'non_verifie'" class="warning-banner">
          <div class="warning-icon">🔒</div>
          <div class="warning-content">
            <h3>Compte non vérifié</h3>
            <p>Le compte du soumissionnaire de ce projet n'a pas encore été vérifié. Aucune action ne peut être effectuée sur ce projet tant que le compte n'est pas validé par un administrateur.</p>
          </div>
        </div>

        <div class="info-grid">
          <div class="info-card">
            <h3>Informations générales</h3>
            <div class="info-row">
              <span class="label">Point focal / Responsable:</span>
              <span class="value">{{ project.point_focal_nom || project.auteur_nom }}</span>
            </div>
            <div class="info-row" v-if="project.point_focal_fonction">
              <span class="label">Fonction:</span>
              <span class="value">{{ project.point_focal_fonction }}</span>
            </div>
            <div class="info-row" v-if="project.point_focal_email">
              <span class="label">Email:</span>
              <span class="value">{{ project.point_focal_email }}</span>
            </div>
            <div class="info-row" v-if="project.point_focal_telephone">
              <span class="label">Téléphone:</span>
              <span class="value">{{ project.point_focal_telephone }}</span>
            </div>
            <!-- Hiérarchie de l'organisme de tutelle -->
            <div v-if="organismeHierarchie" class="organisme-hierarchie">
              <div class="hierarchie-title">Organisme de tutelle</div>
              <div class="hierarchie-item" v-for="(item, index) in organismeHierarchie" :key="index">
                <span class="hierarchie-label">{{ item.label }}:</span>
                <span class="hierarchie-value">{{ item.value }}</span>
              </div>
            </div>
            <!-- Fallback pour anciens projets sans données structurées -->
            <div class="info-row" v-else-if="project.organisme_tutelle">
              <span class="label">Organisme de tutelle:</span>
              <span class="value">{{ project.organisme_tutelle }}</span>
            </div>

            <div class="info-row" v-if="project.structure_soumissionnaire">
              <span class="label">Structure soumissionnaire:</span>
              <span class="value">{{ project.structure_soumissionnaire }}</span>
            </div>
            <div class="info-row">
              <span class="label">Date de soumission:</span>
              <span class="value">{{ formatDateTime(project.date_soumission) }}</span>
            </div>
            <div class="info-row" v-if="project.lieu_soumission_ville || project.lieu_soumission_pays">
              <span class="label">Lieu de soumission:</span>
              <span class="value">{{ formatLieuSoumission() }}</span>
            </div>
            <div class="info-row">
              <span class="label">Secteur de planification:</span>
              <span class="value">{{ project.secteur }}</span>
            </div>
            <div class="info-row">
              <span class="label">Zone(s) d'intervention:</span>
              <span class="value">{{ project.poles }}</span>
            </div>
            <div class="info-row" v-if="project.cout_estimatif">
              <span class="label">Coût estimatif:</span>
              <span class="value">{{ formatCurrency(project.cout_estimatif) }} FCFA</span>
            </div>
            <div class="info-row" v-if="project.type_financement">
              <span class="label">Type de financement:</span>
              <span class="value">{{ formatTypeFinancement(project.type_financement) }}</span>
            </div>
          </div>

          <!-- Nouveaux champs (Décembre 2025) -->
          <div class="info-card" v-if="project.nouveaute || project.niveau_priorite">
            <h3>Caractéristiques du projet</h3>
            <div class="info-row" v-if="project.nouveaute">
              <span class="label">Nouveauté:</span>
              <span class="value">
                <span v-if="project.nouveaute === 'projet_initial'" class="badge badge-initial">Projet initial</span>
                <span v-else-if="project.nouveaute === 'phase_2'" class="badge badge-phase2">Phase II</span>
              </span>
            </div>
            <div class="info-row" v-if="project.nouveaute === 'phase_2' && project.projet_initial_ref">
              <span class="label">Référence Phase I:</span>
              <span class="value">{{ project.projet_initial_ref }}</span>
            </div>
            <div class="info-row" v-if="project.niveau_priorite">
              <span class="label">Niveau de priorité:</span>
              <span class="value">
                <span v-if="project.niveau_priorite === 'prioritaire_ant'" class="badge badge-prioritaire">PROJET PRIORITAIRE Agenda National de Transformation</span>
                <span v-else class="badge badge-standard">Projet standard</span>
              </span>
            </div>
          </div>

          <div class="info-card" v-if="project.description">
            <h3>Description</h3>
            <p class="description">{{ project.description }}</p>
          </div>

          <!-- Pièces jointes du projet (fichiers soumis avec le projet) -->
          <div class="info-card" v-if="project.pieces_jointes && project.pieces_jointes.length > 0">
            <h3>📎 Pièces jointes du projet</h3>
            <p class="info-text-small">Documents soumis avec le projet</p>
            <div class="files-list-grid">
              <div v-for="(fichier, index) in project.pieces_jointes"
                   :key="index"
                   class="file-item"
                   @click="ouvrirFichier(fichier)">
                <div class="file-icon">
                  <svg v-if="isPDF(fichier)" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14,2 14,8 20,8"/>
                    <path d="M9 15v-2h2v2H9z"/>
                  </svg>
                  <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14,2 14,8 20,8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                  </svg>
                </div>
                <div class="file-info">
                  <span class="file-name">{{ getFileName(fichier) }}</span>
                  <span class="file-type">{{ getFileExtension(fichier).toUpperCase() }}</span>
                </div>
                <div class="file-action">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                    <polyline points="15,3 21,3 21,9"/>
                    <line x1="10" y1="14" x2="21" y2="3"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          <!-- Informations sur les compléments -->
          <div class="info-card" v-if="project.complements_reponse_message || project.commentaires">
            <h3>💬 Échanges et compléments</h3>

            <div v-if="project.commentaires" class="complement-section">
              <!-- Afficher le titre approprié selon le statut du projet -->
              <h4 v-if="project.statut === 'rejeté' || project.avis === 'dossier rejeté'">Motif de rejet :</h4>
              <h4 v-else>Demande de compléments :</h4>
              <div class="complement-message demande">{{ project.commentaires }}</div>
            </div>
            
            <div v-if="project.complements_reponse_message" class="complement-section">
              <h4>Réponse du soumissionnaire :</h4>
              <div class="complement-message reponse">{{ project.complements_reponse_message }}</div>
              <div v-if="project.complements_reponse_pieces" class="complement-files">
                <strong>📎 Nouvelles pièces jointes :</strong>
                <div class="files-list">
                  <span v-for="(fichier, index) in parseComplementsFiles(project.complements_reponse_pieces)" 
                        :key="index" 
                        class="file-link"
                        @click="ouvrirFichier(fichier)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14,2 14,8 20,8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                      <line x1="10" y1="9" x2="8" y2="9"/>
                    </svg>
                    {{ fichier }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Section Évaluation - masquée pour les soumissionnaires -->
          <div class="info-card" v-if="project.evaluateur_nom && !isSoumissionnaire() && peutVoirEvaluation()">
            <h3>Évaluation</h3>
            <div class="info-row">
              <span class="label">Évaluateur assigné:</span>
              <span class="value">{{ project.evaluateur_display_name || project.evaluateur_nom }}</span>
            </div>
            <div class="info-row" v-if="project.avis">
              <span class="label">Avis:</span>
              <span class="value" :class="getAvisClass(project.avis)">{{ project.avis }}</span>
            </div>
            <!-- Ne pas afficher les commentaires ici si c'est un rejet (ils sont déjà dans la section "Échanges et compléments") -->
            <div class="info-row" v-if="project.commentaires && project.statut !== 'rejeté' && project.avis !== 'dossier rejeté'">
              <span class="label">Commentaires:</span>
              <span class="value">{{ project.commentaires }}</span>
            </div>
          </div>

          <!-- Section Validation Présidence SCT - masquée pour les soumissionnaires -->
          <div class="info-card" v-if="project.avis_presidencesct && !isSoumissionnaire()">
            <h3>Validation Présidence SCT</h3>
            <div class="info-row">
              <span class="label">Décision:</span>
              <span class="value validated">{{ project.avis_presidencesct }}</span>
            </div>
          </div>

          <!-- Section Motivation de resoumission - masquée pour les soumissionnaires -->
          <div class="info-card" v-if="project.motivation_resoumission && !isSoumissionnaire()">
            <h3>💬 Motivation de la resoumission</h3>
            <div class="resubmission-motivation-detail">
              <p>{{ project.motivation_resoumission }}</p>
            </div>
          </div>

          <!-- Section Décision finale - masquée pour les soumissionnaires -->
          <div class="info-card" v-if="project.decision_finale && !isSoumissionnaire()">
            <h3>Décision finale (Présidence Comité)</h3>
            <div class="info-row">
              <span class="label">Décision:</span>
              <span class="value validated">{{ project.decision_finale }}</span>
            </div>
          </div>

          <!-- Section Évaluation Préalable (lecture seule) -->
          <div class="info-card" v-if="project.evaluation_prealable && !isSoumissionnaire()">
            <h3>🔍 Évaluation de la Recevabilité</h3>
            <div class="evaluation-prealable-resultat">
              <div :class="['decision-badge',
                project.evaluation_prealable === 'dossier_evaluable' ? 'success' :
                project.evaluation_prealable === 'dossier_rejete' ? 'danger' : 'warning']">
                {{ project.evaluation_prealable === 'dossier_evaluable' ? '✅ Dossier évaluable' :
                   project.evaluation_prealable === 'dossier_rejete' ? '❌ Dossier rejeté' :
                   '📝 Compléments requis' }}
              </div>

              <!-- Afficher la matrice d'évaluation si elle existe -->
              <MatriceEvaluationPrealableReadOnly v-if="evaluationPrealableMatrice" :matrice="evaluationPrealableMatrice" />

              <!-- Sinon, afficher le commentaire simple (ancien format) -->
              <template v-else>
                <p v-if="project.evaluation_prealable_commentaire" class="commentaire">
                  <strong>Commentaire:</strong> {{ project.evaluation_prealable_commentaire }}
                </p>
                <p class="date-evaluation" v-if="project.evaluation_prealable_date">
                  Évaluation effectuée le {{ formatDateTime(project.evaluation_prealable_date) }}
                </p>
              </template>
            </div>
          </div>

          <!-- Section PDF Recevabilité - Même style que la fiche d'évaluation -->
          <div class="info-card" v-if="project.evaluation_prealable && project.evaluation_prealable_matrice && !isSoumissionnaire()">
            <h3>📋 Matrice de Recevabilité (PDF)</h3>
            <p>La matrice d'évaluation de la recevabilité a été générée.</p>
            <button @click="ouvrirRecevabilitePDF" class="btn-primary">
              📄 Voir la matrice de recevabilité (PDF)
            </button>
          </div>

          <!-- Section Statut pour soumissionnaire: En attente décision Comité -->
          <div class="info-card" v-if="isSoumissionnaire() && project.statut_comite === 'recommande_comite'">
            <h3>📋 Statut de votre projet</h3>
            <div class="status-box status-pending-comite">
              <div class="status-icon">⏳</div>
              <div class="status-content">
                <h4>En attente de décision du Comité</h4>
                <p>Votre projet est actuellement en cours d'examen par le Comité de Maturation.</p>
                <p>Vous serez informé une fois que le Comité aura statué sur votre projet.</p>
              </div>
            </div>
          </div>

          <!-- Section Fiche d'évaluation PDF -->
          <!-- Visible pour: rôles internes (avec peutVoirEvaluation) OU soumissionnaire (avec soumissionnairePeutVoirFiche) -->
          <div class="info-card" v-if="ficheEvaluation && ficheEvaluation.fichier_pdf && ((!isSoumissionnaire() && peutVoirEvaluation()) || (isSoumissionnaire() && soumissionnairePeutVoirFiche()))">
            <h3>📄 Fiche d'évaluation</h3>
            <p v-if="isSoumissionnaire()" class="info-message">
              ✅ Votre projet a été validé. Vous pouvez consulter la fiche d'évaluation détaillée ci-dessous.
            </p>
            <p v-else>La fiche d'évaluation a été générée.</p>
            <button @click="ouvrirFichePDF" class="btn-primary">
              📄 Voir la fiche d'évaluation (PDF)
            </button>
          </div>

          <!-- Section Archives des fiches d'évaluation - Visible pour tous les rôles autorisés (sauf soumissionnaire) s'il y a des archives -->
          <div class="info-card archives-section" v-if="currentUser && ['admin', 'secretariatsct', 'presidencesct', 'presidencecomite', 'evaluateur'].includes(currentUser.role) && !isSoumissionnaire() && (!loadingArchives && archives.length > 0)">
            <h3>📚 Historique des fiches d'évaluation archivées</h3>
            <div class="archives-list">
              <div v-for="archive in archives" :key="archive.filename" class="archive-item">
                <div class="archive-info">
                  <div class="archive-header">
                    <span class="archive-version">Version {{ archive.version }}</span>
                    <span class="archive-date">{{ formatDateTime(archive.date_archivage) }}</span>
                  </div>
                  <div class="archive-details">
                    <div class="archive-detail-row">
                      <span class="label">Raison :</span>
                      <span class="value">{{ formatRaisonArchivage(archive.raison_archivage) }}</span>
                    </div>
                    <div class="archive-detail-row">
                      <span class="label">Archivé par :</span>
                      <span class="value">{{ archive.archive_par }}</span>
                    </div>
                    <div class="archive-detail-row">
                      <span class="label">Taille :</span>
                      <span class="value">{{ formatFileSize(archive.taille) }}</span>
                    </div>
                  </div>
                </div>
                <div class="archive-actions">
                  <button @click="ouvrirArchive(archive.filename)" class="btn-view" title="Voir">
                    👁️ Voir
                  </button>
                  <button v-if="currentUser.role === 'admin'" @click="supprimerArchive(archive.filename)" class="btn-delete" title="Supprimer">
                    🗑️ Supprimer
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- Documenthèque du projet - Accessible à tous les membres -->
        <DocumenthequeProjet v-if="project" :projectId="project.id" />

        <!-- Section Historique - masquée pour les soumissionnaires -->
        <div class="info-card" v-if="!isSoumissionnaire()">
          <h3>📋 Historique complet du projet</h3>
          <div v-if="loadingHistorique" class="loading-state">
            <p>Chargement de l'historique...</p>
          </div>
          <div v-else-if="historique.length === 0" class="empty-state">
            <p>Aucun historique disponible</p>
          </div>
          <div v-else class="historique-timeline">
            <div v-for="entry in historique" :key="entry.id" class="timeline-item">
              <div class="timeline-date">{{ formatDateTime(entry.date) }}</div>
              <div class="timeline-content">
                <div class="timeline-action">{{ entry.action }}</div>
                <div class="timeline-author">{{ entry.auteur }} ({{ getRoleLabel(entry.role) }})</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Discussion du projet - Espace d'échange entre soumissionnaire et comité -->
        <DiscussionProjet v-if="project" :projectId="project.id" />
      </div>
    </div>
    <div v-else class="loading">Chargement...</div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';
import DocumenthequeProjet from '../components/DocumenthequeProjet.vue';
import DiscussionProjet from '../components/DiscussionProjet.vue';
import MatriceEvaluationPrealableReadOnly from '../components/MatriceEvaluationPrealableReadOnly.vue';

export default {
  name: "ProjectDetail",
  components: { PageWrapper, DocumenthequeProjet, DiscussionProjet, MatriceEvaluationPrealableReadOnly },
  data() {
    return {
      project: null,
      historique: [],
      ficheEvaluation: null,
      loadingHistorique: true,
      currentUser: null,
      archives: [],
      loadingArchives: true
    };
  },
  computed: {
    organismeHierarchie() {
      // Parse les données structurées de l'organisme de tutelle et retourne un tableau de paires label/valeur
      if (!this.project || !this.project.organisme_tutelle_data) {
        return null;
      }

      try {
        const data = JSON.parse(this.project.organisme_tutelle_data);
        const hierarchy = [];

        // Type d'organisme
        if (data.type_organisme) {
          const typeLabels = {
            'institution': 'Institution',
            'collectivite': 'Collectivité territoriale',
            'agence': 'Agence / Établissement public',
            'autre': 'Autre organisme'
          };
          hierarchy.push({
            label: 'Type d\'organisme',
            value: typeLabels[data.type_organisme] || data.type_organisme
          });

          // Institution
          if (data.type_organisme === 'institution' && data.type_institution) {
            const instLabels = {
              'presidence': 'Présidence de la République',
              'primature': 'Primature',
              'ministere': 'Ministère',
              'autre_institution': 'Autre institution'
            };
            hierarchy.push({
              label: 'Type d\'institution',
              value: instLabels[data.type_institution] || data.type_institution
            });

            if (data.type_institution === 'ministere') {
              if (data.nom_ministere === '__autre__' && data.nom_ministere_libre) {
                hierarchy.push({ label: 'Ministère', value: data.nom_ministere_libre });
              } else if (data.nom_ministere) {
                hierarchy.push({ label: 'Ministère', value: data.nom_ministere });
              }
            } else if (data.type_institution === 'autre_institution' && data.nom_institution) {
              hierarchy.push({ label: 'Institution', value: data.nom_institution });
            }
          }

          // Collectivité
          if (data.type_organisme === 'collectivite') {
            if (data.niveau_collectivite) {
              const niveauLabels = {
                'region': 'Région',
                'departement': 'Département',
                'commune': 'Commune'
              };
              hierarchy.push({
                label: 'Niveau',
                value: niveauLabels[data.niveau_collectivite] || data.niveau_collectivite
              });
            }
            if (data.region_parente) {
              hierarchy.push({ label: 'Région', value: data.region_parente });
            }
            if (data.departement_parent && data.niveau_collectivite !== 'region') {
              hierarchy.push({ label: 'Département', value: data.departement_parent });
            }
            // Note: On n'affiche pas le nom de la collectivité ici car il est déjà affiché
            // dans le champ "Structure soumissionnaire" juste en dessous
          }

          // Agence
          if (data.type_organisme === 'agence') {
            // Note: On n'affiche pas le nom de l'agence ici car il est déjà affiché
            // dans le champ "Structure soumissionnaire" juste en dessous
            if (data.tutelle_agence) {
              let tutelle = '';
              if (data.tutelle_agence === 'presidence') {
                tutelle = 'Présidence de la République';
              } else if (data.tutelle_agence === 'primature') {
                tutelle = 'Primature';
              } else if (data.tutelle_agence === '__ministere__') {
                if (data.tutelle_agence_libre === '__autre__' && data.tutelle_agence_autre) {
                  tutelle = data.tutelle_agence_autre;
                } else if (data.tutelle_agence_libre) {
                  tutelle = data.tutelle_agence_libre;
                }
              }
              if (tutelle) {
                hierarchy.push({ label: 'Autorité de tutelle', value: tutelle });
              }
            }
          }

          // Autre
          // Note: On n'affiche pas le nom de la structure ici car il est déjà affiché
          // dans le champ "Structure soumissionnaire" juste en dessous
          if (data.type_organisme === 'autre') {
            // Pas de hiérarchie supplémentaire à afficher
          }
        }

        return hierarchy.length > 0 ? hierarchy : null;
      } catch (e) {
        console.error('[ProjectDetail] Erreur lors du parsing de organisme_tutelle_data:', e);
        return null;
      }
    },
    evaluationPrealableMatrice() {
      // Parse la matrice JSON si elle existe
      if (!this.project || !this.project.evaluation_prealable_matrice) {
        return null;
      }

      try {
        return JSON.parse(this.project.evaluation_prealable_matrice);
      } catch (e) {
        console.error('[ProjectDetail] Erreur lors du parsing de evaluation_prealable_matrice:', e);
        return null;
      }
    }
  },
  async mounted() {
    // Récupérer l'utilisateur connecté
    this.currentUser = JSON.parse(localStorage.getItem("user") || "null");

    const id = this.$route.params.id;
    try {
      // Charger les détails du projet
      const projectRes = await fetch(`/api/projects/${id}`);
      this.project = await projectRes.json();

      // Charger l'historique
      const historiqueRes = await fetch(`/api/logs/${id}`);
      this.historique = await historiqueRes.json();

      // Charger la fiche d'évaluation si elle existe
      try {
        const ficheRes = await fetch(`/api/projects/${id}/fiche-evaluation`);
        if (ficheRes.ok) {
          this.ficheEvaluation = await ficheRes.json();
        } else if (ficheRes.status === 404) {
          // La fiche n'existe pas encore, c'est normal - ne pas afficher d'erreur
          this.ficheEvaluation = null;
        }
      } catch (ficheErr) {
        // Erreur réseau ou autre - ignorer silencieusement
        this.ficheEvaluation = null;
      }

      // Charger les archives des fiches d'évaluation (tous les rôles autorisés sauf soumissionnaire)
      const rolesAutorises = ['admin', 'secretariatsct', 'presidencesct', 'presidencecomite', 'evaluateur'];
      if (this.currentUser && rolesAutorises.includes(this.currentUser.role)) {
        try {
          const archivesRes = await fetch(`/api/projects/${id}/fiches-archives`, {
            headers: {
              'X-Role': this.currentUser.role,
              'X-Username': this.currentUser.username
            }
          });
          if (archivesRes.ok) {
            const data = await archivesRes.json();
            this.archives = data.archives || [];
          } else {
            this.archives = [];
          }
        } catch (archivesErr) {
          console.error('Erreur chargement archives:', archivesErr);
          this.archives = [];
        } finally {
          this.loadingArchives = false;
        }
      } else {
        this.loadingArchives = false;
      }
    } catch (err) {
      console.error(err);
      this.$router.push('/');
    } finally {
      this.loadingHistorique = false;
    }

    // Écouter les messages du popup d'édition de fiche
    window.addEventListener('message', this.handleFicheUpdate);
  },
  beforeUnmount() {
    // Nettoyer le listener quand le composant est détruit
    window.removeEventListener('message', this.handleFicheUpdate);
  },
  methods: {
    handleFicheUpdate(event) {
      console.log('[ProjectDetail] Message reçu:', event.data);
      console.log('[ProjectDetail] Origin:', event.origin, 'Expected:', window.location.origin);

      // Vérifier l'origine pour la sécurité
      if (event.origin !== window.location.origin) {
        console.warn('[ProjectDetail] Message ignoré: origine différente');
        return;
      }

      if (event.data.type === 'ficheUpdated' && event.data.projetId == this.project?.id) {
        console.log('[ProjectDetail] Message ficheUpdated reçu, rechargement des données...');
        this.rechargerFicheEtHistorique();
      } else {
        console.log('[ProjectDetail] Message ignoré:', {
          type: event.data.type,
          projetId: event.data.projetId,
          currentProjectId: this.project?.id
        });
      }
    },
    ouvrirFichePDF() {
      // Ouvrir le PDF de la fiche d'évaluation dans un nouvel onglet
      const pdfUrl = `/api/projects/${this.project.id}/fiche-evaluation/pdf`;
      window.open(pdfUrl, '_blank');
    },
    ouvrirRecevabilitePDF() {
      // Ouvrir le PDF de la matrice de recevabilité dans un nouvel onglet
      const pdfUrl = `/api/projects/${this.project.id}/recevabilite/pdf`;
      window.open(pdfUrl, '_blank');
    },
    async rechargerFicheEtHistorique() {
      const id = this.$route.params.id;
      console.log('[ProjectDetail] Début rechargement pour projet ID:', id);

      try {
        // Recharger l'historique
        console.log('[ProjectDetail] Rechargement historique...');
        const historiqueRes = await fetch(`/api/logs/${id}`);
        this.historique = await historiqueRes.json();
        console.log('[ProjectDetail] Historique rechargé:', this.historique.length, 'entrées');

        // Recharger la fiche d'évaluation
        try {
          console.log('[ProjectDetail] Rechargement fiche d\'évaluation...');
          const ficheRes = await fetch(`/api/projects/${id}/fiche-evaluation`);
          console.log('[ProjectDetail] Statut réponse fiche:', ficheRes.status);

          if (ficheRes.ok) {
            const ficheData = await ficheRes.json();
            this.ficheEvaluation = ficheData;
            console.log('[ProjectDetail] Fiche rechargée avec succès!');
            console.log('[ProjectDetail] Score total:', ficheData.score_total);
            console.log('[ProjectDetail] Recommandations:', ficheData.recommandations);
            console.log('[ProjectDetail] Proposition:', ficheData.proposition);
          } else if (ficheRes.status === 404) {
            console.log('[ProjectDetail] Aucune fiche trouvée (404)');
            this.ficheEvaluation = null;
          }
        } catch (ficheErr) {
          console.error('[ProjectDetail] Erreur rechargement fiche:', ficheErr);
          this.ficheEvaluation = null;
        }
      } catch (err) {
        console.error('[ProjectDetail] Erreur rechargement données:', err);
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return "";
      return new Date(dateStr).toLocaleDateString("fr-FR", {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    formatDateTime(dateStr) {
      if (!dateStr) return "";
      return new Date(dateStr).toLocaleString("fr-FR", {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    getRoleLabel(role) {
      const labels = {
        'evaluateur1': 'Évaluateur 1',
        'evaluateur2': 'Évaluateur 2',
        'secretariatsct': 'Secrétariat SCT',
        'presidencesct': 'Présidence SCT',
        'presidencecomite': 'Présidence Comité'
      };
      return labels[role] || role;
    },
    isSoumissionnaire() {
      // Vérification via paramètre URL (le plus fiable)
      if (this.$route.query.from === 'soumissionnaire') {
        return true;
      }

      // Vérification via rôle utilisateur
      if (!this.currentUser) return false;

      const isRoleSoumissionnaire = this.currentUser.role === 'soumissionnaire';
      const isSoumissionnaireByName = this.currentUser.username === 'soumissionnaire';

      return isRoleSoumissionnaire || isSoumissionnaireByName;
    },
    peutVoirEvaluation() {
      // L'évaluation est visible seulement si:
      // 1. L'utilisateur est admin (voit tout sans intervenir)
      // 2. L'utilisateur est évaluateur OU secrétariat SCT (ils voient toujours)
      // 3. OU le secrétariat a validé l'évaluation (pour présidence SCT et comité)
      if (!this.currentUser || !this.project) return false;

      const role = this.currentUser.role;

      // Admin peut tout voir (sans intervenir)
      if (role === 'admin') {
        return true;
      }

      // Évaluateurs et secrétariat peuvent toujours voir
      if (role === 'evaluateur' || role === 'secretariatsct') {
        return true;
      }

      // Pour présidence SCT et comité, vérifier la validation du secrétariat
      if (role === 'presidencesct' || role === 'presidencecomite') {
        return this.project.validation_secretariat === 'valide';
      }

      return false;
    },
    soumissionnairePeutVoirFiche() {
      // Le soumissionnaire peut voir la fiche d'évaluation dans deux cas:
      // 1. Avis favorable confirmé par PresidenceComite (decision_finale = 'confirme' + avis favorable)
      //    MAIS PAS si le projet est en attente de décision du Comité (statut_comite = 'recommande_comite')
      // 2. Projet entériné par le Comité (statut_comite = 'approuve_definitif')
      if (!this.project) return false;

      // Si le projet est recommandé au Comité mais pas encore décidé, NE PAS afficher la fiche
      if (this.project.statut_comite === 'recommande_comite') {
        return false;
      }

      // Cas 1: Avis favorable confirmé par PresidenceComite
      const avisFavorableConfirme =
        this.project.decision_finale === 'confirme' &&
        (this.project.avis === 'favorable' || this.project.avis === 'favorable sous conditions');

      // Cas 2: Projet entériné par le Comité
      const enterineParComite =
        this.project.statut_comite === 'approuve_definitif';

      return avisFavorableConfirme || enterineParComite;
    },
    formatCurrency(amount) {
      return new Intl.NumberFormat('fr-FR').format(amount);
    },
    formatTypeFinancement(typeFinancementJSON) {
      if (!typeFinancementJSON) return '';
      try {
        const types = JSON.parse(typeFinancementJSON);
        if (Array.isArray(types) && types.length > 0) {
          return types.join(', ');
        }
      } catch (e) {
        console.error('Erreur parsing type_financement:', e);
      }
      return 'Non spécifié';
    },
    formatLieuSoumission() {
      if (!this.project) return '';
      const parts = [];
      if (this.project.lieu_soumission_ville) parts.push(this.project.lieu_soumission_ville);
      if (this.project.lieu_soumission_region && this.project.lieu_soumission_region !== this.project.lieu_soumission_ville) {
        parts.push(this.project.lieu_soumission_region);
      }
      if (this.project.lieu_soumission_pays) parts.push(this.project.lieu_soumission_pays);
      return parts.join(', ') || 'Non disponible';
    },
    getStatusClass(statut) {
      const map = {
        "soumis": "status-new",
        "assigné": "status-assigned",
        "en instruction": "status-processing",
        "en évaluation": "status-processing",
        "évalué": "status-evaluated",
        "compléments demandés": "status-complement",
        "compléments fournis": "status-info",
        "en attente validation presidencesct": "status-pending",
        "validé par presidencesct": "status-validated-sec",
        "validé par presidencecomite": "status-validated",
        "favorable": "status-favorable",
        "favorable sous conditions": "status-conditions",
        "défavorable": "status-defavorable",
        "approuvé définitivement par le Comité": "status-validated",
        "rejeté": "status-defavorable",
        "avis défavorable confirmé": "status-defavorable",
        "en réexamen par le Secrétariat SCT": "status-processing"
      };
      return map[statut] || "status-default";
    },
    getAvisClass(avis) {
      const map = {
        "favorable": "avis-favorable",
        "favorable sous conditions": "avis-conditions",
        "défavorable": "avis-defavorable",
        "compléments demandés": "avis-complement"
      };
      return map[avis] || "";
    },

    getStatusBadgeText() {
      // Si soumissionnaire et projet en attente de décision du Comité
      if (this.isSoumissionnaire() && this.project.statut_comite === 'recommande_comite') {
        return "En attente Comité";
      }

      // Masquer certains statuts intermédiaires pour le soumissionnaire
      if (this.isSoumissionnaire()) {
        const statutsMasques = [
          'validé par presidencecomite',
          'en attente validation presidencesct',
          'validé par presidencesct'
        ];

        if (statutsMasques.includes(this.project.statut)) {
          return "En cours de traitement";
        }
      }

      // Sinon afficher le statut normal
      return this.project.statut;
    },

    getStatusBadgeClass() {
      // Si soumissionnaire et projet en attente de décision du Comité
      if (this.isSoumissionnaire() && this.project.statut_comite === 'recommande_comite') {
        return "status-pending-comite";
      }

      // Si statut masqué pour soumissionnaire
      if (this.isSoumissionnaire()) {
        const statutsMasques = [
          'validé par presidencecomite',
          'en attente validation presidencesct',
          'validé par presidencesct'
        ];

        if (statutsMasques.includes(this.project.statut)) {
          return "status-processing";
        }
      }

      // Sinon utiliser la classe normale
      return this.getStatusClass(this.project.statut);
    },

    parseComplementsFiles(filesString) {
      if (!filesString) return [];
      return filesString.split(',').map(f => f.trim()).filter(f => f.length > 0);
    },
    
    ouvrirFichier(fileName) {
      // Construire l'URL complète pour le fichier
      // En production sur Render, utiliser l'URL backend, sinon utiliser l'origine actuelle
      const isProduction = window.location.hostname.includes('render.com')
      const backendUrl = isProduction ? 'https://maturation-backend.onrender.com' : window.location.origin
      const fileUrl = `${backendUrl}/api/uploads/${fileName}`
      window.open(fileUrl, '_blank')
    },

    ouvrirFichePDF() {
      if (!this.peutAccederFicheEvaluation()) {
        alert('L\'évaluation de la recevabilité doit être positive avant d\'accéder à la fiche d\'évaluation détaillée');
        return;
      }
      // Utiliser l'URL du backend (configurée via VITE_API_URL en production)
      const API_BASE_URL = import.meta.env.VITE_API_URL || '';
      window.open(`${API_BASE_URL}/api/projects/${this.project.id}/fiche-evaluation/pdf`, '_blank');
    },

    peutAccederFicheEvaluation() {
      // Peut accéder si:
      // 1. Pas d'évaluation de la recevabilité requise (ancien système)
      // 2. OU évaluation de la recevabilité positive (dossier évaluable)
      // 3. OU statut >= "en évaluation" (déjà passé l'étape préalable)
      if (!this.project) return false;

      const statutsApres = ['en évaluation', 'évalué', 'validé par presidencesct', 'approuvé', 'rejeté'];

      return !this.project.evaluation_prealable ||
             this.project.evaluation_prealable === 'dossier_evaluable' ||
             statutsApres.includes(this.project.statut);
    },

    getPropositionClass(proposition) {
      const map = {
        "favorable": "proposition-favorable",
        "favorable sous conditions": "proposition-reserve",
        "défavorable": "proposition-defavorable"
      };
      return map[proposition] || "";
    },

    getCriteresConfig() {
      return {
        'pertinence': { label: 'PERTINENCE', max: 5 },
        'alignement': { label: 'ALIGNEMENT À LA DOCTRINE DE TRANSFORMATION SYSTÉMIQUE', max: 10 },
        'activites_couts': { label: 'PERTINENCE DES ACTIVITÉS ET BIEN FONDÉ DES COÛTS/PART DE FONCTIONNEMENT', max: 15 },
        'equite': { label: 'ÉQUITÉ (SOCIALE-TERRITORIALE-GENRE)', max: 15 },
        'viabilite': { label: 'VIABILITÉ/RENTABILITÉ FINANCIÈRE', max: 5 },
        'rentabilite': { label: 'RENTABILITÉ SOCIO-ÉCONOMIQUE (ACA/MPR)', max: 5 },
        'benefices_strategiques': { label: 'BÉNÉFICES STRATÉGIQUES', max: 10 },
        'perennite': { label: 'PÉRENNITÉ ET DURABILITÉ DES EFFETS ET IMPACTS DU PROJET', max: 5 },
        'avantages_intangibles': { label: 'AVANTAGES ET COÛTS INTANGIBLES', max: 10 },
        'faisabilite': { label: 'FAISABILITÉ DU PROJET / RISQUES POTENTIELS', max: 5 },
        'ppp': { label: 'POTENTIALITÉ OU OPPORTUNITÉ DU PROJET À ÊTRE RÉALISÉ EN PPP', max: 5 },
        'impact_environnemental': { label: 'IMPACTS ENVIRONNEMENTAUX', max: 5 }
      };
    },

    formatRaisonArchivage(raison) {
      const raisons = {
        'assignation_initiale': 'Assignation initiale',
        'reassignation_avant_hierarchie': 'Réassignation avant hiérarchie',
        'reassignation_par_secretariat': 'Réassignation par secrétariat',
        'reassignation_apres_rejet_presidencesct': 'Réassignation après rejet Présidence SCT',
        'reassignation_apres_rejet_comite': 'Réassignation après rejet Comité',
        'reevaluation_apres_complements': 'Réévaluation après compléments',
        'suppression_manuelle': 'Suppression manuelle'
      };
      return raisons[raison] || raison;
    },

    formatFileSize(bytes) {
      if (!bytes) return 'N/A';
      const kb = bytes / 1024;
      if (kb < 1024) {
        return `${kb.toFixed(1)} Ko`;
      }
      const mb = kb / 1024;
      return `${mb.toFixed(2)} Mo`;
    },

    // Méthodes pour les pièces jointes du projet
    isPDF(fileName) {
      if (!fileName) return false;
      return fileName.toLowerCase().endsWith('.pdf');
    },

    getFileName(filePath) {
      if (!filePath) return '';
      // Extraire le nom du fichier du chemin complet
      const parts = filePath.split('/');
      const fileName = parts[parts.length - 1];
      // Si le nom est trop long, le tronquer
      if (fileName.length > 40) {
        const ext = this.getFileExtension(fileName);
        return fileName.substring(0, 35) + '...' + ext;
      }
      return fileName;
    },

    getFileExtension(fileName) {
      if (!fileName) return '';
      const parts = fileName.split('.');
      return parts.length > 1 ? '.' + parts[parts.length - 1] : '';
    },

    ouvrirArchive(filename) {
      // Ouvrir l'archive dans un nouvel onglet
      const isProduction = window.location.hostname.includes('render.com');
      const backendUrl = isProduction
        ? 'https://maturation-backend.onrender.com'
        : '';
      const url = `${backendUrl}/api/archives/fiches_evaluation/${filename}`;
      window.open(url, '_blank');
    },

    async supprimerArchive(filename) {
      if (!confirm(`Êtes-vous sûr de vouloir supprimer cette archive ?\n\nFichier : ${filename}\n\nCette action est irréversible.`)) {
        return;
      }

      try {
        const response = await fetch(`/api/projects/${this.project.id}/fiches-archives/${filename}`, {
          method: 'DELETE',
          headers: {
            'X-Role': this.currentUser.role,
            'X-Username': this.currentUser.username
          }
        });

        if (response.ok) {
          alert('Archive supprimée avec succès');
          // Recharger la liste des archives
          const archivesRes = await fetch(`/api/projects/${this.project.id}/fiches-archives`, {
            headers: {
              'X-Role': this.currentUser.role,
              'X-Username': this.currentUser.username
            }
          });
          if (archivesRes.ok) {
            const data = await archivesRes.json();
            this.archives = data.archives || [];
          }
        } else {
          const error = await response.json();
          alert(`Erreur lors de la suppression : ${error.error || 'Erreur inconnue'}`);
        }
      } catch (err) {
        console.error('Erreur suppression archive:', err);
        alert('Erreur lors de la suppression de l\'archive');
      }
    }
  }
};
</script>

<style scoped>
.project-detail-container {
  padding: 1rem;
  max-width: 1000px;
  margin: 0 auto;
}
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}
.btn-back {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}
.btn-back:hover {
  background: #4b5563;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #229954 0%, #27ae60 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(39, 174, 96, 0.4);
}
.badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
}
.status-new { background: #3b82f6 !important; color: white !important; }
.status-assigned { background: #f59e0b !important; color: white !important; }
.status-pending { background: #8b5cf6 !important; color: white !important; }
.status-validated { background: #10b981 !important; color: white !important; }
.status-validated-sec { background: #22c55e !important; color: white !important; }
.status-complement { background: #f97316 !important; color: white !important; }
.status-info { background: #3b82f6 !important; color: white !important; }
.status-confirmed { background: #06b6d4 !important; color: white !important; }
.status-favorable { background: #10b981 !important; color: white !important; }
.status-conditions { background: #f59e0b !important; color: white !important; }
.status-defavorable { background: #ef4444 !important; color: white !important; }
.status-rejected { background: #dc2626 !important; color: white !important; }
.status-evaluated { background: #8b5cf6 !important; color: white !important; }
.status-default { background: #6b7280 !important; color: white !important; }

/* Badges personnalisés pour soumissionnaires */
.status-pending-comite { background: #f59e0b !important; color: white !important; }
.status-processing { background: #0ea5e9 !important; color: white !important; }

/* Nouveaux badges pour caractéristiques du projet (Décembre 2025) */
.badge-initial {
  background: #e0f2fe !important;
  color: #075985 !important;
  padding: 0.4rem 0.8rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
}
.badge-phase2 {
  background: #ddd6fe !important;
  color: #5b21b6 !important;
  padding: 0.4rem 0.8rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
}
.badge-prioritaire {
  background: #fef3c7 !important;
  color: #92400e !important;
  padding: 0.4rem 0.8rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
}
.badge-standard {
  background: #f3f4f6 !important;
  color: #374151 !important;
  padding: 0.4rem 0.8rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
}

.detail-content h1 {
  color: #1a4d7a;
  font-size: 2rem;
  margin-bottom: 2rem;
}
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.info-card h3 {
  color: #1e3a8a;
  font-size: 1.2rem;
  margin: 0 0 1rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #e0f2fe;
}
.info-message {
  padding: 1rem;
  background: #d1fae5;
  border-left: 4px solid #10b981;
  border-radius: 6px;
  color: #065f46;
  font-weight: 500;
  margin-bottom: 1rem;
}

/* Status box pour "En attente décision Comité" */
.status-box {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 12px;
  margin: 1rem 0;
}

.status-pending-comite {
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border: 2px solid #f97316;
}

.status-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.status-content h4 {
  color: #c2410c;
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0 0 0.75rem 0;
}

.status-content p {
  color: #7c2d12;
  line-height: 1.6;
  margin: 0.5rem 0;
}

.status-content p:last-child {
  margin-bottom: 0;
}

.info-row {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f3f4f6;
}
.info-row:last-child {
  border-bottom: none;
}
.label {
  font-weight: 600;
  color: #374151;
}
.value {
  color: #1f2937;
}

/* Styles pour la hiérarchie de l'organisme de tutelle */
.organisme-hierarchie {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px solid #0ea5e9;
  border-radius: 12px;
  padding: 1rem;
  margin: 0.75rem 0;
}

.hierarchie-title {
  font-weight: 700;
  color: #0c4a6e;
  font-size: 1rem;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hierarchie-item {
  display: grid;
  grid-template-columns: 180px 1fr;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #bae6fd;
}

.hierarchie-item:last-child {
  border-bottom: none;
}

.hierarchie-label {
  font-weight: 600;
  color: #0369a1;
  font-size: 0.9rem;
}

.hierarchie-value {
  color: #0c4a6e;
  font-weight: 500;
}

.description {
  color: #374151;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}

/* Styles pour les pièces jointes du projet */
.info-text-small {
  color: #6b7280;
  font-size: 0.85rem;
  margin-bottom: 1rem;
  font-style: italic;
}

.files-list-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.file-item:hover {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.file-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.file-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.95rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-type {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.file-action {
  flex-shrink: 0;
  color: #94a3b8;
  transition: color 0.2s;
}

.file-item:hover .file-action {
  color: #3b82f6;
}

.avis-favorable { color: #10b981 !important; font-weight: 600 !important; }
.avis-conditions { color: #f59e0b !important; font-weight: 600 !important; }
.avis-defavorable { color: #ef4444 !important; font-weight: 600 !important; }
.avis-complement { color: #f97316 !important; font-weight: 600 !important; }
.validated { color: #10b981; font-weight: 600; text-transform: capitalize; }
.files-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.file-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  color: #1e40af;
  text-decoration: none;
  transition: all 0.3s;
}
.file-link:hover {
  background: #dbeafe;
  transform: translateX(4px);
}
.file-link svg {
  flex-shrink: 0;
}
.loading {
  text-align: center;
  padding: 4rem;
  color: #6b7280;
  font-size: 1.2rem;
}

/* Styles pour l'historique */
.historique-timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-left: 4px solid #3b82f6;
  border-radius: 0 8px 8px 0;
  transition: background-color 0.2s;
}

.timeline-item:hover {
  background: #f1f5f9;
}

.timeline-date {
  font-size: 0.9rem;
  color: #64748b;
  font-weight: 600;
  white-space: nowrap;
  min-width: 140px;
}

.timeline-content {
  flex: 1;
}

.timeline-action {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.timeline-author {
  font-size: 0.9rem;
  color: #64748b;
  font-style: italic;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}

/* Styles pour les compléments */
.complement-section {
  margin-bottom: 1.5rem;
}

.complement-section h4 {
  color: #1e40af;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

.complement-message {
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid;
  margin-bottom: 0.5rem;
}

.complement-message.demande {
  background: #fef3c7;
  border-color: #f59e0b;
  color: #92400e;
}

.complement-message.reponse {
  background: #dbeafe;
  border-color: #3b82f6;
  color: #1e40af;
}

.complement-files {
  font-size: 0.9rem;
  color: #64748b;
  margin-top: 0.5rem;
}

.files-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.file-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  color: #3b82f6;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.file-link:hover {
  background: #e2e8f0;
  border-color: #3b82f6;
  color: #1d4ed8;
  transform: translateY(-1px);
}

.file-link svg {
  flex-shrink: 0;
  color: #6b7280;
}

.file-link:hover svg {
  color: #3b82f6;
}

.pdf-link {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  font-weight: 600;
  padding: 0.75rem 1rem;
}

.pdf-link:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.pdf-link svg {
  color: white;
}

.pdf-link:hover svg {
  color: white;
}

/* Évaluation préalable */
.evaluation-prealable-description {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  font-style: italic;
}

.evaluation-prealable-form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 0.9rem;
  resize: vertical;
  margin-bottom: 1rem;
}

.evaluation-prealable-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-start;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-warning {
  background: #f59e0b;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.evaluation-prealable-resultat {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #10b981;
}

.decision-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.decision-badge.success {
  background: #d1fae5;
  color: #065f46;
}

.decision-badge.warning {
  background: #fef3c7;
  color: #92400e;
}

.decision-badge.danger {
  background: #fee2e2;
  color: #991b1b;
}

.evaluation-prealable-resultat .commentaire {
  margin: 0.75rem 0;
  color: #475569;
  font-size: 0.9rem;
}

.evaluation-prealable-resultat .date-evaluation {
  margin: 0;
  color: #94a3b8;
  font-size: 0.85rem;
  font-style: italic;
}

.pdf-link.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  pointer-events: none;
}

.disabled-hint {
  display: block;
  font-size: 0.75rem;
  color: #f59e0b;
  margin-top: 0.25rem;
}

/* Fiche evaluation display styles */
.fiche-summary {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.score-total-box, .avis-global-box {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  padding: 1.5rem;
  border-radius: 12px;
  border: 2px solid #3b82f6;
  text-align: center;
}

.score-label, .avis-label {
  font-size: 0.875rem;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.score-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #1e40af;
  margin-bottom: 0.5rem;
}

.appreciation {
  font-size: 0.95rem;
  color: #475569;
  font-weight: 500;
}

.avis-value {
  font-size: 1.3rem;
  font-weight: 700;
  padding: 0.75rem;
  border-radius: 8px;
  margin-top: 0.5rem;
  text-transform: uppercase;
}

.proposition-favorable {
  background: #d1fae5;
  color: #065f46;
}

.proposition-reserve {
  background: #fef3c7;
  color: #92400e;
}

.proposition-defavorable {
  background: #fee2e2;
  color: #991b1b;
}

.recommandations-section {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.recommandations-section h4 {
  color: #92400e;
  font-size: 1.1rem;
  margin: 0 0 1rem 0;
  font-weight: 600;
}

.recommandations-content {
  color: #78350f;
  line-height: 1.6;
  white-space: pre-wrap;
  font-size: 0.95rem;
}

.criteres-detail {
  margin-top: 2rem;
}

.criteres-detail h4 {
  color: #1e40af;
  font-size: 1.1rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.criteres-list-detail {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.critere-detail-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s;
}

.critere-detail-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.critere-header-detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.critere-label-detail {
  font-weight: 600;
  color: #1e293b;
  font-size: 0.9rem;
}

.critere-score-detail {
  background: #3b82f6;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.875rem;
}

.critere-description {
  color: #475569;
  font-size: 0.875rem;
  line-height: 1.5;
  padding-top: 0.5rem;
  border-top: 1px solid #e2e8f0;
  white-space: pre-wrap;
}

.resubmission-motivation-detail {
  background: #eff6ff;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.resubmission-motivation-detail p {
  margin: 0;
  color: #1e40af;
  font-style: italic;
  line-height: 1.6;
}

/* Styles pour la section Archives */
.archives-section {
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-left: 4px solid #6366f1;
}

.archives-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.archive-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.archive-item:hover {
  border-color: #6366f1;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.archive-info {
  flex: 1;
}

.archive-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.archive-version {
  font-weight: 700;
  color: #6366f1;
  font-size: 1.1rem;
}

.archive-date {
  color: #6b7280;
  font-size: 0.9rem;
}

.archive-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.archive-detail-row {
  display: flex;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.archive-detail-row .label {
  font-weight: 600;
  color: #374151;
  min-width: 100px;
}

.archive-detail-row .value {
  color: #1f2937;
}

.archive-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-view, .btn-delete {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-view {
  background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  color: white;
}

.btn-view:hover {
  background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-delete {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.btn-delete:hover {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

@media (max-width: 1024px) {
  .project-detail-container {
    padding: var(--dgppe-spacing-4);
  }

  .info-card {
    padding: var(--dgppe-spacing-5);
  }

  .project-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--dgppe-spacing-4);
  }

  .project-actions {
    width: 100%;
    flex-direction: column;
  }

  .project-actions .btn {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .project-detail-container {
    padding: var(--dgppe-spacing-3);
  }

  .info-card {
    padding: var(--dgppe-spacing-4);
  }

  .info-card h3 {
    font-size: 1.125rem;
  }

  .info-row {
    grid-template-columns: 1fr;
    gap: 0.25rem;
  }

  .info-label {
    font-weight: 600;
    margin-bottom: var(--dgppe-spacing-1);
  }

  .evaluation-prealable-buttons {
    flex-direction: column;
  }

  .evaluation-prealable-buttons .btn {
    width: 100%;
  }

  .fiche-summary {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .score-value {
    font-size: 2rem;
  }

  .archive-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .archive-actions {
    width: 100%;
    flex-direction: column;
  }

  .btn-download, .btn-delete {
    width: 100%;
  }

  .status-badge {
    font-size: 0.813rem;
    padding: var(--dgppe-spacing-1) var(--dgppe-spacing-2);
  }

  .historique-table {
    font-size: 0.813rem;
  }

  .historique-table th,
  .historique-table td {
    padding: var(--dgppe-spacing-2);
  }
}

@media (max-width: 480px) {
  .project-detail-container {
    padding: var(--dgppe-spacing-2);
  }

  .info-card {
    padding: var(--dgppe-spacing-3);
  }

  .info-card h3 {
    font-size: 1rem;
  }

  .status-badge {
    font-size: 0.75rem;
  }

  .btn-primary,
  .btn-secondary {
    font-size: 0.813rem;
    padding: var(--dgppe-spacing-2) var(--dgppe-spacing-3);
  }

  .archive-detail-row {
    flex-direction: column;
    gap: 0;
  }

  .archive-detail-row .label {
    min-width: auto;
    margin-bottom: var(--dgppe-spacing-1);
  }
}

/* Bannière d'avertissement pour compte non vérifié */
.warning-banner {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border: 2px solid #fbbf24;
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
  box-shadow: 0 4px 12px rgba(251, 191, 36, 0.2);
}

.warning-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.warning-content {
  flex: 1;
}

.warning-content h3 {
  margin: 0 0 8px 0;
  color: #78350f;
  font-size: 18px;
  font-weight: 700;
}

.warning-content p {
  margin: 0;
  color: #92400e;
  font-size: 14px;
  line-height: 1.6;
}
</style>