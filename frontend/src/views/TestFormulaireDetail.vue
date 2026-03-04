<template>
  <PageWrapper>
    <div class="form-detail">
      <div class="detail-header">
        <a href="/test-formulaires" class="back-link">&larr; Retour a la liste</a>
        <h2 :class="['detail-title', formData.category]">
          <span class="detail-number">{{ formData.number }}</span>
          {{ formData.title }}
        </h2>
        <span class="detail-role">Role requis : {{ formData.role }}</span>
      </div>

      <div class="form-replica">

        <!-- CONNEXION -->
        <template v-if="formId === 'login'">
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
        <template v-if="formId === 'register'">
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
        <template v-if="formId === 'contact'">
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
        <template v-if="formId === 'profil'">
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
        <template v-if="formId === 'soumission'">
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
        <template v-if="formId === 'discussion'">
          <div class="field-group"><label>Message</label><textarea disabled rows="3" placeholder="Ecrivez votre message ici..."></textarea></div>
          <div class="field-group"><label>Pieces jointes</label><input type="file" disabled multiple /><span class="hint">PDF, Word, Excel, Images</span></div>
          <div class="btn-row">
            <button class="btn-mock primary">Envoyer</button>
            <span class="hint">Ctrl+Entree pour envoyer</span>
          </div>
        </template>

        <!-- MATRICE RECEVABILITE -->
        <template v-if="formId === 'matrice'">
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

        <!-- FICHE D'EVALUATION (unique formulaire utilise sur la plateforme) -->
        <template v-if="formId === 'fiche-eval'">
          <div class="dgppe-official-header">
            <div class="dgppe-ministry">MINISTERE DE L'ECONOMIE, DU PLAN ET DE LA COOPERATION</div>
            <div class="dgppe-direction">DIRECTION GENERALE DE LA PLANIFICATION ET DES POLITIQUES ECONOMIQUES</div>
            <div class="dgppe-platform">PLATEFORME DE SUIVI DE LA MATURATION DES PROJETS</div>
          </div>

          <h2 class="fiche-main-title">FICHE D'EVALUATION <span class="numero-badge">DGPPE-25-007</span></h2>
          <div class="version-line">v.1.0 - Novembre 2025</div>

          <div class="section-bar">I - PRESENTATION DU PROJET</div>

          <div class="field-group"><label>INTITULE DU PROJET</label><textarea disabled rows="2" placeholder="Projet de developpement de la peche artisanale"></textarea></div>
          <div class="info-grid-2col">
            <div class="field-group"><label>SECTEUR DE PLANIFICATION:</label><input disabled value="agriculture-elevage-peche" /></div>
            <div class="field-group"><label>POLES TERRITORIAUX:</label><input disabled value="Sud (Ziguinchor, Sedhiou, Kolda)" /></div>
            <div class="field-group"><label>COUT DU PROJET (FCFA):</label><input disabled value="90 000 000 000" /></div>
            <div class="field-group"><label>ORGANISME DE TUTELLE:</label><input disabled value="Ministere des Peches et de l'Economie Maritime" /></div>
          </div>
          <div class="field-group"><label>DESCRIPTION DU PROJET:</label><textarea disabled rows="4" placeholder="Description du projet..."></textarea></div>

          <div class="section-bar">II - CLASSIFICATION DU PROJET</div>

          <div class="classification-2col">
            <div>
              <label class="section-label">ORIGINE DU PROJET</label>
              <div class="radio-group-vertical">
                <label class="rb"><input type="radio" disabled name="origine" /> Maturation</label>
                <label class="rb"><input type="radio" disabled name="origine" /> Offre spontanee</label>
                <label class="rb"><input type="radio" disabled name="origine" /> Autres</label>
              </div>
            </div>
            <div>
              <label class="section-label">DIMENSIONS TRANSVERSALES</label>
              <div class="dimensions-box">
                <div><strong>Changement climatique</strong>
                  <label class="cb"><input type="checkbox" disabled /> Adaptation</label>
                  <label class="cb"><input type="checkbox" disabled /> Attenuation</label>
                </div>
                <div><strong>Genre</strong>
                  <label class="cb"><input type="checkbox" disabled /> Prise en compte du genre</label>
                </div>
              </div>
            </div>
          </div>

          <table class="mock-table dgppe-table"><thead><tr><th>ARTICULATION</th><th>AXE(S)</th><th>OBJECTIF(S) STRATEGIQUE(S)</th><th>OBJECTIFS DE DEVELOPPEMENT DURABLE</th></tr></thead>
            <tbody><tr><td><textarea disabled rows="2"></textarea></td><td><textarea disabled rows="2"></textarea></td><td><textarea disabled rows="2"></textarea></td><td><textarea disabled rows="2"></textarea></td></tr></tbody></table>
          <table class="mock-table dgppe-table"><thead><tr><th>DUREE D'ANALYSE</th><th>REALISATION</th><th>EXPLOITATION</th></tr></thead>
            <tbody><tr><td><textarea disabled rows="2"></textarea></td><td><textarea disabled rows="2"></textarea></td><td><textarea disabled rows="2"></textarea></td></tr></tbody></table>
          <table class="mock-table dgppe-table"><thead><tr><th>LOCALISATION</th><th>PARTIES PRENANTES</th><th>AUTRES PROJETS/PROG. CONNEXES</th></tr></thead>
            <tbody><tr><td><textarea disabled rows="3"></textarea></td><td><textarea disabled rows="3"></textarea></td><td><textarea disabled rows="3"></textarea></td></tr></tbody></table>
          <table class="mock-table dgppe-table"><thead><tr><th>OBJECTIF DU PROJET</th><th>ACTIVITES PRINCIPALES</th><th>EXTRANTS / RESULTATS / IMPACTS ATTENDUS</th></tr></thead>
            <tbody><tr><td><textarea disabled rows="4"></textarea></td><td><textarea disabled rows="4"></textarea></td><td><textarea disabled rows="4"></textarea></td></tr></tbody></table>

          <div class="section-bar">III - RESULTATS DE L'EVALUATION</div>

          <table class="mock-table eval-criteria-table">
            <thead><tr><th>CRITERES</th><th>VALEUR ET/OU DESCRIPTION</th><th>SCORE</th><th>RECOMMANDATIONS</th></tr></thead>
            <tbody>
              <tr v-for="c in criteresEvaluation" :key="c.nom">
                <td class="col-critere"><strong>{{ c.nom }}</strong></td>
                <td><textarea disabled rows="2" :placeholder="'Analyser ' + c.nom.toLowerCase() + '...'"></textarea></td>
                <td class="col-score-cell"><input type="number" disabled value="0" style="width:40px" /> /{{ c.max }}</td>
                <td><textarea disabled rows="2" placeholder="Recommandations..."></textarea></td>
              </tr>
              <tr class="total-row-eval">
                <td><strong>SCORE TOTAL =</strong></td>
                <td></td>
                <td class="col-score-cell"><strong class="score-defavorable">0/100</strong></td>
                <td></td>
              </tr>
            </tbody>
          </table>

          <div class="section-bar">IV - CONCLUSION</div>

          <div class="field-group">
            <label><strong>PROPOSITION:</strong></label>
            <input disabled value="Defavorable" class="proposition-defavorable-input" />
            <span class="hint">Score &lt; 70 points = Defavorable (automatique)</span>
          </div>
          <div class="field-group"><label><strong>RECOMMANDATIONS:</strong></label><textarea disabled rows="4" placeholder="Saisir les recommandations finales..."></textarea></div>
          <div class="field-group"><label><strong>NOM DE L'EVALUATEUR:</strong></label><input disabled value="secretariatsct" style="background:#e9ecef" /></div>

          <div class="btn-row">
            <button class="btn-mock secondary">Sauvegarder brouillon</button>
            <button class="btn-mock success">Finaliser l'evaluation</button>
          </div>
        </template>

        <!-- Redirection fiche-dgppe vers fiche-eval (c'est le meme formulaire) -->
        <template v-if="formId === 'fiche-dgppe'">
          <div class="info-redirect">
            Ce formulaire est identique a la Fiche d'evaluation (formulaire n°8). Sur la plateforme, il n'y a qu'un seul formulaire d'evaluation.
            <br/><a href="/test-formulaires/fiche-eval" target="_blank">Voir la Fiche d'evaluation</a>
          </div>
        </template>

        <!-- GESTION COMPTES -->
        <template v-if="formId === 'gestion-comptes'">
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
        <template v-if="formId === 'config-emails'">
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
        <template v-if="formId === 'ministeres'">
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
        <template v-if="formId === 'formulaire-editor'">
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

        <!-- FORMULAIRE INCONNU -->
        <template v-if="!knownIds.includes(formId)">
          <p>Formulaire non trouve.</p>
        </template>

      </div>
    </div>
  </PageWrapper>
</template>

<script>
import PageWrapper from '../components/PageWrapper.vue';

const FORMS = {
  'login': { number: 1, title: 'Connexion', role: 'Public', category: 'public' },
  'register': { number: 2, title: 'Inscription', role: 'Public', category: 'public' },
  'contact': { number: 3, title: 'Contact', role: 'Public / Connecte', category: 'public' },
  'profil': { number: 4, title: 'Mon Profil', role: 'Tous les roles', category: 'soumissionnaire' },
  'soumission': { number: 5, title: 'Soumission de projet', role: 'Soumissionnaire', category: 'soumissionnaire' },
  'discussion': { number: 6, title: 'Discussion projet', role: 'Soumissionnaire / Evaluateur', category: 'soumissionnaire' },
  'matrice': { number: 7, title: 'Matrice de recevabilite', role: 'Evaluateur', category: 'evaluateur' },
  'fiche-eval': { number: 8, title: "Fiche d'evaluation", role: 'Evaluateur', category: 'evaluateur' },
  'gestion-comptes': { number: 9, title: 'Gestion des comptes', role: 'Admin / Secretariat SCT', category: 'admin' },
  'config-emails': { number: 10, title: 'Configuration emails', role: 'Admin', category: 'admin' },
  'ministeres': { number: 11, title: 'Gestion des ministeres', role: 'Admin / Secretariat SCT', category: 'admin' },
  'formulaire-editor': { number: 12, title: "Configuration formulaire d'evaluation", role: 'Admin / Secretariat SCT', category: 'admin' }
};

export default {
  name: 'TestFormulaireDetail',
  components: { PageWrapper },
  data() {
    return {
      criteresEvaluation: [
        { nom: 'PERTINENCE', max: 5 },
        { nom: 'ALIGNEMENT A LA DOCTRINE DE TRANSFORMATION SYSTEMIQUE', max: 10 },
        { nom: 'PERTINENCE DES ACTIVITES ET BIEN FONDE DES COUTS / PART DE FONCTIONNEMENT', max: 15 },
        { nom: 'EQUITE (SOCIALE-TERRITORIALE-GENRE)', max: 15 },
        { nom: 'VIABILITE / RENTABILITE FINANCIERE', max: 5 },
        { nom: 'RENTABILITE SOCIO-ECONOMIQUE (ACA/MPR)', max: 5 },
        { nom: 'BENEFICES STRATEGIQUES (SECURITE-RESILIENCE-INNOVATION-COMPETITIVITE-CONTENU LOCAL, ETC.)', max: 15 },
        { nom: 'PERENNITE ET DURABILITE DES EFFETS ET IMPACTS DU PROJET', max: 5 },
        { nom: 'AVANTAGES ET COUTS INTANGIBLES', max: 10 },
        { nom: 'FAISABILITE DU PROJET / RISQUES POTENTIELS', max: 5 },
        { nom: 'POTENTIALITE OU OPPORTUNITE DU PROJET A ETRE REALISE EN PPP', max: 5 },
        { nom: 'IMPACTS ENVIRONNEMENTAUX', max: 5 }
      ]
    };
  },
  computed: {
    formId() {
      return this.$route.params.id;
    },
    formData() {
      return FORMS[this.formId] || { number: '?', title: 'Formulaire inconnu', role: '-', category: 'public' };
    },
    knownIds() {
      return Object.keys(FORMS);
    }
  }
};
</script>

<style scoped>
.form-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem;
}
.detail-header {
  margin-bottom: 1.5rem;
}
.back-link {
  font-size: 0.85rem;
  color: #003366;
  text-decoration: none;
}
.back-link:hover { text-decoration: underline; }
.detail-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 1.3rem;
  color: white;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  margin: 0.5rem 0 0.25rem;
}
.detail-title.public { background: #17a2b8; }
.detail-title.soumissionnaire { background: #006633; }
.detail-title.evaluateur { background: #e67e00; }
.detail-title.admin { background: #003366; }
.detail-number {
  background: rgba(255,255,255,0.25);
  width: 32px; height: 32px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.9rem; flex-shrink: 0;
}
.detail-role {
  font-size: 0.8rem;
  color: #6c757d;
}

/* Form replica */
.form-replica {
  background: #fafbfc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
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
.field-group { margin-bottom: 0.75rem; }
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
.field-group input[type="file"] { padding: 0.3rem; }
.hint { font-size: 0.7rem; color: #6c757d; font-style: italic; }
.field-row { display: flex; gap: 1rem; }
.field-row .field-group { flex: 1; }
.conditional-box {
  background: #e9ecef; border-radius: 4px; padding: 0.75rem; margin-bottom: 0.75rem;
}
.conditional-label {
  font-size: 0.75rem; font-weight: 700; color: #856404; display: block; margin-bottom: 0.5rem;
}
.checkbox-group, .radio-group { display: flex; flex-wrap: wrap; gap: 0.5rem 1.25rem; }
.cb, .rb {
  display: flex; align-items: center; gap: 0.35rem;
  font-size: 0.8rem; color: #495057; font-weight: normal !important; cursor: default;
}
.cb input, .rb input { width: auto !important; }
.readonly-block { margin-bottom: 0.75rem; }
.readonly-block label { font-size: 0.8rem; font-weight: 600; color: #495057; margin-bottom: 0.25rem; display: block; }
.readonly-value { background: #e9ecef; padding: 0.4rem 0.6rem; border-radius: 4px; font-size: 0.8rem; color: #495057; }
.readonly-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem 1rem; font-size: 0.8rem; color: #495057; }
.slider-row { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.5rem; }
.slider-row label { flex: 1; font-size: 0.78rem; color: #495057; min-width: 0; }
.slider-row input[type="range"] { width: 120px; flex-shrink: 0; }
.slider-val { font-size: 0.75rem; font-weight: 700; color: #003366; min-width: 40px; text-align: right; }
.total-row { text-align: right; font-size: 0.9rem; color: #003366; padding-top: 0.5rem; border-top: 2px solid #003366; margin-top: 0.5rem; }
.mock-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-bottom: 0.75rem; }
.mock-table th { background: #003366; color: white; padding: 0.5rem; text-align: left; font-weight: 600; }
.mock-table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid #dee2e6; }
.mock-table td input { width: auto; }
.badge-missing { background: #f8d7da; color: #721c24; padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.7rem; }
.summary-box { background: #cce5ff; color: #004085; padding: 0.5rem 1rem; border-radius: 4px; font-size: 0.8rem; font-weight: 600; margin: 0.75rem 0; }
.ministry-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }
.flex-input { flex: 1; }
.btn-row { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; margin-top: 0.75rem; }
.btn-mock {
  padding: 0.5rem 1.25rem; border: none; border-radius: 6px;
  font-size: 0.8rem; font-weight: 600; cursor: default; opacity: 0.85;
}
.btn-mock.small { padding: 0.3rem 0.75rem; font-size: 0.75rem; }
.btn-mock.primary { background: #003366; color: white; }
.btn-mock.secondary { background: #6c757d; color: white; }
.btn-mock.success { background: #28a745; color: white; }
.btn-mock.warning { background: #ffc107; color: #1a1a1a; }
.btn-mock.danger { background: #dc3545; color: white; }
/* Fiche evaluation specific */
.fiche-header-bar {
  background: #1e40af; color: white; text-align: center; font-weight: 700;
  padding: 0.75rem; border-radius: 6px; margin-bottom: 1rem; font-size: 0.95rem;
}
.critere-section-box {
  background: #f8fafc; border-left: 4px solid #3b82f6; border-radius: 6px;
  padding: 1rem; margin-bottom: 1rem;
}
.critere-cat { color: #1e40af; font-size: 0.85rem; margin: 0 0 0.75rem; }
.critere-item-box {
  background: white; border: 1px solid #e5e7eb; border-radius: 6px;
  padding: 0.75rem; margin-bottom: 0.75rem;
}
.critere-item-box label { display: block; font-weight: 600; font-size: 0.8rem; color: #374151; margin-bottom: 0.3rem; }
.critere-desc { color: #6b7280; font-size: 0.72rem; font-style: italic; margin: 0.25rem 0 0; }
.sous-total-box {
  background: #dbeafe; text-align: center; padding: 0.5rem;
  border-radius: 4px; font-weight: 600; font-size: 0.8rem; color: #1e40af;
}
.score-total-bar { text-align: center; margin-bottom: 0.75rem; }
.score-bar { width: 100%; height: 16px; background: #e5e7eb; border-radius: 8px; overflow: hidden; margin-top: 0.4rem; }
.score-fill { height: 100%; background: linear-gradient(90deg, #ef4444, #f59e0b, #059669); }
.radio-group-vertical { display: flex; flex-direction: column; gap: 0.4rem; }
.avis-info-box {
  background: #e8f5e9; border-left: 4px solid #2d7a2d; padding: 0.5rem 0.75rem;
  font-size: 0.75rem; color: #333; margin-bottom: 0.5rem; border-radius: 0 4px 4px 0;
}

/* DGPPE fiche specific */
.dgppe-header-box {
  border: 2px solid #2d7a2d; border-radius: 8px; text-align: center;
  margin-bottom: 1rem; overflow: hidden;
}
.dgppe-header-text {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef); padding: 0.75rem;
  font-size: 0.72rem; color: #2d7a2d; border-bottom: 1px solid #2d7a2d;
}
.dgppe-doc-title { font-size: 1.1rem; font-weight: 700; color: #2d7a2d; padding: 0.75rem 0 0.25rem; }
.dgppe-ref { font-size: 0.7rem; color: #666; padding-bottom: 0.5rem; }
.section-bar {
  background: #2d7a2d; color: white; padding: 0.6rem 1rem;
  border-radius: 5px; font-weight: 700; font-size: 0.85rem; margin: 1rem 0 0.75rem;
}
.dimensions-box {
  background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 6px;
  padding: 0.75rem; display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.8rem;
}
.dgppe-table th { background: #2E6B6B !important; font-size: 0.72rem; text-transform: uppercase; }
.dgppe-table td { padding: 0 !important; }
.dgppe-table textarea, .dgppe-table input {
  width: 100%; border: none; padding: 0.5rem; font-size: 0.8rem; background: transparent; box-sizing: border-box;
}
.criterion-box { border: 1px solid #ddd; border-radius: 8px; margin-bottom: 0.75rem; overflow: hidden; }
.criterion-header-bar {
  background: #f8f9fa; padding: 0.6rem 0.75rem; border-bottom: 1px solid #ddd;
  display: flex; justify-content: space-between; align-items: center;
  font-size: 0.78rem; color: #2d7a2d;
}
.criterion-score-badge {
  background: #2d7a2d; color: white; padding: 0.2rem 0.6rem;
  border-radius: 12px; font-weight: 700; font-size: 0.75rem;
}
.criterion-content-box { padding: 0.75rem; }
.total-score-bar {
  text-align: center; padding: 1rem; background: linear-gradient(135deg, #2d7a2d, #4a9a4a);
  color: white; border-radius: 8px; font-weight: 700; font-size: 0.9rem; margin: 0.75rem 0;
}

.mt { margin-top: 0.75rem; }
@media (max-width: 768px) {
  .field-row { flex-direction: column; gap: 0; }
  .slider-row { flex-wrap: wrap; }
  .readonly-grid { grid-template-columns: 1fr; }
}
</style>
