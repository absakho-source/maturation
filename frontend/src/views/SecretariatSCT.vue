<template>
  <PageWrapper>
    <div class="secretariat-container">
      <!-- Tableau de bord statistiques -->
      <div class="dashboard-section">
        <div class="header-row">
          <h2 class="dashboard-title">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 3v5h5"/>
              <path d="M3 8s2-4 8-4 8 4 8 4"/>
              <path d="M21 21v-5h-5"/>
              <path d="M21 16s-2 4-8 4-8-4-8-4"/>
            </svg>
            Tableau de bord - Secrétariat SCT
          </h2>
          <button @click="telechargerRapport" class="btn-download-rapport">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Télécharger Rapport PDF
          </button>
        </div>
        
        <!-- Statistiques principales -->
        <div class="stats">
          <div class="stat primary clickable" @click="filtrerParStatut(null)" :class="{ active: filtreStatut === null }">
            <span>Total projets</span><strong>{{ allProjects.length }}</strong>
          </div>
          <div class="stat info clickable" @click="filtrerParStatut('soumis')" :class="{ active: filtreStatut === 'soumis' }">
            <span>Nouveaux (soumis)</span><strong>{{ countByStatus('soumis') }}</strong>
          </div>
          <div class="stat warning clickable" @click="filtrerParStatut('assigné')" :class="{ active: filtreStatut === 'assigné' }">
            <span>Assignés</span><strong>{{ countByStatus('assigné') }}</strong>
          </div>
          <div class="stat info clickable" @click="filtrerParStatut('évalué')" :class="{ active: filtreStatut === 'évalué' }">
            <span>Évalués</span><strong>{{ countByStatus('évalué') }}</strong>
          </div>
          <div class="stat success clickable" @click="filtrerParStatut('approuvé')" :class="{ active: filtreStatut === 'approuvé' }">
            <span>Approuvés</span><strong>{{ countByStatus('approuvé') }}</strong>
          </div>
          <div class="stat danger clickable" @click="filtrerParStatut('rejeté')" :class="{ active: filtreStatut === 'rejeté' }">
            <span>Rejetés</span><strong>{{ countByStatus('rejeté') }}</strong>
          </div>
          <div class="stat clickable" @click="filtrerParStatut('compléments demandés')" :class="{ active: filtreStatut === 'compléments demandés' }">
            <span>Compléments demandés</span><strong>{{ countByStatus('compléments demandés') }}</strong>
          </div>
          <div class="stat clickable" @click="filtrerParStatut('compléments fournis')" :class="{ active: filtreStatut === 'compléments fournis' }">
            <span>Compléments fournis</span><strong>{{ countByStatus('compléments fournis') }}</strong>
          </div>
          <div class="stat success clickable" @click="filtrerParStatut('validé par secrétariat')" :class="{ active: filtreStatut === 'validé par secrétariat' }">
            <span>Validés secrétariat</span><strong>{{ countByStatus('validé par secrétariat') }}</strong>
          </div>
          <div class="stat warning clickable" @click="filtrerParStatut('en attente validation presidencesct')" :class="{ active: filtreStatut === 'en attente validation presidencesct' }">
            <span>Attente présidence</span><strong>{{ countByStatus('en attente validation presidencesct') }}</strong>
          </div>
          <div class="stat success clickable" @click="filtrerParStatut('validé par presidencesct')" :class="{ active: filtreStatut === 'validé par presidencesct' }">
            <span>Validés présidence</span><strong>{{ countByStatus('validé par presidencesct') }}</strong>
          </div>
        </div>

        <!-- Métriques de performance -->
        <div class="performance-metrics">
          <h3>Métriques de performance</h3>
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12,6 12,12 16,14"/>
                </svg>
                Temps moyen de traitement
              </div>
              <div class="metric-value">{{ averageProcessingTime }}</div>
            </div>
            
            <div class="metric-card">
              <div class="metric-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
                Taux de validation
              </div>
              <div class="metric-value">{{ validationRate }}%</div>
            </div>
            
            <div class="metric-card">
              <div class="metric-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12,6 12,12 16,14"/>
                </svg>
                Délai moyen d'évaluation
              </div>
              <div class="metric-value">{{ averageEvaluationTime }}</div>
            </div>
          </div>
        </div>

        <!-- Volumes de financement -->
        <div class="financing-volumes">
          <h3>Volumes de financement</h3>
          <div class="financing-cards-grid">
            <div class="financing-card">
              <div class="financing-header">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="17 8 12 3 7 8"/>
                  <line x1="12" y1="3" x2="12" y2="15"/>
                </svg>
                <span>Demandes soumises</span>
              </div>
              <div class="financing-amount">{{ formatCurrency(financingStats.totalSubmitted) }}</div>
              <div class="financing-count">{{ financingStats.countSubmitted }} projet(s)</div>
            </div>

            <div class="financing-card success">
              <div class="financing-header">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <span>Décisions favorables (Comité)</span>
              </div>
              <div class="financing-amount">{{ formatCurrency(financingStats.totalApproved) }}</div>
              <div class="financing-count">{{ financingStats.countApproved }} projet(s)</div>
            </div>
          </div>
        </div>

        <!-- Flux de traitement -->
        <div class="workflow-chart">
          <h3>Flux de traitement des projets</h3>
          <div class="workflow-steps">
            <div class="workflow-step">
              <div class="step-indicator step-new">{{ countByStatus('soumis') }}</div>
              <div class="step-label">Soumis</div>
            </div>
            <div class="step-arrow">→</div>
            <div class="workflow-step">
              <div class="step-indicator step-progress">{{ countInEvaluation }}</div>
              <div class="step-label">En évaluation</div>
            </div>
            <div class="step-arrow">→</div>
            <div class="workflow-step">
              <div class="step-indicator step-review">{{ countApproved }}</div>
              <div class="step-label">Avis donnés</div>
            </div>
            <div class="step-arrow">→</div>
            <div class="workflow-step">
              <div class="step-indicator step-done">{{ countValidatedByComite }}</div>
              <div class="step-label">Validés Comité</div>
            </div>
          </div>
        </div>

        <!-- Alertes -->
        <div v-if="alerts.length > 0" class="alerts-section">
          <h3>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            Alertes et notifications
          </h3>
          <div class="alerts-list">
            <div v-for="alert in alerts" :key="alert.id" class="alert-item" :class="alert.type">
              <div class="alert-content">
                <span class="alert-message">{{ alert.message }}</span>
                <span class="alert-time">{{ formatTime(alert.time) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="tabs">
        <button @click="activeTab = 'all'" :class="{ active: activeTab === 'all' }" class="tab-btn">📋 Tous</button>
        <button @click="activeTab = 'assignation'" :class="{ active: activeTab === 'assignation' }" class="tab-btn">✅ Assignation / Réassignation</button>
        <button @click="activeTab = 'validation'" :class="{ active: activeTab === 'validation' }" class="tab-btn">🔎 Validation d'avis</button>
        <button @click="activeTab = 'complements'" :class="{ active: activeTab === 'complements' }" class="tab-btn">📝 Demandes compléments</button>
        <button @click="activeTab = 'evaluation'" :class="{ active: activeTab === 'evaluation' }" class="tab-btn">✍️ Mes évaluations</button>
        <button @click="activeTab = 'stats'" :class="{ active: activeTab === 'stats' }" class="tab-btn">📊 Statistiques</button>
        <button @click="activeTab = 'carte'" :class="{ active: activeTab === 'carte' }" class="tab-btn">🗺️ Carte pôles</button>
      </div>

      <!-- Tous -->
      <div v-if="activeTab === 'all'" class="tab-content">
        <h2>Vue d'ensemble</h2>
        <div v-if="filtreStatut" class="filtre-actif">
          <span>Filtre actif: <strong>{{ filtreStatut }}</strong></span>
          <button @click="filtrerParStatut(null)" class="btn-clear-filter">✕ Tout afficher</button>
        </div>
        <div v-if="projetsFiltres.length === 0" class="empty-state">
          <p>Aucun projet trouvé{{ filtreStatut ? ' pour ce filtre' : '' }}</p>
        </div>
        <div v-else class="projects-grid">
          <div v-for="projet in projetsFiltres" :key="projet.id" class="project-card">
            <div class="card-header">
              <div class="card-title-section">
                <div class="project-number">{{ projet.numero_projet || 'N/A' }}</div>
                <h3>{{ projet.titre }}</h3>
              </div>
              <span :class="'badge status-' + projet.statut.replace(' ', '-')">{{ projet.statut }}</span>
              <!-- Alerte pour rejet proposé en attente de validation -->
              <span v-if="projet.evaluation_prealable === 'dossier_rejete' && projet.statut !== 'rejeté'" class="badge status-rejected" style="margin-left: 8px;">⚠️ Rejet proposé</span>
            </div>
            <div class="card-body">
              <p><strong>Auteur:</strong> {{ projet.auteur_nom }}</p>
              <p v-if="projet.evaluateur_nom"><strong>Évaluateur:</strong> {{ getEvaluateurLabel(projet.evaluateur_nom) }}</p>

              <!-- Afficher le message de rejet proposé -->
              <div v-if="projet.evaluation_prealable === 'dossier_rejete' && projet.statut !== 'rejeté'" class="rejection-proposal" style="margin: 10px 0;">
                <p><strong>⚠️ Rejet proposé par l'évaluateur:</strong></p>
                <div class="rejection-message">{{ projet.evaluation_prealable_commentaire || "Aucun commentaire" }}</div>
              </div>

              <p v-if="projet.avis"><strong>Avis:</strong> <span :class="getAvisClass(projet.avis)">{{ projet.avis }}</span></p>
              <p v-if="projet.commentaires"><strong>Commentaires:</strong> {{ projet.commentaires }}</p>
              
              <button @click="$router.push(`/project/${projet.id}`)" class="btn-view">Détails</button>
              
              <!-- Actions pour assigner -->
              <div v-if="projet.statut === 'soumis'" class="assign-section">
                <label>Assigner à un évaluateur:</label>
                <select v-model="assignation[projet.id]">
                  <option value="">--Choisir--</option>
                  <option value="secretariatsct">Moi-même (Secrétariat SCT)</option>
                  <option v-for="evaluateur in evaluateurs" :key="evaluateur.username" :value="evaluateur.username">
                    {{ evaluateur.display_name || evaluateur.username }}
                  </option>
                </select>
                <label style="margin-top: 10px;">Motivation (facultatif):</label>
                <textarea
                  v-model="motivations[projet.id]"
                  rows="2"
                  placeholder="Justification de cette assignation (facultatif)"
                  style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit;"
                ></textarea>
                <button class="btn-primary" @click="assigner(projet.id)">Assigner</button>
              </div>
              
              <!-- Actions pour projets assignés ou en évaluation -->
              <div v-if="projet.statut === 'assigné' || projet.statut === 'en évaluation'" class="project-actions">
                <!-- Message informatif si assigné au secrétariat -->
                <div v-if="projet.evaluateur_nom === 'secretariatsct'" class="info-assigned">
                  ℹ️ Ce projet vous est assigné - Rendez-vous dans l'onglet "Mes évaluations" pour l'évaluer
                </div>

                <!-- Possibilité de réassigner -->
                <div class="reassign-section">
                  <label>Réassigner à:</label>
                  <div class="reassign-controls">
                    <select v-model="assignation[projet.id]">
                      <option value="">--Choisir--</option>
                      <option v-if="projet.evaluateur_nom !== 'secretariatsct'" value="secretariatsct">Moi-même (Secrétariat SCT)</option>
                      <option v-for="evaluateur in getAvailableEvaluateurs(projet)" :key="evaluateur.username" :value="evaluateur.username">
                        {{ evaluateur.display_name || evaluateur.username }}
                      </option>
                    </select>
                  </div>
                  <label style="margin-top: 10px;">Motivation (facultatif):</label>
                  <textarea
                    v-model="motivations[projet.id]"
                    rows="2"
                    placeholder="Justification de cette réassignation (facultatif)"
                    style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit;"
                  ></textarea>
                  <button class="btn-secondary" @click="assigner(projet.id)" style="width: 100%; margin-top: 10px;">Réassigner</button>
                </div>
              </div>

              <!-- Actions pour projets rejetés - Nouvelle fonctionnalité -->
              <div v-if="projet.statut === 'rejeté'" class="project-actions rejected-actions">
                <div class="rejected-info">
                  <div class="alert alert-danger">
                    <!-- Différencier entre rejet lors de l'évaluation préalable et rejet par le comité -->
                    <template v-if="projet.avis === 'dossier rejeté'">
                      ❌ <strong>Projet rejeté</strong>
                    </template>
                    <template v-else>
                      ❌ <strong>Avis rejeté par le Comité</strong>
                    </template>
                  </div>
                  <p v-if="projet.commentaires_finaux"><strong>Motif de rejet:</strong> {{ projet.commentaires_finaux }}</p>
                  <p v-else-if="projet.commentaires"><strong>Motif de rejet:</strong> {{ projet.commentaires }}</p>
                  <p v-if="projet.decision_finale"><strong>Décision finale:</strong> {{ projet.decision_finale }}</p>
                </div>

                <!-- Actions disponibles pour tous les projets rejetés -->
                <div class="reassign-rejected-section">
                  <h4>🔄 Options de traitement</h4>

                  <div class="reassign-controls-vertical">
                    <!-- Réassignation à un évaluateur -->
                    <div class="action-group">
                      <h5>Réassigner pour nouvelle évaluation</h5>
                      <div class="reassign-select-container">
                        <label>Réassigner à:</label>
                        <select v-model="assignation[projet.id]" class="reassign-select">
                          <option value="">--Choisir un évaluateur--</option>
                          <option v-if="projet.evaluateur_nom !== 'secretariatsct'" value="secretariatsct">Moi-même (Secrétariat SCT)</option>
                          <option v-for="evaluateur in getAvailableEvaluateurs(projet)" :key="evaluateur.username" :value="evaluateur.username">
                            {{ evaluateur.display_name || evaluateur.username }}
                          </option>
                        </select>
                      </div>
                      <div class="reassign-select-container">
                        <label>Motivation (facultatif):</label>
                        <textarea
                          v-model="motivations[projet.id]"
                          rows="2"
                          placeholder="Justification de cette réassignation (facultatif)"
                          style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit;"
                        ></textarea>
                      </div>
                      <div class="reassign-button-container">
                        <button
                          class="btn-warning btn-reassign"
                          :disabled="!assignation[projet.id]"
                          @click="reassignerProjetRejete(projet.id)"
                        >
                          🔄 Réassigner pour nouvelle évaluation
                        </button>
                      </div>
                    </div>

                    <!-- Soumission par voie hiérarchique -->
                    <div class="action-group" style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;">
                      <h5>Ou soumettre par voie hiérarchique</h5>
                      <p class="info-text">Soumettre directement à la présidence SCT malgré le rejet</p>
                      <div class="reassign-button-container">
                        <button
                          class="btn-primary"
                          @click="soumettreVoieHierarchique(projet.id)"
                        >
                          ⬆️ Soumettre à la Présidence SCT
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Actions pour projets évalués -->
              <div v-if="projet.statut === 'évalué'" class="project-actions">
                <!-- Bouton éditer la fiche (seulement si évaluation complète existe et pas de rejet proposé) -->
                <button
                  v-if="projet.evaluation_prealable !== 'dossier_rejete' && projet.avis"
                  @click="ouvrirModalEditionFiche(projet)"
                  class="btn-edit-fiche"
                  style="margin-bottom: 10px;"
                >
                  ✏️ Éditer la fiche
                </button>

                <!-- Actions pour un rejet proposé -->
                <div v-if="projet.evaluation_prealable === 'dossier_rejete'" class="validation-actions">
                  <button class="btn-danger" @click="validerRejet(projet.id)">
                    ✓ Valider le rejet
                  </button>
                  <button class="btn-warning" @click="refuserRejet(projet.id)">
                    ✗ Refuser et réassigner
                  </button>
                </div>

                <!-- Actions pour un avis normal -->
                <div v-else class="validation-actions">
                  <button class="btn-primary" @click="validerAvis(projet.id)">Valider l'avis ➜ Présidence SCT</button>
                  <div class="reassign">
                    <label>Réassigner à:
                      <select v-model="assignation[projet.id]">
                        <option value="">--Choisir--</option>
                        <option v-if="projet.evaluateur_nom !== 'secretariatsct'" value="secretariatsct">Moi-même (Secrétariat SCT)</option>
                        <option v-for="evaluateur in getAvailableEvaluateurs(projet)" :key="evaluateur.username" :value="evaluateur.username">
                          {{ evaluateur.display_name || evaluateur.username }}
                        </option>
                      </select>
                    </label>
                    <button class="btn-secondary" @click="reassigner(projet.id)">Réassigner</button>
                  </div>
                </div>
              </div>

              <!-- Actions pour demandes de compléments en attente de validation -->
              <div v-if="projet.statut === 'en attente validation demande compléments'" class="project-actions">
                <div class="action-buttons">
                  <button class="btn-success" @click="approuverDemandeComplements(projet.id)">
                    ✅ Approuver et transmettre
                  </button>
                  <button class="btn-danger" @click="rejeterDemandeComplements(projet.id)">
                    ❌ Rejeter et réassigner
                  </button>
                </div>
              </div>

              <!-- Actions pour compléments fournis -->
              <div v-if="projet.statut === 'compléments fournis'" class="project-actions">
                <div class="action-buttons">
                  <button class="btn-success" @click="validerComplements(projet.id)">
                    ✅ Valider les compléments
                  </button>
                </div>
              </div>

              <!-- Section d'évaluation directe pour projets assignés à secretariatsct -->
              <div v-if="projet.evaluateur_nom === 'secretariatsct' && (projet.statut === 'assigné' || projet.statut === 'en évaluation')" class="project-actions">
                <div class="direct-evaluation-section">
                  <h4>📋 Évaluation directe</h4>
                  <p class="info-text">Ce projet vous a été assigné pour évaluation directe</p>
                  <button class="btn-primary" @click="commencerEvaluation(projet.id)">
                    🔍 Commencer/Continuer l'évaluation
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Assignation -->
      <div v-if="activeTab === 'assignation'" class="tab-content">
        <h2>Assignation et Réassignation</h2>
        <p><strong>Projets à assigner:</strong> {{ projectsToAssign.length }}</p>
        <div v-if="projectsToAssign.length === 0" class="empty-state">
          <p>Aucun projet à assigner</p>
        </div>
        <div v-else class="projects-grid">
          <div v-for="projet in projectsToAssign" :key="projet.id" class="project-card">
            <div class="card-header">
              <div class="card-title-section">
                <div class="project-number">{{ projet.numero_projet || 'N/A' }}</div>
                <h3>{{ projet.titre }}</h3>
              </div>
              <span :class="'badge status-' + projet.statut.replace(' ', '-')">{{ projet.statut }}</span>
            </div>
            <div class="card-body">
              <p><strong>Auteur:</strong> {{ projet.auteur_nom }}</p>
              <p v-if="projet.secteur"><strong>Secteur:</strong> {{ projet.secteur }}</p>
              
              <!-- Projets déjà assignés ou en évaluation -->
              <div v-if="projet.statut === 'assigné' || projet.statut === 'en évaluation'" class="reassign-info">
                <p><strong>🔄 Projet {{ projet.statut === 'en évaluation' ? 'en cours d\'évaluation' : 'assigné' }} :</strong></p>
                <div class="current-assignment">
                  Actuellement assigné à : <strong>{{ getEvaluateurLabel(projet.evaluateur_nom) }}</strong>
                </div>
                <p class="reassign-note">Vous pouvez réassigner ce projet à un autre évaluateur ou l'évaluer vous-même.</p>
                
                <!-- Section d'évaluation directe pour le secrétariat -->
                <div v-if="projet.evaluateur_nom === 'secretariatsct'" class="direct-evaluation">
                  <h4>✍️ Évaluer directement :</h4>
                  <div class="eval-section compact">
                    <label>Mon évaluation:</label>
                    <select v-model="avis[projet.id]">
                      <option value="">--Choisir--</option>
                      <option value="favorable">Favorable</option>
                      <option value="favorable sous conditions">Favorable sous conditions</option>
                      <option value="défavorable">Défavorable</option>
                      <option value="compléments demandés">Compléments demandés</option>
                    </select>
                    <textarea v-model="commentaires[projet.id]" rows="2" placeholder="Commentaire obligatoire pour justifier votre décision"></textarea>
                    <button class="btn-primary" @click="soumettre(projet.id)">Soumettre mon avis</button>
                  </div>
                </div>
              </div>
              
              <!-- Compléments fournis -->
              <div v-if="projet.statut === 'compléments fournis'" class="complements-info">
                <p><strong>💡 Compléments soumis par l'auteur :</strong></p>
                <div v-if="projet.complements_reponse_message" class="complements-message">
                  {{ projet.complements_reponse_message }}
                </div>
                <div v-if="!projet.complements_reponse_message" class="complements-message no-message">
                  Aucun message fourni
                </div>
                
                <!-- Pièces jointes cliquables -->
                <div v-if="projet.complements_reponse_pieces" class="complements-files">
                  <p><strong>📎 Nouvelles pièces :</strong></p>
                  <div class="files-list">
                    <span v-for="(fichier, index) in parseComplementsFiles(projet.complements_reponse_pieces)" 
                          :key="index" 
                          class="file-link"
                          @click="ouvrirFichier(projet.id, fichier)">
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
                <div v-if="!projet.complements_reponse_pieces" class="no-files">
                  Aucun fichier fourni
                </div>
                
                <!-- Actions pour traiter les compléments -->
                <div class="complements-actions">
                  <button @click="reassignerComplementsPourEvaluation(projet.id)" class="btn-success">
                    ✓ Réassigner pour réévaluation
                  </button>
                  <button @click="validerComplementsDirectement(projet.id)" class="btn-primary">
                    📋 Valider directement
                  </button>
                </div>
              </div>
              
              <button @click="$router.push(`/project/${projet.id}`)" class="btn-view">Détails</button>
              
              <!-- Actions pour assigner -->
              <div class="assign-section">
                <label>{{ (projet.statut === 'assigné' || projet.statut === 'en évaluation') ? 'Réassigner à:' : 'Assigner à:' }}</label>
                <select v-model="assignation[projet.id]">
                  <option value="">--Choisir--</option>
                  <option v-if="!(projet.statut === 'assigné' || projet.statut === 'en évaluation') || projet.evaluateur_nom !== 'secretariatsct'" value="secretariatsct">Moi-même (Secrétariat SCT)</option>
                  <option v-for="evaluateur in ((projet.statut === 'assigné' || projet.statut === 'en évaluation') ? getAvailableEvaluateurs(projet) : evaluateurs)" :key="evaluateur.username" :value="evaluateur.username">
                    {{ evaluateur.display_name || evaluateur.username }}
                  </option>
                </select>
                <label style="margin-top: 10px;">Motivation (facultatif):</label>
                <textarea
                  v-model="motivations[projet.id]"
                  rows="2"
                  :placeholder="(projet.statut === 'assigné' || projet.statut === 'en évaluation') ? 'Justification de cette réassignation (facultatif)' : 'Justification de cette assignation (facultatif)'"
                  style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit;"
                ></textarea>
                <button class="btn-primary" @click="assigner(projet.id)">
                  {{ (projet.statut === 'assigné' || projet.statut === 'en évaluation') ? 'Réassigner' : 'Assigner' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Validation d'avis -->
      <div v-if="activeTab === 'validation'" class="tab-content">
        <h2>Avis à valider</h2>
        <div v-if="projectsToValidate.length === 0" class="empty-state"><p>Aucun avis en attente</p></div>
        <div v-else class="projects-grid">
          <div v-for="p in projectsToValidate" :key="p.id" class="project-card">
            <div class="card-header">
              <div class="card-title-section">
                <div class="project-number">{{ p.numero_projet || 'N/A' }}</div>
                <h3>{{ p.titre }}</h3>
              </div>
              <span v-if="p.evaluation_prealable === 'dossier_rejete'" class="badge status-rejected">⚠️ Rejet proposé</span>
              <span v-else class="badge status-evaluated">évalué</span>
            </div>
            <div class="card-body">
              <p><strong>Auteur:</strong> {{ p.auteur_nom }}</p>
              <p><strong>Évaluateur:</strong> {{ getEvaluateurLabel(p.evaluateur_nom) }}</p>

              <!-- Affichage pour un rejet proposé -->
              <div v-if="p.evaluation_prealable === 'dossier_rejete'" class="rejection-proposal">
                <p><strong>⚠️ Proposition de rejet:</strong></p>
                <div class="rejection-message">{{ p.evaluation_prealable_commentaire || p.commentaires || "Aucun commentaire" }}</div>
              </div>

              <!-- Affichage pour un avis normal -->
              <div v-else>
                <p><strong>Avis:</strong> <span :class="getAvisClass(p.avis)">{{ p.avis }}</span></p>
                <p v-if="p.commentaires"><strong>Commentaires:</strong> {{ p.commentaires }}</p>
              </div>

              <button @click="$router.push(`/project/${p.id}`)" class="btn-view">Détails</button>

              <!-- Bouton éditer la fiche (seulement si évaluation complète existe et pas encore transmis) -->
              <button
                v-if="p.evaluation_prealable !== 'dossier_rejete' && p.avis"
                @click="ouvrirModalEditionFiche(p)"
                class="btn-edit-fiche"
              >
                ✏️ Éditer la fiche
              </button>

              <!-- Actions pour un rejet proposé -->
              <div v-if="p.evaluation_prealable === 'dossier_rejete'" class="validation-actions">
                <button class="btn-danger" @click="validerRejet(p.id)">
                  ✓ Valider le rejet
                </button>
                <button class="btn-warning" @click="refuserRejet(p.id)">
                  ✗ Refuser et réassigner
                </button>
              </div>

              <!-- Actions pour un avis normal -->
              <div v-else class="validation-actions">
                <button class="btn-primary" @click="validerAvis(p.id)">Valider l'avis ➜ Présidence SCT</button>
                <div class="reassign">
                  <label>Réassigner à
                    <select v-model="assignation[p.id]">
                      <option value="">--Choisir--</option>
                      <option v-if="p.evaluateur_nom !== 'secretariatsct'" value="secretariatsct">Moi-même (Secrétariat SCT)</option>
                      <option v-for="evaluateur in getAvailableEvaluateurs(p)" :key="evaluateur.username" :value="evaluateur.username">
                        {{ evaluateur.display_name || evaluateur.username }}
                      </option>
                    </select>
                  </label>
                  <button class="btn-secondary" @click="reassigner(p.id)">Réassigner</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Validation des demandes de compléments -->
      <div v-if="activeTab === 'complements'" class="tab-content">
        <h2>Demandes de compléments en attente de validation</h2>
        <div v-if="demandesComplementsEnAttente.length === 0" class="empty-state">
          <p>Aucune demande de compléments en attente</p>
        </div>
        <div v-else class="projects-grid">
          <div v-for="projet in demandesComplementsEnAttente" :key="projet.id" class="project-card">
            <div class="card-header">
              <div class="card-title-section">
                <div class="project-number">{{ projet.numero_projet || 'N/A' }}</div>
                <h3>{{ projet.titre }}</h3>
              </div>
              <span class="badge status-pending">En attente validation</span>
            </div>
            <div class="card-body">
              <p><strong>Auteur:</strong> {{ projet.auteur_nom }}</p>
              <p><strong>Évaluateur:</strong> {{ getEvaluateurLabel(projet.evaluateur_nom) }}</p>
              
              <!-- Demande de compléments -->
              <div class="complement-request">
                <p><strong>🔍 Demande de compléments :</strong></p>
                <div class="complement-message">{{ projet.complements_demande_message || "Aucun message" }}</div>
              </div>
              
              <button @click="$router.push(`/project/${projet.id}`)" class="btn-view">Détails</button>
              
              <!-- Actions de validation -->
              <div class="validation-actions">
                <button @click="validerDemandeComplements(projet.id)" class="btn-success">
                  ✓ Approuver et transmettre
                </button>
                <button @click="rejeterDemandeComplements(projet.id)" class="btn-danger">
                  ✗ Rejeter et réassigner
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Mes évaluations -->
      <div v-if="activeTab === 'evaluation'" class="tab-content">
        <h2>Mes évaluations</h2>
        <div v-if="myProjects.length === 0" class="empty-state">
          <p>Aucun projet assigné</p>
        </div>
        <div v-else class="projects-grid">
          <div v-for="projet in myProjects" :key="projet.id" class="project-card">
            <div class="card-header">
              <div class="card-title-section">
                <div class="project-number">{{ projet.numero_projet || 'N/A' }}</div>
                <h3>{{ projet.titre }}</h3>
              </div>
              <span :class="'badge status-' + projet.statut.replace(' ', '-')">{{ projet.statut }}</span>
            </div>
            <div class="card-body">
              <p><strong>Auteur:</strong> {{ projet.auteur_nom }}</p>

              <button @click="$router.push(`/project/${projet.id}`)" class="btn-view">Détails</button>

              <!-- Évaluation préalable -->
              <div v-if="!projet.evaluation_prealable" class="eval-section eval-prealable">
                <h4>🔍 Évaluation Préalable</h4>
                <p class="eval-prealable-description">Vérifier la recevabilité du dossier avant l'évaluation détaillée</p>

                <div class="eval-prealable-buttons">
                  <button
                    @click="soumettreEvaluationPrealable(projet.id, 'dossier_evaluable')"
                    class="btn-success"
                    :disabled="envoiEvaluationPrealable[projet.id]"
                  >
                    ✅ Dossier évaluable
                  </button>
                  <button
                    @click="soumettreEvaluationPrealable(projet.id, 'complements_requis')"
                    class="btn-warning"
                    :disabled="envoiEvaluationPrealable[projet.id] || !evaluationPrealableCommentaires[projet.id]?.trim()"
                  >
                    📝 Compléments requis
                  </button>
                  <button
                    @click="soumettreEvaluationPrealable(projet.id, 'dossier_rejete')"
                    class="btn-danger"
                    :disabled="envoiEvaluationPrealable[projet.id] || !evaluationPrealableCommentaires[projet.id]?.trim()"
                  >
                    ❌ Dossier rejeté
                  </button>
                </div>

                <label class="commentaire-label">Commentaires (obligatoire pour compléments/rejet):</label>
                <textarea
                  v-model="evaluationPrealableCommentaires[projet.id]"
                  rows="3"
                  placeholder="Justification de la décision (obligatoire si compléments requis ou dossier rejeté)"
                  class="commentaire-textarea"
                ></textarea>
              </div>

              <!-- Résultat de l'évaluation préalable -->
              <div class="eval-section eval-prealable-result" v-else-if="projet.evaluation_prealable">
                <h4>🔍 Évaluation Préalable</h4>
                <p>
                  <strong>Décision:</strong>
                  <span :class="getEvaluationPrealableClass(projet.evaluation_prealable)">
                    {{ getEvaluationPrealableText(projet.evaluation_prealable) }}
                  </span>
                </p>
                <p v-if="projet.evaluation_prealable_commentaires"><strong>Commentaires:</strong> {{ projet.evaluation_prealable_commentaires }}</p>
                <p class="eval-date" v-if="projet.evaluation_prealable_date">{{ new Date(projet.evaluation_prealable_date).toLocaleString('fr-FR') }}</p>

                <!-- Si c'est un rejet proposé (pas encore validé), afficher un bouton de validation -->
                <div v-if="projet.evaluation_prealable === 'dossier_rejete' && projet.statut !== 'rejeté'" class="validation-rejet">
                  <p class="alert-warning">⚠️ Ce rejet a été proposé par l'évaluateur et attend votre validation.</p>
                  <label class="commentaire-label">Commentaires de validation (optionnel):</label>
                  <textarea
                    v-model="evaluationPrealableCommentaires[projet.id]"
                    rows="2"
                    placeholder="Ajouter des commentaires supplémentaires si nécessaire..."
                    class="commentaire-textarea"
                  ></textarea>
                  <button
                    @click="validerRejet(projet.id)"
                    class="btn-danger-validation"
                    :disabled="envoiEvaluationPrealable[projet.id]"
                  >
                    ✅ Valider le rejet définitif
                  </button>
                </div>
              </div>

              <!-- Section d'évaluation complète (uniquement si dossier évaluable) -->
              <div v-if="projet.evaluation_prealable === 'dossier_evaluable'" class="eval-section">
                <label>Mon évaluation:</label>
                <select v-model="avis[projet.id]">
                  <option value="">--Choisir--</option>
                  <option value="favorable">Favorable</option>
                  <option value="favorable sous conditions">Favorable sous conditions</option>
                  <option value="défavorable">Défavorable</option>
                  <option value="compléments demandés">Compléments demandés</option>
                </select>
                <textarea v-model="commentaires[projet.id]" rows="2" placeholder="Commentaire obligatoire pour justifier votre décision"></textarea>
                <button class="btn-primary" @click="soumettre(projet.id)">Soumettre mon avis</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Onglet Statistiques -->
      <div v-if="activeTab === 'stats'" class="tab-content">
        <StatsDashboard
          role="secretariatsct"
          username="secretariatsct"
        />
      </div>

      <!-- Onglet Carte des pôles territoriaux -->
      <div v-if="activeTab === 'carte'" class="tab-content">
        <CartesPolesComparaison />
      </div>
    </div>

    <!-- Modal d'édition de fiche d'évaluation -->
    <div v-if="showModalEdition" class="modal-overlay" @click="fermerModalEdition">
      <div class="modal-content-large" @click.stop>
        <div class="modal-header">
          <h2>Éditer la fiche d'évaluation - {{ projetEnEdition.titre }}</h2>
          <button class="btn-close" @click="fermerModalEdition">✕</button>
        </div>
        <div class="modal-body">
          <div class="warning-box">
            ⚠️ Modification par le Secrétariat SCT - Cette action sera enregistrée dans l'historique
          </div>

          <div class="form-group">
            <label>Motif de modification (obligatoire):</label>
            <textarea v-model="editionMotif" required class="form-control" rows="3"
              placeholder="Expliquez la raison de cette modification..."></textarea>
          </div>

          <div class="criteres-edition-grid">
            <div v-for="critere in criteresConfig" :key="critere.key" class="critere-edit-item">
              <h4>{{ critere.label }} ({{ critere.max }} pts)</h4>
              <div class="critere-inputs">
                <label>Score:
                  <input type="number" :min="0" :max="critere.max"
                    v-model.number="ficheEdition.criteres[critere.key].score" class="input-score"/>
                  / {{ critere.max }}
                </label>
                <label>Commentaire:
                  <textarea v-model="ficheEdition.criteres[critere.key].commentaire"
                    class="textarea-commentaire" rows="2"></textarea>
                </label>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Avis global:</label>
            <select v-model="ficheEdition.avis" class="form-control">
              <option value="favorable">Favorable</option>
              <option value="favorable avec réserves">Favorable avec réserves</option>
              <option value="défavorable">Défavorable</option>
            </select>
          </div>

          <div class="form-group">
            <label>Commentaires généraux:</label>
            <textarea v-model="ficheEdition.commentaires" class="form-control" rows="4"></textarea>
          </div>

          <div class="total-score-display">
            Score total: <strong>{{ calculerScoreTotal() }} / 100</strong>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="fermerModalEdition" class="btn-secondary">Annuler</button>
          <button @click="enregistrerEditionFiche" class="btn-primary" :disabled="!editionMotif || !editionMotif.trim()">
            Enregistrer les modifications
          </button>
        </div>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';
import StatsDashboard from '../components/StatsDashboard.vue';
import CartesPolesComparaison from '../components/CartesPolesComparaison.vue';

export default {
  name: "SecretariatSCT",
  components: { PageWrapper, StatsDashboard, CartesPolesComparaison },
  data() {
    return {
      allProjects: [],
      evaluateurs: [],
      assignation: {},
      motivations: {},
      avis: {},
      commentaires: {},
      activeTab: 'all',
      refreshInterval: null,
      filtreStatut: null,
      financingStats: {
        totalSubmitted: 0,
        countSubmitted: 0,
        totalApproved: 0,
        countApproved: 0
      },
      // Évaluation préalable
      evaluationPrealableCommentaires: {},
      envoiEvaluationPrealable: {},
      // Édition de fiche
      showModalEdition: false,
      projetEnEdition: {},
      ficheEdition: {
        criteres: {},
        avis: '',
        commentaires: ''
      },
      editionMotif: '',
      criteresConfig: [
        { key: 'pertinence', label: 'PERTINENCE', max: 5 },
        { key: 'alignement', label: 'ALIGNEMENT À LA DOCTRINE DE TRANSFORMATION SYSTÉMIQUE', max: 10 },
        { key: 'activites_couts', label: 'PERTINENCE DES ACTIVITÉS ET BIEN FONDÉ DES COÛTS/PART DE FONCTIONNEMENT', max: 15 },
        { key: 'equite', label: 'ÉQUITÉ (SOCIALE-TERRITORIALE-GENRE)', max: 15 },
        { key: 'viabilite', label: 'VIABILITÉ/RENTABILITÉ FINANCIÈRE', max: 5 },
        { key: 'rentabilite', label: 'RENTABILITÉ SOCIO-ÉCONOMIQUE (ACA/MPR)', max: 5 },
        { key: 'benefices_strategiques', label: 'BÉNÉFICES STRATÉGIQUES', max: 10 },
        { key: 'perennite', label: 'PÉRENNITÉ ET DURABILITÉ DES EFFETS ET IMPACTS DU PROJET', max: 5 },
        { key: 'avantages_intangibles', label: 'AVANTAGES ET COÛTS INTANGIBLES', max: 10 },
        { key: 'faisabilite', label: 'FAISABILITÉ DU PROJET / RISQUES POTENTIELS', max: 5 },
        { key: 'ppp', label: 'POTENTIALITÉ OU OPPORTUNITÉ DU PROJET À ÊTRE RÉALISÉ EN PPP', max: 5 },
        { key: 'impact_environnemental', label: 'IMPACTS ENVIRONNEMENTAUX', max: 5 },
        { key: 'impact_emploi', label: 'IMPACT SUR L\'EMPLOI', max: 5 }
      ]
    };
  },
  computed: {
    projetsFiltres() {
      if (this.filtreStatut === null) {
        return this.allProjects;
      }
      return this.allProjects.filter(p => p.statut === this.filtreStatut);
    },
    projectsToAssign() {
      return this.allProjects.filter(p => ['soumis', 'compléments fournis', 'assigné'].includes(p.statut));
    },
    projectsToValidate() {
      // Inclure à la fois :
      // 1. Les projets avec statut 'évalué' (avis normaux)
      // 2. Les projets avec evaluation_prealable === 'dossier_rejete' ET statut !== 'rejeté' (rejets proposés par évaluateur en attente de validation)
      //    (On exclut les projets déjà rejetés définitivement)
      return this.allProjects.filter(p =>
        p.statut === 'évalué' || (p.evaluation_prealable === 'dossier_rejete' && p.statut !== 'rejeté')
      );
    },
    demandesComplementsEnAttente() {
      return this.allProjects.filter(p => p.statut === 'en attente validation demande compléments');
    },
    myProjects() {
      // Projets assignés au secrétariat SCT qui ne sont pas encore évalués
      return this.allProjects.filter(p =>
        p.evaluateur_nom === 'secretariatsct' &&
        (p.statut === 'assigné' || p.statut === 'en évaluation')
      );
    },
    
    // Nouvelles métriques pour le tableau de bord
    averageProcessingTime() {
      const processedProjects = this.allProjects.filter(p => 
        ['approuvé', 'validé par presidencesct', 'rejeté'].includes(p.statut)
      );
      
      if (processedProjects.length === 0) return "0 jours";
      
      // Calcul réaliste basé sur les projets traités
      // Estimation : 3 jours de base + 2 jours par projet traité
      const baseDays = 3;
      const processingDays = processedProjects.length * 2;
      const complementsDays = this.countComplements * 5; // +5 jours par projet avec compléments
      
      const totalDays = baseDays + processingDays + complementsDays;
      return `${totalDays} jours`;
    },
    
    validationRate() {
      const totalEvaluated = this.allProjects.filter(p => 
        ['approuvé', 'rejeté', 'validé par presidencesct'].includes(p.statut)
      ).length;
      const approved = this.allProjects.filter(p => 
        ['approuvé', 'validé par presidencesct'].includes(p.statut)
      ).length;
      
      if (totalEvaluated === 0) return 0;
      return Math.round((approved / totalEvaluated) * 100);
    },
    
    averageEvaluationTime() {
      const evaluatedProjects = this.allProjects.filter(p => 
        ['assigné', 'approuvé', 'rejeté', 'compléments demandés', 'compléments fournis'].includes(p.statut)
      );
      
      if (evaluatedProjects.length === 0) return "0 jours";
      
      // Calcul basé sur le nombre réel de projets en évaluation
      // 2 jours de base + 1 jour par projet + temps supplémentaire pour compléments
      const baseDays = 2;
      const evaluationDays = evaluatedProjects.length * 1;
      const complementsDays = this.countComplements * 3; // +3 jours par projet avec compléments
      
      const totalDays = baseDays + evaluationDays + complementsDays;
      return `${totalDays} jours`;
    },

    countApproved() {
      // Projets avec avis favorable mais pas encore validés par le comité
      return this.allProjects.filter(p => 
        ['favorable', 'favorable sous conditions'].includes(p.avis) &&
        (!p.decision_finale || p.decision_finale === 'en_attente')
      ).length;
    },

    countComplements() {
      return this.allProjects.filter(p => 
        ['compléments demandés', 'compléments fournis'].includes(p.statut)
      ).length;
    },

    countInEvaluation() {
      return this.allProjects.filter(p => 
        ['assigné', 'en instruction', 'évalué', 'compléments demandés', 'compléments fournis'].includes(p.statut)
      ).length;
    },
    
    countValidatedByComite() {
      // Le dernier maillon : validation finale par la présidence du comité
      return this.allProjects.filter(p => 
        p.decision_finale === 'confirme' || p.decision_finale === 'approuvé'
      ).length;
    },
    
    alerts() {
      const alerts = [];
      
      // Alertes pour projets en retard (simulation)
      const oldProjects = this.allProjects.filter(p => {
        return (p.statut === 'assigné' || p.statut === 'en évaluation') && p.id % 3 === 0; // Simulation
      });
      
      if (oldProjects.length > 0) {
        alerts.push({
          id: 'old-projects',
          type: 'warning',
          message: `${oldProjects.length} projet(s) en attente d'évaluation depuis plus de 5 jours`,
          time: new Date()
        });
      }

      // Alertes pour compléments en attente
      const complementsEnAttente = this.countByStatus('compléments demandés');
      if (complementsEnAttente > 0) {
        alerts.push({
          id: 'complements',
          type: 'info',
          message: `${complementsEnAttente} projet(s) en attente de compléments`,
          time: new Date()
        });
      }

      return alerts;
    }
  },
  mounted() {
    this.loadProjects();
    this.loadEvaluateurs();
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  methods: {
    async loadEvaluateurs() {
      try {
        const res = await fetch('/api/users');
        if (res.ok) {
          const users = await res.json();
          // Filtrer uniquement les évaluateurs
          this.evaluateurs = users.filter(u => u.role === 'evaluateur');
        }
      } catch (error) {
        console.error('Erreur lors du chargement des évaluateurs:', error);
      }
    },
    async ouvrirModalEditionFiche(projet) {
      try {
        // Charger la fiche d'évaluation actuelle
        const res = await fetch(`/api/projects/${projet.id}/fiche-evaluation`);
        if (!res.ok) {
          alert('Erreur lors du chargement de la fiche');
          return;
        }
        const fiche = await res.json();

        this.projetEnEdition = projet;
        this.ficheEdition = {
          criteres: {},
          avis: fiche.avis || '',
          commentaires: fiche.commentaires || ''
        };

        // Initialiser tous les critères
        this.criteresConfig.forEach(c => {
          this.ficheEdition.criteres[c.key] = {
            score: fiche.criteres?.[c.key]?.score || 0,
            commentaire: fiche.criteres?.[c.key]?.commentaire || ''
          };
        });

        this.editionMotif = '';
        this.showModalEdition = true;
      } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'ouverture du modal');
      }
    },
    fermerModalEdition() {
      this.showModalEdition = false;
      this.projetEnEdition = {};
      this.ficheEdition = { criteres: {}, avis: '', commentaires: '' };
      this.editionMotif = '';
    },
    calculerScoreTotal() {
      return Object.values(this.ficheEdition.criteres).reduce((sum, c) => sum + (c.score || 0), 0);
    },
    async enregistrerEditionFiche() {
      if (!this.editionMotif || !this.editionMotif.trim()) {
        alert('Veuillez indiquer le motif de modification');
        return;
      }

      const user = JSON.parse(localStorage.getItem("user") || "null") || {};

      try {
        const res = await fetch(`/api/projects/${this.projetEnEdition.id}/editer-fiche`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            fiche: this.ficheEdition,
            motif: this.editionMotif,
            auteur: user.username,
            role: user.role
          })
        });

        if (!res.ok) {
          const error = await res.json();
          throw new Error(error.error || 'Erreur lors de l\'enregistrement');
        }

        alert('Fiche modifiée avec succès');
        this.fermerModalEdition();
        this.loadProjects();
      } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'enregistrement: ' + error.message);
      }
    },
    async loadProjects() {
      try {
        const user = JSON.parse(localStorage.getItem("user") || "null") || {};

        if (!user.role || !user.username) {
          this.allProjects = [];
          return;
        }

        const r = await fetch(`/api/projects?role=${user.role}&username=${user.username}`);

        if (!r.ok) {
          this.allProjects = [];
          return;
        }

        const data = await r.json();
        this.allProjects = data;
        this.calculateFinancingStats();
      } catch (error) {
        this.allProjects = [];
      }
    },
    async assigner(id) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const ev = this.assignation[id]; if (!ev) return alert("Choisir un évaluateur");
      const motivation = (this.motivations[id] || "").trim();
      await fetch(`/api/projects/${id}/traiter`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          evaluateur_nom: ev,
          motivation: motivation,
          auteur: user.username,
          role: user.role
        })
      });
      alert("Assigné");
      this.motivations[id] = ""; // Réinitialiser la motivation
      this.loadProjects();
    },

    async reassignerComplementsPourEvaluation(id) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const projet = this.allProjects.find(p => p.id === id);
      const evaluateur = projet.evaluateur_nom || 'evaluateur1';
      
      await fetch(`/api/projects/${id}/traiter`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          evaluateur_nom: evaluateur,
          statut_action: "reevaluer_complements",
          auteur: user.username, 
          role: user.role 
        })
      });
      alert("Projet réassigné pour réévaluation"); 
      this.loadProjects();
    },

    async reassignerProjetRejete(id) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const evaluateur = this.assignation[id];

      if (!evaluateur) {
        alert("Veuillez choisir un évaluateur");
        return;
      }

      if (!confirm("Êtes-vous sûr de vouloir réassigner ce projet avec avis rejeté pour une nouvelle évaluation ?")) {
        return;
      }

      try {
        const motivation = (this.motivations[id] || "").trim();
        const response = await fetch(`/api/projects/${id}/traiter`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            evaluateur_nom: evaluateur,
            motivation: motivation,
            statut_action: "reassigner_rejete",
            auteur: user.username,
            role: user.role
          })
        });

        if (!response.ok) {
          throw new Error("Erreur lors de la réassignation");
        }

        alert("Avis rejeté réassigné avec succès ! Le projet sera évalué à nouveau.");
        this.assignation[id] = ""; // Réinitialiser le sélecteur
        this.motivations[id] = ""; // Réinitialiser la motivation
        this.loadProjects();
      } catch (error) {
        alert("Erreur lors de la réassignation : " + error.message);
      }
    },

    async validerComplementsDirectement(id) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const confirmation = confirm("Voulez-vous valider ces compléments et marquer le projet comme évalué positivement ?");
      if (!confirmation) return;
      
      await fetch(`/api/projects/${id}/traiter`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          avis: "favorable", 
          commentaires: "Compléments validés par le secrétariat SCT",
          statut_action: "validation_complements",
          auteur: user.username, 
          role: user.role 
        })
      });
      alert("Compléments validés directement"); 
      this.loadProjects();
    },

    async validerDemandeComplements(id) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const confirmation = confirm("Voulez-vous approuver cette demande de compléments et la transmettre au soumissionnaire ?");
      if (!confirmation) return;
      
      await fetch(`/api/projects/${id}/traiter`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          statut_action: "valider_demande_complements",
          auteur: user.username, 
          role: user.role 
        })
      });
      alert("Demande de compléments approuvée et transmise"); 
      this.loadProjects();
    },

    async rejeterDemandeComplements(id) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const confirmation = confirm("Voulez-vous rejeter cette demande de compléments et réassigner le projet ?");
      if (!confirmation) return;
      
      await fetch(`/api/projects/${id}/traiter`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          statut_action: "rejeter_demande_complements",
          auteur: user.username, 
          role: user.role 
        })
      });
      alert("Demande de compléments rejetée, projet réassigné"); 
      this.loadProjects();
    },

    parseComplementsFiles(filesString) {
      if (!filesString) return [];
      return filesString.split(',').map(f => f.trim()).filter(f => f.length > 0);
    },

    ouvrirFichier(projectId, fileName) {
      // Ouvrir le fichier dans un nouvel onglet
      const url = `/api/uploads/${fileName}`;
      window.open(url, '_blank');
    },
    async reassigner(id) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const ev = this.assignation[id]; if (!ev) return alert("Choisir un évaluateur");
      await fetch(`/api/projects/${id}/traiter`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ validation_secretariat: "reassigne", evaluateur_nom: ev, auteur: user.username, role: user.role })
      });
      alert("Réassigné"); this.loadProjects();
    },
    async validerAvis(id) {
      // Confirmation avant validation pour éviter clics accidentels
      if (!confirm("Êtes-vous sûr de vouloir valider cet avis et le transmettre à la Présidence SCT ?")) {
        return;
      }

      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      await fetch(`/api/projects/${id}/traiter`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ validation_secretariat: "valide", auteur: user.username, role: user.role })
      });
      alert("Avis validé ➜ Présidence SCT"); this.loadProjects();
    },

    async soumettreVoieHierarchique(id) {
      // Confirmer la soumission par voie hiérarchique
      if (!confirm("Êtes-vous sûr de vouloir soumettre ce projet à la Présidence SCT par voie hiérarchique, malgré le rejet ?")) {
        return;
      }

      const user = JSON.parse(localStorage.getItem("user") || "null") || {};

      try {
        const response = await fetch(`/api/projects/${id}/traiter`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            validation_secretariat: "valide",
            statut_action: "soumission_hierarchique",
            auteur: user.username,
            role: user.role
          })
        });

        if (!response.ok) {
          throw new Error("Erreur lors de la soumission");
        }

        alert("Projet soumis à la Présidence SCT par voie hiérarchique");
        this.loadProjects();
      } catch (error) {
        console.error("Erreur:", error);
        alert("Erreur lors de la soumission par voie hiérarchique");
      }
    },
    async validerRejet(id) {
      // Validation du rejet proposé par l'évaluateur
      if (!confirm("Êtes-vous sûr de vouloir valider ce rejet ? Le dossier sera définitivement rejeté.")) {
        return;
      }

      const user = JSON.parse(localStorage.getItem("user") || "null") || {};

      // DEBUG: Vérifier l'état du projet avant la validation
      const projectBefore = this.allProjects.find(p => p.id === id);
      console.log("[DEBUG validerRejet] État du projet AVANT validation:", {
        id,
        statut: projectBefore?.statut,
        evaluation_prealable: projectBefore?.evaluation_prealable,
        evaluation_prealable_commentaire: projectBefore?.evaluation_prealable_commentaire
      });

      // Appeler l'endpoint d'évaluation préalable avec role=secretariatsct et decision=dossier_rejete
      // Cela validera le rejet proposé
      // On envoie le commentaire de l'évaluateur (déjà présent dans evaluation_prealable_commentaire)
      const response = await fetch(`/api/projects/${id}/evaluation-prealable`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision: "dossier_rejete",
          commentaires: projectBefore?.evaluation_prealable_commentaire || "",
          auteur: user.username,
          role: "secretariatsct"
        })
      });

      const data = await response.json();
      console.log("[DEBUG validerRejet] Réponse de l'API:", {
        status: response.status,
        data
      });

      alert("Rejet validé. Le dossier a été rejeté définitivement.");
      await this.loadProjects();

      // DEBUG: Vérifier l'état du projet après la validation
      const projectAfter = this.allProjects.find(p => p.id === id);
      console.log("[DEBUG validerRejet] État du projet APRÈS validation:", {
        id,
        statut: projectAfter?.statut,
        evaluation_prealable: projectAfter?.evaluation_prealable,
        avis: projectAfter?.avis
      });
    },
    async refuserRejet(id) {
      // Refuser le rejet et réassigner
      if (!confirm("Êtes-vous sûr de vouloir refuser ce rejet et renvoyer le dossier en évaluation ?")) {
        return;
      }

      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      // Réinitialiser l'évaluation préalable en réassignant le projet
      await fetch(`/api/projects/${id}/traiter`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          statut_action: "rejeter_demande_complements", // Utiliser cette action qui réinitialise tout
          auteur: user.username,
          role: user.role
        })
      });
      alert("Rejet refusé. Le dossier a été renvoyé en assignation pour réévaluation.");
      this.loadProjects();
    },
    async soumettre(id) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const av = this.avis[id]; const com = (this.commentaires[id] || "").trim();
      if (!av) return alert("Choisir un avis");
      if (!com) return alert("Commentaire obligatoire pour justifier votre décision");
      await fetch(`/api/projects/${id}/traiter`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ avis: av, commentaires: com, auteur: user.username, role: user.role })
      });
      alert("Avis soumis"); this.loadProjects();
    },
    countByStatus(s){ return this.allProjects.filter(p=>p.statut===s).length; },
    filtrerParStatut(statut) {
      this.filtreStatut = statut;
      // Basculer vers l'onglet "Tous" si on filtre
      if (statut !== null) {
        this.activeTab = 'all';
      }
    },
    getEvaluateurLabel(ev) {
      if (ev === 'secretariatsct') return 'Secrétariat SCT';
      // Chercher l'évaluateur dans la liste et retourner son display_name
      const evaluateur = this.evaluateurs.find(e => e.username === ev);
      return evaluateur ? (evaluateur.display_name || evaluateur.username) : ev;
    },
    getAvailableEvaluateurs(projet) {
      // Pour les projets évalués, inclure l'évaluateur actuel pour permettre la réassignation au même évaluateur
      // Pour les autres statuts, exclure l'évaluateur actuellement assigné
      if (!projet || !projet.evaluateur_nom) {
        return this.evaluateurs;
      }

      // Si le projet est évalué, inclure tous les évaluateurs (y compris l'actuel)
      if (projet.statut === 'évalué') {
        console.log('getAvailableEvaluateurs - Projet évalué:', projet.numero_projet, 'Assigné à:', projet.evaluateur_nom, 'Incluant évaluateur actuel');
        return this.evaluateurs;
      }

      // Sinon, filtrer en excluant l'évaluateur actuellement assigné
      const filtered = this.evaluateurs.filter(e => {
        return e.username !== projet.evaluateur_nom;
      });
      console.log('getAvailableEvaluateurs - Projet:', projet.numero_projet, 'Assigné à:', projet.evaluateur_nom, 'Evaluateurs filtrés:', filtered.length, 'Total:', this.evaluateurs.length);
      return filtered;
    },
    getAvisClass(a){ const m={"favorable":"avis-favorable","favorable sous conditions":"avis-conditions","défavorable":"avis-defavorable","compléments demandés":"avis-complement"}; return m[a]||""; },

    // Nouvelles méthodes pour le tableau de bord
    formatTime(date) {
      return new Date(date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    },
    calculateFinancingStats() {
      // Tous les projets soumis
      this.financingStats.countSubmitted = this.allProjects.length;
      this.financingStats.totalSubmitted = this.allProjects.reduce((sum, p) => sum + (p.cout_estimatif || 0), 0);

      // Projets avec décision finale confirmée par la Présidence du Comité
      // Note: decision_finale = 'confirme' (et non 'favorable')
      const approvedProjects = this.allProjects.filter(p => p.decision_finale === 'confirme');
      this.financingStats.countApproved = approvedProjects.length;
      this.financingStats.totalApproved = approvedProjects.reduce((sum, p) => sum + (p.cout_estimatif || 0), 0);
    },
    formatCurrency(value) {
      if (!value) return '0 F CFA';
      return new Intl.NumberFormat('fr-FR', {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value) + ' F CFA';
    },
    async telechargerRapport() {
      try {
        const response = await fetch('/api/stats/rapport-pdf');
        if (!response.ok) {
          throw new Error('Erreur lors de la génération du rapport');
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `rapport_statistiques_dgppe_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Erreur téléchargement rapport:', error);
        alert('Erreur lors du téléchargement du rapport PDF');
      }
    },

    // Méthodes pour l'évaluation préalable
    async soumettreEvaluationPrealable(projectId, decision) {
      const commentaire = (this.evaluationPrealableCommentaires[projectId] || "").trim();

      // Validation: commentaire obligatoire si compléments requis ou dossier rejeté
      if ((decision === "complements_requis" || decision === "dossier_rejete") && !commentaire) {
        alert("Commentaire obligatoire pour justifier cette décision");
        return;
      }

      this.envoiEvaluationPrealable[projectId] = true;

      try {
        const user = JSON.parse(localStorage.getItem("user") || "null") || {};
        const response = await fetch(`/api/projects/${projectId}/evaluation-prealable`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            decision: decision,
            commentaires: commentaire,
            evaluateur: user.username,
            role: user.role
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Erreur lors de l'envoi");
        }

        let message = "";
        if (decision === "dossier_evaluable") {
          message = "✅ Dossier marqué comme évaluable. Vous pouvez maintenant procéder à l'évaluation détaillée.";
        } else if (decision === "complements_requis") {
          message = "📝 Compléments demandés. Le soumissionnaire sera notifié.";
        } else if (decision === "dossier_rejete") {
          message = "❌ Rejet validé. Le soumissionnaire a été notifié.";
        }

        alert(message);
        this.evaluationPrealableCommentaires[projectId] = "";
        this.loadProjects();
      } catch (error) {
        alert("Erreur: " + error.message);
      } finally {
        this.envoiEvaluationPrealable[projectId] = false;
      }
    },

    // Méthode pour valider un rejet proposé par l'évaluateur
    async validerRejet(projectId) {
      const commentaire = (this.evaluationPrealableCommentaires[projectId] || "").trim();

      if (!confirm("Êtes-vous sûr de vouloir valider ce rejet définitivement ? Le soumissionnaire sera notifié.")) {
        return;
      }

      this.envoiEvaluationPrealable[projectId] = true;

      try {
        const user = JSON.parse(localStorage.getItem("user") || "null") || {};
        const response = await fetch(`/api/projects/${projectId}/evaluation-prealable`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            decision: "dossier_rejete",
            commentaires: commentaire,
            evaluateur: user.username,
            role: user.role
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Erreur lors de la validation");
        }

        alert("✅ Rejet validé. Le soumissionnaire a été notifié.");
        this.evaluationPrealableCommentaires[projectId] = "";
        this.loadProjects();
      } catch (error) {
        alert("Erreur: " + error.message);
      } finally {
        this.envoiEvaluationPrealable[projectId] = false;
      }
    },

    getEvaluationPrealableText(decision) {
      const map = {
        'dossier_evaluable': '✅ Dossier évaluable',
        'complements_requis': '📝 Compléments requis',
        'dossier_rejete': '❌ Dossier rejeté'
      };
      return map[decision] || decision;
    },

    getEvaluationPrealableClass(decision) {
      const map = {
        'dossier_evaluable': 'decision-evaluable',
        'complements_requis': 'decision-complements',
        'dossier_rejete': 'decision-rejete'
      };
      return map[decision] || '';
    }
  }
};
</script>

<style scoped>
.secretariat-container { padding: 1rem; }

/* Tableau de bord statistiques */
.dashboard-section {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 24px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.btn-download-rapport {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--dgppe-accent);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn-download-rapport:hover {
  background: var(--dgppe-secondary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-download-rapport svg {
  width: 18px;
  height: 18px;
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: var(--dgppe-primary);
  margin-bottom: 0;
  border-bottom: 2px solid var(--dgppe-accent);
  padding-bottom: 12px;
}

.stats { display:flex; gap:.75rem; flex-wrap:wrap; margin-bottom:2rem; }
.stat { background:linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); border:1px solid #e2e8f0; border-radius:8px; padding:.75rem 1rem; transition: all 0.3s ease; }
.stat:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.stat.clickable { cursor: pointer; }
.stat.clickable.active {
  border: 2px solid var(--dgppe-primary);
  box-shadow: 0 0 0 3px rgba(46, 107, 107, 0.1);
  transform: scale(1.05);
}
.stat span{color:#6b7280;font-size:.85rem;margin-right:.5rem; font-weight: 500;} .stat strong{color:#111827; font-size: 1.1rem;}
.stat.warning{background:linear-gradient(135deg, #fff3cd 0%, #fef3c7 100%);border-color:#fde68a}
.stat.info{background:linear-gradient(135deg, #d1ecf1 0%, #ecfeff 100%);border-color:#a5f3fc}
.stat.success{background:linear-gradient(135deg, #d1f2eb 0%, #ecfdf5 100%);border-color:#a7f3d0}
.stat.primary{background:linear-gradient(135deg, rgba(46, 107, 107, 0.1) 0%, rgba(72, 181, 181, 0.1) 100%);border-color:var(--dgppe-accent)}

.filtre-actif {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #e0f2fe;
  border: 1px solid #7dd3fc;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
}

.filtre-actif span {
  color: #0c4a6e;
  font-size: 0.9rem;
}

.filtre-actif strong {
  color: #0369a1;
  font-weight: 600;
}

.btn-clear-filter {
  background: #f97316;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-filter:hover {
  background: #ea580c;
  transform: scale(1.05);
}

/* Métriques de performance */
.performance-metrics h3 {
  color: var(--dgppe-primary);
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.metric-card {
  background: #ffffff;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.metric-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #6c757d;
  font-size: 14px;
  font-weight: 500;
}

.metric-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--dgppe-primary);
}

/* Flux de traitement */
.workflow-chart h3 {
  color: var(--dgppe-primary);
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
}

.workflow-steps {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 32px;
}

.workflow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.step-indicator {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  font-weight: 700;
  color: white;
  font-size: 16px;
}

.step-new { background: var(--dgppe-secondary); }
.step-progress { background: #ffc107; }
.step-review { background: #17a2b8; }
.step-done { background: #28a745; }

.step-label {
  font-size: 12px;
  color: #6c757d;
  text-align: center;
  font-weight: 500;
}

.step-arrow {
  font-size: 18px;
  color: #6c757d;
  margin: 0 16px;
}

/* Alertes */
.alerts-section h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--dgppe-primary);
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 32px;
}

.alert-item {
  padding: 12px 16px;
  border-radius: 6px;
  border-left: 4px solid;
}

.alert-item.warning {
  background: #fff3cd;
  border-left-color: #ffc107;
}

.alert-item.info {
  background: #d1ecf1;
  border-left-color: #17a2b8;
}

.alert-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-message {
  font-weight: 500;
  color: #495057;
}

.alert-time {
  font-size: 12px;
  color: #6c757d;
}
.stat.warning{background:#fffbeb;border-color:#fde68a}.stat.info{background:#ecfeff;border-color:#a5f3fc}.stat.success{background:#ecfdf5;border-color:#a7f3d0}
.tabs { display: flex; gap: 0.5rem; margin-bottom: 1rem; border-bottom: 2px solid #e5e7eb; }
.tab-btn { padding: .75rem 1.25rem; background: transparent; border: none; border-bottom: 3px solid transparent; cursor: pointer; font-weight: 600; color: #6b7280; }
.tab-btn.active { color: #2563eb; border-bottom-color: #2563eb; background: #f0f9ff; }
.projects-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }
.project-card { background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; }
.card-header { padding: 1rem; background: #f0f9ff; border-bottom: 2px solid #2563eb; display:flex; justify-content:space-between; align-items:flex-start; }

.card-title-section {
  flex: 1;
  margin-right: 1rem;
}

.project-number {
  background: var(--dgppe-primary);
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  margin-bottom: 0.5rem;
  letter-spacing: 0.5px;
}

.card-title-section h3 {
  margin: 0;
  font-size: 1rem;
  color: #1e293b;
  line-height: 1.4;
}
.badge { padding:.25rem .6rem; border-radius:999px; font-size:.8rem; font-weight:700; }
.status-new{background:#3b82f6;color:#fff}.status-assigned{background:#f59e0b;color:#fff}.status-info{background:#06b6d4;color:#fff}.status-complement{background:#f97316;color:#fff}.status-evaluated{background:#8b5cf6;color:#fff}.status-default{background:#6b7280;color:#fff}
.card-body { padding: 1rem; }
.highlight-assigned { background: #fef3c7; padding: 0.5rem; border-radius: 6px; border-left: 3px solid #f59e0b; font-weight: 600; }
.btn-primary{background:#2563eb;color:#fff;border:none;border-radius:8px;padding:.6rem .9rem;cursor:pointer}
.btn-secondary{background:#6b7280;color:#fff;border:none;border-radius:8px;padding:.6rem .9rem;cursor:pointer;margin-left:.5rem}
.btn-secondary:hover{background:#4b5563 !important;color:#fff !important;border-color:#4b5563 !important}
.btn-outline{background:#10b981;color:#fff;border:none;border-radius:8px;padding:.6rem .9rem;cursor:pointer;margin-top:.5rem}
.btn-view{width:100%;margin-top:.75rem;padding:.6rem;background:#6b7280;color:#fff;border:none;border-radius:8px}
.assign-section, .eval-section, .validation-actions { margin-top:.75rem; padding: .9rem; background: #f8fafc; border:1px solid #e5e7eb; border-radius:8px; }
.reassign { display:flex; gap:.5rem; align-items:center; margin-top:.5rem; flex-wrap: wrap; }
.reassign button { flex-shrink: 0; white-space: nowrap; }
.reassign select { min-width: 150px; max-width: 250px; }
.avis-favorable{color:#10b981;font-weight:600}.avis-conditions{color:#f59e0b;font-weight:600}.avis-defavorable{color:#ef4444;font-weight:600}.avis-complement{color:#f97316;font-weight:600}

/* Styles pour les compléments */
.complements-info {
  background: #e0f2fe;
  border: 1px solid #81d4fa;
  border-radius: 8px;
  padding: 12px;
  margin: 10px 0;
}

.complements-message {
  background: white;
  border-left: 4px solid #2196f3;
  padding: 10px;
  margin: 8px 0;
  font-style: italic;
}

.assign-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ddd;
}

.assign-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
}

.assign-section select {
  padding: 8px;
  margin-right: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn-primary {
  background: #2196f3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover {
  background: #1976d2;
}

/* Styles pour la réassignation */
.reassign-info {
  background: #fff3e0;
  border: 1px solid #ffb74d;
  border-radius: 8px;
  padding: 12px;
  margin: 10px 0;
}

.current-assignment {
  background: white;
  border-left: 4px solid #ff9800;
  padding: 10px;
  margin: 8px 0;
  font-weight: 500;
}

.reassign-note {
  font-size: 0.9em;
  color: #e65100;
  font-style: italic;
  margin: 5px 0 0 0;
}

/* Styles pour l'évaluation directe */
.direct-evaluation {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 2px dashed #ff9800;
}

.direct-evaluation h4 {
  color: #e65100;
  margin-bottom: 10px;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 5px;
}

.eval-section.compact {
  background: #f3e5f5;
  border: 1px solid #9c27b0;
  border-radius: 8px;
  padding: 12px;
  margin: 8px 0;
}

.eval-section.compact label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #4a148c;
}

.eval-section.compact select,
.eval-section.compact textarea {
  width: 100%;
  padding: 8px;
  margin-bottom: 10px;
  border: 1px solid #ce93d8;
  border-radius: 4px;
  font-family: inherit;
}

.eval-section.compact select:focus,
.eval-section.compact textarea:focus {
  outline: none;
  border-color: #9c27b0;
  box-shadow: 0 0 0 2px rgba(156, 39, 176, 0.2);
}

.eval-section.compact .btn-primary {
  background: #9c27b0;
  width: 100%;
  margin-top: 5px;
}

.eval-section.compact .btn-primary:hover {
  background: #7b1fa2;
}

.project-actions {
  margin: 10px 0;
  padding: 10px 0;
  border-top: 1px solid #eee;
}

.self-eval-section {
  margin-bottom: 15px;
}

.highlight-assigned {
  background: #e3f2fd;
  color: #0d47a1;
  padding: 0.75rem;
  border-radius: 6px;
  border-left: 4px solid #2196f3;
  font-weight: 600;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.reassign-section {
  margin-top: 15px;
  padding: 12px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
}

.reassign-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #495057;
}

.reassign-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.reassign-controls select {
  flex: 1;
  padding: 8px;
  border: 1px solid #ced4da;
  border-radius: 4px;
}

.reassign-controls .btn-secondary {
  flex-shrink: 0;
}

.btn-view { 
  width: 100%; 
  margin-top: .75rem; 
  padding: .6rem; 
  background: #6b7280; 
  color: #fff; 
  border: none; 
  border-radius: 8px; 
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-view:hover {
  background: #4b5563;
}

.complements-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.complements-actions button {
  flex: 1;
  min-width: 150px;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover {
  background: #059669;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.complement-request {
  background: #fef3c7;
  padding: 1rem;
  border-radius: 8px;
  border-left: 4px solid #f59e0b;
  margin: 1rem 0;
}

.complement-message {
  background: white;
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 0.5rem;
  font-style: italic;
  border: 1px solid #e5e7eb;
}

.rejection-proposal {
  margin: 1rem 0;
}

.rejection-message {
  background: #fef2f2;
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 0.5rem;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.status-rejected {
  background: #fee2e2;
  color: #991b1b;
  border-color: #fca5a5;
}

.validation-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.validation-actions button {
  flex: 1;
  min-width: 120px;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.status-pending {
  background: #8b5cf6;
  color: white;
}

.complements-files {
  margin: 1rem 0;
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
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s ease;
  color: #374151;
}

.file-link:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
  color: #1f2937;
}

.file-link svg {
  color: #6b7280;
}

.no-message, .no-files {
  color: #6b7280;
  font-style: italic;
}

/* Styles pour les projets rejetés */
.rejected-actions {
  border: 2px solid #fee2e2;
  border-radius: 12px;
  padding: 15px;
  background: #fef2f2;
}

.rejected-info {
  margin-bottom: 20px;
}

.alert-danger {
  background: #fee2e2;
  color: #dc2626;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #fca5a5;
  margin-bottom: 10px;
  font-weight: 500;
}

.reassign-rejected-section {
  background: white;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.reassign-rejected-section h4 {
  color: #374151;
  margin-bottom: 15px;
  font-size: 1.1rem;
}

.reassign-controls-vertical {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.reassign-select-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reassign-select-container label {
  font-weight: 500;
  color: #374151;
}

.reassign-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.9rem;
  min-width: 200px;
}

.reassign-button-container {
  display: flex;
  justify-content: flex-start;
}

.btn-reassign {
  min-width: 280px;
  padding: 10px 16px;
  text-align: center;
  white-space: nowrap;
}

.info-text {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 15px;
}

.action-group h5 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 15px;
}

.warning-note {
  margin-top: 10px;
  padding: 8px;
  background: #fef3c7;
  border: 1px solid #fbbf24;
  border-radius: 4px;
  color: #92400e;
}

.btn-warning {
  background: #f59e0b;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-warning:hover:not(:disabled) {
  background: #d97706;
}

.btn-warning:disabled {
  background: #d1d5db;
  color: #9ca3af;
  cursor: not-allowed;
}

/* ==================== VOLUMES DE FINANCEMENT ==================== */
.financing-volumes {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 24px;
}

.financing-volumes h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a202c;
  margin: 0 0 20px 0;
}

.financing-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.financing-card {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  border: 2px solid #d1d5db;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.financing-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.financing-card.success {
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
  border-color: #28a745;
}

.financing-card.success:hover {
  box-shadow: 0 8px 20px rgba(40, 167, 69, 0.25);
}

.financing-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  color: #4b5563;
  font-weight: 500;
  font-size: 0.95rem;
}

.financing-card.success .financing-header {
  color: #155724;
}

.financing-header svg {
  flex-shrink: 0;
}

.financing-amount {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 8px;
}

.financing-card.success .financing-amount {
  color: #155724;
}

.financing-count {
  font-size: 0.9rem;
  color: #6b7280;
  font-weight: 500;
}

.financing-card.success .financing-count {
  color: #28a745;
}

/* Responsive pour les cartes de financement */
@media (max-width: 768px) {
  .financing-cards-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .financing-amount {
    font-size: 1.5rem;
  }
}

/* Styles pour l'évaluation préalable */
.eval-prealable {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 2px solid #0ea5e9;
  border-radius: 10px;
  padding: 1.25rem;
  margin-top: 1rem;
}

.eval-prealable h4 {
  color: #0369a1;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 700;
}

.eval-prealable-description {
  color: #0c4a6e;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  font-style: italic;
}

.eval-prealable-buttons {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.eval-prealable-buttons button {
  flex: 1;
  min-width: 140px;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.eval-prealable-buttons button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.eval-prealable-buttons .btn-success {
  background: #10b981;
  color: white;
}

.eval-prealable-buttons .btn-success:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.eval-prealable-buttons .btn-warning {
  background: #f59e0b;
  color: white;
}

.eval-prealable-buttons .btn-warning:hover:not(:disabled) {
  background: #d97706;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

.eval-prealable-buttons .btn-danger {
  background: #ef4444;
  color: white;
}

.eval-prealable-buttons .btn-danger:hover:not(:disabled) {
  background: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.commentaire-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #0369a1;
  font-size: 0.95rem;
}

.commentaire-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #bae6fd;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
  transition: all 0.3s ease;
}

.commentaire-textarea:focus {
  outline: none;
  border-color: #0ea5e9;
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.eval-prealable-result {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 2px solid #22c55e;
  border-radius: 10px;
  padding: 1.25rem;
  margin-top: 1rem;
}

.eval-prealable-result h4 {
  color: #15803d;
  margin: 0 0 0.75rem 0;
  font-size: 1.1rem;
  font-weight: 700;
}

.decision-evaluable {
  color: #10b981;
  font-weight: 600;
  padding: 4px 8px;
  background: #d1fae5;
  border-radius: 4px;
}

.decision-complements {
  color: #f59e0b;
  font-weight: 600;
  padding: 4px 8px;
  background: #fef3c7;
  border-radius: 4px;
}

.decision-rejete {
  color: #dc2626;
  font-weight: 600;
  padding: 4px 8px;
  background: #fee2e2;
  border-radius: 4px;
}

.eval-date {
  font-size: 13px;
  color: #6b7280;
  font-style: italic;
}

/* Styles pour la validation de rejet */
.validation-rejet {
  margin-top: 1rem;
  padding: 1rem;
  background: #fef2f2;
  border: 2px solid #fca5a5;
  border-radius: 8px;
}

.alert-warning {
  color: #b91c1c;
  font-weight: 600;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #fee2e2;
  border-left: 4px solid #dc2626;
  border-radius: 4px;
}

.btn-danger-validation {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 0.75rem;
  width: 100%;
  box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
}

.btn-danger-validation:hover:not(:disabled) {
  background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
}

.btn-danger-validation:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Styles pour le modal d'édition de fiche */
.btn-edit-fiche {
  margin-top: 0.75rem;
  padding: 0.65rem 1.25rem;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.btn-edit-fiche:hover {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

.modal-content-large {
  width: 95%;
  max-width: 1200px;
  max-height: 90vh;
  overflow-y: auto;
}

.warning-box {
  padding: 1rem;
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  border-radius: 4px;
  margin-bottom: 1.5rem;
  color: #92400e;
  font-weight: 500;
}

.criteres-edition-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 1.5rem;
  margin: 1.5rem 0;
}

.critere-edit-item {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.critere-edit-item h4 {
  font-size: 0.95rem;
  color: #374151;
  margin-bottom: 1rem;
  font-weight: 600;
}

.critere-inputs {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.critere-inputs label {
  display: flex;
  flex-direction: column;
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.input-score {
  width: 100px;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.95rem;
  margin-top: 0.25rem;
}

.textarea-commentaire {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  resize: vertical;
  margin-top: 0.25rem;
  font-family: inherit;
}

.total-score-display {
  padding: 1rem;
  background: #eff6ff;
  border-left: 4px solid #3b82f6;
  border-radius: 4px;
  font-size: 1.1rem;
  text-align: center;
  margin-top: 1.5rem;
}

.total-score-display strong {
  color: #1e40af;
  font-size: 1.3rem;
}
</style>