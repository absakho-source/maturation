<template>
  <PageWrapper>
    <div class="dashboard-container">
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
          <button v-if="!showSubmissionForm" @click="showSubmissionForm = true" class="btn-new-project">
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

          <!-- Structure soumissionnaire et Organisme de tutelle -->
          <div class="form-row">
            <div class="form-group">
              <label>Structure soumissionnaire / Maître d'ouvrage *</label>
              <input v-model="form.structure_soumissionnaire" type="text" required placeholder="Ex: Direction des Infrastructures Sanitaires" />
            </div>
            <div class="form-group">
              <label>Organisme de tutelle *</label>
              <select v-model="form.organisme_tutelle" required>
                <option value="" disabled>-- Sélectionner un ministère --</option>
                <option v-for="ministere in ministeres" :key="ministere" :value="ministere">{{ ministere }}</option>
              </select>
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
              <input v-model="form.point_focal_telephone" type="tel" required placeholder="Ex: +221 77 123 45 67" />
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

          <button type="submit" class="btn-submit" :disabled="submitting || !form.certification">
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

      ministeres: [
        "Ministère de l'Intérieur et de la Sécurité publique",
        "Ministère des Affaires étrangères et des Sénégalais de l'Extérieur",
        "Ministère de la Justice",
        "Ministère des Forces armées",
        "Ministère de l'Économie, du Plan et de la Coopération",
        "Ministère des Finances et du Budget",
        "Ministère de l'Hydraulique et de l'Assainissement",
        "Ministère de l'Énergie, du Pétrole et des Mines",
        "Ministère de l'Agriculture, de la Souveraineté alimentaire et de l'Élevage",
        "Ministère de la Pêche et de l'Économie maritime",
        "Ministère de l'Industrie et du Commerce",
        "Ministère des Infrastructures et des Transports terrestres et aériens",
        "Ministère de l'Urbanisme, des Collectivités territoriales et de l'Aménagement des territoires",
        "Ministère de l'Enseignement supérieur, de la Recherche et de l'Innovation",
        "Ministère de l'Éducation nationale",
        "Ministère de la Formation professionnelle",
        "Ministère de la Santé et de l'Action sociale",
        "Ministère de la Jeunesse, des Sports et de la Culture",
        "Ministère de la Famille et des Solidarités",
        "Ministère de l'Emploi et des Relations avec les institutions",
        "Ministère de l'Environnement et de la Transition écologique",
        "Ministère du Tourisme et de l'Artisanat",
        "Ministère de la Communication, des Télécommunications et de l'Économie numérique",
        "Ministère de la Fonction publique et de la Réforme du service public",
        "Ministère de la Microfinance et de l'Économie sociale et solidaire",
        "Autre administration (à préciser)"
      ],

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
  mounted() { this.loadProjects(); },
  methods: {
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
        this.submitError = "Vous devez cocher la case de certification pour soumettre votre projet";
        this.submitting = false;
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

        // Gérer l'organisme de tutelle avec l'option "Autre administration"
        let organismeValue = this.form.organisme_tutelle || "";
        if (organismeValue === "Autre administration (à préciser)" && this.form.autre_administration) {
          organismeValue = this.form.autre_administration;
        }
        formData.append("organisme_tutelle", organismeValue);
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

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: var(--dgppe-primary);
  margin: 0 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--dgppe-accent);
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
</style>