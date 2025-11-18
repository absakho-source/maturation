<template>
  <PageWrapper>
    <div class="dashboard-container">
      <!-- Bannière d'avertissement pour compte non vérifié -->
      <div v-if="userAccountStatus === 'non_verifie'" class="warning-banner warning-banner-info">
        <div class="banner-icon">⏳</div>
        <div class="banner-content">
          <h3>Compte en attente de vérification</h3>
          <p>Votre compte n'a pas encore été vérifié par l'administration. Vous ne pouvez pas soumettre de projet tant que votre compte n'a pas été validé.</p>
          <p class="banner-note">Veuillez patienter ou contacter l'administration si cela prend trop de temps.</p>
        </div>
      </div>

      <!-- Bannière d'avertissement pour compte suspendu -->
      <div v-if="userAccountStatus === 'suspendu'" class="warning-banner warning-banner-danger">
        <div class="banner-icon">🚫</div>
        <div class="banner-content">
          <h3>Compte suspendu</h3>
          <p>Votre compte a été suspendu. Vous ne pouvez pas soumettre de nouveaux projets.</p>
          <p class="banner-note">Pour plus d'informations, veuillez contacter l'administration.</p>
        </div>
      </div>

      <!-- Tableau de bord -->
      <div class="dashboard-section">
        <h2 class="dashboard-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 3v5h5"/>
            <path d="M3 8s2-4 8-4 8 4 8 4"/>
            <path d="M21 21v-5h-5"/>
            <path d="M21 16s-2 4-8 4-8-4-8-4"/>
          </svg>
          Tableau de bord - Soumissionnaire
        </h2>

        <!-- Action principale -->
        <div class="action-section">
          <button
            v-if="!showSubmissionForm && canSubmitProject"
            @click="openSubmissionForm"
            class="btn-new-project"
          >
            📝 Soumettre un nouveau projet
            <span class="icon-plus">➕</span>
          </button>
          <button
            v-if="!showSubmissionForm && !canSubmitProject"
            @click="showBlockedMessage"
            class="btn-new-project btn-disabled"
            disabled
          >
            📝 Soumettre un nouveau projet
            <span class="icon-plus">➕</span>
          </button>
          <button v-if="showSubmissionForm" @click="cancelSubmission" class="btn-cancel">
            ✖️ Annuler
          </button>
        </div>
      </div>

      <div v-if="showSubmissionForm" class="section">
        <div class="section-header">
          <h3>📝 Nouveau projet</h3>
        </div>
        
        <form v-if="showSubmissionForm" @submit.prevent="handleSubmit" class="submit-form">
          <!-- Intitulé du projet -->
          <div class="form-row">
            <div class="form-group full-width">
              <label>Intitulé du projet *</label>
              <input v-model="form.titre" type="text" required placeholder="Ex: Construction d'un centre de santé" />
            </div>
          </div>

          <!-- Structure soumissionnaire -->
          <div class="form-row">
            <div class="form-group full-width">
              <label>Structure soumissionnaire / Maître d'ouvrage *</label>
              <input v-model="form.structure_soumissionnaire" type="text" required placeholder="Ex: Direction des Infrastructures Sanitaires" />
            </div>
          </div>

          <!-- Organisme de tutelle - Sélection hiérarchique -->
          <div class="form-section-title">Organisme de tutelle</div>
          <div class="form-row">
            <div class="form-group full-width">
              <label>Type d'organisme de tutelle *</label>
              <select v-model="typeOrganisme" @change="onTypeOrganismeChange" required>
                <option value="">-- Sélectionnez --</option>
                <option value="institution">Institution</option>
                <option value="collectivite">Collectivité territoriale</option>
                <option value="agence">Agence / Établissement public</option>
                <option value="autre">Autre (ONG, Association, Cabinet, etc.)</option>
              </select>
            </div>
          </div>

          <!-- Institution -->
          <div v-if="typeOrganisme === 'institution'" class="form-row">
            <div class="form-group full-width">
              <label>Type d'institution *</label>
              <select v-model="typeInstitution" @change="onTypeInstitutionChange" required>
                <option value="">-- Sélectionnez --</option>
                <option value="presidence">Présidence de la République</option>
                <option value="primature">Primature</option>
                <option value="ministere">Ministère</option>
                <option value="autre_institution">Autre Institution</option>
              </select>
            </div>
          </div>

          <div v-if="typeOrganisme === 'institution' && typeInstitution === 'ministere'" class="form-row">
            <div class="form-group full-width">
              <label>Ministère *</label>
              <select v-model="nomMinistere" required>
                <option value="">-- Sélectionnez --</option>
                <option v-for="m in ministeresActifs" :key="m.id" :value="m.nom_complet">{{ m.nom_complet }}</option>
                <option value="__autre__">Autre (à préciser)</option>
              </select>
            </div>
          </div>

          <div v-if="typeOrganisme === 'institution' && typeInstitution === 'ministere' && nomMinistere === '__autre__'" class="form-row">
            <div class="form-group full-width">
              <label>Préciser le ministère *</label>
              <input v-model="nomMinistereLibre" type="text" required placeholder="Ex: Ministère de..." />
            </div>
          </div>

          <div v-if="typeOrganisme === 'institution' && typeInstitution === 'autre_institution'" class="form-row">
            <div class="form-group full-width">
              <label>Nom de l'institution *</label>
              <input v-model="nomInstitution" type="text" required placeholder="Ex: Conseil économique, social et environnemental" />
            </div>
          </div>

          <!-- Collectivité territoriale -->
          <div v-if="typeOrganisme === 'collectivite'" class="form-row">
            <div class="form-group full-width">
              <label>Niveau de collectivité *</label>
              <select v-model="niveauCollectivite" @change="onNiveauCollectiviteChange" required>
                <option value="">-- Sélectionnez --</option>
                <option value="region">Région</option>
                <option value="departement">Département</option>
                <option value="commune">Commune</option>
              </select>
            </div>
          </div>

          <div v-if="typeOrganisme === 'collectivite' && niveauCollectivite === 'region'" class="form-row">
            <div class="form-group full-width">
              <label>Région *</label>
              <select v-model="nomStructure" required>
                <option value="">-- Sélectionnez --</option>
                <option v-for="r in regions" :key="r" :value="`Région de ${r}`">Région de {{ r }}</option>
              </select>
            </div>
          </div>

          <div v-if="typeOrganisme === 'collectivite' && niveauCollectivite === 'departement'" class="form-row">
            <div class="form-group">
              <label>Région parente *</label>
              <select v-model="regionParente" required>
                <option value="">-- Sélectionnez --</option>
                <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Département *</label>
              <select v-model="nomStructure" required :disabled="!regionParente">
                <option value="">-- Sélectionnez --</option>
                <option v-for="d in departementsFiltered" :key="d" :value="`Département de ${d}`">Département de {{ d }}</option>
              </select>
            </div>
          </div>

          <div v-if="typeOrganisme === 'collectivite' && niveauCollectivite === 'commune'">
            <div class="form-row">
              <div class="form-group">
                <label>Région *</label>
                <select v-model="regionParente" required>
                  <option value="">-- Sélectionnez --</option>
                  <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>Département *</label>
                <select v-model="departementParent" required :disabled="!regionParente">
                  <option value="">-- Sélectionnez --</option>
                  <option v-for="d in departementsFiltered" :key="d" :value="d">{{ d }}</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group full-width">
                <label>Commune *</label>
                <select v-model="nomStructure" required :disabled="!departementParent">
                  <option value="">-- Sélectionnez --</option>
                  <option v-for="c in communesFiltered" :key="c" :value="`Commune de ${c}`">Commune de {{ c }}</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Agence / Établissement public -->
          <div v-if="typeOrganisme === 'agence'" class="form-row">
            <div class="form-group full-width">
              <label>Nom de l'agence / établissement *</label>
              <input v-model="nomAgence" type="text" required placeholder="Ex: ADIE, APIX, ARTP..." />
            </div>
          </div>

          <div v-if="typeOrganisme === 'agence'" class="form-row">
            <div class="form-group full-width">
              <label>Autorité de tutelle *</label>
              <select v-model="tutelleAgence" @change="onTutelleAgenceChange" required>
                <option value="">-- Sélectionnez --</option>
                <option value="presidence">Présidence de la République</option>
                <option value="primature">Primature</option>
                <option value="__ministere__">Ministère (à préciser)</option>
              </select>
            </div>
          </div>

          <div v-if="typeOrganisme === 'agence' && tutelleAgence === '__ministere__'" class="form-row">
            <div class="form-group full-width">
              <label>Ministère de tutelle *</label>
              <select v-model="tutelleAgenceLibre" required>
                <option value="">-- Sélectionnez --</option>
                <option v-for="m in ministeresActifs" :key="m.id" :value="m.nom_complet">{{ m.nom_complet }}</option>
                <option value="__autre__">Autre (à préciser)</option>
              </select>
            </div>
          </div>

          <div v-if="typeOrganisme === 'agence' && tutelleAgence === '__ministere__' && tutelleAgenceLibre === '__autre__'" class="form-row">
            <div class="form-group full-width">
              <label>Préciser le ministère de tutelle *</label>
              <input v-model="tutelleAgenceAutre" type="text" required placeholder="Ex: Ministère de..." />
            </div>
          </div>

          <!-- Autre -->
          <div v-if="typeOrganisme === 'autre'" class="form-row">
            <div class="form-group full-width">
              <label>Nom de la structure *</label>
              <input v-model="nomStructure" type="text" required placeholder="Ex: ONG Caritas, Cabinet XYZ..." />
            </div>
          </div>

          <!-- Point focal -->
          <div class="form-section-title">Point focal / Responsable du projet</div>
          <div class="form-row">
            <div class="form-group">
              <label>Nom complet *</label>
              <input v-model="form.point_focal_nom" type="text" required placeholder="Ex: Prénom NOM" />
            </div>
            <div class="form-group">
              <label>Fonction *</label>
              <input v-model="form.point_focal_fonction" type="text" required placeholder="Ex: Chef de projet" />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Téléphone *</label>
              <input
                v-model="form.point_focal_telephone"
                type="tel"
                required
                placeholder="Ex: +221 77 123 45 67"
                @input="formatTelephone"
                @focus="initTelephone"
              />
            </div>
            <div class="form-group">
              <label>Email *</label>
              <input v-model="form.point_focal_email" type="email" required placeholder="Ex: prenom.nom@gouv.sn" />
            </div>
          </div>

          <!-- Pôles et Secteur -->
          <div class="form-row">
            <div class="form-group">
              <label>Pôles territoriaux concernés *</label>
              <select v-model="form.poles" multiple required size="1" class="multi-select-compact">
                <option value="" disabled>-- Sélectionner --</option>
                <option v-for="pole in polesOptions" :key="pole" :value="pole">{{ pole }}</option>
              </select>
              <small class="hint">Maintenez Cmd (Mac) ou Ctrl (Windows) pour sélectionner plusieurs pôles</small>
            </div>
            <div class="form-group">
              <label>Secteur de planification *</label>
              <select v-model="form.secteur" required>
                <option value="" disabled>-- Sélectionner --</option>
                <option v-for="s in secteurs" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
          </div>

          <!-- Description -->
          <div class="form-row">
            <div class="form-group full-width">
              <label>Description du projet * (max. 1000 caractères)</label>
              <textarea
                v-model="form.description"
                rows="6"
                maxlength="1000"
                required
                placeholder="Décrivez les objectifs, les bénéficiaires, et les résultats attendus du projet..."
              ></textarea>
              <small class="hint">{{ form.description ? form.description.length : 0 }} / 1000 caractères</small>
            </div>
          </div>

          <!-- Coût et Durée -->
          <div class="form-row">
            <div class="form-group">
              <label>Coût estimatif (FCFA) *</label>
              <input
                v-model="coutFormate"
                type="text"
                required
                placeholder="Ex: 1 000 000 000"
                @input="onCoutInput"
                @blur="onCoutBlur"
              />
              <small class="hint">Le montant sera automatiquement formaté</small>
            </div>
            <div class="form-group">
              <label>Durée estimée du projet (en mois)</label>
              <input v-model.number="form.duree_mois" type="number" min="1" placeholder="Ex: 24" />
              <small class="hint">Facultatif</small>
            </div>
          </div>

          <!-- Pièces jointes -->
          <div class="form-section-title">Pièces jointes</div>
          <p class="file-info">📎 Formats autorisés : .pdf, .docx, .xlsx, .pptx, .jpg, .png — Taille max. 10 Mo / fichier</p>

          <div class="form-row">
            <div class="form-group">
              <label>Lettre de soumission signée *</label>
              <input
                type="file"
                @change="handleLettreFile"
                accept=".pdf,.doc,.docx"
                ref="lettreInput"
              />
              <ul v-if="form.lettre_soumission.length" class="file-list">
                <li v-for="(f,i) in form.lettre_soumission" :key="f.name + '_' + i">
                  <span class="file-name">{{ f.name }}</span>
                  <span class="file-size">({{ formatFileSize(f.size) }})</span>
                  <button type="button" class="btn-link" @click="removeLettreFile(i)">✕</button>
                </li>
              </ul>
            </div>

            <div class="form-group">
              <label>Note conceptuelle du projet *</label>
              <input
                type="file"
                @change="handleNoteFile"
                accept=".pdf,.doc,.docx"
                ref="noteInput"
              />
              <ul v-if="form.note_conceptuelle.length" class="file-list">
                <li v-for="(f,i) in form.note_conceptuelle" :key="f.name + '_' + i">
                  <span class="file-name">{{ f.name }}</span>
                  <span class="file-size">({{ formatFileSize(f.size) }})</span>
                  <button type="button" class="btn-link" @click="removeNoteFile(i)">✕</button>
                </li>
              </ul>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Études ou plans techniques *</label>
              <input
                type="file"
                multiple
                @change="handleEtudesFile"
                accept=".pdf,.doc,.docx,.xlsx,.pptx,.jpg,.jpeg,.png"
                ref="etudesInput"
              />
              <small class="hint">Vous pouvez sélectionner plusieurs fichiers</small>
              <ul v-if="form.etudes_plans.length" class="file-list">
                <li v-for="(f,i) in form.etudes_plans" :key="f.name + '_' + i">
                  <span class="file-name">{{ f.name }}</span>
                  <span class="file-size">({{ formatFileSize(f.size) }})</span>
                  <button type="button" class="btn-link" @click="removeEtudesFile(i)">✕</button>
                </li>
              </ul>
            </div>

            <div class="form-group">
              <label>Autres pièces justificatives (facultatif)</label>
              <input
                type="file"
                multiple
                @change="handleAutresFile"
                accept=".pdf,.doc,.docx,.xlsx,.pptx,.jpg,.jpeg,.png"
                ref="autresInput"
              />
              <small class="hint">Vous pouvez sélectionner plusieurs fichiers</small>
              <ul v-if="form.autres_pieces.length" class="file-list">
                <li v-for="(f,i) in form.autres_pieces" :key="f.name + '_' + i">
                  <span class="file-name">{{ f.name }}</span>
                  <span class="file-size">({{ formatFileSize(f.size) }})</span>
                  <button type="button" class="btn-link" @click="removeAutresFile(i)">✕</button>
                </li>
              </ul>
            </div>
          </div>

          <!-- Certification -->
          <div class="form-row">
            <div class="form-group full-width">
              <label class="checkbox-label certification">
                <input type="checkbox" v-model="form.certification" required />
                <span>✅ Je certifie que les informations fournies sont exactes et conformes aux documents joints, et que le projet a été validé par ma hiérarchie.</span>
              </label>
            </div>
          </div>

          <div v-if="submitError" class="error-message">{{ submitError }}</div>

          <button type="submit" class="btn-submit" :disabled="submitting">
            <span v-if="!submitting">✓ Soumettre le projet</span>
            <span v-else>⏳ Envoi en cours...</span>
          </button>
        </form>
      </div>

      <!-- Popup de confirmation de soumission -->
      <div v-if="submitSuccess" class="popup-overlay" @click="closeSuccessPopup">
        <div class="popup-content" @click.stop>
          <div class="popup-icon">✓</div>
          <h3>Projet soumis avec succès !</h3>
          <p>{{ submitSuccess }}</p>
          <button @click="closeSuccessPopup" class="btn-primary">OK</button>
        </div>
      </div>

      <div class="section">
        <h3>📂 Mes projets</h3>

        <div class="stats">
          <div class="stat"><span>Total</span><strong>{{ projects.length }}</strong></div>
          <div class="stat"><span>En instruction</span><strong>{{ countByStatus('en instruction') }}</strong></div>
          <div class="stat warning"><span>Compléments demandés</span><strong>{{ countByStatus('compléments demandés') }}</strong></div>
          <div class="stat info"><span>Compléments fournis</span><strong>{{ countByStatus('compléments soumis') }}</strong></div>
          <div class="stat"><span>Évalués</span><strong>{{ countEvaluated() }}</strong></div>
        </div>

        <div v-if="loading" class="loading-state"><div class="spinner"></div><p>Chargement...</p></div>
        <div v-else-if="projects.length === 0" class="empty-state">
          <p>Aucun projet soumis</p>
        </div>
        <div v-else class="projects-grid">
          <div v-for="p in projects" :key="p.id" class="project-card">
            <div class="card-header">
              <div class="card-title-section">
                <div class="project-number">{{ p.numero_projet || 'N/A' }}</div>
                <h4>{{ p.titre }}</h4>
              </div>
              <span class="badge" :class="getStatusClass(p.statut)">{{ p.statut }}</span>
            </div>
            <div class="card-body">
              <p v-if="p.secteur"><strong>Secteur:</strong> {{ p.secteur }}</p>
              <p v-if="p.poles"><strong>Pôles:</strong> {{ p.poles }}</p>
              <p v-if="p.cout_estimatif"><strong>Coût:</strong> {{ formatCurrency(p.cout_estimatif) }}</p>
              <p v-if="p.evaluateur_nom"><strong>Assigné à:</strong> {{ labelEval(p.evaluateur_nom) }}</p>
              <p v-if="p.statut === 'compléments demandés' && p.complements_demande_message">
                <strong>Demande de compléments:</strong> {{ p.complements_demande_message }}
              </p>

              <!-- Formulaire de compléments -->
              <div v-if="p.statut === 'compléments demandés' && complements[p.id]" class="complements-box">
                <h5>Fournir des compléments</h5>
                <label>Message (optionnel si pièces jointes fournies)</label>
                <textarea v-model="complements[p.id].message" rows="3" placeholder="Message optionnel si vous ajoutez des pièces jointes"></textarea>
                <label>Pièces jointes</label>
                <input type="file" multiple @change="e => handleComplementFiles(p.id, e)" accept=".pdf,.doc,.docx,.xls,.xlsx" />
                <ul v-if="complements[p.id].files && complements[p.id].files.length" class="file-list">
                  <li v-for="(f,i) in complements[p.id].files" :key="f.name + '_' + i">
                    {{ f.name }}
                    <button type="button" class="btn-link" @click="removeComplementFile(p.id, i)">Retirer</button>
                  </li>
                </ul>
                <button class="btn-primary" @click="submitComplements(p.id)">Envoyer les compléments</button>
                <div v-if="complements[p.id].error" class="error-message">{{ complements[p.id].error }}</div>
                <div v-if="complements[p.id].ok" class="success-message">{{ complements[p.id].ok }}</div>
              </div>

              <button @click="$router.push(`/project/${p.id}?from=soumissionnaire`)" class="btn-view">📋 Voir détails</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';

export default {
  name: "DashboardSoumissionnaire",
  components: { PageWrapper },
  data() {
    return {
      form: {
        titre: "",
        description: "",
        secteur: "",
        poles: [],
        cout_estimatif: null,
        duree_mois: null,
        organisme_tutelle: "",
        autre_administration: "",
        structure_soumissionnaire: "",
        point_focal_nom: "",
        point_focal_fonction: "",
        point_focal_telephone: "",
        point_focal_email: "",
        certification: false,
        lettre_soumission: [],
        note_conceptuelle: [],
        etudes_plans: [],
        autres_pieces: []
      },
      coutFormate: "", // Pour afficher le coût avec séparateur de milliers
      files: [],
      projects: [],
      loading: false,
      submitting: false,
      submitError: "",
      submitSuccess: "",
      complements: {},
      showSubmissionForm: false, // Nouveau: contrôle l'affichage du formulaire
      userAccountStatus: null, // Statut du compte utilisateur (verifie, non_verifie, suspendu)

      ministeres: [], // Chargé dynamiquement depuis l'API (deprecated - use ministeresActifs)
      ministeresActifs: [], // Liste d'objets ministères actifs

      // Variables pour l'organisme de tutelle hiérarchique
      typeOrganisme: "",
      typeInstitution: "",
      nomInstitution: "",
      nomMinistere: "",
      nomMinistereLibre: "",
      niveauCollectivite: "",
      regionParente: "",
      departementParent: "",
      communeSelectionnee: "",
      nomStructure: "",
      nomAgence: "",
      tutelleAgence: "",
      tutelleAgenceLibre: "",
      tutelleAgenceAutre: "",

      // Données de collectivités territoriales
      regions: [],
      departements: {}, // Format: { region: [dept1, dept2, ...] }
      communes: {}, // Format: { departement: [commune1, commune2, ...] }

      secteurs: [
        "agriculture-élevage-pêche",
        "environnement-eau-assainissement",
        "énergies-mines",
        "industrie-artisanat",
        "économie-finances-commerce",
        "tourisme-culture",
        "transports-infrastructures",
        "postes-communication-télécommunications-économie numérique",
        "population-jeunesse-emploi-travail-fonction publique",
        "habitat-urbanisme",
        "éducation-formation-recherche",
        "gouvernance-justice-défense-sécurité",
        "santé-action sociale",
        "sports-loisirs",
        "aménagement-développement territorial-décentralisation",
        "affaires étrangères-intégration"
      ],
      // 8 pôles territoriaux officiels
      polesOptions: [
        "Dakar",
        "Thiès",
        "Centre (Kaolack, Fatick, Kaffrine)",
        "Diourbel-Louga",
        "Sud (Ziguinchor, Sédhiou, Kolda)",
        "Sud-Est (Tambacounda, Kédougou)",
        "Nord (Saint-Louis)",
        "Nord-Est (Matam)"
      ]
    };
  },
  computed: {
    departementsFiltered() {
      if (!this.regionParente) return [];
      return this.departements[this.regionParente] || [];
    },

    communesFiltered() {
      if (!this.departementParent) return [];
      return this.communes[this.departementParent] || [];
    },

    canSubmitProject() {
      // L'utilisateur peut soumettre un projet seulement si son compte est vérifié
      return this.userAccountStatus === 'verifie';
    }
  },
  mounted() {
    this.loadUserAccountStatus();
    this.loadProjects();
    this.loadMinisteres();
    this.loadDataLists();
  },
  methods: {
    async loadUserAccountStatus() {
      try {
        const user = JSON.parse(localStorage.getItem("user") || "null");
        if (!user) {
          this.$router.push("/login");
          return;
        }

        // Récupérer le statut du compte utilisateur
        const res = await fetch(`/api/users/${user.username}/status`);
        if (res.ok) {
          const data = await res.json();
          this.userAccountStatus = data.statut_compte || 'verifie'; // Par défaut vérifié si pas de statut
        } else {
          // En cas d'erreur, on suppose que le compte est vérifié (pour ne pas bloquer les anciens comptes)
          this.userAccountStatus = 'verifie';
        }
      } catch (error) {
        console.error('Erreur lors du chargement du statut du compte:', error);
        this.userAccountStatus = 'verifie'; // Par défaut vérifié en cas d'erreur
      }
    },

    showBlockedMessage() {
      if (this.userAccountStatus === 'non_verifie') {
        alert("Votre compte n'a pas encore été vérifié. Veuillez attendre la validation de votre compte avant de soumettre un projet.");
      } else if (this.userAccountStatus === 'suspendu') {
        alert("Votre compte est suspendu. Vous ne pouvez pas soumettre de projet. Veuillez contacter l'administration.");
      }
    },

    async loadMinisteres() {
      try {
        const response = await fetch('/api/ministeres');
        if (response.ok) {
          const data = await response.json();
          this.ministeresActifs = data.filter(m => m.actif);
          // Pour la compatibilité avec l'ancien code (si utilisé ailleurs)
          this.ministeres = data.map(m =>
            m.abreviation ? `${m.abreviation} - ${m.nom_complet}` : m.nom_complet
          );
        }
      } catch (error) {
        console.error('Erreur lors du chargement des ministères:', error);
        this.ministeresActifs = [];
        this.ministeres = [];
      }
    },

    async loadDataLists() {
      try {
        const resRegions = await fetch('/api/data/regions');
        if (resRegions.ok) {
          this.regions = await resRegions.json();
        }

        const resDept = await fetch('/api/data/departements?format=dict');
        if (resDept.ok) {
          this.departements = await resDept.json();
        }

        const resCommunes = await fetch('/api/data/communes?format=dict');
        if (resCommunes.ok) {
          this.communes = await resCommunes.json();
        }
      } catch (err) {
        console.error('Erreur lors du chargement des données territoriales:', err);
      }
    },

    // Gestionnaires de changement pour réinitialiser les champs enfants
    onTypeOrganismeChange() {
      // Réinitialiser tous les champs
      this.typeInstitution = "";
      this.nomInstitution = "";
      this.nomMinistere = "";
      this.nomMinistereLibre = "";
      this.niveauCollectivite = "";
      this.regionParente = "";
      this.departementParent = "";
      this.nomStructure = "";
      this.nomAgence = "";
      this.tutelleAgence = "";
      this.tutelleAgenceLibre = "";
      this.tutelleAgenceAutre = "";
    },

    onTypeInstitutionChange() {
      this.nomInstitution = "";
      this.nomMinistere = "";
      this.nomMinistereLibre = "";
    },

    onNiveauCollectiviteChange() {
      this.regionParente = "";
      this.departementParent = "";
      this.nomStructure = "";
    },

    onTutelleAgenceChange() {
      this.tutelleAgenceLibre = "";
      this.tutelleAgenceAutre = "";
    },

    // Construire la valeur finale de l'organisme de tutelle
    construireOrganismeTutelle() {
      if (this.typeOrganisme === 'institution') {
        if (this.typeInstitution === 'presidence') {
          return 'Présidence de la République';
        } else if (this.typeInstitution === 'primature') {
          return 'Primature';
        } else if (this.typeInstitution === 'ministere') {
          if (this.nomMinistere === '__autre__') {
            return this.nomMinistereLibre;
          } else {
            return this.nomMinistere;
          }
        } else if (this.typeInstitution === 'autre_institution') {
          return this.nomInstitution;
        }
      } else if (this.typeOrganisme === 'collectivite') {
        return this.nomStructure;
      } else if (this.typeOrganisme === 'agence') {
        let tutelle = '';
        if (this.tutelleAgence === 'presidence') {
          tutelle = 'Présidence de la République';
        } else if (this.tutelleAgence === 'primature') {
          tutelle = 'Primature';
        } else if (this.tutelleAgence === '__ministere__') {
          tutelle = this.tutelleAgenceLibre === '__autre__' ? this.tutelleAgenceAutre : this.tutelleAgenceLibre;
        }
        return `${this.nomAgence} (Tutelle: ${tutelle})`;
      } else if (this.typeOrganisme === 'autre') {
        return this.nomStructure;
      }
      return '';
    },
    // Méthodes pour le formatage du téléphone
    initTelephone() {
      // Pré-remplir avec +221 si le champ est vide (par défaut pour le Sénégal)
      if (!this.form.point_focal_telephone || this.form.point_focal_telephone.trim() === "") {
        this.form.point_focal_telephone = "+221 ";
      }
    },

    formatTelephone(event) {
      let value = event.target.value;

      // Permettre la modification de l'indicatif (ne plus forcer +221)
      // L'utilisateur peut saisir n'importe quel indicatif international

      // Si le champ ne commence pas par +, l'ajouter automatiquement
      if (value && !value.startsWith("+")) {
        value = "+" + value;
      }

      // Formater simplement en ajoutant des espaces tous les 3 chiffres après l'indicatif
      // Ceci permet une flexibilité pour tous les pays
      this.form.point_focal_telephone = value;
    },

    // Ouvrir le formulaire et pré-remplir avec les données utilisateur
    openSubmissionForm() {
      this.showSubmissionForm = true;
      this.initializeFormWithUserData();
    },

    // Pré-remplir le formulaire avec les données du compte utilisateur
    async initializeFormWithUserData() {
      try {
        const user = JSON.parse(localStorage.getItem("user") || "null");
        if (!user) return;

        // Charger les données complètes du profil utilisateur
        const response = await fetch(`/api/users/${user.username}/profile`);
        if (response.ok) {
          const userData = await response.json();

          // Pré-remplir la structure soumissionnaire
          if (userData.nom_structure) {
            this.form.structure_soumissionnaire = userData.nom_structure;
          }

          // Pré-remplir l'organisme de tutelle si disponible
          if (userData.nom_structure) {
            // Mettre la même valeur que la structure par défaut
            // L'utilisateur pourra la modifier si nécessaire
            this.nomStructure = userData.nom_structure;
          }

          // Pré-remplir les informations du point focal
          if (userData.display_name) {
            this.form.point_focal_nom = userData.display_name;
          }
          if (userData.fonction) {
            this.form.point_focal_fonction = userData.fonction;
          }
          if (userData.telephone) {
            this.form.point_focal_telephone = userData.telephone;
          }
          if (userData.email || userData.username) {
            this.form.point_focal_email = userData.email || userData.username;
          }
        }
      } catch (error) {
        console.error('Erreur lors du chargement des données utilisateur:', error);
        // En cas d'erreur, utiliser les données du localStorage
        const user = JSON.parse(localStorage.getItem("user") || "null");
        if (user) {
          if (user.display_name) {
            this.form.point_focal_nom = user.display_name;
          }
          if (user.fonction) {
            this.form.point_focal_fonction = user.fonction;
          }
          if (user.telephone) {
            this.form.point_focal_telephone = user.telephone;
          }
          if (user.username) {
            this.form.point_focal_email = user.username;
          }
          if (user.nom_structure) {
            this.form.structure_soumissionnaire = user.nom_structure;
            this.nomStructure = user.nom_structure;
          }
        }
      }
    },

    // Méthodes pour le formatage du coût estimatif
    formatNumber(value) {
      if (!value && value !== 0) return "";
      const number = typeof value === "string" ? parseFloat(value.replace(/\s/g, "")) : value;
      if (isNaN(number)) return "";
      return new Intl.NumberFormat('fr-FR').format(number);
    },
    
    parseNumber(formattedValue) {
      if (!formattedValue) return null;
      const cleaned = formattedValue.replace(/\s/g, "");
      const number = parseFloat(cleaned);
      return isNaN(number) ? null : number;
    },
    
    onCoutInput(event) {
      const value = event.target.value;
      // Supprimer tout ce qui n'est pas un chiffre ou un point décimal
      const cleaned = value.replace(/[^\d.,]/g, "").replace(',', '.');
      
      // Convertir en nombre et formater
      const number = parseFloat(cleaned);
      if (!isNaN(number)) {
        this.form.cout_estimatif = number;
        this.coutFormate = this.formatNumber(number);
      } else {
        this.form.cout_estimatif = null;
        this.coutFormate = cleaned; // Garder la saisie en cours
      }
    },
    
    onCoutBlur() {
      // Au moment où l'utilisateur quitte le champ, formater proprement
      if (this.form.cout_estimatif) {
        this.coutFormate = this.formatNumber(this.form.cout_estimatif);
      }
    },
    
    async loadProjects() {
      this.loading = true;
      try {
        const user = JSON.parse(localStorage.getItem("user") || "null");
        if (!user) return this.$router.push("/login");
        const res = await fetch(`/api/projects?role=${user.role}&username=${user.username}`);
        if (!res.ok) throw new Error(`GET /api/projects ${res.status}`);
        this.projects = await res.json();
        // init complements state - créer un nouvel objet pour la réactivité Vue 3
        const newComplements = {};
        this.projects.forEach(p => {
          newComplements[p.id] = this.complements[p.id] || { message: "", files: [], error: "", ok: "" };
        });
        this.complements = newComplements;
      } catch (e) {
        console.error(e); alert("Erreur chargement projets");
      } finally { this.loading = false; }
    },
    // Gestion des fichiers séparés
    handleLettreFile(e) {
      const added = Array.from(e.target.files || []);
      this.form.lettre_soumission = this.form.lettre_soumission.concat(added);
      e.target.value = "";
    },
    removeLettreFile(i) {
      this.form.lettre_soumission.splice(i, 1);
    },
    handleNoteFile(e) {
      const added = Array.from(e.target.files || []);
      this.form.note_conceptuelle = this.form.note_conceptuelle.concat(added);
      e.target.value = "";
    },
    removeNoteFile(i) {
      this.form.note_conceptuelle.splice(i, 1);
    },
    handleEtudesFile(e) {
      const added = Array.from(e.target.files || []);
      this.form.etudes_plans = this.form.etudes_plans.concat(added);
      e.target.value = "";
    },
    removeEtudesFile(i) {
      this.form.etudes_plans.splice(i, 1);
    },
    handleAutresFile(e) {
      const added = Array.from(e.target.files || []);
      this.form.autres_pieces = this.form.autres_pieces.concat(added);
      e.target.value = "";
    },
    removeAutresFile(i) {
      this.form.autres_pieces.splice(i, 1);
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    },
    // Compléments — accumuler/retirer
    handleComplementFiles(id, e) {
      const added = Array.from(e.target.files || []);
      const prev = (this.complements[id] && this.complements[id].files) ? this.complements[id].files : [];
      const next = prev.concat(added);
      if (!this.complements[id]) {
        this.complements[id] = { message: "", files: [], error: "", ok: "" };
      }
      this.complements[id].files = next;
      e.target.value = "";
    },
    removeComplementFile(id, idx) {
      const arr = (this.complements[id] && this.complements[id].files) ? this.complements[id].files.slice() : [];
      arr.splice(idx, 1);
      if (!this.complements[id]) {
        this.complements[id] = { message: "", files: [], error: "", ok: "" };
      }
      this.complements[id].files = arr;
    },
    async handleSubmit() {
      this.submitError = ""; this.submitSuccess = ""; this.submitting = true;

      // Validation: vérifier la certification
      if (!this.form.certification) {
        this.submitError = "Veuillez certifier que les informations fournies sont exactes avant de soumettre le projet";
        this.submitting = false;
        alert("Veuillez certifier que les informations fournies sont exactes avant de soumettre le projet");
        return;
      }

      // Validation: vérifier que les 3 documents requis sont fournis
      if (this.form.lettre_soumission.length === 0) {
        this.submitError = "La lettre de soumission signée est requise";
        this.submitting = false;
        return;
      }
      if (this.form.note_conceptuelle.length === 0) {
        this.submitError = "La note conceptuelle du projet est requise";
        this.submitting = false;
        return;
      }
      if (this.form.etudes_plans.length === 0) {
        this.submitError = "Les études ou plans techniques sont requis";
        this.submitting = false;
        return;
      }

      // Construire et valider l'organisme de tutelle
      const organismeTutelle = this.construireOrganismeTutelle();
      if (!organismeTutelle || organismeTutelle.trim() === '') {
        this.submitError = "Veuillez sélectionner un organisme de tutelle avant de soumettre le projet.";
        this.submitting = false;
        return;
      }

      try {
        const user = JSON.parse(localStorage.getItem("user") || "null");
        if (!user) return this.$router.push("/login");

        const formData = new FormData();
        formData.append("titre", this.form.titre);
        formData.append("description", this.form.description || "");
        formData.append("secteur", this.form.secteur || "");
        formData.append("poles", (this.form.poles || []).join(","));
        formData.append("cout_estimatif", this.form.cout_estimatif || "");
        formData.append("duree_mois", this.form.duree_mois || "");
        formData.append("structure_soumissionnaire", this.form.structure_soumissionnaire || "");
        formData.append("point_focal_nom", this.form.point_focal_nom || "");
        formData.append("point_focal_fonction", this.form.point_focal_fonction || "");
        formData.append("point_focal_telephone", this.form.point_focal_telephone || "");
        formData.append("point_focal_email", this.form.point_focal_email || "");

        // Utiliser l'organisme de tutelle construit
        formData.append("organisme_tutelle", organismeTutelle);
        formData.append("auteur_nom", user.username);

        // Ajouter tous les fichiers avec leurs catégories
        this.form.lettre_soumission.forEach(f => formData.append("lettre_soumission", f));
        this.form.note_conceptuelle.forEach(f => formData.append("note_conceptuelle", f));
        this.form.etudes_plans.forEach(f => formData.append("etudes_plans", f));
        this.form.autres_pieces.forEach(f => formData.append("autres_pieces", f));

        const res = await fetch("/api/projects", { method: "POST", body: formData });
        if (!res.ok) throw new Error(await res.text());
        const j = await res.json();
        this.submitSuccess = j.numero_projet ?
          `Projet soumis avec succès. Numéro de projet: ${j.numero_projet}` :
          (j.message || "Projet soumis");

        // Réinitialiser le formulaire
        this.form = {
          titre: "",
          description: "",
          secteur: "",
          poles: [],
          cout_estimatif: null,
          duree_mois: null,
          organisme_tutelle: "",
          autre_administration: "",
          structure_soumissionnaire: "",
          point_focal_nom: "",
          point_focal_fonction: "",
          point_focal_telephone: "",
          point_focal_email: "",
          certification: false,
          lettre_soumission: [],
          note_conceptuelle: [],
          etudes_plans: [],
          autres_pieces: []
        };
        // Réinitialiser les champs hiérarchiques
        this.typeOrganisme = "";
        this.typeInstitution = "";
        this.nomInstitution = "";
        this.nomMinistere = "";
        this.nomMinistereLibre = "";
        this.niveauCollectivite = "";
        this.regionParente = "";
        this.departementParent = "";
        this.nomStructure = "";
        this.nomAgence = "";
        this.tutelleAgence = "";
        this.tutelleAgenceLibre = "";
        this.tutelleAgenceAutre = "";

        this.coutFormate = "";
        this.files = [];
        this.showSubmissionForm = false; // Fermer le formulaire après soumission réussie
        this.loadProjects();
      } catch (e) {
        this.submitError = typeof e === "string" ? e : e.message;
      } finally { this.submitting = false; }
    },
    async submitComplements(id) {
      const st = this.complements[id] || { message: "", files: [] };
      if (!this.complements[id]) {
        this.complements[id] = { message: "", files: [], error: "", ok: "" };
      }
      this.complements[id].error = "";
      this.complements[id].ok = "";
      
      // Le message n'est obligatoire que s'il n'y a pas de pièces jointes
      const hasMessage = st.message && st.message.trim();
      const hasFiles = st.files && st.files.length > 0;
      
      if (!hasMessage && !hasFiles) {
        this.complements[id].error = "Veuillez fournir soit un message, soit des pièces jointes";
        return;
      }
      
      try {
        const fd = new FormData();
        fd.append("message", st.message ? st.message.trim() : "");
        (st.files || []).forEach(f => fd.append("files", f));
        const res = await fetch(`/api/projects/${id}/complements`, { method: "POST", body: fd });
        if (!res.ok) throw new Error(await res.text());
        this.complements[id].ok = "Compléments envoyés";
        this.loadProjects();
      } catch (e) {
        this.complements[id].error = typeof e === "string" ? e : e.message;
      }
    },
    formatCurrency(a) { return new Intl.NumberFormat('fr-FR',{style:'currency',currency:'XOF',minimumFractionDigits:0}).format(a); },
    labelEval(ev) { return ({evaluateur1:"Évaluateur 1", evaluateur2:"Évaluateur 2", secretariatsct:"Secrétariat SCT"}[ev]||ev); },
    getStatusClass(s) {
      const m = { 
        "soumis":"status-new",
        "en instruction":"status-processing",
        "compléments demandés":"status-complement",
        "compléments soumis":"status-info",
        "favorable":"status-favorable",
        "favorable sous conditions":"status-conditions", 
        "défavorable":"status-defavorable"
      };
      return m[s]||"status-default";
    },
    getAvisClass(a) {
      const m = { "favorable":"avis-favorable","favorable sous conditions":"avis-conditions","défavorable":"avis-defavorable","compléments demandés":"avis-complement" };
      return m[a]||"";
    },
    cancelSubmission() {
      this.showSubmissionForm = false;
      // Réinitialiser le formulaire
      this.form = {
        titre: "",
        description: "",
        secteur: "",
        poles: [],
        cout_estimatif: null,
        duree_mois: null,
        organisme_tutelle: "",
        autre_administration: "",
        structure_soumissionnaire: "",
        point_focal_nom: "",
        point_focal_fonction: "",
        point_focal_telephone: "",
        point_focal_email: "",
        certification: false,
        lettre_soumission: [],
        note_conceptuelle: [],
        etudes_plans: [],
        autres_pieces: []
      };
      // Réinitialiser les champs hiérarchiques
      this.typeOrganisme = "";
      this.typeInstitution = "";
      this.nomInstitution = "";
      this.nomMinistere = "";
      this.nomMinistereLibre = "";
      this.niveauCollectivite = "";
      this.regionParente = "";
      this.departementParent = "";
      this.nomStructure = "";
      this.nomAgence = "";
      this.tutelleAgence = "";
      this.tutelleAgenceLibre = "";
      this.tutelleAgenceAutre = "";

      this.coutFormate = "";
      this.files = [];
      this.submitError = "";
      this.submitSuccess = "";
    },
    closeSuccessPopup() {
      this.submitSuccess = "";
    },
    countByStatus(s){ return this.projects.filter(p=>p.statut===s).length; },
    countEvaluated(){ 
      const evaluatedStatuses = ['favorable', 'favorable sous conditions', 'défavorable', 'évalué'];
      return this.projects.filter(p => evaluatedStatuses.includes(p.statut)).length; 
    }
  }
};
</script>

<style scoped>
.dashboard-container { padding: 1.5rem; max-width: 1400px; margin: 0 auto; }
.section { background: white; border-radius: 12px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.section-header h3 { margin: 0; }
.submit-form { display: flex; flex-direction: column; gap: 1.2rem; }
.form-row { display: grid; gap: 1.2rem; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
.form-group { display: flex; flex-direction: column; }
.form-group label { margin-bottom: 0.5rem; font-weight: 600; color: #2c3e50; }
.form-group input, .form-group textarea, .form-group select { padding: 0.75rem; border: 2px solid #e5e7eb; border-radius: 8px; }
.hint { color:#6b7280; font-size:.85rem; }
.file-list { list-style: none; padding-left: 0; margin: .5rem 0 0; }
.file-list li { display: flex; align-items: center; justify-content: space-between; gap: .75rem; padding: .4rem .6rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: .4rem; }
.btn-link { background: transparent; border: none; color: #2563eb; cursor: pointer; padding: 0; }
.error-message { padding: .75rem; background:#fee2e2; border:1px solid #fca5a5; border-radius:8px; color:#b91c1c; }
.success-message { padding: .75rem; background:#d1fae5; border:1px solid #6ee7b7; border-radius:8px; color:#065f46; }
.btn-submit, .btn-primary, .btn-secondary, .btn-view { padding: .75rem 1.25rem; border:none; border-radius:8px; color:white; cursor:pointer; transition: all 0.3s; }
.btn-submit { background:#059669; }
.btn-primary { background:#2563eb; }
.btn-primary:hover { background:#1d4ed8; }
.btn-secondary { background:#6b7280; }
.btn-secondary:hover { background:#4b5563; }
.btn-view { width: 100%; margin-top: .75rem; background:#6b7280; }
.projects-grid { display:grid; gap:1.2rem; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }
.project-card { background:white; border:1px solid #e5e7eb; border-radius:12px; overflow:hidden; }
.card-header { padding: 1rem; background:#f0f9ff; border-bottom:2px solid #2563eb; display:flex; justify-content:space-between; align-items:center; }
.badge { padding:.25rem .6rem; border-radius:999px; font-size:.8rem; font-weight:700; }
.status-new{background:#3b82f6;color:#fff}
.status-processing{background:#f59e0b;color:#fff}
.status-complement{background:#f97316;color:#fff}
.status-info{background:#06b6d4;color:#fff}
.status-favorable{background:#10b981;color:#fff}
.status-conditions{background:#eab308;color:#fff}
.status-defavorable{background:#ef4444;color:#fff}
.status-default{background:#6b7280;color:#fff}
.card-body { padding: 1rem; }
.avis-favorable{color:#10b981;font-weight:600}.avis-conditions{color:#f59e0b;font-weight:600}.avis-defavorable{color:#ef4444;font-weight:600}.avis-complement{color:#f97316;font-weight:600}
.complements-box { margin-top: .75rem; padding: 1rem; background:#f9fafb; border:1px dashed #e5e7eb; border-radius:8px; }
.stats { display:flex; gap:.75rem; flex-wrap:wrap; margin-bottom:1rem; }
.stat { background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:.5rem .75rem; }
.stat span{color:#6b7280;font-size:.8rem;margin-right:.5rem} .stat strong{color:#111827}
.stat.warning{background:#fffbeb;border-color:#fde68a} .stat.info{background:#ecfeff;border-color:#a5f3fc}
.loading-state{display:flex;flex-direction:column;align-items:center;padding:2rem;color:#6b7280}.spinner{width:40px;height:40px;border:4px solid #e5e7eb;border-top-color:#2563eb;border-radius:50%;animation:spin 1s linear infinite}@keyframes spin{to{transform:rotate(360deg)}}

/* Styles pour l'affichage des numéros de projets */
.card-title-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.project-number {
  background: var(--dgppe-primary);
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  width: fit-content;
  letter-spacing: 0.5px;
}

.card-title-section h4 {
  margin: 0;
  color: #2c3e50;
}

/* Popup de confirmation */
.popup-overlay {
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

.popup-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.popup-icon {
  font-size: 4rem;
  color: #10b981;
  margin-bottom: 1rem;
}

.popup-content h3 {
  color: #10b981;
  margin-bottom: 1rem;
}

.popup-content p {
  color: #374151;
  margin-bottom: 1.5rem;
}

/* Tableau de bord */
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

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: var(--dgppe-primary);
  margin: 0;
}

/* Section d'action */
.action-section {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 16px;
}

.btn-new-project {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 28px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--dgppe-primary) 0%, var(--dgppe-primary-light) 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(46, 107, 107, 0.2);
}

.btn-new-project:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(46, 107, 107, 0.3);
  background: linear-gradient(135deg, var(--dgppe-primary-light) 0%, var(--dgppe-primary) 100%);
}

.btn-cancel {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  font-size: 16px;
  font-weight: 600;
  background: #6b7280;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-cancel:hover {
  background: #4b5563;
  transform: translateY(-2px);
}

.btn-profile-header {
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

.btn-profile-header:hover {
  background: var(--dgppe-secondary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-profile-header svg {
  width: 18px;
  height: 18px;
}

.icon-plus {
  font-size: 18px;
  font-weight: bold;
}

/* Form section title */
.form-section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--dgppe-primary);
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
}

/* Full width form group */
.form-group.full-width {
  grid-column: 1 / -1;
}

/* File info text */
.file-info {
  color: #6b7280;
  font-size: 0.9rem;
  margin: 0.5rem 0 1rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

/* File list styling */
.file-name {
  font-weight: 500;
  color: #374151;
  word-break: break-word;
}

.file-size {
  color: #6b7280;
  font-size: 0.85rem;
}

/* Certification checkbox styling */
.certification {
  display: flex;
  align-items: start;
  gap: 0.75rem;
  padding: 1rem;
  background: #f0f9ff;
  border: 2px solid #3b82f6;
  border-radius: 8px;
  cursor: pointer;
}

.certification input[type="checkbox"] {
  margin-top: 0.25rem;
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.certification span {
  flex: 1;
  line-height: 1.5;
  color: #1e40af;
  font-weight: 500;
}

/* Multi-select styling - compact mode (dropdown style) */
.multi-select-compact {
  height: auto;
  min-height: 42px;
}

.multi-select-compact option {
  padding: 8px;
  cursor: pointer;
}

.multi-select-compact option:checked {
  background: var(--dgppe-primary);
  color: white;
  font-weight: 600;
}

/* Bannières d'avertissement */
.warning-banner {
  display: flex;
  align-items: flex-start;
  gap: 1.5rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.warning-banner-info {
  background: linear-gradient(135deg, #e0f2fe 0%, #f0f9ff 100%);
  border: 2px solid #0ea5e9;
}

.warning-banner-danger {
  background: linear-gradient(135deg, #fee2e2 0%, #fef2f2 100%);
  border: 2px solid #ef4444;
}

.banner-icon {
  font-size: 3rem;
  flex-shrink: 0;
}

.banner-content {
  flex: 1;
}

.warning-banner-info .banner-content h3 {
  color: #0369a1;
  margin: 0 0 0.75rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.warning-banner-danger .banner-content h3 {
  color: #b91c1c;
  margin: 0 0 0.75rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.warning-banner-info .banner-content p {
  color: #075985;
  margin: 0.5rem 0;
  line-height: 1.6;
}

.warning-banner-danger .banner-content p {
  color: #991b1b;
  margin: 0.5rem 0;
  line-height: 1.6;
}

.banner-note {
  font-style: italic;
  font-size: 0.9rem;
  margin-top: 0.75rem;
}

/* Bouton désactivé */
.btn-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #9ca3af;
}

.btn-disabled:hover {
  transform: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: #9ca3af;
}
</style>