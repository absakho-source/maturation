<template>
  <PageWrapper>
    <div class="secretariat-container">
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
        <div class="header-buttons">
          <button @click="telechargerRapport" class="btn-download-rapport">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Télécharger Rapport
          </button>
          <button @click="telechargerRapportElabore" class="btn-download-rapport elabore">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            Générer Rapport Élaboré
          </button>
        </div>
      </div>

      <div class="tabs">
        <button @click="activeTab = 'all'" :class="{ active: activeTab === 'all' }" class="tab-btn">📋 Tous</button>
        <button @click="activeTab = 'assignation'" :class="{ active: activeTab === 'assignation' }" class="tab-btn">✅ Assignation / Réassignation</button>
        <button @click="activeTab = 'validation'" :class="{ active: activeTab === 'validation' }" class="tab-btn">🔎 Validation d'avis</button>
        <button @click="activeTab = 'decisions-comite'" :class="{ active: activeTab === 'decisions-comite' }" class="tab-btn">🏛️ Décisions du Comité</button>
        <button @click="activeTab = 'evaluation'" :class="{ active: activeTab === 'evaluation' }" class="tab-btn">✍️ Mes évaluations</button>
        <button @click="activeTab = 'stats'" :class="{ active: activeTab === 'stats' }" class="tab-btn">📊 Statistiques</button>
        <button @click="activeTab = 'carte'" :class="{ active: activeTab === 'carte' }" class="tab-btn">🗺️ Carte pôles</button>
      </div>

      <!-- Tous -->
      <div v-if="activeTab === 'all'" class="tab-content">
        <div class="projects-section">
          <div class="section-header">
            <h2>📋 Tous les projets</h2>
            <div class="project-stats">
              <span class="stat-item">Total: <strong>{{ allProjects.length }}</strong></span>
              <span class="stat-item">En cours: <strong>{{ countInEvaluation }}</strong></span>
            </div>
          </div>

          <!-- Barre de recherche et filtres -->
          <div class="search-and-filters">
            <div class="search-bar-container">
              <input
                type="text"
                v-model="searchQuery"
                @input="applyFiltersAll"
                placeholder="🔍 Rechercher par titre, auteur ou numéro..."
                class="search-input"
              />
            </div>
            <button @click="toggleFilters" class="btn-toggle-filters">
              {{ showFilters ? '▲ Masquer les filtres avancés' : '▼ Afficher les filtres avancés' }}
            </button>
            <button @click="exporterProjetsCSV" class="btn-export-csv">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="12" y1="11" x2="12" y2="17"/>
                <polyline points="9 14 12 17 15 14"/>
              </svg>
              Exporter CSV
            </button>
          </div>

          <div v-if="showFilters" class="filters-container">
            <div class="filter-group">
              <label class="filter-label collapsible" @click="toggleFilterGroup('years')">
                <span class="collapse-icon">{{ filterGroupsOpen.years ? '▼' : '▶' }}</span>
                Années: <span v-if="selectedYears.length > 0" class="filter-count">({{ selectedYears.length }})</span>
              </label>
              <div v-if="filterGroupsOpen.years" class="checkbox-group">
                <label v-for="year in availableYears" :key="year" class="checkbox-label">
                  <input type="checkbox" :value="year" v-model="selectedYears">
                  <span>{{ year }}</span>
                </label>
              </div>
            </div>
            <div class="filter-group">
              <label class="filter-label collapsible" @click="toggleFilterGroup('secteurs')">
                <span class="collapse-icon">{{ filterGroupsOpen.secteurs ? '▼' : '▶' }}</span>
                Secteurs: <span v-if="selectedSecteurs.length > 0" class="filter-count">({{ selectedSecteurs.length }})</span>
              </label>
              <div v-if="filterGroupsOpen.secteurs" class="checkbox-group">
                <label v-for="secteur in secteurs" :key="secteur" class="checkbox-label">
                  <input type="checkbox" :value="secteur" v-model="selectedSecteurs">
                  <span>{{ secteur }}</span>
                </label>
              </div>
            </div>
            <div class="filter-group">
              <label class="filter-label collapsible" @click="toggleFilterGroup('statuts')">
                <span class="collapse-icon">{{ filterGroupsOpen.statuts ? '▼' : '▶' }}</span>
                Statuts: <span v-if="selectedStatuts.length > 0" class="filter-count">({{ selectedStatuts.length }})</span>
              </label>
              <div v-if="filterGroupsOpen.statuts" class="checkbox-group">
                <label class="checkbox-label">
                  <input type="checkbox" value="soumis" v-model="selectedStatuts">
                  <span>Soumis</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" value="assigné" v-model="selectedStatuts">
                  <span>Assigné</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" value="évalué" v-model="selectedStatuts">
                  <span>Évalué</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" value="favorable" v-model="selectedStatuts">
                  <span>Favorable</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" value="favorable sous conditions" v-model="selectedStatuts">
                  <span>Favorable sous conditions</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" value="défavorable" v-model="selectedStatuts">
                  <span>Défavorable</span>
                </label>
              </div>
            </div>
            <div class="filter-group">
              <label class="filter-label collapsible" @click="toggleFilterGroup('poles')">
                <span class="collapse-icon">{{ filterGroupsOpen.poles ? '▼' : '▶' }}</span>
                Pôles: <span v-if="selectedPoles.length > 0" class="filter-count">({{ selectedPoles.length }})</span>
              </label>
              <div v-if="filterGroupsOpen.poles" class="checkbox-group">
                <label v-for="pole in polesList" :key="pole" class="checkbox-label">
                  <input type="checkbox" :value="pole" v-model="selectedPoles">
                  <span>{{ pole }}</span>
                </label>
              </div>
            </div>
            <button @click="resetFilters" class="btn-reset">Réinitialiser</button>
          </div>

          <!-- Tableau des projets -->
          <div class="projects-table-container">
            <table class="projects-table">
              <thead>
                <tr>
                  <th>N° Projet</th>
                  <th>Titre</th>
                  <th>Structure soumissionnaire</th>
                  <th>Secteur</th>
                  <th>Statut</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="projetsFiltres.length === 0">
                  <td colspan="6" class="empty-state">Aucun projet trouvé</td>
                </tr>
                <tr v-for="projet in projetsFiltres" :key="projet.id" :class="{ 'compte-non-verifie': projet.soumissionnaire_statut_compte === 'non_verifie' }">
                  <td><strong class="project-number-table">{{ projet.numero_projet || 'N/A' }}</strong></td>
                  <td class="project-title">
                    {{ projet.titre }}
                    <span v-if="projet.soumissionnaire_statut_compte === 'non_verifie'"
                          class="badge status-warning"
                          style="margin-left: 8px; font-size: 11px;"
                          title="Le compte du soumissionnaire n'est pas encore vérifié. Aucune action ne peut être effectuée sur ce projet tant que le compte n'est pas validé.">
                      🔒 Compte non vérifié
                    </span>
                  </td>
                  <td>{{ projet.structure_soumissionnaire || projet.organisme_tutelle || projet.auteur_nom || 'N/A' }}</td>
                  <td>{{ projet.secteur || 'N/A' }}</td>
                  <td>
                    <span class="badge" :class="getStatutBadge(projet).class">{{ getStatutBadge(projet).text }}</span>
                    <span v-if="projet.evaluation_prealable === 'dossier_rejete' && projet.statut !== 'rejeté'"
                          class="badge status-rejected" style="margin-left: 4px;">⚠️</span>
                  </td>
                  <td>
                    <div class="action-buttons">
                      <!-- Détails - toujours disponible -->
                      <button @click="$router.push(`/project/${projet.id}`)" class="btn-sm btn-view" title="Voir les détails">📋 Détails</button>

                      <!-- Assigner : projets soumis ou compléments fournis (sans statut définitif) -->
                      <button
                        v-if="['soumis', 'compléments fournis'].includes(projet.statut) && projet.soumissionnaire_statut_compte !== 'non_verifie' && estProjetAssignable(projet)"
                        @click="activeTab = 'assignation'"
                        class="btn-sm btn-primary"
                        title="Assigner à un évaluateur"
                      >
                        ➕ Assigner
                      </button>

                      <!-- Réassigner : projets assignés ou en évaluation (sans statut définitif) -->
                      <button
                        v-if="['assigné', 'en évaluation'].includes(projet.statut) && projet.soumissionnaire_statut_compte !== 'non_verifie' && estProjetAssignable(projet)"
                        @click="activeTab = 'assignation'"
                        class="btn-sm btn-secondary"
                        title="Réassigner à un autre évaluateur"
                      >
                        🔄 Réassigner
                      </button>

                      <!-- Valider : projets évalués ou rejet proposé -->
                      <button
                        v-if="(projet.statut === 'évalué' || (projet.evaluation_prealable === 'dossier_rejete' && projet.statut !== 'rejeté')) && projet.soumissionnaire_statut_compte !== 'non_verifie'"
                        @click="activeTab = 'validation'"
                        class="btn-sm btn-success"
                        title="Valider l'avis de l'évaluateur"
                      >
                        ✓ Valider avis
                      </button>

                      <!-- Traiter : projets en réexamen (rejetés par présidence SCT ou comité) -->
                      <button
                        v-if="projet.statut === 'en réexamen par le Secrétariat SCT' && projet.soumissionnaire_statut_compte !== 'non_verifie'"
                        @click="activeTab = 'assignation'"
                        class="btn-sm btn-warning"
                        title="Traiter ce projet en réexamen"
                      >
                        🔄 Traiter
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Assignation -->
      <div v-if="activeTab === 'assignation'" class="tab-content">
        <h2>Assignation / Réassignation</h2>
        <div v-if="projectsToAssign.length === 0" class="empty-state">
          <p>Aucun projet trouvé</p>
        </div>
        <div v-else class="projects-compact-grid">
          <div v-for="projet in projectsToAssign" :key="projet.id" class="project-compact-card" :class="{ 'compte-non-verifie': projet.soumissionnaire_statut_compte === 'non_verifie' }">
            <!-- En-tête compacte cliquable -->
            <div class="compact-card-header" @click="toggleProjectExpansion(projet.id)">
              <div class="compact-card-top">
                <span class="project-number-badge-small">{{ projet.numero_projet || 'N/A' }}</span>
                <span :class="'badge-small status-' + projet.statut.replace(/ /g, '-')">{{ projet.statut }}</span>
              </div>
              <h4 class="compact-card-title">{{ projet.titre }}</h4>
              <!-- Badge compte non vérifié sur une ligne séparée pour plus de clarté -->
              <div v-if="projet.soumissionnaire_statut_compte === 'non_verifie'" class="warning-badge-row">
                <span class="badge-small status-warning"
                      title="Le compte du soumissionnaire n'est pas encore vérifié. Aucune action ne peut être effectuée sur ce projet tant que le compte n'est pas validé.">
                  🔒 Compte non vérifié
                </span>
              </div>
              <button class="btn-expand-small" @click.stop="toggleProjectExpansion(projet.id)">
                {{ expandedProjects[projet.id] ? '▲' : '▼ Actions' }}
              </button>
            </div>

            <!-- Carte détaillée (expanded) -->
            <div v-if="expandedProjects[projet.id]" class="project-card-expanded">
            <div class="card-body">
              <p><strong>Auteur:</strong> {{ projet.auteur_nom }}</p>
              <p v-if="projet.secteur"><strong>Secteur de planification:</strong> {{ projet.secteur }}</p>
              <p v-if="projet.poles"><strong>Pôle(s) territorial(aux):</strong> {{ projet.poles }}</p>
              
              <!-- Projets déjà assignés ou en évaluation -->
              <div v-if="projet.statut === 'assigné' || projet.statut === 'en évaluation'" class="reassign-info">
                <p><strong>🔄 Projet {{ projet.statut === 'en évaluation' ? 'en cours d\'évaluation' : 'assigné' }} :</strong></p>
                <div class="current-assignment">
                  Actuellement assigné à : <strong>{{ getEvaluateurLabel(projet.evaluateur_nom) }}</strong>
                </div>
                <p v-if="projet.soumissionnaire_statut_compte !== 'non_verifie'" class="reassign-note">Vous pouvez réassigner ce projet à un autre évaluateur.</p>
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

                <!-- Actions pour traiter les compléments - masquées pour comptes non vérifiés -->
                <div v-if="projet.soumissionnaire_statut_compte !== 'non_verifie'" class="complements-actions">
                  <button @click="reassignerComplementsPourEvaluation(projet.id)" class="btn-success">
                    ✓ Réassigner pour réévaluation
                  </button>
                  <button @click="validerComplementsDirectement(projet.id)" class="btn-primary">
                    📋 Valider directement
                  </button>
                </div>
              </div>
              
              <button @click="$router.push(`/project/${projet.id}`)" class="btn-view">Détails</button>

              <!-- Actions pour projets en réexamen - Présentation contextuelle -->
              <div v-if="projet.statut === 'en réexamen par le Secrétariat SCT' && projet.soumissionnaire_statut_compte !== 'non_verifie'" class="project-actions rejected-actions">
                <div class="rejected-info">
                  <div class="alert alert-danger">
                    <!-- Différencier entre rejet par présidence SCT et infirmation par comité -->
                    <template v-if="projet.avis_presidencesct === 'rejete' && projet.decision_finale !== 'infirme'">
                      ⚠️ <strong>Avis rejeté par la Présidence SCT - Action requise</strong>
                    </template>
                    <template v-else-if="projet.decision_finale === 'infirme'">
                      ⚠️ <strong>Avis infirmé par la Présidence du Comité - Action requise</strong>
                    </template>
                    <template v-else>
                      ⚠️ <strong>Projet en réexamen - Action requise</strong>
                    </template>
                  </div>
                  <p v-if="projet.commentaires_finaux">
                    <strong>{{ projet.decision_finale === 'infirme' ? 'Motif de l\'infirmation:' : 'Motif du rejet:' }}</strong>
                    {{ projet.commentaires_finaux }}
                  </p>
                  <p v-else-if="projet.commentaires"><strong>Motif:</strong> {{ projet.commentaires }}</p>
                </div>

                <!-- Options de traitement -->
                <div class="reassign-rejected-section">
                  <h4>🔄 Options de traitement</h4>

                  <div class="reassign-controls-vertical">
                    <!-- Option 1: Réassignation à un évaluateur (orange) -->
                    <div class="action-group action-group-orange">
                      <h5><span class="action-bullet orange">1</span> Réassigner pour nouvelle évaluation</h5>
                      <p class="info-text">Confier le dossier à un évaluateur pour une nouvelle analyse</p>
                      <div class="reassign-select-container">
                        <label>Réassigner à:</label>
                        <select v-model="assignation[projet.id]" class="reassign-select">
                          <option value="">--Choisir un évaluateur--</option>
                          <option v-if="projet.evaluateur_nom !== currentUser?.username" :value="currentUser?.username">Moi-même ({{ currentUser?.display_name || 'Secrétariat SCT' }})</option>
                          <option v-for="autre in autresSecretariatSCT" :key="autre.username" :value="autre.username">
                            {{ autre.display_name || autre.username }} (Secrétariat SCT)
                          </option>
                          <option v-for="evaluateur in evaluateurs" :key="evaluateur.username" :value="evaluateur.username">
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

                    <!-- Option 2: Soumettre de nouveau (bleu) -->
                    <div class="action-group action-group-blue">
                      <h5><span class="action-bullet blue">2</span> Soumettre de nouveau à la hiérarchie</h5>
                      <p class="info-text">Transmettre directement à la Présidence SCT malgré le rejet</p>

                      <label class="motif-label" style="display: block; margin-top: 10px; margin-bottom: 5px;">
                        Motivation de la resoumission
                        <span class="motif-hint">(obligatoire)</span>
                      </label>
                      <textarea
                        v-model="motivationsResoumission[projet.id]"
                        rows="3"
                        placeholder="Expliquez pourquoi ce projet mérite d'être soumis à la Présidence SCT malgré le rejet..."
                        :class="{ 'error-border': erreursResoumission[projet.id] }"
                        style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; resize: vertical;"
                      ></textarea>
                      <p v-if="erreursResoumission[projet.id]" class="error-message">{{ erreursResoumission[projet.id] }}</p>

                      <div class="reassign-button-container" style="margin-top: 10px;">
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

              <!-- Actions pour assigner (projets non en réexamen) -->
              <div v-if="projet.statut !== 'en réexamen par le Secrétariat SCT' && projet.soumissionnaire_statut_compte !== 'non_verifie' && estProjetAssignable(projet)" class="assign-section">
                <label>{{ ['assigné', 'en évaluation', 'évalué'].includes(projet.statut) ? 'Réassigner à:' : 'Assigner à:' }}</label>
                <select v-model="assignation[projet.id]">
                  <option value="">--Choisir--</option>
                  <option v-if="!['assigné', 'en évaluation', 'évalué'].includes(projet.statut) || projet.evaluateur_nom !== currentUser?.username" :value="currentUser?.username">Moi-même ({{ currentUser?.display_name || 'Secrétariat SCT' }})</option>
                  <option v-for="autre in autresSecretariatSCT" :key="'sct-' + autre.username" :value="autre.username">
                    {{ autre.display_name || autre.username }} (Secrétariat SCT)
                  </option>
                  <option v-for="evaluateur in (['assigné', 'en évaluation', 'évalué'].includes(projet.statut) ? getAvailableEvaluateurs(projet) : evaluateurs)" :key="evaluateur.username" :value="evaluateur.username">
                    {{ evaluateur.display_name || evaluateur.username }}
                  </option>
                </select>
                <label style="margin-top: 10px;">Motivation (facultatif):</label>
                <textarea
                  v-model="motivations[projet.id]"
                  rows="2"
                  :placeholder="['assigné', 'en évaluation', 'évalué'].includes(projet.statut) ? 'Justification de cette réassignation (facultatif)' : 'Justification de cette assignation (facultatif)'"
                  style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit;"
                ></textarea>
                <button class="btn-primary" @click="assigner(projet.id)">
                  {{ ['assigné', 'en évaluation', 'évalué'].includes(projet.statut) ? 'Réassigner' : 'Assigner' }}
                </button>
              </div>

              <!-- Message si projet non réassignable (validation secrétariat ou statut définitif) -->
              <div v-if="(projet.statut === 'assigné' || projet.statut === 'en évaluation') && !estProjetAssignable(projet)" class="info-message">
                <p>⚠️ Ce projet ne peut plus être réassigné (validation secrétariat ou décision hiérarchique en cours).</p>
              </div>
            </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Validation d'avis -->
      <div v-if="activeTab === 'validation'" class="tab-content">
        <h2>Avis à valider</h2>
        <div v-if="projectsToValidate.length === 0" class="empty-state"><p>Aucun avis en attente</p></div>

        <div v-else class="projects-compact-grid">
          <div v-for="p in projectsToValidate" :key="p.id" class="project-compact-card">
            <!-- En-tête compacte cliquable -->
            <div class="compact-card-header" @click="toggleProjectExpansion(p.id)">
              <div class="compact-card-top">
                <span class="project-number-badge-small">{{ p.numero_projet || 'N/A' }}</span>
                <span v-if="p.evaluation_prealable === 'dossier_rejete'" class="badge-small status-rejected">⚠️ Rejet</span>
                <span v-else class="badge-small status-evaluated">Évalué</span>
              </div>
              <h4 class="compact-card-title">{{ p.titre }}</h4>
              <button class="btn-expand-small" @click.stop="toggleProjectExpansion(p.id)">
                {{ expandedProjects[p.id] ? '▲' : '▼ Actions' }}
              </button>
            </div>

            <!-- Carte détaillée (expanded) -->
            <div v-if="expandedProjects[p.id]" class="project-card-expanded">
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
              <div style="display: flex; justify-content: center; margin-top: 10px;">
                <button
                  v-if="p.evaluation_prealable !== 'dossier_rejete' && p.avis"
                  @click="ouvrirModalEditionFiche(p)"
                  class="btn-edit-fiche"
                >
                  ✏️ Éditer la fiche
                </button>
              </div>

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
                <div v-if="estProjetAssignable(p)" class="reassign">
                  <label>Réassigner à
                    <select v-model="assignation[p.id]">
                      <option value="">--Choisir--</option>
                      <option v-if="p.evaluateur_nom !== currentUser?.username" :value="currentUser?.username">Moi-même ({{ currentUser?.display_name || 'Secrétariat SCT' }})</option>
                      <option v-for="autre in autresSecretariatSCT" :key="'val-sct-' + autre.username" :value="autre.username">
                        {{ autre.display_name || autre.username }} (Secrétariat SCT)
                      </option>
                      <option v-for="evaluateur in getAvailableEvaluateurs(p)" :key="evaluateur.username" :value="evaluateur.username">
                        {{ evaluateur.display_name || evaluateur.username }}
                      </option>
                    </select>
                  </label>
                  <label style="margin-top: 10px;">Motivation (facultatif):</label>
                  <textarea
                    v-model="motivations[p.id]"
                    rows="2"
                    placeholder="Justification de cette réassignation (facultatif)"
                    style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; margin-bottom: 10px;"
                  ></textarea>
                  <button class="btn-secondary" @click="reassigner(p.id)">Réassigner</button>
                </div>
              </div>
            </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Validation des demandes de compléments -->
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
              <span :class="'badge status-' + projet.statut.replace(/ /g, '-')">{{ projet.statut }}</span>
            </div>
            <div class="card-body">
              <p><strong>Auteur:</strong> {{ projet.auteur_nom }}</p>

              <button @click="$router.push(`/project/${projet.id}`)" class="btn-view">Détails</button>

              <!-- Matrice d'évaluation de la recevabilité (en modal pour avoir toute la largeur) -->
              <div v-if="needsEvaluationPrealable(projet)" class="eval-prealable-container">
                <button
                  @click="openEvalPrealableModal(projet.id)"
                  class="btn-toggle-eval-prealable"
                >
                  📋 Ouvrir l'évaluation de la recevabilité
                </button>
              </div>

              <!-- Modal pour l'évaluation de la recevabilité -->
              <div v-if="modalEvalPrealableId === projet.id" class="modal-overlay" @click="closeEvalPrealableModal">
                <div class="modal-content" @click.stop>
                  <button class="modal-close" @click="closeEvalPrealableModal">✕</button>
                  <MatriceEvaluationPrealable
                    :projectId="projet.id"
                    @evaluation-soumise="handleEvaluationPrealableSubmitted"
                  />
                </div>
              </div>

              <!-- Résultat de l'évaluation de la recevabilité -->
              <div class="eval-section eval-prealable-result" v-else-if="projet.evaluation_prealable">
                <h4>🔍 Évaluation de la Recevabilité</h4>
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

              <!-- Interface d'évaluabilité (si recevable mais pas encore évaluable) -->
              <div v-if="needsEvaluabilite(projet)" class="eval-section eval-evaluabilite">
                <h4>📊 Évaluabilité du Dossier</h4>
                <p class="eval-info">Le dossier a été jugé recevable. Vous devez maintenant confirmer qu'il est évaluable.</p>
                <label class="required-label">
                  Commentaires (obligatoire) - Expliquez pourquoi le dossier est évaluable:
                </label>
                <textarea
                  v-model="evaluabiliteCommentaires[projet.id]"
                  rows="3"
                  placeholder="Justifiez pourquoi ce dossier est évaluable..."
                  required
                ></textarea>
                <button
                  @click="marquerEvaluable(projet.id)"
                  class="btn-success"
                  :disabled="envoiEvaluabilite[projet.id] || !evaluabiliteCommentaires[projet.id]?.trim()"
                >
                  {{ envoiEvaluabilite[projet.id] ? '⏳ Envoi en cours...' : '✓ Marquer comme évaluable' }}
                </button>
              </div>

              <!-- Résultat évaluabilité (si déjà marqué évaluable) -->
              <div v-else-if="projet.evaluation_prealable === 'dossier_evaluable' && projet.evaluabilite === 'evaluable'" class="eval-section eval-evaluabilite-result">
                <h4>✅ Dossier Évaluable</h4>
                <p v-if="projet.evaluabilite_commentaire"><strong>Commentaires:</strong> {{ projet.evaluabilite_commentaire }}</p>
                <p class="eval-date" v-if="projet.evaluabilite_date">{{ new Date(projet.evaluabilite_date).toLocaleString('fr-FR') }}</p>
              </div>

              <!-- Bouton Fiche d'évaluation détaillée (uniquement si dossier recevable ET évaluable) -->
              <div v-if="projet.evaluation_prealable === 'dossier_evaluable' && projet.evaluabilite === 'evaluable'" class="eval-section">
                <div class="eval-options">
                  <button @click="$router.push(`/evaluation/${projet.id}`)" class="btn-evaluation-detaillee">
                    📋 Fiche d'évaluation détaillée
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Onglet Décisions du Comité -->
      <div v-if="activeTab === 'decisions-comite'" class="tab-content">
        <h2>🏛️ Décisions du Comité</h2>
        <p class="info-text">Projets recommandés au Comité par la Présidence SCT, en attente de décision finale.</p>

        <div v-if="projectsDecisionsComite.length === 0" class="empty-state">
          <p>Aucun projet en attente de décision du Comité</p>
        </div>

        <div v-else class="projects-compact-grid">
          <div v-for="p in projectsDecisionsComite" :key="p.id" class="project-compact-card">
            <!-- En-tête compacte cliquable -->
            <div class="compact-card-header" @click="toggleProjectExpansion(p.id)">
              <div class="compact-card-top">
                <span class="project-number-badge-small">{{ p.numero_projet || 'N/A' }}</span>
                <span class="badge-small status-comite">🟡 En attente Comité</span>
              </div>
              <h4 class="compact-card-title">{{ p.titre }}</h4>
              <button class="btn-expand-small" @click.stop="toggleProjectExpansion(p.id)">
                {{ expandedProjects[p.id] ? '▲' : '▼ Actions' }}
              </button>
            </div>

            <!-- Carte détaillée (expanded) -->
            <div v-if="expandedProjects[p.id]" class="project-card-expanded">
              <div class="card-header">
                <div class="card-title-section">
                  <div class="project-number">{{ p.numero_projet || 'N/A' }}</div>
                  <h3>{{ p.titre }}</h3>
                </div>
                <span class="badge status-comite">🟡 En attente décision Comité</span>
              </div>
              <div class="card-body">
                <p><strong>Auteur:</strong> {{ p.auteur_nom }}</p>
                <p><strong>Évaluateur:</strong> {{ p.evaluateur_display_name || p.evaluateur_nom || 'Non assigné' }}</p>
                <p><strong>Avis:</strong> <span :class="'avis-' + (p.avis || '').toLowerCase().replace(/ /g, '-')">{{ p.avis }}</span></p>
                <p v-if="p.commentaires"><strong>Commentaires évaluateur:</strong> {{ p.commentaires }}</p>
                <p><strong>Statut SCT:</strong> Validé par Présidence SCT</p>
                <p v-if="p.commentaires_finaux"><strong>Commentaires antérieurs:</strong> {{ p.commentaires_finaux }}</p>
              </div>

              <div class="decision-comite-section">
                <h4>Enregistrer la décision du Comité</h4>

                <!-- Message d'avertissement important -->
                <div class="warning-box">
                  <p style="font-weight: 600; margin-bottom: 0;">⚠️ ATTENTION: À renseigner uniquement après la tenue du Comité (le soumissionnaire sera notifié immédiatement).</p>
                </div>

                <p class="info-small">Le Comité a-t-il entériné ou contesté la recommandation ?</p>

                <div class="decision-buttons">
                  <button @click="enregistrerDecisionComite(p.id, 'enterine')" class="btn-enteriner">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                    Entériner (Approuvé définitivement)
                  </button>
                  <button @click="prepareContesterDecision(p)" class="btn-contester">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M10 9l5 5-5 5M19 9l-5 5 5 5"/>
                      <circle cx="12" cy="12" r="10"/>
                    </svg>
                    Contester (Retour pour réévaluation)
                  </button>
                </div>
              </div>

              <div class="card-footer">
                <button @click="goToProject(p.id)" class="btn-details">Détails complets</button>
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

          <!-- Messages de succès et d'erreur -->
          <div v-if="messageSucces" class="alert alert-success">
            ✓ {{ messageSucces }}
          </div>
          <div v-if="messageErreur" class="alert alert-danger">
            ✗ {{ messageErreur }}
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
              <option value="favorable sous conditions">Favorable sous conditions</option>
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
          <button @click="fermerModalEdition" class="btn-secondary" :disabled="enregistrementEnCours">Annuler</button>
          <button @click="enregistrerEditionFiche" class="btn-primary"
                  :disabled="enregistrementEnCours">
            <span v-if="enregistrementEnCours">⏳ Enregistrement en cours...</span>
            <span v-else>Enregistrer les modifications</span>
          </button>
        </div>
      </div>

      <!-- Tableau de bord statistiques déplacé en bas -->
      <div class="dashboard-section bottom-dashboard">
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
              <div class="metric-value">{{ metrics.averageProcessingTime }}</div>
            </div>

            <div class="metric-card">
              <div class="metric-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
                Taux de validation
              </div>
              <div class="metric-value">{{ metrics.validationRate }}%</div>
            </div>

            <div class="metric-card">
              <div class="metric-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12,6 12,12 16,14"/>
                </svg>
                Délai moyen d'évaluation
              </div>
              <div class="metric-value">{{ metrics.averageEvaluationTime }}</div>
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
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';
import StatsDashboard from '../components/StatsDashboard.vue';
import CartesPolesComparaison from '../components/CartesPolesComparaison.vue';
import MatriceEvaluationPrealable from '../components/MatriceEvaluationPrealable.vue';
import { POLES_TERRITORIAUX } from '../config/polesConfig.js';

export default {
  name: "SecretariatSCT",
  components: { PageWrapper, StatsDashboard, CartesPolesComparaison, MatriceEvaluationPrealable },
  data() {
    return {
      allProjects: [],
      evaluateurs: [],
      autresSecretariatSCT: [], // Autres comptes secretariatsct (hors l'utilisateur connecté)
      currentUser: null, // Utilisateur connecté
      assignation: {},
      motivations: {},
      motivationsResoumission: {},
      erreursResoumission: {},
      activeTab: 'all',
      refreshInterval: null,
      filtreStatut: null,
      searchQuery: '',
      expandedProjects: {},
      financingStats: {
        totalSubmitted: 0,
        countSubmitted: 0,
        totalApproved: 0,
        countApproved: 0
      },
      // Métriques de performance (depuis l'API)
      metrics: {
        averageProcessingTime: '0 jours',
        validationRate: 0,
        averageEvaluationTime: '0 jours'
      },
      // Évaluation préalable
      evaluationPrealableCommentaires: {},
      envoiEvaluationPrealable: {},
      modalEvalPrealableId: null, // ID du projet dont le modal est ouvert dans "Mes évaluations"
      // Évaluabilité
      evaluabiliteCommentaires: {},
      envoiEvaluabilite: {},
      // Édition de fiche
      showModalEdition: false,
      projetEnEdition: {},
      ficheEdition: {
        criteres: {},
        avis: '',
        commentaires: ''
      },
      editionMotif: '',
      enregistrementEnCours: false,
      messageSucces: '',
      messageErreur: '',
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
        { key: 'impact_environnemental', label: 'IMPACTS ENVIRONNEMENTAUX', max: 5 }
      ],
      // Filtres multi-sélection
      showFilters: true,
      selectedYears: [],
      selectedSecteurs: [],
      selectedStatuts: [],
      selectedPoles: [],
      filterGroupsOpen: {
        years: false,
        secteurs: false,
        statuts: false,
        poles: false
      },
      secteurs: [
        'Agriculture et Développement rural',
        'Eau et Assainissement',
        'Éducation et Formation',
        'Énergie',
        'Environnement',
        'Gouvernance',
        'Industrie et Commerce',
        'Justice',
        'Mines',
        'Numérique',
        'Pêche et Aquaculture',
        'Santé',
        'Social',
        'Sport',
        'Tourisme et Artisanat',
        'Transport et Mobilité urbaine',
        'Urbanisme et Habitat'
      ],
      polesList: POLES_TERRITORIAUX
    };
  },
  computed: {
    availableYears() {
      const years = new Set();
      this.allProjects.forEach(p => {
        if (p.date_soumission) {
          const year = new Date(p.date_soumission).getFullYear();
          if (!isNaN(year)) years.add(year);
        }
      });
      return Array.from(years).sort((a, b) => b - a);
    },
    projetsFiltres() {
      let projets = this.allProjects;

      // Filtre par statut (ancien système - via stats cliquables)
      if (this.filtreStatut) {
        projets = projets.filter(p => p.statut === this.filtreStatut);
      }

      // Filtres multi-sélection
      // Filtre par années (multi-select)
      if (this.selectedYears.length > 0) {
        projets = projets.filter(p => {
          if (p.date_soumission) {
            const projectYear = new Date(p.date_soumission).getFullYear();
            return this.selectedYears.includes(projectYear);
          }
          return false;
        });
      }

      // Filtre par secteurs (multi-select)
      if (this.selectedSecteurs.length > 0) {
        projets = projets.filter(p => this.selectedSecteurs.includes(p.secteur));
      }

      // Filtre par statuts (multi-select)
      if (this.selectedStatuts.length > 0) {
        projets = projets.filter(p => this.selectedStatuts.includes(p.statut));
      }

      // Filtre par pôles (multi-select)
      if (this.selectedPoles.length > 0) {
        projets = projets.filter(p =>
          p.poles && this.selectedPoles.some(pole => p.poles.includes(pole))
        );
      }

      // Filtre par recherche
      if (this.searchQuery && this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        projets = projets.filter(p =>
          (p.titre && p.titre.toLowerCase().includes(query)) ||
          (p.auteur_nom && p.auteur_nom.toLowerCase().includes(query)) ||
          (p.numero_projet && p.numero_projet.toLowerCase().includes(query))
        );
      }

      return projets;
    },
    projectsToAssign() {
      // Afficher tous les projets réassignables (non bloqués par validation secrétariat ou décision hiérarchique)
      // Inclure aussi les projets en réexamen (rejetés par Présidence SCT ou Présidence Comité)
      return this.allProjects.filter(p =>
        this.estProjetAssignable(p) ||
        p.statut === 'en réexamen par le Secrétariat SCT'
      );
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
    projectsDecisionsComite() {
      // Projets recommandés au Comité (validés par Présidence SCT) avec statut_comite = 'recommande_comite'
      return this.allProjects.filter(p => p.statut_comite === 'recommande_comite');
    },
    myProjects() {
      // Projets assignés à l'équipe secretariatsct (basé sur est_assigne_a_moi calculé par le backend)
      // Tous les secretariatsct avec le même rôle voient les projets assignés à n'importe quel membre
      return this.allProjects.filter(p =>
        p.est_assigne_a_moi &&
        (p.statut === 'assigné' || p.statut === 'en évaluation')
      );
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
    this.loadMetrics();
  },
  beforeUnmount() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  },
  methods: {
    estProjetAssignable(projet) {
      // Un projet est assignable uniquement s'il n'a PAS de statut définitif
      // Bloquer dès que le secrétariat a validé (montée hiérarchique)
      const aValidationSecretariat = ['valide', 'approuve'].includes(projet.validation_secretariat);

      // Statuts définitifs du workflow (après validation finale)
      const statutsDefinitifs = ['favorable', 'favorable sous conditions', 'défavorable'];
      const aStatutDefinitif = statutsDefinitifs.includes(projet.statut);
      const aDecisionConfirmee = projet.decision_finale === 'confirme';
      const estApprouveDefinitif = projet.statut_comite === 'approuve_definitif';

      // Ne PAS permettre l'assignation/réassignation si validation secrétariat ou statut définitif
      if (aValidationSecretariat || aStatutDefinitif || aDecisionConfirmee || estApprouveDefinitif) {
        return false;
      }

      return true;
    },
    toggleProjectExpansion(projectId) {
      this.expandedProjects[projectId] = !this.expandedProjects[projectId];
      this.$forceUpdate(); // Force Vue to re-render
    },
    toggleFilters() {
      this.showFilters = !this.showFilters;
    },
    toggleFilterGroup(groupName) {
      this.filterGroupsOpen[groupName] = !this.filterGroupsOpen[groupName];
    },
    resetFilters() {
      this.selectedYears = [];
      this.selectedSecteurs = [];
      this.selectedStatuts = [];
      this.selectedPoles = [];
    },
    async exporterProjetsCSV() {
      try {
        const user = JSON.parse(localStorage.getItem("user") || "null") || {};

        if (!user.role || !user.username) {
          alert('Erreur: Utilisateur non connecté');
          return;
        }

        // Construire le message de confirmation avec les filtres actifs
        let filtresActifs = [];
        if (this.selectedYears.length > 0) {
          filtresActifs.push(`Années: ${this.selectedYears.join(', ')}`);
        }
        if (this.selectedStatuts.length > 0) {
          filtresActifs.push(`Statuts: ${this.selectedStatuts.join(', ')}`);
        }
        if (this.selectedSecteurs.length > 0) {
          filtresActifs.push(`Secteurs: ${this.selectedSecteurs.join(', ')}`);
        }
        if (this.selectedPoles.length > 0) {
          filtresActifs.push(`Pôles: ${this.selectedPoles.join(', ')}`);
        }

        const messageConfirmation = filtresActifs.length > 0
          ? `Exporter les projets avec les filtres suivants ?\n\n${filtresActifs.join('\n')}`
          : `Exporter tous les projets ?`;

        if (!confirm(messageConfirmation)) {
          return;
        }

        const params = new URLSearchParams();

        // Appliquer les filtres actifs (multi-valeurs)
        this.selectedStatuts.forEach(statut => params.append('statut', statut));
        this.selectedSecteurs.forEach(secteur => params.append('secteur', secteur));
        this.selectedPoles.forEach(pole => params.append('poles', pole));
        this.selectedYears.forEach(year => params.append('year', year));

        const response = await fetch(`/api/export/projects/csv?${params.toString()}`, {
          headers: {
            'X-Role': user.role,
            'X-Username': user.username
          }
        });

        if (!response.ok) {
          throw new Error('Erreur lors de l\'export CSV');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `projets_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

      } catch (error) {
        console.error('Erreur export CSV:', error);
        alert('Erreur lors de l\'export CSV');
      }
    },
    async loadMetrics() {
      try {
        const response = await fetch('/api/performance-metrics');
        if (response.ok) {
          const data = await response.json();
          this.metrics = {
            averageProcessingTime: data.averageProcessingTime || '0 jours',
            validationRate: data.validationRate || 0,
            averageEvaluationTime: data.averageEvaluationTime || '0 jours'
          };
        }
      } catch (error) {
        console.error('Erreur chargement métriques:', error);
      }
    },
    async loadEvaluateurs() {
      try {
        // Récupérer l'utilisateur connecté
        this.currentUser = JSON.parse(localStorage.getItem("user") || "null") || {};

        const res = await fetch('/api/users');
        if (res.ok) {
          const users = await res.json();
          // Filtrer uniquement les évaluateurs
          this.evaluateurs = users.filter(u => u.role === 'evaluateur');

          // Filtrer les autres comptes secretariatsct (hors l'utilisateur connecté)
          this.autresSecretariatSCT = users.filter(u =>
            u.role === 'secretariatsct' && u.username !== this.currentUser.username
          );
        }
      } catch (error) {
        console.error('Erreur lors du chargement des évaluateurs:', error);
      }
    },
    async ouvrirModalEditionFiche(projet) {
      // Ouvrir un popup avec la page d'édition
      const popupUrl = `/edition-fiche-popup?projetId=${projet.id}`;
      const popupFeatures = 'width=1000,height=800,scrollbars=yes,resizable=yes';
      // Utiliser un nom unique pour forcer le rechargement complet à chaque ouverture
      const uniqueWindowName = `EditionFiche_${Date.now()}`;
      const popup = window.open(popupUrl, uniqueWindowName, popupFeatures);

      if (!popup) {
        alert('Le popup a été bloqué par le navigateur. Veuillez autoriser les popups pour ce site.');
        return;
      }

      // Écouter les messages du popup
      const messageHandler = (event) => {
        console.log('[SecretariatSCT] Message reçu:', event.data);
        console.log('[SecretariatSCT] Origin:', event.origin, 'Expected:', window.location.origin);

        // Vérifier l'origine pour la sécurité
        if (event.origin !== window.location.origin) {
          console.warn('[SecretariatSCT] Message ignoré: origine différente');
          return;
        }

        if (event.data.type === 'ficheUpdated' && event.data.projetId === projet.id) {
          console.log('[SecretariatSCT] Message ficheUpdated reçu, rechargement des projets...');
          // Recharger les projets pour afficher les modifications
          this.chargerProjets();
          window.removeEventListener('message', messageHandler);
          console.log('[SecretariatSCT] Projets rechargés');
        } else {
          console.log('[SecretariatSCT] Message ignoré:', {
            type: event.data.type,
            projetId: event.data.projetId,
            expectedProjetId: projet.id
          });
        }
      };

      window.addEventListener('message', messageHandler);
    },
    fermerModalEdition() {
      this.showModalEdition = false;
      this.projetEnEdition = {};
      this.ficheEdition = { criteres: {}, avis: '', commentaires: '' };
      this.editionMotif = '';
      this.messageSucces = '';
      this.messageErreur = '';
      this.enregistrementEnCours = false;
    },
    calculerScoreTotal() {
      return Object.values(this.ficheEdition.criteres).reduce((sum, c) => sum + (c.score || 0), 0);
    },
    async enregistrerEditionFiche() {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};

      // Réinitialiser les messages
      this.messageSucces = '';
      this.messageErreur = '';
      this.enregistrementEnCours = true;

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

        this.messageSucces = 'Fiche modifiée avec succès! Les modifications ont été enregistrées dans l\'historique.';

        // Recharger les projets
        await this.loadProjects();

        // Fermer le modal après 2 secondes
        setTimeout(() => {
          this.fermerModalEdition();
        }, 2000);
      } catch (error) {
        console.error('Erreur:', error);
        this.messageErreur = 'Erreur lors de l\'enregistrement: ' + error.message;
      } finally {
        this.enregistrementEnCours = false;
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


    parseComplementsFiles(filesString) {
      if (!filesString) return [];
      return filesString.split(',').map(f => f.trim()).filter(f => f.length > 0);
    },

    ouvrirFichier(projectId, fileName) {
      // Ouvrir le fichier dans un nouvel onglet
      // En production sur Render, utiliser l'URL backend complète
      const isProduction = window.location.hostname.includes('render.com');
      const backendUrl = isProduction
        ? 'https://maturation-backend.onrender.com'
        : '';
      const url = `${backendUrl}/api/uploads/${fileName}`;
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
      // Effacer l'erreur précédente
      this.erreursResoumission[id] = null;

      // Récupérer la motivation depuis le textarea
      const motivation = (this.motivationsResoumission[id] || "").trim();

      // Vérification: motif obligatoire pour la resoumission
      if (!motivation) {
        this.erreursResoumission[id] = "La motivation de la resoumission est obligatoire. Veuillez justifier votre décision.";
        return;
      }

      // Confirmer la soumission
      if (!confirm(`Êtes-vous sûr de vouloir soumettre ce projet à la Présidence SCT malgré le rejet ?\n\nMotif: "${motivation}"`)) {
        return;
      }

      const user = JSON.parse(localStorage.getItem("user") || "null") || {};

      try {
        const requestBody = {
          validation_secretariat: "valide",
          statut_action: "resoumission_apres_rejet",
          motivation_resoumission: motivation,
          auteur: user.username,
          role: user.role
        };

        const response = await fetch(`/api/projects/${id}/traiter`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
          throw new Error("Erreur lors de la soumission");
        }

        // Effacer le champ motivation après soumission réussie
        this.motivationsResoumission[id] = "";
        this.erreursResoumission[id] = null;

        alert("Projet soumis à la Présidence SCT");
        this.loadProjects();
      } catch (error) {
        console.error("Erreur:", error);
        alert("Erreur lors de la soumission");
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

      // Appeler l'endpoint d'évaluation de la recevabilité avec role=secretariatsct et decision=dossier_rejete
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
      // Réinitialiser l'évaluation de la recevabilité en réassignant le projet
      await fetch(`/api/projects/${id}/traiter`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          statut_action: "reinitialiser_evaluation", // Réinitialise le projet pour réévaluation
          auteur: user.username,
          role: user.role
        })
      });
      alert("Rejet refusé. Le dossier a été renvoyé en assignation pour réévaluation.");
      this.loadProjects();
    },
    async enregistrerDecisionComite(projectId, decision) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};

      // Demander confirmation
      const confirmMessage = decision === 'enterine'
        ? "Confirmer que le Comité a entériné ce projet (approuvé définitivement) ?"
        : "Confirmer que le Comité a contesté ce projet (retour pour réévaluation) ?";

      if (!confirm(confirmMessage)) {
        return;
      }

      // Si on conteste, demander un commentaire OBLIGATOIRE
      let commentaires = "";
      if (decision === 'conteste') {
        commentaires = prompt("⚠️ Commentaires OBLIGATOIRES pour justifier la contestation du Comité :");
        if (commentaires === null) {
          // L'utilisateur a annulé
          return;
        }
        // Validation : commentaires obligatoires
        if (!commentaires || commentaires.trim() === '') {
          alert("❌ Les commentaires sont obligatoires lorsque le Comité conteste la recommandation.");
          return;
        }
      }

      try {
        const response = await fetch(`/api/projects/${projectId}/decision-comite`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            decision: decision,
            commentaires: commentaires,
            auteur: user.username,
            role: user.role
          })
        });

        if (!response.ok) {
          const error = await response.json();
          alert(`Erreur: ${error.error || 'Impossible d\'enregistrer la décision'}`);
          return;
        }

        const successMessage = decision === 'enterine'
          ? "Décision enregistrée : Projet entériné par le Comité (approuvé définitivement)"
          : "Décision enregistrée : Projet contesté par le Comité, retourné pour réévaluation";

        alert(successMessage);
        await this.loadProjects();
      } catch (error) {
        console.error("Erreur lors de l'enregistrement de la décision:", error);
        alert("Erreur lors de l'enregistrement de la décision");
      }
    },
    prepareContesterDecision(projet) {
      // Simplifiée: appeler directement enregistrerDecisionComite avec 'conteste'
      this.enregistrerDecisionComite(projet.id, 'conteste');
    },
    getStatutBadge(projet) {
      // Fonction helper pour obtenir le badge de statut approprié en tenant compte du statut_comite
      if (projet.statut_comite === 'recommande_comite') {
        return { text: '🟡 En attente décision Comité', class: 'status-comite' };
      } else if (projet.statut_comite === 'approuve_definitif') {
        // Afficher l'avis réel au lieu de "Approuvé définitivement"
        const avisFinal = projet.statut || projet.avis || 'Entériné par le Comité';
        const avisClass = avisFinal === 'favorable' ? 'status-favorable' :
                         avisFinal === 'favorable sous conditions' ? 'status-conditions' :
                         'status-approved-final';
        return { text: avisFinal, class: avisClass };
      } else if (projet.statut_comite === 'en_reevaluation') {
        return { text: '🔄 En réévaluation', class: 'status-reevaluation' };
      }
      // Statut par défaut basé sur le champ statut
      return { text: projet.statut, class: 'status-' + (projet.statut || '').replace(/ /g, '-') };
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
      // Inclure tous les évaluateurs SAUF si le projet est encore dans le panier de l'évaluateur actuel
      // (c'est-à-dire statut 'assigné' ou 'en évaluation')
      // Une fois évalué, l'évaluateur précédent doit pouvoir être réassigné le projet
      if (!projet || !projet.evaluateur_nom) {
        return this.evaluateurs;
      }

      // Seulement filtrer l'évaluateur actuel si le projet est toujours dans son panier
      if (projet.statut === 'assigné' || projet.statut === 'en évaluation') {
        const filtered = this.evaluateurs.filter(e => {
          return e.username !== projet.evaluateur_nom;
        });
        console.log('getAvailableEvaluateurs - Projet dans panier:', projet.numero_projet, 'Assigné à:', projet.evaluateur_nom, 'Filtré');
        return filtered;
      }

      // Pour tous les autres statuts (évalué, rejeté, etc.), inclure tous les évaluateurs
      console.log('getAvailableEvaluateurs - Projet hors panier:', projet.numero_projet, 'Incluant tous les évaluateurs');
      return this.evaluateurs;
    },
    getAvisClass(a){ const m={"favorable":"avis-favorable","favorable sous conditions":"avis-conditions","défavorable":"avis-defavorable","compléments demandés":"avis-complement"}; return m[a]||""; },

    // Nouvelles méthodes pour le tableau de bord
    formatTime(date) {
      return new Date(date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    },
    formatDate(date) {
      if (!date) return 'N/A';
      return new Date(date).toLocaleDateString('fr-FR');
    },
    applyFiltersAll() {
      // Les filtres sont appliqués via le computed projetsFiltres
    },
    resetFiltersAll() {
      this.filtreStatut = null;
      this.searchQuery = '';
    },
    calculateFinancingStats() {
      // Tous les projets soumis
      this.financingStats.countSubmitted = this.allProjects.length;
      this.financingStats.totalSubmitted = this.allProjects.reduce((sum, p) => sum + (p.cout_estimatif || 0), 0);

      // Projets avec décision finale confirmée par la Présidence du Comité
      // ET avec avis favorable ou favorable sous conditions uniquement
      const approvedProjects = this.allProjects.filter(p =>
        p.decision_finale === 'confirme' &&
        (p.avis === 'favorable' || p.avis === 'favorable sous conditions')
      );
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

    async telechargerRapportElabore() {
      try {
        const response = await fetch('/api/admin/rapport-elabore');
        if (!response.ok) {
          throw new Error('Erreur lors de la génération du rapport élaboré');
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `rapport_elabore_dgppe_${new Date().toISOString().split('T')[0]}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Erreur téléchargement rapport élaboré:', error);
        alert('Erreur lors du téléchargement du rapport élaboré');
      }
    },

    // Méthodes pour l'évaluation de la recevabilité
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
          message = "✅ Dossier marqué comme recevable. Vous pouvez maintenant procéder à l'évaluation détaillée.";
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

    // Méthode appelée par le composant MatriceEvaluationPrealable
    async handleEvaluationPrealableSubmitted() {
      // Fermer la modal
      this.closeEvalPrealableModal();
      // Recharger la liste des projets après soumission
      await this.loadProjects();
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
        'dossier_evaluable': '✅ Dossier recevable',
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
    },

    // Détermine si un projet nécessite une évaluation d'évaluabilité
    needsEvaluabilite(project) {
      // L'interface d'évaluabilité est affichée si:
      // - Le dossier est recevable (evaluation_prealable === "dossier_evaluable")
      // - L'évaluabilité n'a pas encore été définie (evaluabilite === null)
      // - Le statut est "en évaluation" ou "assigné"
      return project.evaluation_prealable === "dossier_evaluable" &&
             !project.evaluabilite &&
             (project.statut === "en évaluation" || project.statut === "assigné");
    },

    async marquerEvaluable(projectId) {
      const user = JSON.parse(localStorage.getItem("user") || "null") || {};
      const commentaire = (this.evaluabiliteCommentaires[projectId] || "").trim();

      // Validation: commentaires obligatoires
      if (!commentaire) {
        alert("⚠️ Les commentaires sont obligatoires pour justifier l'évaluabilité du dossier.");
        return;
      }

      this.envoiEvaluabilite[projectId] = true;

      try {
        const response = await fetch(`/api/projects/${projectId}/evaluabilite`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            decision: "evaluable",
            commentaire: commentaire,
            auteur: user.username,
            role: user.role
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || "Erreur lors de l'enregistrement");
        }

        alert("✅ Dossier marqué comme évaluable. Vous pouvez maintenant accéder à la fiche d'évaluation détaillée.");
        this.evaluabiliteCommentaires[projectId] = "";
        await this.loadProjects();
      } catch (error) {
        alert("Erreur: " + error.message);
      } finally {
        this.envoiEvaluabilite[projectId] = false;
      }
    },

    // Détermine si un projet nécessite une évaluation de la recevabilité
    needsEvaluationPrealable(project) {
      // Afficher l'interface d'évaluation de la recevabilité si:
      // - Le projet est assigné OU en évaluation, ET aucune évaluation de la recevabilité n'a été faite
      // OU
      // - Des compléments ont été demandés ET le soumissionnaire a répondu
      const statutsEligibles = ["assigné", "en évaluation"];
      const isInitialAssignment = statutsEligibles.includes(project.statut) && !project.evaluation_prealable;
      const hasReceivedComplements = project.evaluation_prealable === "complements_requis" &&
                                     project.complements_reponse_message &&
                                     project.complements_reponse_message.trim() !== "";

      return isInitialAssignment || hasReceivedComplements;
    },

    // Toggle pour afficher/masquer la matrice d'évaluation de la recevabilité dans "Mes évaluations"
    // Ouvrir le modal d'évaluation de la recevabilité
    openEvalPrealableModal(projectId) {
      this.modalEvalPrealableId = projectId;
    },
    // Fermer le modal d'évaluation de la recevabilité
    closeEvalPrealableModal() {
      this.modalEvalPrealableId = null;
    },

    // Méthode appelée après soumission de la matrice d'évaluation de la recevabilité
    async handleEvaluationPrealableSubmitted() {
      // Fermer le modal et recharger la page
      this.modalEvalPrealableId = null;
      window.location.reload();
    },

    commencerEvaluation(projetId) {
      // Basculer vers l'onglet "Mes évaluations"
      this.activeTab = 'evaluation';
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

.header-buttons {
  display: flex;
  gap: 12px;
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

.btn-download-rapport.elabore {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.btn-download-rapport:hover {
  background: var(--dgppe-secondary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-download-rapport.elabore:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.btn-download-rapport.soumissionnaires-btn {
  background: #6366f1;
  border: 2px solid #6366f1;
}

.btn-download-rapport.soumissionnaires-btn:hover {
  background: #4f46e5;
  border-color: #4f46e5;
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
.performance-metrics {
  margin-top: 3rem;
  padding-top: 2rem;
  border-top: 2px solid #e5e7eb;
}

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
.badge { padding:.25rem .6rem; border-radius:999px; font-size:.8rem; font-weight:700; display: inline-block; }

/* Classes de statuts uniformisées */
.status-new { background: #3b82f6 !important; color: white !important; }
.status-assigned { background: #f59e0b !important; color: white !important; }
.status-processing { background: #0ea5e9 !important; color: white !important; }
.status-evaluated { background: #8b5cf6 !important; color: white !important; }
.status-complement { background: #f97316 !important; color: white !important; }
.status-info { background: #3b82f6 !important; color: white !important; }
.status-pending { background: #8b5cf6 !important; color: white !important; }
.status-validated-sec { background: #22c55e !important; color: white !important; }
.status-validated { background: #10b981 !important; color: white !important; }
.status-favorable { background: #10b981 !important; color: white !important; }
.status-conditions { background: #f59e0b !important; color: white !important; }
.status-defavorable { background: #ef4444 !important; color: white !important; }
.status-default { background: #6b7280 !important; color: white !important; }

/* Statuts avec tirets (pour compatibilité avec replace) */
.status-soumis { background: #3b82f6 !important; color: white !important; }
.status-assigné { background: #f59e0b !important; color: white !important; }
.status-en-instruction { background: #0ea5e9 !important; color: white !important; }
.status-en-évaluation { background: #0ea5e9 !important; color: white !important; }
.status-évalué { background: #8b5cf6 !important; color: white !important; }
.status-compléments-demandés { background: #f97316 !important; color: white !important; }
.status-compléments-fournis { background: #3b82f6 !important; color: white !important; }
.status-en-attente-validation-presidencesct { background: #8b5cf6 !important; color: white !important; }
.status-validé-par-presidencesct { background: #22c55e !important; color: white !important; }
.status-validé-par-presidencecomite { background: #10b981 !important; color: white !important; }
.status-favorable { background: #10b981 !important; color: white !important; }
.status-favorable-sous-conditions { background: #f59e0b !important; color: white !important; }
.status-défavorable { background: #ef4444 !important; color: white !important; }
.status-approuvé-définitivement-par-le-Comité { background: #10b981 !important; color: white !important; }
.status-rejeté { background: #ef4444 !important; color: white !important; }
.status-avis-défavorable-confirmé { background: #ef4444 !important; color: white !important; }
.status-en-réexamen-par-le-Secrétariat-SCT { background: #0ea5e9 !important; color: white !important; }
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
.avis-favorable{color:#10b981 !important;font-weight:600 !important}.avis-conditions{color:#f59e0b !important;font-weight:600 !important}.avis-defavorable{color:#ef4444 !important;font-weight:600 !important}.avis-complement{color:#f97316 !important;font-weight:600 !important}

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

.resubmission-motivation {
  margin: 1rem 0;
}

.motivation-message {
  background: #eff6ff;
  padding: 0.75rem;
  border-radius: 6px;
  margin-top: 0.5rem;
  border: 1px solid #bfdbfe;
  color: #1e40af;
  font-style: italic;
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

/* Alerte réexamen après infirmation */
.reexamen-alert {
  background: #fffbeb;
  border: 2px solid #fbbf24;
  border-radius: 10px;
  padding: 15px;
  margin: 12px 0;
}

.reexamen-alert .alert-warning {
  background: #fef3c7;
  color: #92400e;
  padding: 12px;
  border-radius: 8px;
  border-left: 4px solid #f59e0b;
  margin-bottom: 12px;
}

.reexamen-alert .alert-warning strong {
  display: block;
  font-size: 1rem;
  margin-bottom: 4px;
}

.reexamen-alert .alert-warning p {
  margin: 0;
  font-size: 0.9rem;
}

.motif-infirmation {
  background: white;
  border: 1px solid #fcd34d;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 10px;
}

.motif-infirmation strong {
  color: #b45309;
  display: block;
  margin-bottom: 6px;
}

.motif-text {
  margin: 0;
  color: #451a03;
  font-style: italic;
  line-height: 1.5;
}

.action-required {
  color: #92400e;
  font-weight: 500;
  font-size: 0.9rem;
  margin: 0;
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
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Puces colorées pour les options */
.action-bullet {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.85rem;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.action-bullet.orange {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.action-bullet.blue {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

.action-bullet.red {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

/* Bordures colorées pour les groupes d'action */
.action-group-orange {
  border-left: 4px solid #f59e0b;
  padding-left: 15px;
  margin-bottom: 20px;
}

.action-group-blue {
  border-left: 4px solid #3b82f6;
  padding-left: 15px;
  margin-bottom: 20px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.action-group-red {
  border-left: 4px solid #ef4444;
  padding-left: 15px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
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

/* Styles pour l'évaluation de la recevabilité */
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

/* Styles pour l'interface d'évaluabilité */
.eval-evaluabilite {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border: 2px solid #3b82f6;
  border-radius: 10px;
  padding: 1.25rem;
  margin-top: 1rem;
}

.eval-evaluabilite h4 {
  color: #1e40af;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  font-weight: 700;
}

.eval-evaluabilite .eval-info {
  color: #1e40af;
  margin-bottom: 1rem;
  font-size: 0.95rem;
}

.eval-evaluabilite .required-label {
  display: block;
  font-weight: 600;
  color: #1e3a8a;
  margin-bottom: 0.5rem;
}

.eval-evaluabilite .required-label::after {
  content: " *";
  color: #dc2626;
}

.eval-evaluabilite textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #93c5fd;
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: inherit;
  margin-bottom: 1rem;
  resize: vertical;
  min-height: 80px;
}

.eval-evaluabilite textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.eval-evaluabilite-result {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 2px solid #22c55e;
  border-radius: 10px;
  padding: 1.25rem;
  margin-top: 1rem;
}

.eval-evaluabilite-result h4 {
  color: #15803d;
  margin: 0 0 0.75rem 0;
  font-size: 1.1rem;
  font-weight: 700;
}

.eval-evaluabilite-result p {
  margin: 0.5rem 0;
  color: #166534;
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
  background: #fef2f2;
  border: 2px solid #ef4444;
  border-radius: 8px;
  margin-bottom: 1rem;
  color: #991b1b;
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

/* Style pour le bouton Fiche d'évaluation détaillée */
.btn-evaluation-detaillee {
  width: 100%;
  padding: 12px 20px;
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.btn-evaluation-detaillee:hover {
  background: linear-gradient(135deg, #229954 0%, #27ae60 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(39, 174, 96, 0.4);
}

/* Styles pour vue tableau */
.projects-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.project-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  font-size: 14px;
  color: #666;
}

.stat-item strong {
  color: var(--dgppe-primary);
  font-size: 16px;
}

.filters-container {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-size: 13px;
  font-weight: 600;
  color: #555;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.btn-reset {
  padding: 8px 16px;
  background: #e0e0e0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
}

.btn-reset:hover {
  background: #d0d0d0;
}

.projects-table-container {
  overflow-x: auto;
}

.projects-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.projects-table thead {
  background: var(--dgppe-primary);
  color: white;
}

.projects-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
}

.projects-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.projects-table tbody tr:hover {
  background: #f9f9f9;
}

.project-number-table {
  color: var(--dgppe-accent);
  font-weight: 700;
}

.project-title {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-view-small {
  padding: 6px 12px;
  background: var(--dgppe-accent);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.btn-view-small:hover {
  background: var(--dgppe-secondary);
  transform: scale(1.1);
}

/* Filtres multi-sélection */
.filters-compact {
  margin-bottom: 1rem;
}

.btn-toggle-filters {
  padding: 10px 20px;
  background: white;
  border: 2px solid var(--dgppe-primary);
  color: var(--dgppe-primary);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-toggle-filters:hover {
  background: var(--dgppe-primary);
  color: white;
}

.btn-export-csv {
  padding: 10px 20px;
  background: #10b981;
  border: 2px solid #10b981;
  color: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-export-csv:hover {
  background: #059669;
  border-color: #059669;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.btn-export-csv svg {
  flex-shrink: 0;
}

.filters-container {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.filter-group {
  flex: 1;
  min-width: 180px;
}

.filter-label {
  display: block;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.filter-label.collapsible {
  cursor: pointer;
  user-select: none;
  transition: color 0.2s;
}

.filter-label.collapsible:hover {
  color: var(--dgppe-primary);
}

.collapse-icon {
  display: inline-block;
  width: 16px;
  font-size: 0.8rem;
  color: var(--dgppe-primary);
}

.filter-count {
  color: var(--dgppe-accent);
  font-weight: 700;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s;
}

.checkbox-label:hover {
  background: #f3f4f6;
}

.checkbox-label input[type="checkbox"] {
  cursor: pointer;
}

.btn-reset {
  padding: 8px 16px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  align-self: flex-start;
}

.btn-reset:hover {
  background: #dc2626;
  transform: translateY(-1px);
}

.export-csv {
  background: #059669;
}

.export-csv:hover {
  background: #047857;
}

/* Ces classes sont déjà définies plus haut - supprimées pour éviter les doublons */

.rejection-text {
  font-style: italic;
  color: #dc2626;
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.search-and-filters {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 20px;
}

.search-bar-container {
  flex: 0 1 400px;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: var(--dgppe-primary);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.action-buttons {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
  justify-content: center;
}

/* Vue compacte avec expansion */
.projects-compact-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.project-compact-item {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  transition: all 0.2s;
}

.project-compact-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.compact-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  background: #f9fafb;
  transition: background 0.2s;
}

.compact-row:hover {
  background: #f3f4f6;
}

.compact-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.project-number-badge {
  background: var(--dgppe-primary);
  color: white;
  padding: 4px 12px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.85rem;
  white-space: nowrap;
  flex-shrink: 0;
}

.project-title-compact {
  font-size: 0.95rem;
  font-weight: 500;
  color: #1f2937;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.compact-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.btn-expand {
  padding: 6px 12px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-expand:hover {
  background: var(--dgppe-primary);
  color: white;
  border-color: var(--dgppe-primary);
}

.project-card-expanded {
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  background: white;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 2000px;
  }
}

/* Vue grille compacte pour Assignation */
.projects-compact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.project-compact-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  overflow: hidden;
  transition: all 0.2s;
}

.project-compact-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.compact-card-header {
  padding: 12px;
  cursor: pointer;
  background: #f9fafb;
  transition: background 0.2s;
}

.compact-card-header:hover {
  background: #f3f4f6;
}

.compact-card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.project-number-badge-small {
  background: var(--dgppe-primary);
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.75rem;
}

.badge-small {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.7rem;
  font-weight: 600;
}

.compact-card-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: #1f2937;
  margin: 0 0 8px 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 2.6em;
}

.btn-expand-small {
  width: 100%;
  padding: 6px 10px;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.btn-expand-small:hover {
  background: var(--dgppe-primary);
  color: white;
  border-color: var(--dgppe-primary);
}

/* Styles pour l'onglet Décisions du Comité */
.decision-comite-section {
  background: #fef3c7;
  border-left: 4px solid #f59e0b;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 4px;
}

.decision-comite-section h4 {
  margin: 0 0 0.5rem 0;
  color: #92400e;
  font-size: 0.95rem;
}

.info-small {
  font-size: 0.85rem;
  color: #78350f;
  margin-bottom: 0.75rem;
}

.decision-buttons {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-enteriner,
.btn-contester {
  flex: 1;
  min-width: 200px;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-enteriner {
  background: #10b981;
  color: white;
}

.btn-enteriner:hover {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-contester {
  background: #ef4444;
  color: white;
}

.btn-contester:hover {
  background: #dc2626;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.status-comite {
  background: #f59e0b !important;
  color: white !important;
}

.status-approved-final {
  background: #10b981 !important;
  color: white !important;
  font-weight: 600;
}

.status-reevaluation {
  background: #0ea5e9 !important;
  color: white !important;
}

.info-text {
  background: #e0f2fe;
  border-left: 4px solid #0284c7;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  border-radius: 4px;
  color: #075985;
  font-size: 0.9rem;
}

/* Style pour les projets dont le compte soumissionnaire n'est pas vérifié */
tr.compte-non-verifie {
  background-color: #fef3c7 !important;
  opacity: 0.7;
}

tr.compte-non-verifie:hover {
  background-color: #fde68a !important;
  opacity: 0.85;
}

/* Style pour les cartes compactes avec compte non vérifié */
.project-compact-card.compte-non-verifie {
  background-color: #fef3c7 !important;
  opacity: 0.7;
  border-color: #fbbf24 !important;
}

.project-compact-card.compte-non-verifie:hover {
  background-color: #fde68a !important;
  opacity: 0.85;
}

.status-warning {
  background: #fbbf24 !important;
  color: #78350f !important;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  white-space: nowrap;
}

/* Ligne séparée pour le badge d'avertissement compte non vérifié */
.warning-badge-row {
  margin: 6px 0;
  display: flex;
  align-items: center;
}

/* Section collapsible pour l'évaluation de la recevabilité */
.eval-prealable-container {
  padding: 1.5rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  margin-top: 1rem;
}

.btn-toggle-eval-prealable {
  width: 100%;
  padding: 12px 20px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn-toggle-eval-prealable:hover {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

/* Modal overlay pour l'évaluation de la recevabilité */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 1400px;
  width: 100%;
  max-height: none;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  margin: 20px 0;
}

.modal-close {
  position: sticky;
  top: 10px;
  right: 10px;
  float: right;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.modal-close:hover {
  background: #dc2626;
  transform: scale(1.1);
}
</style>