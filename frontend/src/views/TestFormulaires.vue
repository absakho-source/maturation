<template>
  <PageWrapper>
    <div class="test-formulaires">
      <div class="header-row">
        <h2 class="page-title">Revue des Formulaires — Atelier Jour 3</h2>
        <span class="form-count">{{ forms.length }} formulaires</span>
      </div>

      <p class="intro">
        Cliquez sur un formulaire pour le deplier et visualiser ses champs. Cette page permet de passer en revue tous les formulaires sans avoir besoin de se connecter.
      </p>

      <!-- Navigation rapide -->
      <div class="nav-pills">
        <button v-for="cat in categories" :key="cat.id" :class="['pill', cat.id, { active: activeCategory === cat.id }]" @click="activeCategory = activeCategory === cat.id ? null : cat.id">
          {{ cat.label }} ({{ forms.filter(f => f.category === cat.id).length }})
        </button>
      </div>

      <!-- Liste des formulaires -->
      <div v-for="form in filteredForms" :key="form.id" class="form-block">
        <div :class="['form-header', form.category]" @click="toggle(form.id)">
          <div class="form-header-left">
            <span class="form-number">{{ form.number }}</span>
            <div>
              <h3>{{ form.title }}</h3>
              <span class="form-role">{{ form.role }}</span>
            </div>
          </div>
          <span class="chevron" :class="{ open: openForms[form.id] }">&#9660;</span>
        </div>

        <div v-if="openForms[form.id]" class="form-replica">
          <!-- CONNEXION -->
          <template v-if="form.id === 'login'">
            <div class="field-group">
              <label>Compte</label>
              <select disabled><option>-- Selectionner un compte --</option></select>
            </div>
            <div class="field-group">
              <label>Mot de passe</label>
              <input type="password" disabled placeholder="Entrez votre mot de passe" />
            </div>
            <button class="btn-mock primary">Se connecter</button>
          </template>

          <!-- INSCRIPTION -->
          <template v-if="form.id === 'register'">
            <fieldset>
              <legend>Informations personnelles</legend>
              <div class="field-group"><label>Nom complet *</label><input disabled placeholder="Prenom NOM" /></div>
              <div class="field-group"><label>Telephone</label><input disabled placeholder="+221 77 000 00 00" /></div>
              <div class="field-group"><label>Fonction / Poste</label><input disabled placeholder="Chef de division" /></div>
            </fieldset>
            <fieldset>
              <legend>Structure d'appartenance</legend>
              <div class="field-group">
                <label>Type de structure *</label>
                <select disabled><option>-- Choisir --</option><option>Institution</option><option>Collectivite territoriale</option><option>Agence / Etablissement public</option><option>Autre (ONG, Association, Cabinet...)</option></select>
              </div>
              <div class="conditional-box">
                <span class="conditional-label">Si Institution :</span>
                <div class="field-group"><label>Type d'institution</label><select disabled><option>Presidence</option><option>Primature</option><option>Ministere / Direction nationale</option><option>Autre</option></select></div>
                <div class="field-group"><label>Nom du ministere</label><select disabled><option>-- Liste des ministeres --</option></select></div>
                <div class="field-group"><label>Direction / Service</label><input disabled placeholder="Ex: DGPPE / DPSE" /></div>
              </div>
              <div class="conditional-box">
                <span class="conditional-label">Si Collectivite territoriale :</span>
                <div class="field-group"><label>Niveau</label><select disabled><option>Departement</option><option>Commune</option></select></div>
                <div class="field-group"><label>Region</label><select disabled><option>-- Cascading --</option></select></div>
                <div class="field-group"><label>Departement</label><select disabled><option>-- Cascading --</option></select></div>
                <div class="field-group"><label>Commune</label><select disabled><option>-- Cascading --</option></select></div>
              </div>
              <div class="conditional-box">
                <span class="conditional-label">Si Agence :</span>
                <div class="field-group"><label>Nom de l'agence</label><input disabled placeholder="AGETIP, APIX..." /></div>
                <div class="field-group"><label>Autorite de tutelle</label><select disabled><option>Primature</option><option>Presidence</option><option>Ministere sectoriel</option></select></div>
              </div>
            </fieldset>
            <fieldset>
              <legend>Justificatifs (optionnel)</legend>
              <div class="field-group"><label>Pieces jointes</label><input type="file" disabled multiple /><span class="hint">PDF, JPG, PNG</span></div>
            </fieldset>
            <fieldset>
              <legend>Identifiants de connexion</legend>
              <div class="field-group"><label>Adresse email professionnelle *</label><input type="email" disabled placeholder="prenom.nom@structure.gouv.sn" /></div>
              <div class="field-group"><label>Mot de passe *</label><input type="password" disabled placeholder="Min. 6 caracteres" /></div>
              <div class="field-group"><label>Confirmer le mot de passe *</label><input type="password" disabled /></div>
            </fieldset>
            <button class="btn-mock primary">Creer mon compte</button>
          </template>

          <!-- CONTACT -->
          <template v-if="form.id === 'contact'">
            <div class="field-group"><label>Nom complet *</label><input disabled placeholder="Prenom NOM" /></div>
            <div class="field-group"><label>Email *</label><input type="email" disabled placeholder="email@exemple.com" /></div>
            <div class="field-group"><label>Telephone</label><input disabled placeholder="+221 77 000 00 00" /></div>
            <div class="field-group">
              <label>Objet *</label>
              <select disabled><option>-- Choisir --</option><option>Demande d'information</option><option>Probleme technique</option><option>Question sur la soumission</option><option>Demande de compte</option><option>Autre</option></select>
            </div>
            <div class="field-group"><label>Message *</label><textarea disabled rows="4" placeholder="Votre message..."></textarea></div>
            <div class="field-group"><label>Pieces jointes</label><input type="file" disabled multiple /><span class="hint">PDF, Word, Excel, Images (max 5 Mo)</span></div>
            <div class="field-group"><label>Verification (captcha)</label><input disabled placeholder="12 + 7 = ?" /></div>
            <button class="btn-mock primary">Envoyer le message</button>
          </template>

          <!-- MON PROFIL -->
          <template v-if="form.id === 'profil'">
            <fieldset>
              <legend>Informations personnelles</legend>
              <div class="field-group"><label>Email</label><input type="email" disabled placeholder="email@structure.gouv.sn" /></div>
              <div class="field-group"><label>Telephone</label><input disabled placeholder="+221 77 000 00 00" /></div>
              <div class="field-group"><label>Fonction / Poste</label><input disabled placeholder="Chef de division" /></div>
              <div class="readonly-block">
                <label>Structure d'appartenance</label>
                <div class="readonly-value">Type: Institution | Ministere: MEPC | Direction: DGPPE / DPSE</div>
              </div>
            </fieldset>
            <div class="btn-row">
              <button class="btn-mock secondary">Annuler</button>
              <button class="btn-mock primary">Mettre a jour</button>
            </div>
            <fieldset>
              <legend>Changer le mot de passe</legend>
              <div class="field-group"><label>Ancien mot de passe *</label><input type="password" disabled /></div>
              <div class="field-group"><label>Nouveau mot de passe *</label><input type="password" disabled /></div>
              <div class="field-group"><label>Confirmer le nouveau mot de passe *</label><input type="password" disabled /></div>
            </fieldset>
            <button class="btn-mock primary">Changer le mot de passe</button>
          </template>

          <!-- SOUMISSION PROJET -->
          <template v-if="form.id === 'soumission'">
            <fieldset>
              <legend>Informations du projet</legend>
              <div class="field-group"><label>Titre du projet *</label><input disabled placeholder="Ex: Construction d'un centre de sante" /></div>
              <div class="field-group"><label>Structure soumissionnaire / Maitre d'ouvrage *</label><input disabled placeholder="Nom de la structure" /></div>
            </fieldset>
            <fieldset>
              <legend>Organisme de tutelle</legend>
              <div class="field-group"><label>Type d'organisme de tutelle *</label><select disabled><option>Institution</option><option>Collectivite territoriale</option><option>Agence</option><option>Autre</option></select></div>
              <span class="hint">Memes champs cascading que l'inscription (type institution, ministere, direction...)</span>
            </fieldset>
            <fieldset>
              <legend>Point Focal du projet</legend>
              <div class="field-group"><label>Nom complet</label><input disabled placeholder="Prenom NOM" /></div>
              <div class="field-group"><label>Fonction</label><input disabled /></div>
              <div class="field-group"><label>Telephone</label><input disabled placeholder="+221 77 000 00 00" /></div>
              <div class="field-group"><label>Email</label><input type="email" disabled /></div>
            </fieldset>
            <fieldset>
              <legend>Contexte geographique et secteur</legend>
              <div class="field-group">
                <label>Poles territoriaux concernes *</label>
                <div class="checkbox-group">
                  <label class="cb"><input type="checkbox" disabled /> Dakar</label>
                  <label class="cb"><input type="checkbox" disabled /> Thies - Diourbel</label>
                  <label class="cb"><input type="checkbox" disabled /> Saint-Louis - Matam - Louga</label>
                  <label class="cb"><input type="checkbox" disabled /> Kaolack - Kaffrine - Fatick</label>
                  <label class="cb"><input type="checkbox" disabled /> Ziguinchor - Sedhiou - Kolda</label>
                  <label class="cb"><input type="checkbox" disabled /> Tambacounda - Kedougou</label>
                </div>
              </div>
              <div class="field-group"><label>Secteur de planification *</label><select disabled><option>-- Choisir un secteur --</option></select></div>
            </fieldset>
            <fieldset>
              <legend>Description et couts</legend>
              <div class="field-group"><label>Description du projet *</label><textarea disabled rows="4" placeholder="Max 1000 caracteres"></textarea></div>
              <div class="field-group"><label>Cout estimatif (FCFA) *</label><input disabled placeholder="Ex: 500 000 000" /></div>
              <div class="field-group"><label>Duree estimee (mois)</label><input type="number" disabled placeholder="Ex: 24" /></div>
            </fieldset>
            <fieldset>
              <legend>Nature et priorite</legend>
              <div class="field-group">
                <label>Ce projet est-il</label>
                <div class="radio-group">
                  <label class="rb"><input type="radio" disabled name="nature" /> Projet initial</label>
                  <label class="rb"><input type="radio" disabled name="nature" /> Deuxieme phase (ou plus)</label>
                </div>
              </div>
              <div class="field-group">
                <label>Niveau de priorite</label>
                <div class="radio-group">
                  <label class="rb"><input type="radio" disabled name="priorite" /> Prioritaire (ANT)</label>
                  <label class="rb"><input type="radio" disabled name="priorite" /> Standard</label>
                </div>
              </div>
            </fieldset>
            <fieldset>
              <legend>Financement</legend>
              <div class="field-group">
                <label>Types de financement envisage(s)</label>
                <div class="checkbox-group">
                  <label class="cb"><input type="checkbox" disabled /> PPP</label>
                  <label class="cb"><input type="checkbox" disabled /> Financement public</label>
                  <label class="cb"><input type="checkbox" disabled /> Financement prive</label>
                  <label class="cb"><input type="checkbox" disabled /> Collectivite territoriale</label>
                  <label class="cb"><input type="checkbox" disabled /> Financement international</label>
                  <label class="cb"><input type="checkbox" disabled /> Financement mixte</label>
                </div>
              </div>
            </fieldset>
            <fieldset>
              <legend>Documents a joindre</legend>
              <div class="field-group"><label>Document de formulation du projet</label><input type="file" disabled /></div>
              <div class="field-group"><label>Etude de faisabilite technique</label><input type="file" disabled /></div>
              <div class="field-group"><label>Etude de faisabilite economique</label><input type="file" disabled /></div>
              <div class="field-group"><label>Autres pieces justificatives</label><input type="file" disabled /></div>
            </fieldset>
            <div class="field-group">
              <label class="cb"><input type="checkbox" disabled /> Je certifie l'exactitude des informations fournies *</label>
            </div>
            <button class="btn-mock primary">Soumettre le projet</button>
          </template>

          <!-- DISCUSSION -->
          <template v-if="form.id === 'discussion'">
            <div class="field-group"><label>Message</label><textarea disabled rows="3" placeholder="Ecrivez votre message ici..."></textarea></div>
            <div class="field-group"><label>Pieces jointes</label><input type="file" disabled multiple /><span class="hint">PDF, Word, Excel, Images</span></div>
            <div class="btn-row">
              <button class="btn-mock primary">Envoyer</button>
              <span class="hint">Ctrl+Entree pour envoyer</span>
            </div>
          </template>

          <!-- MATRICE RECEVABILITE -->
          <template v-if="form.id === 'matrice'">
            <table class="mock-table">
              <thead><tr><th>Documents a fournir</th><th>Requis</th><th>Transmis</th><th>Statut</th></tr></thead>
              <tbody>
                <tr v-for="doc in ['Document de formulation du projet', 'Etude de faisabilite technique', 'Etude de faisabilite economique', 'Etude de faisabilite financiere', 'Etude sociale et environnementale', 'Rapport evaluation phase precedente']" :key="doc">
                  <td>{{ doc }}</td>
                  <td><input type="checkbox" disabled checked /></td>
                  <td><input type="checkbox" disabled /></td>
                  <td><span class="badge-missing">Manquant</span></td>
                </tr>
              </tbody>
            </table>
            <button class="btn-mock small secondary">+ Ajouter un document</button>
            <div class="field-group mt"><label>Commentaires et suite a donner</label><textarea disabled rows="3" placeholder="Precisez les documents manquants..."></textarea></div>
            <div class="summary-box">Requis: 6 | Transmis: 0 | Manquants: 6</div>
            <div class="btn-row">
              <button class="btn-mock success">Dossier recevable</button>
              <button class="btn-mock warning">Complements requis</button>
              <button class="btn-mock danger">Dossier rejete</button>
            </div>
          </template>

          <!-- FICHE EVALUATION -->
          <template v-if="form.id === 'fiche-eval'">
            <fieldset>
              <legend>Informations du projet (lecture seule)</legend>
              <div class="readonly-grid">
                <div><strong>Numero:</strong> PRJ-2026-001</div>
                <div><strong>Titre:</strong> Projet exemple</div>
                <div><strong>Soumissionnaire:</strong> Structure X</div>
                <div><strong>Pole:</strong> Dakar</div>
                <div><strong>Secteur:</strong> Infrastructures</div>
                <div><strong>Cout:</strong> 500 000 000 FCFA</div>
                <div><strong>Evaluateur:</strong> Nom Evaluateur</div>
                <div><strong>Date:</strong> 04/03/2026</div>
              </div>
            </fieldset>
            <fieldset>
              <legend>Criteres de notation</legend>
              <div v-for="critere in criteresEval" :key="critere.nom" class="slider-row">
                <label>{{ critere.nom }}</label>
                <input type="range" :min="0" :max="critere.max" :value="Math.floor(critere.max/2)" disabled />
                <span class="slider-val">{{ Math.floor(critere.max/2) }}/{{ critere.max }}</span>
              </div>
              <div class="total-row"><strong>TOTAL : 50 / 100 points</strong></div>
            </fieldset>
            <fieldset>
              <legend>Analyse textuelle</legend>
              <div class="field-group"><label>Points forts identifies</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>Points faibles et risques</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>Recommandations d'amelioration</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>Conditions particulieres</label><textarea disabled rows="2"></textarea></div>
            </fieldset>
            <fieldset>
              <legend>Avis final</legend>
              <div class="radio-group">
                <label class="rb"><input type="radio" disabled name="avis" /> Favorable</label>
                <label class="rb"><input type="radio" disabled name="avis" /> Favorable sous conditions</label>
              </div>
              <div class="field-group mt"><label>Commentaires finaux</label><textarea disabled rows="2"></textarea></div>
            </fieldset>
            <button class="btn-mock primary">Soumettre l'evaluation</button>
          </template>

          <!-- FICHE DGPPE -->
          <template v-if="form.id === 'fiche-dgppe'">
            <fieldset>
              <legend>Informations de base</legend>
              <div class="field-group"><label>Cout du projet</label><input disabled placeholder="Ex: 3,982 Milliards FCFA" /></div>
              <div class="field-group">
                <label>Origine du projet</label>
                <div class="radio-group">
                  <label class="rb"><input type="radio" disabled name="origine" /> Maturation</label>
                  <label class="rb"><input type="radio" disabled name="origine" /> Offre spontanee</label>
                  <label class="rb"><input type="radio" disabled name="origine" /> Autres</label>
                </div>
              </div>
            </fieldset>
            <fieldset>
              <legend>Dimensions transversales</legend>
              <div class="checkbox-group">
                <label class="cb"><input type="checkbox" disabled /> Changement climatique - Adaptation</label>
                <label class="cb"><input type="checkbox" disabled /> Changement climatique - Attenuation</label>
                <label class="cb"><input type="checkbox" disabled /> Genre</label>
              </div>
            </fieldset>
            <fieldset>
              <legend>Analyse strategique</legend>
              <div class="field-group"><label>Articulation</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>Axes</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>Objectifs strategiques</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>ODD</label><textarea disabled rows="2"></textarea></div>
            </fieldset>
            <fieldset>
              <legend>Calendrier et duree</legend>
              <div class="field-row">
                <div class="field-group"><label>Duree de l'analyse</label><input disabled placeholder="25 ans" /></div>
                <div class="field-group"><label>Realisation</label><input disabled placeholder="02 ans" /></div>
                <div class="field-group"><label>Exploitation</label><input disabled placeholder="20 ans" /></div>
              </div>
            </fieldset>
            <fieldset>
              <legend>Contenu du projet</legend>
              <div class="field-group"><label>Localisation</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>Parties prenantes</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>Objectif du projet</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>Activites principales</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>Resultats / Impacts attendus</label><textarea disabled rows="2"></textarea></div>
            </fieldset>
            <fieldset>
              <legend>Criteres d'evaluation DGPPE</legend>
              <div v-for="c in criteresDGPPE" :key="c.nom" class="slider-row">
                <label>{{ c.nom }}</label>
                <input type="range" :min="0" :max="c.max" :value="0" disabled />
                <span class="slider-val">0/{{ c.max }}</span>
              </div>
              <div class="field-group mt"><label>Appreciation</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>Recommandations</label><textarea disabled rows="2"></textarea></div>
            </fieldset>
            <fieldset>
              <legend>Avis final</legend>
              <div class="radio-group">
                <label class="rb"><input type="radio" disabled name="avis-dgppe" /> Avis favorable</label>
                <label class="rb"><input type="radio" disabled name="avis-dgppe" /> Avis favorable sous conditions</label>
              </div>
              <div class="field-group mt"><label>Proposition</label><textarea disabled rows="2"></textarea></div>
              <div class="field-group"><label>Recommandations</label><textarea disabled rows="2"></textarea></div>
            </fieldset>
            <button class="btn-mock primary">Soumettre l'evaluation DGPPE</button>
          </template>

          <!-- GESTION COMPTES -->
          <template v-if="form.id === 'gestion-comptes'">
            <fieldset>
              <legend>Filtres et recherche</legend>
              <div class="field-row">
                <div class="field-group"><label>Statut</label><select disabled><option>Tous</option><option>Non verifie</option><option>Verifie</option><option>Suspendu</option></select></div>
                <div class="field-group"><label>Rechercher</label><input disabled placeholder="Nom, structure, email..." /></div>
              </div>
            </fieldset>
            <fieldset>
              <legend>Creation utilisateur interne</legend>
              <div class="field-group"><label>Nom d'utilisateur (email) *</label><input type="email" disabled placeholder="prenom.nom@dgppe.gouv.sn" /></div>
              <div class="field-group"><label>Nom complet *</label><input disabled placeholder="Prenom NOM" /></div>
              <div class="field-group"><label>Mot de passe *</label><input type="password" disabled /></div>
              <div class="field-group">
                <label>Role *</label>
                <select disabled><option>-- Choisir --</option><option>admin</option><option>evaluateur</option><option>secretariatsct</option><option>presidencesct</option><option>presidencecomite</option><option>membrecomite</option><option>invite</option></select>
              </div>
            </fieldset>
            <fieldset>
              <legend>Detail / Edition compte soumissionnaire</legend>
              <div class="field-group"><label>Nom complet</label><input disabled /></div>
              <div class="field-group"><label>Email</label><input type="email" disabled /></div>
              <div class="field-group"><label>Telephone</label><input disabled placeholder="+221 77 000 00 00" /></div>
              <div class="field-group"><label>Fonction</label><input disabled /></div>
              <div class="field-group"><label>Structure d'appartenance</label><select disabled><option>-- Memes champs cascading --</option></select></div>
              <label class="cb"><input type="checkbox" disabled /> Cet utilisateur est un Point Focal</label>
            </fieldset>
            <div class="btn-row">
              <button class="btn-mock success">Verifier</button>
              <button class="btn-mock warning">Suspendre</button>
              <button class="btn-mock danger">Supprimer</button>
            </div>
          </template>

          <!-- CONFIG EMAILS -->
          <template v-if="form.id === 'config-emails'">
            <fieldset>
              <legend>Parametres du service</legend>
              <label class="cb"><input type="checkbox" disabled checked /> Active</label>
              <label class="cb"><input type="checkbox" disabled /> Mode debug</label>
            </fieldset>
            <fieldset>
              <legend>Configuration SMTP</legend>
              <div class="field-group"><label>Serveur SMTP</label><input disabled placeholder="smtp.office365.com" /></div>
              <div class="field-group"><label>Port SMTP</label><input type="number" disabled placeholder="587" /></div>
              <div class="field-group"><label>Nom d'utilisateur SMTP</label><input disabled placeholder="votre.email@exemple.com" /></div>
              <div class="field-group"><label>Mot de passe SMTP</label><input type="password" disabled /></div>
              <div class="field-group"><label>Email expediteur</label><input type="email" disabled placeholder="noreply@exemple.com" /></div>
              <div class="field-group"><label>Nom d'affichage</label><input disabled placeholder="Maturation DGPPE" /></div>
              <div class="field-group"><label>URL de la Plateforme</label><input disabled placeholder="https://maturation-frontend.onrender.com" /></div>
            </fieldset>
            <fieldset>
              <legend>Templates d'emails</legend>
              <div class="field-group"><label>Sujet de l'email</label><input disabled placeholder="Notification - {{type}}" /></div>
              <div class="field-group"><label>Contenu HTML</label><textarea disabled rows="3"></textarea></div>
              <label class="cb"><input type="checkbox" disabled checked /> Actif</label>
            </fieldset>
            <fieldset>
              <legend>Test</legend>
              <div class="field-group"><label>Adresse email de test</label><input type="email" disabled placeholder="votre.email@exemple.com" /></div>
            </fieldset>
            <div class="btn-row">
              <button class="btn-mock primary">Enregistrer</button>
              <button class="btn-mock secondary">Tester la configuration</button>
            </div>
          </template>

          <!-- MINISTERES -->
          <template v-if="form.id === 'ministeres'">
            <fieldset>
              <legend>Liste des ministeres</legend>
              <div v-for="m in ['Ministere de l\'Economie, du Plan et de la Cooperation', 'Ministere de l\'Education nationale', 'Ministere de la Sante et de l\'Action sociale']" :key="m" class="ministry-row">
                <label class="cb"><input type="checkbox" disabled checked /> Actif</label>
                <input disabled :value="m" class="flex-input" />
                <button class="btn-mock small secondary">&#9650;</button>
                <button class="btn-mock small secondary">&#9660;</button>
              </div>
            </fieldset>
            <fieldset>
              <legend>Ajouter un ministere</legend>
              <div class="field-group"><label>Nom complet du ministere</label><input disabled placeholder="Ex: Ministere de l'Education nationale" /></div>
              <label class="cb"><input type="checkbox" disabled checked /> Actif</label>
            </fieldset>
            <div class="btn-row">
              <button class="btn-mock primary">Ajouter</button>
              <button class="btn-mock success">Enregistrer tout</button>
            </div>
          </template>

          <!-- FORMULAIRE EDITOR -->
          <template v-if="form.id === 'formulaire-editor'">
            <fieldset>
              <legend>Parametres generaux</legend>
              <div class="field-row">
                <div class="field-group"><label>Score Total Maximum</label><input type="number" disabled value="100" /></div>
                <div class="field-group"><label>Seuil Minimum (points)</label><input type="number" disabled value="60" /></div>
              </div>
            </fieldset>
            <fieldset>
              <legend>Criteres d'evaluation</legend>
              <table class="mock-table">
                <thead><tr><th>Critere</th><th>Score max</th><th>Description</th><th>Recommandations</th></tr></thead>
                <tbody>
                  <tr v-for="c in ['Pertinence', 'Alignement', 'Solidite technique', 'Viabilite financiere', 'Impact', 'Faisabilite']" :key="c">
                    <td><input disabled :value="c" /></td>
                    <td><input type="number" disabled value="15" style="width:60px" /></td>
                    <td><input type="checkbox" disabled checked /></td>
                    <td><input type="checkbox" disabled checked /></td>
                  </tr>
                </tbody>
              </table>
              <button class="btn-mock small secondary mt">+ Ajouter un critere</button>
            </fieldset>
            <div class="summary-box">Total configure: 90 / 100 points</div>
            <button class="btn-mock primary">Enregistrer la configuration</button>
          </template>

        </div>
      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';

export default {
  name: 'TestFormulaires',
  components: { PageWrapper },
  data() {
    return {
      activeCategory: null,
      openForms: {},
      categories: [
        { id: 'public', label: 'Public' },
        { id: 'soumissionnaire', label: 'Soumissionnaire' },
        { id: 'evaluateur', label: 'Evaluateur' },
        { id: 'admin', label: 'Administration' }
      ],
      forms: [
        { id: 'login', number: 1, title: 'Connexion', role: 'Public', category: 'public' },
        { id: 'register', number: 2, title: 'Inscription', role: 'Public', category: 'public' },
        { id: 'contact', number: 3, title: 'Contact', role: 'Public / Connecte', category: 'public' },
        { id: 'profil', number: 4, title: 'Mon Profil', role: 'Tous les roles', category: 'soumissionnaire' },
        { id: 'soumission', number: 5, title: 'Soumission de projet', role: 'Soumissionnaire', category: 'soumissionnaire' },
        { id: 'discussion', number: 6, title: 'Discussion projet', role: 'Soumissionnaire / Evaluateur', category: 'soumissionnaire' },
        { id: 'matrice', number: 7, title: 'Matrice de recevabilite', role: 'Evaluateur', category: 'evaluateur' },
        { id: 'fiche-eval', number: 8, title: 'Fiche d\'evaluation', role: 'Evaluateur', category: 'evaluateur' },
        { id: 'fiche-dgppe', number: 9, title: 'Fiche d\'evaluation DGPPE', role: 'Evaluateur', category: 'evaluateur' },
        { id: 'gestion-comptes', number: 10, title: 'Gestion des comptes', role: 'Admin / Secretariat SCT', category: 'admin' },
        { id: 'config-emails', number: 11, title: 'Configuration emails', role: 'Admin', category: 'admin' },
        { id: 'ministeres', number: 12, title: 'Gestion des ministeres', role: 'Admin / Secretariat SCT', category: 'admin' },
        { id: 'formulaire-editor', number: 13, title: 'Configuration formulaire d\'evaluation', role: 'Admin / Secretariat SCT', category: 'admin' }
      ],
      criteresEval: [
        { nom: '3.1 Alignement avec les priorites nationales', max: 5 },
        { nom: '3.2 Pertinence territoriale', max: 5 },
        { nom: '3.3 Innovation et valeur ajoutee', max: 5 },
        { nom: '3.4 Urgence et priorite', max: 5 },
        { nom: '3.5 Solidite technique', max: 10 },
        { nom: '3.6 Capacites de mise en oeuvre', max: 5 },
        { nom: '3.7 Gestion des risques', max: 5 },
        { nom: '3.8 Realisme du budget', max: 10 },
        { nom: '3.9 Rapport cout/benefice', max: 5 },
        { nom: '3.10 Durabilite financiere', max: 5 },
        { nom: '3.11 Impact social', max: 5 },
        { nom: '3.12 Impact economique', max: 5 },
        { nom: '3.13 Impact environnemental', max: 5 },
        { nom: '3.14 Effet multiplicateur', max: 5 },
        { nom: '3.15 Organisation du projet', max: 5 },
        { nom: '3.16 Planification', max: 5 },
        { nom: '3.17 Suivi-evaluation', max: 5 },
        { nom: '3.18 Transparence et redevabilite', max: 5 }
      ],
      criteresDGPPE: [
        { nom: 'Pertinence', max: 5 },
        { nom: 'Alignement', max: 10 },
        { nom: 'Pertinence des activites', max: 15 },
        { nom: 'Equite', max: 15 }
      ]
    };
  },
  computed: {
    filteredForms() {
      if (!this.activeCategory) return this.forms;
      return this.forms.filter(f => f.category === this.activeCategory);
    }
  },
  methods: {
    toggle(id) {
      this.openForms = { ...this.openForms, [id]: !this.openForms[id] };
    }
  }
};
</script>

<style scoped>
.test-formulaires {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.5rem;
}
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}
.page-title {
  font-size: 1.3rem;
  color: #003366;
  margin: 0;
}
.form-count {
  background: #003366;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
}
.intro {
  color: #6c757d;
  font-size: 0.85rem;
  margin-bottom: 1.25rem;
}

/* Nav pills */
.nav-pills {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.pill {
  padding: 0.4rem 1rem;
  border: 2px solid #ccc;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.2s;
}
.pill.public { border-color: #17a2b8; color: #17a2b8; }
.pill.soumissionnaire { border-color: #006633; color: #006633; }
.pill.evaluateur { border-color: #e67e00; color: #e67e00; }
.pill.admin { border-color: #003366; color: #003366; }
.pill.active.public { background: #17a2b8; color: white; }
.pill.active.soumissionnaire { background: #006633; color: white; }
.pill.active.evaluateur { background: #e67e00; color: white; }
.pill.active.admin { background: #003366; color: white; }

/* Form blocks */
.form-block {
  margin-bottom: 0.75rem;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}
.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  cursor: pointer;
  color: white;
  user-select: none;
}
.form-header.public { background: #17a2b8; }
.form-header.soumissionnaire { background: #006633; }
.form-header.evaluateur { background: #e67e00; }
.form-header.admin { background: #003366; }
.form-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.form-number {
  background: rgba(255,255,255,0.25);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
}
.form-header h3 {
  margin: 0;
  font-size: 0.95rem;
}
.form-role {
  font-size: 0.7rem;
  opacity: 0.8;
}
.chevron {
  transition: transform 0.2s;
  font-size: 0.7rem;
}
.chevron.open {
  transform: rotate(180deg);
}

/* Form replica content */
.form-replica {
  padding: 1.25rem;
  background: #fafbfc;
}
fieldset {
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 1rem;
  margin: 0 0 1rem;
}
legend {
  font-size: 0.85rem;
  font-weight: 700;
  color: #003366;
  padding: 0 0.5rem;
}
.field-group {
  margin-bottom: 0.75rem;
}
.field-group label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
}
.field-group input,
.field-group select,
.field-group textarea {
  width: 100%;
  padding: 0.4rem 0.6rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.8rem;
  background: #fff;
  box-sizing: border-box;
}
.field-group input:disabled,
.field-group select:disabled,
.field-group textarea:disabled {
  background: #f8f9fa;
  color: #6c757d;
}
.field-group input[type="file"] {
  padding: 0.3rem;
}
.hint {
  font-size: 0.7rem;
  color: #6c757d;
  font-style: italic;
}
.field-row {
  display: flex;
  gap: 1rem;
}
.field-row .field-group {
  flex: 1;
}

/* Conditional boxes */
.conditional-box {
  background: #e9ecef;
  border-radius: 4px;
  padding: 0.75rem;
  margin-bottom: 0.75rem;
}
.conditional-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #856404;
  display: block;
  margin-bottom: 0.5rem;
}

/* Checkboxes and radios */
.checkbox-group, .radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.25rem;
}
.cb, .rb {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: #495057;
  font-weight: normal !important;
  cursor: default;
}
.cb input, .rb input {
  width: auto !important;
}

/* Read-only */
.readonly-block {
  margin-bottom: 0.75rem;
}
.readonly-block label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #495057;
  margin-bottom: 0.25rem;
  display: block;
}
.readonly-value {
  background: #e9ecef;
  padding: 0.4rem 0.6rem;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #495057;
}
.readonly-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.4rem 1rem;
  font-size: 0.8rem;
  color: #495057;
}

/* Sliders */
.slider-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}
.slider-row label {
  flex: 1;
  font-size: 0.78rem;
  color: #495057;
  min-width: 0;
}
.slider-row input[type="range"] {
  width: 120px;
  flex-shrink: 0;
}
.slider-val {
  font-size: 0.75rem;
  font-weight: 700;
  color: #003366;
  min-width: 40px;
  text-align: right;
}
.total-row {
  text-align: right;
  font-size: 0.9rem;
  color: #003366;
  padding-top: 0.5rem;
  border-top: 2px solid #003366;
  margin-top: 0.5rem;
}

/* Tables */
.mock-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
  margin-bottom: 0.75rem;
}
.mock-table th {
  background: #003366;
  color: white;
  padding: 0.5rem;
  text-align: left;
  font-weight: 600;
}
.mock-table td {
  padding: 0.4rem 0.5rem;
  border-bottom: 1px solid #dee2e6;
}
.mock-table td input {
  width: auto;
}
.badge-missing {
  background: #f8d7da;
  color: #721c24;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  font-size: 0.7rem;
}

/* Summary */
.summary-box {
  background: #cce5ff;
  color: #004085;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  margin: 0.75rem 0;
}

/* Ministry rows */
.ministry-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.flex-input {
  flex: 1;
}

/* Buttons */
.btn-row {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  align-items: center;
  margin-top: 0.75rem;
}
.btn-mock {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: default;
  opacity: 0.85;
}
.btn-mock.small {
  padding: 0.3rem 0.75rem;
  font-size: 0.75rem;
}
.btn-mock.primary { background: #003366; color: white; }
.btn-mock.secondary { background: #6c757d; color: white; }
.btn-mock.success { background: #28a745; color: white; }
.btn-mock.warning { background: #ffc107; color: #1a1a1a; }
.btn-mock.danger { background: #dc3545; color: white; }
.mt { margin-top: 0.75rem; }

@media (max-width: 768px) {
  .field-row { flex-direction: column; gap: 0; }
  .slider-row { flex-wrap: wrap; }
  .readonly-grid { grid-template-columns: 1fr; }
  .nav-pills { gap: 0.35rem; }
}
</style>
