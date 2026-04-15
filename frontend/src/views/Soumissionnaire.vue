<template>
  <!-- Version 1.0.5 - DEPLOY 2025-12-09 19:20 - Force rebuild avec Présumé -->
  <PageWrapper>
    <div class="container">
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
          <button @click="afficherFormulaire = !afficherFormulaire" class="btn-new-project">
            📝 Soumettre un nouveau projet
            <span class="icon-plus">➕</span>
          </button>
        </div>
      </div>

      <!-- ✅ Formulaire de soumission -->
      <div v-if="afficherFormulaire" class="form-container">
        <h3 class="form-title">📝 Nouveau projet</h3>
        <form @submit.prevent="soumettreProjet" class="formulaire">
          <div class="form-group">
            <label>Titre du projet</label>
            <input type="text" v-model="nouveauProjet.titre" required />
          </div>

          <!-- Nouveauté -->
          <div class="form-group">
            <label>Nouveauté du projet *</label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" v-model="nouveauProjet.nouveaute" value="projet_initial" required />
                Projet initial
              </label>
              <label class="radio-label">
                <input type="radio" v-model="nouveauProjet.nouveaute" value="phase_2" />
                Phase II d'un projet
              </label>
            </div>
          </div>

          <!-- Référence au projet initial (si Phase II) -->
          <div v-if="nouveauProjet.nouveaute === 'phase_2'" class="form-group">
            <label>Référence du projet initial (Phase I) *</label>
            <input
              type="text"
              v-model="nouveauProjet.projet_initial_ref"
              placeholder="Ex: DGPPE-24-001"
              required
            />
            <small>Indiquez le numéro du projet initial dont celui-ci est la continuation</small>
          </div>

          <!-- Niveau de priorité -->
          <div class="form-group">
            <label>Niveau de priorité *</label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" v-model="nouveauProjet.niveau_priorite" value="standard" required />
                Projet standard
              </label>
              <label class="radio-label">
                <input type="radio" v-model="nouveauProjet.niveau_priorite" value="prioritaire_ant" />
                Projet prioritaire ANT Sénégal2050 (étude accélérée)
              </label>
            </div>
            <small>Les projets prioritaires ANT bénéficient d'une étude accélérée</small>
          </div>

          <div class="form-group">
            <label>Description du projet</label>
            <textarea
              v-model="nouveauProjet.description"
              rows="4"
              placeholder="Décrivez brièvement votre projet..."
              required
            ></textarea>
          </div>

          <!-- Organisme de tutelle - Sélection hiérarchique -->
          <div class="form-group">
            <label>Type d'organisme de tutelle *</label>
            <select v-model="typeOrganisme" @change="onTypeOrganismeChange" required>
              <option value="">-- Sélectionnez --</option>
              <option value="ministere">Ministère / Direction nationale</option>
              <option value="collectivite">Collectivité territoriale</option>
              <option value="entite">Entité publique</option>
            </select>
          </div>

          <!-- Institution - avec sous-catégories -->
          <div v-if="typeOrganisme === 'ministere'" class="form-group">
            <label>Type d'institution *</label>
            <select v-model="typeInstitution" @change="onTypeInstitutionChange" required>
              <option value="">-- Sélectionnez --</option>
              <option value="presidence">Présidence de la République</option>
              <option value="primature">Primature</option>
              <option value="ministere">Ministère</option>
              <option value="autre_institution">Autre Institution</option>
            </select>

            <!-- Champ pour préciser l'institution si "Autre Institution" -->
            <div v-if="typeInstitution === 'autre_institution'" class="form-group">
              <label>Nom de l'institution *</label>
              <input v-model="nomInstitution" placeholder="Ex: Assemblée nationale" required />
            </div>

            <!-- Champ pour sélectionner le ministère -->
            <div v-if="typeInstitution === 'ministere'" class="form-group">
              <label>Nom du ministère *</label>
              <select v-model="nomMinistere" @change="onMinistereChange" required>
                <option value="">-- Sélectionnez un ministère --</option>
                <option v-for="ministere in ministeresActifs" :key="ministere.id" :value="ministere.nom_complet">
                  {{ ministere.nom_complet }}
                </option>
                <option value="__autre__">Autre (non listé)</option>
              </select>

              <!-- Champ libre si "Autre" est sélectionné -->
              <div v-if="nomMinistere === '__autre__'" class="form-group">
                <label>Nom du ministère *</label>
                <input v-model="nomMinistereLibre" placeholder="Ex: Autre ministère" required />
              </div>
            </div>
          </div>

          <!-- Collectivité territoriale - sélection en cascade -->
          <div v-if="typeOrganisme === 'collectivite'">
            <div class="form-group">
              <label>Niveau *</label>
              <select v-model="niveauCollectivite" @change="onNiveauCollectiviteChange" required>
                <option value="">-- Sélectionnez le niveau --</option>
                <option value="departement">Département</option>
                <option value="commune">Commune</option>
              </select>
            </div>

            <!-- Si département sélectionné -->
            <div v-if="niveauCollectivite === 'departement'">
              <div class="form-group">
                <label>Région *</label>
                <select v-model="regionParente" @change="onRegionChange" required>
                  <option value="">-- Sélectionnez une région --</option>
                  <option v-for="region in regions" :key="region" :value="region">
                    {{ region }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Département *</label>
                <select v-model="nomStructure" :disabled="!regionParente" required>
                  <option value="">-- Sélectionnez un département --</option>
                  <option v-for="dept in departementsFiltered" :key="dept" :value="`Département de ${dept}`">
                    Département de {{ dept }}
                  </option>
                </select>
              </div>
            </div>

            <!-- Si commune sélectionnée -->
            <div v-if="niveauCollectivite === 'commune'">
              <div class="form-group">
                <label>Région *</label>
                <select v-model="regionParente" @change="onRegionChangeCommunes" required>
                  <option value="">-- Sélectionnez une région --</option>
                  <option v-for="region in regions" :key="region" :value="region">
                    {{ region }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>Département *</label>
                <select v-model="departementParent" @change="onDepartementChangeCommunes" :disabled="!regionParente" required>
                  <option value="">-- Sélectionnez un département --</option>
                  <option v-for="dept in departementsFiltered" :key="dept" :value="dept">
                    {{ dept }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label>Commune *</label>
                <select v-model="communeSelectionnee" @change="onCommuneChange" :disabled="!departementParent" required>
                  <option value="">-- Sélectionnez une commune --</option>
                  <option v-for="commune in communesFiltered" :key="commune" :value="commune">
                    {{ commune }}
                  </option>
                  <option value="__autre__">Autre commune (non listée)</option>
                </select>

                <!-- Champ de saisie libre si "Autre commune" est sélectionnée -->
                <div v-if="communeSelectionnee === '__autre__'" class="form-group">
                  <label>Nom de la commune *</label>
                  <input v-model="nomStructure" placeholder="Ex: Commune de Dar Salam" required />
                </div>
              </div>
            </div>
          </div>

          <!-- Entité publique -->
          <div v-if="typeOrganisme === 'entite'">
            <div class="form-group">
              <label>Nom de l'entité *</label>
              <input v-model="nomAgence" placeholder="Ex: APIX SA, Présidence de la République, Assemblée nationale, etc." required />
            </div>

            <div class="form-group">
              <label>Autorité de tutelle (si applicable)</label>
              <select v-model="tutelleAgence" @change="onTutelleAgenceChange">
                <option value="">-- Aucune / Non applicable --</option>
                <option value="Primature">Primature</option>
                <option value="Présidence de la République">Présidence de la République</option>
                <option value="__ministere__">Ministère sectoriel</option>
              </select>

              <!-- Sélection du ministère de tutelle si ministère sélectionné -->
              <div v-if="tutelleAgence === '__ministere__'" class="form-group">
                <label>Ministère de tutelle *</label>
                <select v-model="tutelleAgenceLibre" @change="onTutelleMinistereChange" required>
                  <option value="">-- Sélectionnez un ministère --</option>
                  <option v-for="ministere in ministeresActifs" :key="ministere.id" :value="ministere.nom_complet">
                    {{ ministere.nom_complet }}
                  </option>
                  <option value="__autre__">Autre (non listé)</option>
                </select>

                <!-- Champ libre si "Autre" est sélectionné -->
                <div v-if="tutelleAgenceLibre === '__autre__'" class="form-group">
                  <label>Nom du ministère de tutelle *</label>
                  <input v-model="tutelleAgenceAutre" placeholder="Précisez le ministère" required />
                </div>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Secteur de planification</label>
            <select v-model="nouveauProjet.secteur" required>
              <option value="">-- Choisir un secteur --</option>
              <option v-for="secteur in secteursPlanification" :key="secteur" :value="secteur">
                {{ secteur }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Pôles territoriaux concernés</label>
            <select v-model="nouveauProjet.poles" required>
              <option value="">-- Choisir un pôle --</option>
              <option v-for="pole in polesTerritori


" :key="pole" :value="pole">
                {{ pole }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Coût estimatif (FCFA)</label>
            <input
              type="number"
              v-model="nouveauProjet.cout_estimatif"
              required
              min="0"
            />
          </div>

          <!-- Type de financement -->
          <div class="form-group">
            <label>Type de financement * (plusieurs choix possibles)</label>
            <div class="checkbox-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="typesFinancement.ppp" />
                Partenariat Public-Privé (PPP)
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="typesFinancement.public" />
                Financement public (État)
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="typesFinancement.prive" />
                Financement privé pur
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="typesFinancement.collectivite" />
                Collectivités territoriales
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="typesFinancement.presume" />
                Présumé
              </label>
            </div>
            <small>Sélectionnez au moins un type de financement envisagé</small>
          </div>

          <div class="form-group">
            <label>Pièces jointes</label>
            <input
              type="file"
              ref="fichiers"
              multiple
              @change="gererFichiers"
              accept=".pdf,.doc,.docx,.xlsx,.jpg,.png"
            />
          </div>

          <button type="submit">Soumettre le projet</button>
        </form>
      </div>

    <!-- ✅ Popup de confirmation -->
    <div v-if="popupVisible" class="popup">
      <div class="popup-content">
        <h3>Projet soumis avec succès !</h3>
        <p>Votre projet a bien été enregistré.</p>
        <button @click="fermerPopup">OK</button>
      </div>
    </div>

    <!-- ✅ Projets nécessitant des compléments -->
    <div v-if="projetsAvecComplements.length > 0" class="complements-section">
      <h3>Projets nécessitant des compléments</h3>
      <div v-for="projet in projetsAvecComplements" :key="projet.id" class="complement-card">
        <div class="card-header">
          <h4>{{ projet.titre }}</h4>
          <span class="badge status-complement">Compléments demandés</span>
        </div>
        <div class="card-body">
          <p><strong>Secteur de planification:</strong> {{ projet.secteur }}</p>
          <p v-if="projet.poles"><strong>Pôle(s) territorial(aux):</strong> {{ projet.poles }}</p>
          <p><strong>Commentaires de l'évaluateur:</strong></p>
          <div class="evaluator-comment">{{ projet.commentaires || "Aucun commentaire spécifique" }}</div>
          
          <!-- Formulaire de soumission des compléments -->
          <form @submit.prevent="soumettreComplements(projet.id)" class="complement-form" v-if="complementsData[projet.id]">
            <div class="form-group">
              <label>Votre réponse / Explications (optionnel) :</label>
              <textarea 
                v-model="complementsData[projet.id].message" 
                rows="4" 
                placeholder="Expliquez les modifications apportées ou répondez aux questions (optionnel)..."
              ></textarea>
              <small>Vous pouvez soumettre uniquement des fichiers, ou uniquement un message, ou les deux.</small>
            </div>
            
            <div class="form-group">
              <label>Pièces jointes complémentaires :</label>
              <input
                type="file"
                :ref="`files_${projet.id}`"
                multiple
                @change="gererFichiersComplements(projet.id, $event)"
                accept=".pdf,.doc,.docx,.xlsx,.jpg,.png"
              />
              <small>Formats acceptés: PDF, DOC, DOCX, XLSX, JPG, PNG</small>
            </div>
            
            <button type="submit" class="btn-submit-complements">
              Soumettre les compléments
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- ✅ Tableau des projets soumis -->
    <div class="table-wrapper" v-if="projets.length > 0">
      <h3>Mes projets soumis</h3>
      <table>
        <thead>
          <tr>
            <th>N° Projet</th>
            <th>Titre</th>
            <th>Secteur</th>
            <th>Pôles</th>
            <th>Coût estimatif</th>
            <th>Pièces jointes</th>
            <th>Statut</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in projets" :key="p.id">
            <td><strong>{{ p.numero_projet || 'N/A' }}</strong></td>
            <td>{{ p.titre }}</td>
            <td>{{ p.secteur }}</td>
            <td>{{ p.poles }}</td>
            <td>{{ formatMontant(p.cout_estimatif) }}</td>
            <td>{{ p.pieces_jointes || "—" }}</td>
            <td>
              <span :class="getStatusClass(p.statut)">{{ p.statut || "En attente" }}</span>
            </td>
            <td>
              <button @click="voirHistorique(p.id)" class="btn-small">Historique</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Popup historique -->
    <div v-if="historiqueVisible" class="popup">
      <div class="popup-content historique-popup">
        <h3>Historique du projet</h3>
        <div class="historique-list">
          <div v-for="entry in historiqueData" :key="entry.id" class="historique-item">
            <div class="historique-date">{{ formatDate(entry.timestamp) }}</div>
            <div class="historique-action">{{ entry.action }}</div>
            <div class="historique-auteur">{{ entry.auteur }} ({{ entry.role }})</div>
          </div>
        </div>
        <button @click="fermerHistorique">Fermer</button>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';

export default {
  components: {
    PageWrapper
  },
  data() {
    return {
      afficherFormulaire: false,
      nouveauProjet: {
        titre: "",
        description: "",
        ministere: "",
        secteur: "",
        poles: "",
        cout_estimatif: "",
        pieces_jointes: "",
        nouveaute: "projet_initial", // Valeur par défaut
        projet_initial_ref: "",
        niveau_priorite: "standard", // Valeur par défaut
      },
      typesFinancement: {
        ppp: false,
        public: false,
        prive: false,
        collectivite: false,
        presume: false
      },
      fichiers: [],
      projets: [],
      complementsData: {},
      fichiersByProject: {},
      popupVisible: false,
      historiqueVisible: false,
      historiqueData: [],
      soumissionnaire: null, // sera initialisé depuis localStorage
      ministeresActifs: [],

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

      secteursPlanification: [
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
      polesTerritori: [
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
    projetsAvecComplements() {
      const result = this.projets.filter(p => p.statut === 'compléments demandés');
      console.log("Computed projetsAvecComplements:", result.length, result);
      return result;
    },

    // Départements filtrés selon la région sélectionnée
    departementsFiltered() {
      if (!this.regionParente) return [];
      return this.departements[this.regionParente] || [];
    },

    // Communes filtrées selon le département sélectionné
    communesFiltered() {
      if (!this.departementParent) return [];
      return this.communes[this.departementParent] || [];
    }
  },
  methods: {
    gererFichiers(event) {
      this.fichiers = Array.from(event.target.files);
    },

    gererFichiersComplements(projectId, event) {
      this.fichiersByProject[projectId] = Array.from(event.target.files);
    },

    // Méthodes pour gérer les changements de sélection hiérarchique
    onTypeOrganismeChange() {
      // Réinitialiser tous les champs quand le type change
      this.typeInstitution = "";
      this.nomInstitution = "";
      this.nomMinistere = "";
      this.nomMinistereLibre = "";
      this.niveauCollectivite = "";
      this.regionParente = "";
      this.departementParent = "";
      this.communeSelectionnee = "";
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

    onMinistereChange() {
      if (this.nomMinistere !== '__autre__') {
        this.nomMinistereLibre = "";
      }
    },

    onNiveauCollectiviteChange() {
      this.regionParente = "";
      this.departementParent = "";
      this.communeSelectionnee = "";
      this.nomStructure = "";
    },

    onRegionChange() {
      this.nomStructure = "";
    },

    onRegionChangeCommunes() {
      this.departementParent = "";
      this.communeSelectionnee = "";
      this.nomStructure = "";
    },

    onDepartementChangeCommunes() {
      this.communeSelectionnee = "";
      this.nomStructure = "";
    },

    onCommuneChange() {
      if (this.communeSelectionnee !== '__autre__') {
        this.nomStructure = `Commune de ${this.communeSelectionnee}`;
      } else {
        this.nomStructure = "";
      }
    },

    onTutelleAgenceChange() {
      this.tutelleAgenceLibre = "";
      this.tutelleAgenceAutre = "";
    },

    onTutelleMinistereChange() {
      if (this.tutelleAgenceLibre !== '__autre__') {
        this.tutelleAgenceAutre = "";
      }
    },

    // Construire la valeur finale de l'organisme de tutelle
    construireOrganismeTutelle() {
      if (this.typeOrganisme === 'ministere') {
        const nom = this.nomMinistere === '__autre__' ? this.nomMinistereLibre : this.nomMinistere;
        return nom || '';
      } else if (this.typeOrganisme === 'collectivite') {
        return this.nomStructure;
      } else if (this.typeOrganisme === 'entite') {
        let result = this.nomAgence || '';
        let tutelle = '';
        if (this.tutelleAgence === '__ministere__') {
          tutelle = this.tutelleAgenceLibre === '__autre__' ? this.tutelleAgenceAutre : this.tutelleAgenceLibre;
        } else if (this.tutelleAgence) {
          tutelle = this.tutelleAgence;
        }
        if (tutelle) {
          result += ` (Tutelle: ${tutelle})`;
        }
        return result;
      }
      return '';
    },

    async soumettreProjet() {
      // Construire l'organisme de tutelle final
      const organismeTutelle = this.construireOrganismeTutelle();

      // Validation: l'organisme de tutelle est obligatoire
      if (!organismeTutelle || organismeTutelle.trim() === '') {
        alert("Veuillez sélectionner un organisme de tutelle avant de soumettre le projet.");
        return;
      }

      console.log("DEBUG - Organisme de tutelle construit:", organismeTutelle);
      console.log("DEBUG - Type organisme:", this.typeOrganisme);

      // Tentative de récupération de la géolocalisation du projet
      let gpsCoordinates = null;
      if (navigator.geolocation) {
        try {
          const position = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
              resolve,
              reject,
              { timeout: 5000, enableHighAccuracy: true, maximumAge: 0 }
            );
          });

          gpsCoordinates = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: Math.round(position.coords.accuracy)
          };

          console.log('[PROJET] Géolocalisation obtenue:', gpsCoordinates);
        } catch (geoError) {
          console.log('[PROJET] Géolocalisation refusée ou indisponible:', geoError.message);
          // Continue sans GPS - le projet sera soumis sans coordonnées
        }
      }

      const formData = new FormData();
      formData.append("titre", this.nouveauProjet.titre);
      formData.append("description", this.nouveauProjet.description);
      formData.append("organisme_tutelle", organismeTutelle);
      formData.append("secteur", this.nouveauProjet.secteur);
      formData.append("poles", this.nouveauProjet.poles);
      formData.append("cout_estimatif", this.nouveauProjet.cout_estimatif);
      formData.append("auteur_nom", this.soumissionnaire);

      // Nouveaux champs (Décembre 2025)
      formData.append("nouveaute", this.nouveauProjet.nouveaute);
      if (this.nouveauProjet.nouveaute === 'phase_2' && this.nouveauProjet.projet_initial_ref) {
        formData.append("projet_initial_ref", this.nouveauProjet.projet_initial_ref);
      }
      formData.append("niveau_priorite", this.nouveauProjet.niveau_priorite);

      // Type de financement (JSON array)
      const typesFinancementArray = [];
      if (this.typesFinancement.ppp) typesFinancementArray.push('PPP');
      if (this.typesFinancement.public) typesFinancementArray.push('Public');
      if (this.typesFinancement.prive) typesFinancementArray.push('Privé');
      if (this.typesFinancement.collectivite) typesFinancementArray.push('Collectivités');
      if (this.typesFinancement.presume) typesFinancementArray.push('Présumé');

      if (typesFinancementArray.length > 0) {
        formData.append("type_financement", JSON.stringify(typesFinancementArray));
      }

      // Ajouter les coordonnées GPS si disponibles
      if (gpsCoordinates) {
        formData.append("gps_coordinates", JSON.stringify(gpsCoordinates));
      }

      this.fichiers.forEach((fichier) =>
        formData.append("files", fichier, fichier.name)
      );

      const response = await fetch("/api/projects", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        this.popupVisible = true;
        this.fetchProjets();
        this.resetFormulaire();
      } else {
        alert("Erreur lors de la soumission !");
      }
    },

    async soumettreComplements(projectId) {
      try {
        const message = this.complementsData[projectId].message || "";
        const fichiers = this.fichiersByProject[projectId] || [];
        
        // Validation : au moins un message ou un fichier
        if (!message.trim() && fichiers.length === 0) {
          alert("Veuillez fournir au moins un message ou un fichier en complément.");
          return;
        }
        
        const formData = new FormData();
        formData.append("message", message);
        
        // Ajouter les fichiers s'il y en a
        fichiers.forEach((fichier) => {
          formData.append("files", fichier);
        });

        const response = await fetch(`/api/projects/${projectId}/complements`, {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          alert("Compléments soumis avec succès !");
          this.fetchProjets();
          // Reset du formulaire
          this.complementsData[projectId] = { message: '' };
          this.fichiersByProject[projectId] = [];
          if (this.$refs[`files_${projectId}`] && this.$refs[`files_${projectId}`][0]) {
            this.$refs[`files_${projectId}`][0].value = "";
          }
        } else {
          const error = await response.json();
          alert("Erreur : " + (error.error || "Problème lors de la soumission"));
        }
      } catch (err) {
        console.error("Erreur:", err);
        alert("Erreur de connexion");
      }
    },

    async fetchMinisteres() {
      try {
        const res = await fetch("/api/ministeres");
        if (res.ok) {
          const data = await res.json();
          this.ministeresActifs = data.filter(m => m.actif);
        }
      } catch (err) {
        console.error("Erreur lors du chargement des ministères:", err);
      }
    },

    async loadDataLists() {
      try {
        // Charger les régions
        const resRegions = await fetch('/api/data/regions');
        if (resRegions.ok) {
          this.regions = await resRegions.json();
        }

        // Charger les départements (format dictionnaire)
        const resDept = await fetch('/api/data/departements?format=dict');
        if (resDept.ok) {
          this.departements = await resDept.json();
        }

        // Charger les communes (format dictionnaire par département)
        const resCommunes = await fetch('/api/data/communes?format=dict');
        if (resCommunes.ok) {
          this.communes = await resCommunes.json();
        }
      } catch (err) {
        console.error('Erreur lors du chargement des données territoriales:', err);
      }
    },

    async fetchProjets() {
      try {
        console.log("Fetching projets pour:", this.soumissionnaire);
        const url = "/api/projects?role=soumissionnaire&username=" + encodeURIComponent(this.soumissionnaire);
        console.log("URL:", url);
        const res = await fetch(url);

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }

        const data = await res.json();
        console.log("Projets reçus:", data.length, data);
        this.projets = data;

        // Initialiser complementsData pour chaque projet nécessitant des compléments
        this.projets.forEach(projet => {
          console.log("Projet:", projet.titre, "Statut:", projet.statut);
          if (projet.statut === 'compléments demandés') {
            console.log("Initialisation complementsData pour projet", projet.id);
            this.complementsData[projet.id] = { message: '' };
            this.fichiersByProject[projet.id] = [];
          }
        });
        console.log("projetsAvecComplements:", this.projetsAvecComplements.length);
        console.log("complementsData final:", this.complementsData);
      } catch (error) {
        console.error("Erreur dans fetchProjets:", error);
        alert("Erreur lors du chargement des projets: " + error.message);
      }
    },

    async voirHistorique(projectId) {
      try {
        const res = await fetch(`/api/logs/${projectId}`);
        this.historiqueData = await res.json();
        this.historiqueVisible = true;
      } catch (err) {
        alert("Erreur lors du chargement de l'historique");
      }
    },

    formatMontant(val) {
      return Number(val).toLocaleString("fr-FR") + " F CFA";
    },

    formatDate(timestamp) {
      return new Date(timestamp).toLocaleString('fr-FR');
    },

    getStatusClass(statut) {
      const classes = {
        'soumis': 'status-new',
        'assigné': 'status-assigned',
        'évalué': 'status-evaluated',
        'compléments demandés': 'status-complement',
        'compléments fournis': 'status-info',
        'validé': 'status-validated'
      };
      return classes[statut] || 'status-default';
    },

    resetFormulaire() {
      this.nouveauProjet = {
        titre: "",
        description: "",
        ministere: "",
        secteur: "",
        poles: "",
        cout_estimatif: "",
        nouveaute: "projet_initial",
        projet_initial_ref: "",
        niveau_priorite: "standard",
      };

      // Réinitialiser les types de financement
      this.typesFinancement = {
        ppp: false,
        public: false,
        prive: false,
        collectivite: false,
        presume: false
      };

      // Réinitialiser les champs de l'organisme de tutelle
      this.typeOrganisme = "";
      this.typeInstitution = "";
      this.nomInstitution = "";
      this.nomMinistere = "";
      this.nomMinistereLibre = "";
      this.niveauCollectivite = "";
      this.regionParente = "";
      this.departementParent = "";
      this.communeSelectionnee = "";
      this.nomStructure = "";
      this.nomAgence = "";
      this.tutelleAgence = "";
      this.tutelleAgenceLibre = "";
      this.tutelleAgenceAutre = "";

      this.$refs.fichiers.value = "";
      this.fichiers = [];
      this.afficherFormulaire = false;
    },

    fermerPopup() {
      this.popupVisible = false;
    },

    fermerHistorique() {
      this.historiqueVisible = false;
    },
  },
  mounted() {
    // Récupérer l'utilisateur connecté
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    this.soumissionnaire = user.username || 'soumissionnaire';
    console.log("Utilisateur connecté:", this.soumissionnaire);

    // Charger les ministères et les données territoriales
    this.fetchMinisteres();
    this.loadDataLists();

    if (this.soumissionnaire) {
      this.fetchProjets();
    } else {
      alert("Erreur: utilisateur non connecté");
    }
  },
};
</script>

<style scoped>
@import "../assets/styles-shared.css";

.formulaire {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 40px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

.radio-group,
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}

.radio-label,
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: normal;
  cursor: pointer;
}

.radio-label input[type="radio"],
.checkbox-label input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

.form-group small {
  display: block;
  margin-top: 5px;
  color: #666;
  font-size: 0.9em;
  font-style: italic;
}

input,
select {
  width: 100%;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 1rem;
}

button[type="submit"] {
  background-color: #1a73e8;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s;
}

button[type="submit"]:hover {
  background-color: #125ecb;
}

/* ✅ Popup */
.popup {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
}

.popup-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.popup-content h3 {
  color: #1a73e8;
  margin-bottom: 10px;
}

.popup-content button {
  margin-top: 10px;
  background: #1a73e8;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  cursor: pointer;
}

.popup-content button:hover {
  background: #125ecb;
}

/* ✅ Section compléments */
.complements-section {
  margin: 30px 0;
}

.complement-card {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 10px;
  margin-bottom: 20px;
  overflow: hidden;
}

.card-header {
  background: #ffd93d;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h4 {
  margin: 0;
  color: #856404;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8em;
  font-weight: bold;
}

.status-complement {
  background: #dc3545;
  color: white;
}

.card-body {
  padding: 20px;
}

.evaluator-comment {
  background: #f8f9fa;
  border-left: 4px solid #ffd93d;
  padding: 15px;
  margin: 10px 0;
  font-style: italic;
}

.complement-form {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}

.btn-submit-complements {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.btn-submit-complements:hover {
  background: #218838;
}

/* ✅ Statuts dans le tableau */
.status-new { color: #007bff; }
.status-assigned { color: #6f42c1; }
.status-evaluated { color: #28a745; }
.status-complement { color: #dc3545; }
.status-info { color: #17a2b8; }
.status-validated { color: #28a745; font-weight: bold; }
.status-default { color: #6c757d; }

.btn-small {
  padding: 4px 8px;
  font-size: 0.8em;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-small:hover {
  background: #545b62;
}

/* ✅ Popup historique */
.historique-popup {
  max-width: 600px;
  max-height: 500px;
  overflow-y: auto;
}

.historique-list {
  margin: 20px 0;
}

.historique-item {
  padding: 10px;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
}

.historique-date {
  font-size: 0.9em;
  color: #666;
  font-weight: bold;
}

.historique-action {
  margin: 5px 0;
  font-weight: 500;
}

.historique-auteur {
  font-size: 0.8em;
  color: #666;
  font-style: italic;
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

.icon-plus {
  font-size: 18px;
  font-weight: bold;
}

/* Container du formulaire */
.form-container {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 24px;
}

.form-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--dgppe-primary);
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--dgppe-gray-200);
}
</style>
