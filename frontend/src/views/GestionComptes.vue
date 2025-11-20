<template>
  <PageWrapper>
    <div class="gestion-comptes-page">
      <div class="header-section">
        <div class="header-with-back">
          <button @click="retourDashboard" class="btn-retour">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Retour au tableau de bord
          </button>
          <div class="header-content">
            <h1>Gestion des comptes et messages</h1>
            <p class="subtitle">Validation des comptes et traitement des demandes</p>
          </div>
        </div>

        <!-- Onglets -->
        <div class="tabs-container">
          <button
            :class="['tab-btn', { active: activeTab === 'comptes' }]"
            @click="activeTab = 'comptes'"
          >
            Comptes soumissionnaires
            <span v-if="stats.non_verifie > 0" class="tab-badge">{{ stats.non_verifie }}</span>
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'messages' }]"
            @click="activeTab = 'messages'; chargerMessages()"
          >
            Messages de contact
            <span v-if="messagesNonLus > 0" class="tab-badge">{{ messagesNonLus }}</span>
          </button>
        </div>
      </div>

    <!-- Contenu onglet Comptes -->
    <div v-if="activeTab === 'comptes'">

    <!-- Filtres -->
    <div class="filters-section">
      <div class="filter-group">
        <label>Filtrer par statut :</label>
        <select v-model="filtreStatut" @change="chargerComptes">
          <option value="">Tous les comptes</option>
          <option value="non_verifie">Non vérifiés</option>
          <option value="verifie">Vérifiés</option>
          <option value="suspendu">Suspendus</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Rechercher :</label>
        <input
          v-model="rechercheTexte"
          type="text"
          placeholder="Nom, structure, email..."
          @input="filtrerComptes"
        />
      </div>
    </div>

    <!-- Statistiques rapides -->
    <div class="stats-section">
      <div class="stat-card non-verifie">
        <div class="stat-icon">⚠️</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.non_verifie }}</div>
          <div class="stat-label">Non vérifiés</div>
        </div>
      </div>
      <div class="stat-card verifie">
        <div class="stat-icon">✓</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.verifie }}</div>
          <div class="stat-label">Vérifiés</div>
        </div>
      </div>
      <div class="stat-card suspendu">
        <div class="stat-icon">🔴</div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.suspendu }}</div>
          <div class="stat-label">Suspendus</div>
        </div>
      </div>
    </div>

    <!-- Tableau des comptes -->
    <div class="comptes-table-container">
      <div v-if="loading" class="loading">Chargement des comptes...</div>
      <div v-else-if="error" class="error-message">{{ error }}</div>
      <div v-else-if="comptesFiltres.length === 0" class="no-data">
        Aucun compte trouvé avec ces critères
      </div>

      <table v-else class="comptes-table">
        <thead>
          <tr>
            <th>Utilisateur</th>
            <th>Structure</th>
            <th>Contact</th>
            <th>Date création</th>
            <th>Statut</th>
            <th>Justificatif</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="compte in comptesFiltres" :key="compte.id">
            <td>
              <div class="user-info">
                <div class="user-name">{{ compte.display_name || compte.username }}</div>
                <div class="user-email">{{ compte.username }}</div>
                <div v-if="compte.fonction" class="user-fonction">{{ compte.fonction }}</div>
              </div>
            </td>
            <td>
              <div class="structure-info">
                <div v-if="compte.type_structure || compte.nom_structure" class="structure-hierarchy-compact">
                  <div v-if="compte.type_structure" class="structure-type">{{ getTypeStructureLabel(compte.type_structure) }}</div>
                  <div v-if="compte.type_institution" class="structure-subtype">→ {{ getTypeInstitutionLabel(compte.type_institution) }}</div>
                  <div v-if="compte.nom_structure" class="structure-nom">{{ compte.nom_structure }}</div>
                  <div v-if="compte.direction_service" class="structure-direction">{{ compte.direction_service }}</div>
                </div>
                <div v-else class="structure-empty">N/A</div>
              </div>
            </td>
            <td>
              <div class="contact-info">
                <div class="contact-email">✉️ {{ compte.username }}</div>
              </div>
            </td>
            <td>
              <div class="date-info">
                {{ formatDate(compte.date_creation) }}
              </div>
            </td>
            <td>
              <span :class="['badge-statut', compte.statut_compte || 'non_verifie']">
                {{ formatStatut(compte.statut_compte) }}
              </span>
              <div v-if="compte.verifie_par" class="verif-info">
                Par {{ compte.verifie_par }}
              </div>
            </td>
            <td>
              <button
                v-if="compte.justificatif_path"
                @click="voirJustificatif(compte.justificatif_path)"
                class="btn-voir-justificatif"
              >
                📄 Voir
              </button>
              <span v-else class="no-justificatif">Non fourni</span>
            </td>
            <td>
              <div class="actions-buttons">
                <button
                  v-if="compte.statut_compte === 'non_verifie'"
                  @click="verifierCompte(compte.id)"
                  class="btn-action btn-verify"
                  :disabled="actionEnCours === compte.id"
                >
                  {{ actionEnCours === compte.id ? '...' : '✓ Vérifier' }}
                </button>
                <button
                  v-if="compte.statut_compte === 'verifie' || compte.statut_compte === 'non_verifie'"
                  @click="suspendreCompte(compte.id)"
                  class="btn-action btn-suspend"
                  :disabled="actionEnCours === compte.id"
                >
                  {{ actionEnCours === compte.id ? '...' : '🔴 Suspendre' }}
                </button>
                <button
                  v-if="compte.statut_compte === 'suspendu'"
                  @click="reintegrerCompte(compte.id)"
                  class="btn-action btn-reintegrate"
                  :disabled="actionEnCours === compte.id"
                >
                  {{ actionEnCours === compte.id ? '...' : '✅ Réintégrer' }}
                </button>
                <button
                  @click="voirDetails(compte)"
                  class="btn-action btn-details"
                >
                  👁️ Détails
                </button>
                <button
                  @click="supprimerCompte(compte.id, compte.username)"
                  class="btn-action btn-delete"
                  :disabled="actionEnCours === compte.id"
                >
                  {{ actionEnCours === compte.id ? '...' : '🗑️ Supprimer' }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    </div><!-- Fin onglet Comptes -->

    <!-- Contenu onglet Messages de contact -->
    <div v-if="activeTab === 'messages'" class="messages-section">
      <div class="messages-filters">
        <div class="filter-group">
          <label>Filtrer par statut :</label>
          <select v-model="filtreStatutMessage" @change="filtrerMessages">
            <option value="">Tous les messages</option>
            <option value="nouveau">Non lus</option>
            <option value="lu">Lus</option>
            <option value="traite">Traités</option>
          </select>
        </div>
      </div>

      <div v-if="loadingMessages" class="loading">Chargement des messages...</div>
      <div v-else-if="messagesContact.length === 0" class="no-data">
        Aucun message de contact
      </div>

      <div v-else class="messages-list">
        <div
          v-for="msg in messagesFiltres"
          :key="msg.id"
          :class="['message-card', { 'non-lu': msg.statut === 'nouveau' }]"
        >
          <div class="message-header">
            <div class="message-info">
              <span class="message-nom">{{ msg.nom }}</span>
              <span class="message-email">{{ msg.email }}</span>
              <span v-if="msg.telephone" class="message-tel">{{ msg.telephone }}</span>
            </div>
            <div class="message-meta">
              <span :class="['message-statut', msg.statut]">{{ formatStatutMessage(msg.statut) }}</span>
              <span class="message-date">{{ formatDate(msg.date_creation) }}</span>
            </div>
          </div>
          <div class="message-objet">
            <strong>{{ msg.objet }}</strong>
          </div>
          <div class="message-contenu">
            {{ msg.message }}
          </div>
          <div v-if="msg.pieces_jointes && msg.pieces_jointes.length > 0" class="message-pieces">
            <span class="pieces-label">Pièces jointes:</span>
            <a
              v-for="(pj, idx) in msg.pieces_jointes"
              :key="idx"
              :href="`${backendUrl}/api/uploads/${pj}`"
              target="_blank"
              class="piece-link"
            >
              📎 {{ pj.split('/').pop() }}
            </a>
          </div>
          <div v-if="msg.reponse" class="message-reponse">
            <strong>Réponse ({{ msg.traite_par }}):</strong>
            <p>{{ msg.reponse }}</p>
          </div>
          <div class="message-actions">
            <button
              v-if="msg.statut === 'nouveau'"
              @click="marquerLu(msg.id)"
              class="btn-action btn-lu"
            >
              ✓ Marquer lu
            </button>
            <button
              @click="ouvrirModalReponse(msg)"
              class="btn-action btn-repondre"
            >
              ✉️ Répondre
            </button>
          </div>
        </div>
      </div>
    </div><!-- Fin onglet Messages -->

    <!-- Modal réponse message -->
    <div v-if="messageSelectionne" class="modal-overlay" @click.self="fermerModalMessage">
      <div class="modal-content modal-message">
        <div class="modal-header">
          <h2>Répondre au message</h2>
          <button @click="fermerModalMessage" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="message-detail">
            <p><strong>De:</strong> {{ messageSelectionne.nom }} ({{ messageSelectionne.email }})</p>
            <p><strong>Objet:</strong> {{ messageSelectionne.objet }}</p>
            <p><strong>Message:</strong></p>
            <div class="message-original">{{ messageSelectionne.message }}</div>
          </div>
          <div class="form-group-modal">
            <label>Votre réponse :</label>
            <textarea
              v-model="reponseMessage"
              rows="6"
              placeholder="Tapez votre réponse ici..."
            ></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="fermerModalMessage" class="btn-modal-cancel">
              Annuler
            </button>
            <button @click="envoyerReponse" class="btn-modal-save" :disabled="!reponseMessage.trim()">
              Envoyer la réponse
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal édition des détails -->
    <div v-if="compteSelectionne" class="modal-overlay" @click.self="fermerDetails">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Modifier le compte</h2>
          <button @click="fermerDetails" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="sauvegarderModifications" class="edit-form">
            <div class="form-group-modal">
              <label>Nom complet :</label>
              <input
                v-model="compteSelectionne.display_name"
                type="text"
                placeholder="Nom complet de l'utilisateur"
              />
            </div>
            <div class="form-group-modal">
              <label>Email :</label>
              <input
                v-model="compteSelectionne.username"
                type="email"
                placeholder="Email de l'utilisateur"
                readonly
                class="readonly-field"
              />
              <small class="field-hint">L'email ne peut pas être modifié</small>
            </div>
            <div class="form-group-modal">
              <label>Téléphone :</label>
              <input
                v-model="compteSelectionne.telephone"
                type="tel"
                placeholder="+221 XX XXX XX XX"
                @focus="initTelephone"
              />
            </div>
            <div class="form-group-modal">
              <label>Fonction :</label>
              <input
                v-model="compteSelectionne.fonction"
                type="text"
                placeholder="Fonction de l'utilisateur"
              />
            </div>

            <!-- Structure d'appartenance - Formulaire hiérarchique identique à Register.vue -->
            <div class="form-group-modal">
              <label>Structure d'appartenance</label>
              <small class="field-hint">Ces champs définissent l'organisme de tutelle qui sera pré-rempli lors de la soumission de projets</small>
            </div>

            <div class="form-group-modal">
              <label for="edit-type-structure">Type de structure *</label>
              <select id="edit-type-structure" v-model="editTypeStructure" @change="onEditTypeStructureChange" required>
                <option value="">-- Sélectionnez --</option>
                <option value="institution">Institution</option>
                <option value="collectivite">Collectivité territoriale</option>
                <option value="agence">Agence / Établissement public</option>
                <option value="autre">Autre (ONG, Association, Cabinet, etc.)</option>
              </select>
            </div>

            <!-- Institution - avec sous-catégories -->
            <div v-if="editTypeStructure === 'institution'">
              <div class="form-group-modal">
                <label for="edit-type-institution">Type d'institution *</label>
                <select id="edit-type-institution" v-model="editTypeInstitution" @change="onEditTypeInstitutionChange" required>
                  <option value="">-- Sélectionnez --</option>
                  <option value="presidence">Présidence de la République</option>
                  <option value="primature">Primature</option>
                  <option value="ministere">Ministère / Direction nationale</option>
                  <option value="autre_institution">Autre Institution</option>
                </select>
              </div>

              <!-- Champ pour préciser l'institution si "Autre Institution" -->
              <div v-if="editTypeInstitution === 'autre_institution'" class="form-group-modal">
                <label for="edit-nom-institution">Nom de l'institution *</label>
                <input
                  id="edit-nom-institution"
                  v-model="editNomInstitution"
                  placeholder="Ex: Assemblée nationale"
                  required
                />
              </div>

              <!-- Champ pour sélectionner le ministère -->
              <div v-if="editTypeInstitution === 'ministere'" class="form-group-modal">
                <label for="edit-nom-ministere">Nom du ministère / Direction nationale *</label>
                <select
                  id="edit-nom-ministere"
                  v-model="editNomMinistere"
                  @change="onEditMinistereChange"
                  required
                >
                  <option value="">-- Sélectionnez un ministère --</option>
                  <option v-for="ministere in ministeresActifs" :key="ministere.id" :value="ministere.nom_complet">
                    {{ ministere.nom_complet }}
                  </option>
                  <option value="__autre__">Autre (non listé)</option>
                </select>
              </div>

              <!-- Champ libre si "Autre" est sélectionné -->
              <div v-if="editNomMinistere === '__autre__'" class="form-group-modal">
                <label for="edit-nom-ministere-libre">Nom du ministère *</label>
                <input
                  id="edit-nom-ministere-libre"
                  v-model="editNomMinistereLibre"
                  placeholder="Ex: Autre ministère ou direction nationale"
                  required
                />
              </div>

              <!-- Direction/Service - commun à tous les types d'institution -->
              <div class="form-group-modal">
                <label for="edit-direction-service">Direction / Service *</label>
                <input
                  id="edit-direction-service"
                  v-model="editDirectionService"
                  placeholder="Ex: Direction Générale de la Planification des Politiques Économiques (DGPPE)"
                  required
                />
              </div>
            </div>

            <!-- Collectivité territoriale - sélection en cascade -->
            <div v-else-if="editTypeStructure === 'collectivite'">
              <div class="form-group-modal">
                <label for="edit-niveau-collectivite">Niveau *</label>
                <select id="edit-niveau-collectivite" v-model="editNiveauCollectivite" @change="onEditNiveauCollectiviteChange" required>
                  <option value="">-- Sélectionnez le niveau --</option>
                  <option value="region">Région</option>
                  <option value="departement">Département</option>
                  <option value="commune">Commune</option>
                </select>
              </div>

              <!-- Si région sélectionnée -->
              <div v-if="editNiveauCollectivite === 'region'" class="form-group-modal">
                <label for="edit-nom-structure-region">Région *</label>
                <select id="edit-nom-structure-region" v-model="editNomStructure" required>
                  <option value="">-- Sélectionnez une région --</option>
                  <option v-for="region in regions" :key="region" :value="`Région de ${region}`">
                    Région de {{ region }}
                  </option>
                </select>
              </div>

              <!-- Si département sélectionné -->
              <div v-if="editNiveauCollectivite === 'departement'">
                <div class="form-group-modal">
                  <label for="edit-region-parent">Région *</label>
                  <select id="edit-region-parent" v-model="editRegionParente" @change="onEditRegionChange" required>
                    <option value="">-- Sélectionnez une région --</option>
                    <option v-for="region in regions" :key="region" :value="region">
                      {{ region }}
                    </option>
                  </select>
                </div>
                <div class="form-group-modal">
                  <label for="edit-nom-structure-dept">Département *</label>
                  <select id="edit-nom-structure-dept" v-model="editNomStructure" :disabled="!editRegionParente" required>
                    <option value="">-- Sélectionnez un département --</option>
                    <option v-for="dept in editDepartementsFiltered" :key="dept" :value="`Département de ${dept}`">
                      Département de {{ dept }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- Si commune sélectionnée -->
              <div v-if="editNiveauCollectivite === 'commune'">
                <div class="form-group-modal">
                  <label for="edit-region-parent-commune">Région *</label>
                  <select id="edit-region-parent-commune" v-model="editRegionParente" @change="onEditRegionChangeCommunes" required>
                    <option value="">-- Sélectionnez une région --</option>
                    <option v-for="region in regions" :key="region" :value="region">
                      {{ region }}
                    </option>
                  </select>
                </div>

                <div class="form-group-modal">
                  <label for="edit-departement-parent">Département *</label>
                  <select id="edit-departement-parent" v-model="editDepartementParent" @change="onEditDepartementChangeCommunes" :disabled="!editRegionParente" required>
                    <option value="">-- Sélectionnez un département --</option>
                    <option v-for="dept in editDepartementsFiltered" :key="dept" :value="dept">
                      {{ dept }}
                    </option>
                  </select>
                </div>

                <div class="form-group-modal">
                  <label for="edit-commune-select">Commune *</label>
                  <select id="edit-commune-select" v-model="editCommuneSelectionnee" @change="onEditCommuneChange" :disabled="!editDepartementParent" required>
                    <option value="">-- Sélectionnez une commune --</option>
                    <option v-for="commune in editCommunesFiltered" :key="commune" :value="commune">
                      {{ commune }}
                    </option>
                    <option value="__autre__">Autre commune (non listée)</option>
                  </select>
                </div>

                <!-- Champ de saisie libre si "Autre commune" est sélectionnée -->
                <div v-if="editCommuneSelectionnee === '__autre__'" class="form-group-modal">
                  <label for="edit-nom-structure-commune">Nom de la commune *</label>
                  <input
                    id="edit-nom-structure-commune"
                    v-model="editNomStructure"
                    placeholder="Ex: Commune de Dar Salam"
                    required
                  />
                </div>
              </div>
            </div>

            <!-- Agence - champ libre + autorité de tutelle -->
            <div v-else-if="editTypeStructure === 'agence'">
              <div class="form-group-modal">
                <label for="edit-nom-agence">Nom de l'agence / établissement *</label>
                <input
                  id="edit-nom-agence"
                  v-model="editNomAgence"
                  placeholder="Ex: APIX SA, SENELEC, etc."
                  required
                />
              </div>

              <div class="form-group-modal">
                <label for="edit-tutelle-agence">Autorité de tutelle *</label>
                <select id="edit-tutelle-agence" v-model="editTutelleAgence" @change="onEditTutelleAgenceChange" required>
                  <option value="">-- Sélectionnez l'autorité de tutelle --</option>
                  <option value="Primature">Primature</option>
                  <option value="Présidence de la République">Présidence de la République</option>
                  <option value="__ministere__">Ministère sectoriel</option>
                </select>
              </div>

              <!-- Sélection du ministère de tutelle si ministère sélectionné -->
              <div v-if="editTutelleAgence === '__ministere__'">
                <div class="form-group-modal">
                  <label for="edit-tutelle-ministere-select">Ministère de tutelle *</label>
                  <select
                    id="edit-tutelle-ministere-select"
                    v-model="editTutelleAgenceLibre"
                    @change="onEditTutelleMinistereChange"
                    required
                  >
                    <option value="">-- Sélectionnez un ministère --</option>
                    <option v-for="ministere in ministeresActifs" :key="ministere.id" :value="ministere.nom_complet">
                      {{ ministere.nom_complet }}
                    </option>
                    <option value="__autre__">Autre (non listé)</option>
                  </select>
                </div>

                <!-- Champ libre si "Autre" est sélectionné -->
                <div v-if="editTutelleAgenceLibre === '__autre__'" class="form-group-modal">
                  <label for="edit-tutelle-agence-autre">Nom du ministère de tutelle *</label>
                  <input
                    id="edit-tutelle-agence-autre"
                    v-model="editTutelleAgenceAutre"
                    placeholder="Ex: Autre ministère de tutelle"
                    required
                  />
                </div>
              </div>
            </div>

            <!-- Autre - champ libre -->
            <div v-else-if="editTypeStructure === 'autre'" class="form-group-modal">
              <label for="edit-nom-structure-autre">Nom de la structure *</label>
              <input
                id="edit-nom-structure-autre"
                v-model="editNomStructure"
                placeholder="Ex: ONG XYZ, Cabinet ABC, etc."
                required
              />
            </div>

            <div class="detail-row readonly-section">
              <span class="detail-label">Statut du compte :</span>
              <span :class="['badge-statut', compteSelectionne.statut_compte || 'non_verifie']">
                {{ formatStatut(compteSelectionne.statut_compte) }}
              </span>
            </div>
            <div v-if="compteSelectionne.date_verification" class="detail-row readonly-section">
              <span class="detail-label">Date de vérification :</span>
              <span class="detail-value">{{ formatDate(compteSelectionne.date_verification) }}</span>
            </div>
            <div v-if="compteSelectionne.verifie_par" class="detail-row readonly-section">
              <span class="detail-label">Vérifié par :</span>
              <span class="detail-value">{{ compteSelectionne.verifie_par }}</span>
            </div>
            <div class="detail-row readonly-section">
              <span class="detail-label">Date de création :</span>
              <span class="detail-value">{{ formatDate(compteSelectionne.date_creation) }}</span>
            </div>

            <div class="modal-actions">
              <button type="button" @click="fermerDetails" class="btn-modal-cancel">
                Annuler
              </button>
              <button type="submit" class="btn-modal-save" :disabled="enregistrementEnCours">
                {{ enregistrementEnCours ? 'Enregistrement...' : 'Enregistrer les modifications' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    </div>
  </PageWrapper>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import PageWrapper from '../components/PageWrapper.vue'

const router = useRouter()

// État
const comptes = ref([])
const comptesFiltres = ref([])
const filtreStatut = ref('')
const rechercheTexte = ref('')
const loading = ref(false)
const error = ref('')
const actionEnCours = ref(null)
const compteSelectionne = ref(null)
const enregistrementEnCours = ref(false)

// État onglets
const activeTab = ref('comptes')

// État messages de contact
const messagesContact = ref([])
const messagesFiltresData = ref([])
const filtreStatutMessage = ref('')
const loadingMessages = ref(false)
const messageSelectionne = ref(null)
const reponseMessage = ref('')
const messageAAssigner = ref(null)
const utilisateurAssigne = ref('')
const utilisateursAssignables = ref([])

// Listes de données pour le formulaire hiérarchique
const regions = ref([])
const departements = ref({}) // Format: { region: [dept1, dept2, ...] }
const communes = ref({}) // Format: { departement: [commune1, commune2, ...] }
const ministeresActifs = ref([]) // Liste des ministères actifs depuis la base de données

// Variables d'édition pour le formulaire de structure (avec préfixe "edit")
const editTypeStructure = ref('')
const editTypeInstitution = ref('')
const editNomMinistere = ref('')
const editNomMinistereLibre = ref('')
const editNomInstitution = ref('')
const editDirectionService = ref('')
const editNiveauCollectivite = ref('')
const editRegionParente = ref('')
const editDepartementParent = ref('')
const editCommuneSelectionnee = ref('')
const editNomStructure = ref('')
const editNomAgence = ref('')
const editTutelleAgence = ref('')
const editTutelleAgenceLibre = ref('')
const editTutelleAgenceAutre = ref('')

// Récupérer l'utilisateur connecté
const userStr = localStorage.getItem('user')
const user = userStr ? JSON.parse(userStr) : null

// URL de base du backend
const backendUrl = import.meta.env.VITE_API_URL || ''

// Statistiques
const stats = computed(() => {
  return {
    non_verifie: comptes.value.filter(c => (c.statut_compte || 'non_verifie') === 'non_verifie').length,
    verifie: comptes.value.filter(c => c.statut_compte === 'verifie').length,
    suspendu: comptes.value.filter(c => c.statut_compte === 'suspendu').length
  }
})

// Computed pour messages
const messagesNonLus = computed(() => {
  return messagesContact.value.filter(m => m.statut === 'nouveau').length
})

const messagesFiltres = computed(() => {
  if (!filtreStatutMessage.value) {
    return messagesContact.value
  }
  return messagesContact.value.filter(m => m.statut === filtreStatutMessage.value)
})

// Computed properties pour le formulaire d'édition
const editDepartementsFiltered = computed(() => {
  if (!editRegionParente.value) return []
  return departements.value[editRegionParente.value] || []
})

const editCommunesFiltered = computed(() => {
  if (!editDepartementParent.value) return []
  return communes.value[editDepartementParent.value] || []
})

// Computed properties pour l'affichage conditionnel des champs de structure (anciens - à supprimer)
const showNomStructureField = computed(() => {
  if (!compteSelectionne.value) return false
  const type = compteSelectionne.value.type_structure
  if (type === 'institution') {
    const typeInst = compteSelectionne.value.type_institution
    return typeInst === 'ministere' || typeInst === 'autre_institution'
  }
  return type === 'collectivite' || type === 'agence' || type === 'autre'
})

const showDirectionField = computed(() => {
  if (!compteSelectionne.value) return false
  return compteSelectionne.value.type_structure && compteSelectionne.value.nom_structure
})

// Charger les comptes au montage
onMounted(async () => {
  await loadDataLists()
  chargerComptes()
})

// Fonction pour charger les données des listes (régions, départements, communes, ministères)
async function loadDataLists() {
  try {
    // Charger les régions
    const resRegions = await axios.get('/api/data/regions')
    regions.value = resRegions.data

    // Charger les départements (format dictionnaire)
    const resDept = await axios.get('/api/data/departements?format=dict')
    departements.value = resDept.data

    // Charger les communes (format dictionnaire par département)
    const resCommunes = await axios.get('/api/data/communes?format=dict')
    communes.value = resCommunes.data

    // Charger les ministères actifs depuis la nouvelle API
    const resMinisteres = await axios.get('/api/ministeres')
    ministeresActifs.value = resMinisteres.data

  } catch (err) {
    console.error('Erreur lors du chargement des données:', err)
    // Pas d'affichage d'erreur pour ne pas bloquer l'utilisateur
  }
}

async function chargerComptes() {
  loading.value = true
  error.value = ''

  try {
    const params = {
      role: user?.role
    }
    if (filtreStatut.value) {
      params.statut = filtreStatut.value
    }

    const response = await axios.get('/api/admin/users', { params })
    comptes.value = response.data.filter(u => u.role === 'soumissionnaire' || u.role === 'invite')
    filtrerComptes()
  } catch (err) {
    console.error('Erreur lors du chargement des comptes:', err)
    error.value = 'Erreur lors du chargement des comptes'
  } finally {
    loading.value = false
  }
}

function filtrerComptes() {
  if (!rechercheTexte.value) {
    comptesFiltres.value = comptes.value
    return
  }

  const texte = rechercheTexte.value.toLowerCase()
  comptesFiltres.value = comptes.value.filter(compte => {
    return (
      (compte.display_name || '').toLowerCase().includes(texte) ||
      (compte.username || '').toLowerCase().includes(texte) ||
      (compte.nom_structure || '').toLowerCase().includes(texte) ||
      (compte.fonction || '').toLowerCase().includes(texte)
    )
  })
}

async function verifierCompte(compteId) {
  if (!confirm('Voulez-vous vérifier ce compte ?')) return

  actionEnCours.value = compteId

  try {
    await axios.post(`/api/admin/users/${compteId}/verify`, {
      role: user?.role,
      validateur_username: user?.username
    })

    // Recharger les comptes
    await chargerComptes()
    alert('Compte vérifié avec succès')
  } catch (err) {
    console.error('Erreur lors de la vérification:', err)
    alert('Erreur lors de la vérification du compte')
  } finally {
    actionEnCours.value = null
  }
}

async function suspendreCompte(compteId) {
  if (!confirm('Voulez-vous suspendre ce compte ? Cette action empêchera l\'utilisateur de soumettre des projets.')) return

  actionEnCours.value = compteId

  try {
    await axios.post(`/api/admin/users/${compteId}/suspend`, {
      role: user?.role
    })

    // Recharger les comptes
    await chargerComptes()
    alert('Compte suspendu avec succès')
  } catch (err) {
    console.error('Erreur lors de la suspension:', err)
    alert('Erreur lors de la suspension du compte')
  } finally {
    actionEnCours.value = null
  }
}

async function reintegrerCompte(compteId) {
  if (!confirm('Voulez-vous réintégrer ce compte suspendu ? L\'utilisateur pourra à nouveau soumettre des projets.')) return

  actionEnCours.value = compteId

  try {
    await axios.post(`/api/admin/users/${compteId}/reintegrate`, {
      role: user?.role
    })

    // Recharger les comptes
    await chargerComptes()
    alert('Compte réintégré avec succès')
  } catch (err) {
    console.error('Erreur lors de la réintégration:', err)
    alert('Erreur lors de la réintégration du compte')
  } finally {
    actionEnCours.value = null
  }
}

async function supprimerCompte(compteId, username) {
  if (!confirm(`Voulez-vous SUPPRIMER DÉFINITIVEMENT le compte "${username}" ?\n\n⚠️ ATTENTION : Cette action est IRRÉVERSIBLE.\nTous les projets associés à ce compte seront également supprimés.`)) return

  actionEnCours.value = compteId

  try {
    await axios.delete(`/api/users/${compteId}`)

    // Recharger les comptes
    await chargerComptes()
    alert('Compte supprimé définitivement')
  } catch (err) {
    console.error('Erreur lors de la suppression:', err)
    alert('Erreur lors de la suppression du compte')
  } finally {
    actionEnCours.value = null
  }
}

function voirJustificatif(path) {
  // Gérer les chemins multiples (séparés par virgules)
  const paths = path.split(',').map(p => p.trim())

  // Ouvrir chaque justificatif dans un nouvel onglet
  paths.forEach(p => {
    // Construire l'URL complète pour le fichier
    // En production sur Render, utiliser l'URL backend, sinon utiliser l'origine actuelle
    const isProduction = window.location.hostname.includes('render.com')
    const backendUrl = isProduction ? 'https://maturation-backend.onrender.com' : window.location.origin
    const fileUrl = `${backendUrl}/api/uploads/${p}`
    window.open(fileUrl, '_blank')
  })
}

function voirDetails(compte) {
  // Créer une copie pour éviter la modification directe
  compteSelectionne.value = { ...compte }

  // Initialiser les variables d'édition avec les valeurs du compte
  editTypeStructure.value = compte.type_structure || ''
  editTypeInstitution.value = compte.type_institution || ''
  editDirectionService.value = compte.direction_service || ''
  editNomStructure.value = compte.nom_structure || ''

  // Réinitialiser les autres variables d'édition
  editNomMinistere.value = ''
  editNomMinistereLibre.value = ''
  editNomInstitution.value = ''
  editNiveauCollectivite.value = ''
  editRegionParente.value = ''
  editDepartementParent.value = ''
  editCommuneSelectionnee.value = ''
  editNomAgence.value = ''
  editTutelleAgence.value = ''
  editTutelleAgenceLibre.value = ''
  editTutelleAgenceAutre.value = ''
}

function fermerDetails() {
  compteSelectionne.value = null
}

function initTelephone() {
  if (compteSelectionne.value && (!compteSelectionne.value.telephone || compteSelectionne.value.telephone.trim() === '')) {
    compteSelectionne.value.telephone = '+221 '
  }
}

// Fonctions de gestion des changements du formulaire hiérarchique
function onEditTypeStructureChange() {
  // Réinitialiser tous les champs quand le type change
  editTypeInstitution.value = ''
  editNomInstitution.value = ''
  editDirectionService.value = ''
  editNomMinistere.value = ''
  editNomMinistereLibre.value = ''
  editNomAgence.value = ''
  editTutelleAgence.value = ''
  editTutelleAgenceLibre.value = ''
  editTutelleAgenceAutre.value = ''
  editNomStructure.value = ''
  editNiveauCollectivite.value = ''
  editRegionParente.value = ''
  editDepartementParent.value = ''
  editCommuneSelectionnee.value = ''
}

function onEditTypeInstitutionChange() {
  // Réinitialiser les champs spécifiques quand le type d'institution change
  editNomInstitution.value = ''
  editNomMinistere.value = ''
  editNomMinistereLibre.value = ''

  // Auto-remplir pour présidence et primature
  if (editTypeInstitution.value === 'presidence') {
    editNomStructure.value = 'Présidence de la République'
  } else if (editTypeInstitution.value === 'primature') {
    editNomStructure.value = 'Primature'
  } else {
    editNomStructure.value = ''
  }
}

function onEditMinistereChange() {
  // Réinitialiser le champ libre si on change la sélection
  if (editNomMinistere.value !== '__autre__') {
    editNomMinistereLibre.value = ''
  }
}

function onEditNiveauCollectiviteChange() {
  // Réinitialiser le nom de structure et la région parente quand le niveau change
  editNomStructure.value = ''
  editRegionParente.value = ''
  editDepartementParent.value = ''
  editCommuneSelectionnee.value = ''
}

function onEditRegionChange() {
  // Réinitialiser le département quand la région change (pour les départements)
  editNomStructure.value = ''
}

function onEditRegionChangeCommunes() {
  // Réinitialiser le département et la commune quand la région change (pour les communes)
  editDepartementParent.value = ''
  editCommuneSelectionnee.value = ''
  editNomStructure.value = ''
}

function onEditDepartementChangeCommunes() {
  // Réinitialiser la commune quand le département change
  editNomStructure.value = ''
  editCommuneSelectionnee.value = ''
}

function onEditCommuneChange() {
  if (editCommuneSelectionnee.value !== '__autre__') {
    editNomStructure.value = editCommuneSelectionnee.value
  } else {
    editNomStructure.value = ''
  }
}

function onEditTutelleAgenceChange() {
  // Réinitialiser les champs de tutelle si on change le type de tutelle
  if (editTutelleAgence.value !== '__ministere__') {
    editTutelleAgenceLibre.value = ''
    editTutelleAgenceAutre.value = ''
  }
}

function onEditTutelleMinistereChange() {
  // Réinitialiser le champ libre si on change la sélection de ministère
  if (editTutelleAgenceLibre.value !== '__autre__') {
    editTutelleAgenceAutre.value = ''
  }
}

async function sauvegarderModifications() {
  if (!compteSelectionne.value) return

  enregistrementEnCours.value = true

  try {
    // Construction de la structure selon le nouveau système (comme dans Register.vue)
    let structureFinal = editNomStructure.value
    let typeInstitutionFinal = ''
    let directionServiceFinal = ''

    if (editTypeStructure.value === 'institution') {
      typeInstitutionFinal = editTypeInstitution.value
      directionServiceFinal = editDirectionService.value

      // Déterminer le nom de la structure selon le type d'institution
      if (editTypeInstitution.value === 'presidence') {
        structureFinal = 'Présidence de la République'
      } else if (editTypeInstitution.value === 'primature') {
        structureFinal = 'Primature'
      } else if (editTypeInstitution.value === 'ministere') {
        // Utiliser le champ libre si "Autre" est sélectionné
        structureFinal = editNomMinistere.value === '__autre__' ? editNomMinistereLibre.value : editNomMinistere.value
      } else if (editTypeInstitution.value === 'autre_institution') {
        structureFinal = editNomInstitution.value
      }
    }

    // Pour les agences, combiner nom agence et tutelle
    if (editTypeStructure.value === 'agence' && editNomAgence.value && editTutelleAgence.value) {
      let tutelleFinal = editTutelleAgence.value
      if (editTutelleAgence.value === '__ministere__') {
        // Utiliser le champ libre si "Autre" est sélectionné pour le ministère de tutelle
        tutelleFinal = editTutelleAgenceLibre.value === '__autre__' ? editTutelleAgenceAutre.value : editTutelleAgenceLibre.value
      }
      structureFinal = `${editNomAgence.value} - ${tutelleFinal}`
    }

    const response = await axios.put(`/api/admin/users/${compteSelectionne.value.id}`, {
      display_name: compteSelectionne.value.display_name,
      telephone: compteSelectionne.value.telephone,
      fonction: compteSelectionne.value.fonction,
      type_structure: editTypeStructure.value,
      type_institution: typeInstitutionFinal,
      nom_structure: structureFinal,
      direction_service: directionServiceFinal,
      role: user?.role
    })

    if (response.status === 200) {
      alert('Modifications enregistrées avec succès')
      await chargerComptes()
      fermerDetails()
    }
  } catch (err) {
    console.error('Erreur lors de la sauvegarde:', err)
    alert('Erreur lors de la sauvegarde des modifications')
  } finally {
    enregistrementEnCours.value = false
  }
}

function formatStatut(statut) {
  const labels = {
    non_verifie: '⚠️ Non vérifié',
    verifie: '✓ Vérifié',
    suspendu: '🔴 Suspendu'
  }
  return labels[statut] || labels.non_verifie
}

function formatTypeStructure(type) {
  const labels = {
    ministere: 'Ministère',
    region: 'Région',
    departement: 'Département',
    commune: 'Commune',
    agence: 'Agence',
    autre: 'Autre'
  }
  return labels[type] || type || 'N/A'
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}


function retourDashboard() {
  // Déterminer la route du dashboard selon le rôle
  const roleRoutes = {
    admin: '/admin',
    presidencesct: '/presidencesct',
    secretariatsct: '/secretariatsct',
    presidencecomite: '/presidencecomite'
  }
  const route = roleRoutes[user?.role] || '/'
  router.push(route)
}

// Fonctions helper pour les labels de structure hiérarchique
function getTypeStructureLabel(type) {
  const labels = {
    'institution': 'Institution',
    'collectivite': 'Collectivité territoriale',
    'agence': 'Agence / Établissement public',
    'autre': 'Autre (ONG, Association, Cabinet, etc.)'
  }
  return labels[type] || type
}

function getTypeInstitutionLabel(type) {
  const labels = {
    'presidence': 'Présidence de la République',
    'primature': 'Primature',
    'ministere': 'Ministère',
    'autre_institution': 'Autre Institution'
  }
  return labels[type] || type
}

// ===== Fonctions pour les messages de contact =====

async function chargerMessages() {
  loadingMessages.value = true
  try {
    const response = await axios.get('/api/contact/messages', {
      params: { role: user?.role }
    })
    messagesContact.value = response.data

    // Charger aussi les utilisateurs assignables (admin, secrétariat)
    const usersResponse = await axios.get('/api/admin/users', {
      params: { role: user?.role }
    })
    utilisateursAssignables.value = usersResponse.data.filter(u =>
      ['admin', 'secretariatsct'].includes(u.role)
    )
  } catch (err) {
    console.error('Erreur chargement messages:', err)
  } finally {
    loadingMessages.value = false
  }
}

function filtrerMessages() {
  // Le filtrage est géré par le computed messagesFiltres
}

function formatStatutMessage(statut) {
  const labels = {
    'nouveau': 'Non lu',
    'lu': 'Lu',
    'traite': 'Traité'
  }
  return labels[statut] || statut
}

async function marquerLu(messageId) {
  try {
    await axios.get(`/api/contact/messages/${messageId}`)
    // Mettre à jour localement
    const msg = messagesContact.value.find(m => m.id === messageId)
    if (msg) {
      msg.statut = 'lu'
    }
  } catch (err) {
    console.error('Erreur marquer lu:', err)
  }
}

function ouvrirModalReponse(msg) {
  messageSelectionne.value = msg
  reponseMessage.value = ''
}

async function envoyerReponse() {
  if (!messageSelectionne.value || !reponseMessage.value.trim()) return

  try {
    await axios.put(`/api/contact/messages/${messageSelectionne.value.id}`, {
      statut: 'traite',
      reponse: reponseMessage.value,
      traite_par: user?.username || user?.display_name
    })

    // Mettre à jour localement
    const msg = messagesContact.value.find(m => m.id === messageSelectionne.value.id)
    if (msg) {
      msg.statut = 'traite'
      msg.reponse = reponseMessage.value
      msg.traite_par = user?.username || user?.display_name
    }

    fermerModalMessage()
    alert('Réponse enregistrée avec succès')
  } catch (err) {
    console.error('Erreur envoi réponse:', err)
    alert('Erreur lors de l\'envoi de la réponse')
  }
}

function fermerModalMessage() {
  messageSelectionne.value = null
  reponseMessage.value = ''
}

function ouvrirModalAssigner(msg) {
  messageAAssigner.value = msg
  utilisateurAssigne.value = msg.assigne_a || ''
}

async function confirmerAssignation() {
  if (!messageAAssigner.value || !utilisateurAssigne.value) return

  try {
    await axios.put(`/api/contact/messages/${messageAAssigner.value.id}`, {
      assigne_a: utilisateurAssigne.value
    })

    // Mettre à jour localement
    const msg = messagesContact.value.find(m => m.id === messageAAssigner.value.id)
    if (msg) {
      msg.assigne_a = utilisateurAssigne.value
    }

    fermerModalAssigner()
    alert('Message assigné avec succès')
  } catch (err) {
    console.error('Erreur assignation:', err)
    alert('Erreur lors de l\'assignation')
  }
}

function fermerModalAssigner() {
  messageAAssigner.value = null
  utilisateurAssigne.value = ''
}
</script>

<style scoped>
.gestion-comptes-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  margin-bottom: 2rem;
}

.header-with-back {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn-retour {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: white;
  color: var(--dgppe-primary, #1e40af);
  border: 2px solid var(--dgppe-primary, #1e40af);
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-start;
}

.btn-retour:hover {
  background: var(--dgppe-primary, #1e40af);
  color: white;
  transform: translateX(-4px);
}

.btn-retour svg {
  transition: transform 0.3s ease;
}

.btn-retour:hover svg {
  transform: translateX(-4px);
}

.header-content h1 {
  font-size: 2rem;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #718096;
  font-size: 1rem;
}

/* Filtres */
.filters-section {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  min-width: 200px;
}

.filter-group label {
  font-weight: 600;
  color: #4a5568;
  font-size: 0.9rem;
}

.filter-group select,
.filter-group input {
  padding: 0.75rem;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  font-size: 1rem;
}

/* Statistiques */
.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-card.non-verifie {
  background: #fff3cd;
  border-left: 4px solid #ffc107;
}

.stat-card.verifie {
  background: #d4edda;
  border-left: 4px solid #28a745;
}

.stat-card.suspendu {
  background: #f8d7da;
  border-left: 4px solid #dc3545;
}

.stat-icon {
  font-size: 2rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
}

.stat-label {
  font-size: 0.9rem;
  color: #4a5568;
}

/* Tableau */
.comptes-table-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.loading,
.error-message,
.no-data {
  padding: 3rem;
  text-align: center;
  color: #718096;
}

.error-message {
  color: #e53e3e;
}

.comptes-table {
  width: 100%;
  border-collapse: collapse;
}

.comptes-table thead {
  background: #f7fafc;
}

.comptes-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #2d3748;
  border-bottom: 2px solid #e2e8f0;
  font-size: 0.9rem;
}

.comptes-table td {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: top;
}

.comptes-table tbody tr:hover {
  background: #f7fafc;
}

/* Cellules */
.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  font-weight: 600;
  color: #1a202c;
}

.user-email {
  font-size: 0.85rem;
  color: #718096;
  font-family: 'Courier New', monospace;
}

.user-fonction {
  font-size: 0.85rem;
  color: #4a5568;
  font-style: italic;
}

.structure-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.structure-type {
  font-size: 0.8rem;
  color: #718096;
  text-transform: uppercase;
  font-weight: 600;
}

.structure-nom {
  color: #2d3748;
}

/* Affichage hiérarchique compact pour la structure */
.structure-hierarchy-compact {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  font-size: 0.85rem;
  line-height: 1.4;
}

.structure-hierarchy-compact .structure-type {
  font-size: 0.75rem;
  color: #4a5568;
  font-weight: 600;
  text-transform: uppercase;
}

.structure-hierarchy-compact .structure-subtype {
  font-size: 0.8rem;
  color: #718096;
  padding-left: 0.5rem;
}

.structure-hierarchy-compact .structure-nom {
  color: #2d3748;
  font-weight: 500;
}

.structure-hierarchy-compact .structure-direction {
  font-size: 0.8rem;
  color: #4a5568;
  font-style: italic;
}

.structure-empty {
  color: #a0aec0;
  font-style: italic;
  font-size: 0.85rem;
}

.contact-info {
  font-size: 0.9rem;
  color: #4a5568;
}

.date-info {
  font-size: 0.85rem;
  color: #718096;
  white-space: nowrap;
}

.badge-statut {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}

.badge-statut.non_verifie {
  background: #fff3cd;
  color: #856404;
}

.badge-statut.verifie {
  background: #d4edda;
  color: #155724;
}

.badge-statut.suspendu {
  background: #f8d7da;
  color: #721c24;
}

.verif-info {
  font-size: 0.75rem;
  color: #718096;
  margin-top: 0.25rem;
}

.btn-voir-justificatif {
  background: #3182ce;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-voir-justificatif:hover {
  background: #2c5282;
}

.no-justificatif {
  color: #a0aec0;
  font-size: 0.85rem;
  font-style: italic;
}

.actions-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn-action {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-verify {
  background: #28a745;
  color: white;
}

.btn-verify:hover:not(:disabled) {
  background: #218838;
}

.btn-suspend {
  background: #dc3545;
  color: white;
}

.btn-suspend:hover:not(:disabled) {
  background: #c82333;
}

.btn-reintegrate {
  background: #17a2b8;
  color: white;
}

.btn-reintegrate:hover:not(:disabled) {
  background: #138496;
}

.btn-delete {
  background: #ff6b6b;
  color: white;
}

.btn-delete:hover:not(:disabled) {
  background: #ee5a52;
}

.btn-details {
  background: #6c757d;
  color: white;
}

.btn-details:hover {
  background: #5a6268;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h2 {
  margin: 0;
  color: #1a202c;
  font-size: 1.5rem;
}

.btn-close {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #718096;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #2d3748;
}

.modal-body {
  padding: 1.5rem;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group-modal {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group-modal label {
  font-weight: 600;
  color: #4a5568;
  font-size: 0.9rem;
}

.form-group-modal input,
.form-group-modal select {
  padding: 0.75rem;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.form-group-modal input:focus,
.form-group-modal select:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}

.form-group-modal select:disabled {
  background-color: #f7fafc;
  cursor: not-allowed;
  opacity: 0.6;
}

.readonly-field {
  background-color: #f7fafc;
  cursor: not-allowed;
  color: #718096;
}

.field-hint {
  font-size: 0.8rem;
  color: #718096;
  font-style: italic;
}

.readonly-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 2px solid #e2e8f0;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 2px solid #e2e8f0;
}

.btn-modal-cancel {
  flex: 1;
  padding: 0.75rem 1.5rem;
  background: #e2e8f0;
  color: #4a5568;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-modal-cancel:hover {
  background: #cbd5e0;
}

.btn-modal-save {
  flex: 2;
  padding: 0.75rem 1.5rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-modal-save:hover:not(:disabled) {
  background: #3182ce;
}

.btn-modal-save:disabled {
  background: #a0aec0;
  cursor: not-allowed;
  opacity: 0.6;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f7fafc;
}

.detail-label {
  font-weight: 600;
  color: #4a5568;
  flex: 0 0 40%;
}

.detail-value {
  color: #1a202c;
  flex: 1;
  text-align: right;
}

@media (max-width: 1024px) {
  .comptes-table {
    font-size: 0.85rem;
  }

  .comptes-table th,
  .comptes-table td {
    padding: 0.75rem 0.5rem;
  }

  .actions-buttons {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .btn-action {
    flex: 1;
    min-width: 80px;
  }
}

@media (max-width: 768px) {
  .gestion-comptes-page {
    padding: 1rem;
  }

  .comptes-table-container {
    overflow-x: auto;
  }

  .comptes-table {
    min-width: 800px;
  }

  .stats-section {
    grid-template-columns: 1fr;
  }
}

/* Onglets */
.tabs-container {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.5rem;
  border-bottom: 2px solid #e2e8f0;
}

.tab-btn {
  padding: 0.75rem 1.5rem;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 1rem;
  font-weight: 600;
  color: #718096;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.tab-btn:hover {
  color: #4a5568;
}

.tab-btn.active {
  color: var(--dgppe-primary, #1e40af);
  border-bottom-color: var(--dgppe-primary, #1e40af);
}

.tab-badge {
  position: absolute;
  top: 0.25rem;
  right: 0.25rem;
  background: #e53e3e;
  color: white;
  font-size: 0.7rem;
  padding: 0.15rem 0.4rem;
  border-radius: 999px;
  min-width: 18px;
  text-align: center;
}

/* Section messages */
.messages-section {
  margin-top: 1.5rem;
}

.messages-filters {
  margin-bottom: 1.5rem;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #cbd5e0;
}

.message-card.non-lu {
  border-left-color: #3182ce;
  background: #f0f7ff;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.message-info {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

.message-nom {
  font-weight: 700;
  color: #1a202c;
}

.message-email {
  font-size: 0.9rem;
  color: #3182ce;
}

.message-tel {
  font-size: 0.85rem;
  color: #718096;
}

.message-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.message-statut {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
}

.message-statut.nouveau {
  background: #bee3f8;
  color: #2a4365;
}

.message-statut.lu {
  background: #e2e8f0;
  color: #4a5568;
}

.message-statut.traite {
  background: #c6f6d5;
  color: #22543d;
}

.message-date {
  font-size: 0.85rem;
  color: #718096;
}

.message-objet {
  font-size: 1.1rem;
  color: #2d3748;
  margin-bottom: 0.75rem;
}

.message-contenu {
  color: #4a5568;
  line-height: 1.6;
  margin-bottom: 1rem;
  white-space: pre-wrap;
}

.message-pieces {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 8px;
}

.pieces-label {
  font-weight: 600;
  color: #4a5568;
  margin-right: 0.5rem;
}

.piece-link {
  display: inline-block;
  margin: 0.25rem 0.5rem;
  color: #3182ce;
  text-decoration: none;
  font-size: 0.9rem;
}

.piece-link:hover {
  text-decoration: underline;
}

.message-assignation {
  font-size: 0.9rem;
  color: #553c9a;
  margin-bottom: 0.75rem;
  padding: 0.5rem;
  background: #faf5ff;
  border-radius: 6px;
}

.message-reponse {
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f0fff4;
  border-radius: 8px;
  border-left: 3px solid #38a169;
}

.message-reponse strong {
  color: #22543d;
  display: block;
  margin-bottom: 0.5rem;
}

.message-reponse p {
  margin: 0;
  color: #2d3748;
  white-space: pre-wrap;
}

.message-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-lu {
  background: #4299e1;
  color: white;
}

.btn-lu:hover {
  background: #3182ce;
}

.btn-repondre {
  background: #38a169;
  color: white;
}

.btn-repondre:hover {
  background: #2f855a;
}

.btn-assigner {
  background: #805ad5;
  color: white;
}

.btn-assigner:hover {
  background: #6b46c1;
}

/* Modal messages */
.modal-message,
.modal-assigner {
  max-width: 700px;
}

.message-detail {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f7fafc;
  border-radius: 8px;
}

.message-detail p {
  margin: 0.5rem 0;
}

.message-original {
  margin-top: 0.75rem;
  padding: 1rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}

.form-group-modal textarea {
  padding: 0.75rem;
  border: 1px solid #cbd5e0;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  width: 100%;
  box-sizing: border-box;
}

.form-group-modal textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
}
</style>
