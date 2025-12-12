/**
 * Configuration centralisée des pôles territoriaux du Sénégal
 * Ces pôles correspondent aux 8 pôles territoriaux officiels
 */

export const POLES_TERRITORIAUX = [
  'Dakar',
  'Thiès',
  'Centre (Kaolack, Fatick, Kaffrine)',
  'Diourbel-Louga',
  'Sud (Ziguinchor, Sédhiou, Kolda)',
  'Sud-Est (Tambacounda, Kédougou)',
  'Nord (Saint-Louis)',
  'Nord-Est (Matam)'
];

/**
 * Mapping des variations de noms vers les pôles officiels
 * Utilisé pour normaliser les données de la base de données
 */
export const POLE_MAPPING = {
  // Centre regroupe Fatick, Kaolack, Kaffrine
  'Centre (Fatick)': 'Centre (Kaolack, Fatick, Kaffrine)',
  'Centre (Kaolack)': 'Centre (Kaolack, Fatick, Kaffrine)',
  'Centre (Kaffrine)': 'Centre (Kaolack, Fatick, Kaffrine)',
  'Fatick': 'Centre (Kaolack, Fatick, Kaffrine)',
  'Kaolack': 'Centre (Kaolack, Fatick, Kaffrine)',
  'Kaffrine': 'Centre (Kaolack, Fatick, Kaffrine)',
  'Centre': 'Centre (Kaolack, Fatick, Kaffrine)',

  // Diourbel-Louga
  'Diourbel': 'Diourbel-Louga',
  'Louga': 'Diourbel-Louga',

  // Sud regroupe Ziguinchor, Sédhiou, Kolda
  'Sud (Ziguinchor)': 'Sud (Ziguinchor, Sédhiou, Kolda)',
  'Sud (Sédhiou)': 'Sud (Ziguinchor, Sédhiou, Kolda)',
  'Sud (Kolda)': 'Sud (Ziguinchor, Sédhiou, Kolda)',
  'Ziguinchor': 'Sud (Ziguinchor, Sédhiou, Kolda)',
  'Sédhiou': 'Sud (Ziguinchor, Sédhiou, Kolda)',
  'Kolda': 'Sud (Ziguinchor, Sédhiou, Kolda)',
  'Sud': 'Sud (Ziguinchor, Sédhiou, Kolda)',

  // Sud-Est regroupe Tambacounda, Kédougou
  'Sud-Est (Tambacounda)': 'Sud-Est (Tambacounda, Kédougou)',
  'Sud-Est (Kédougou)': 'Sud-Est (Tambacounda, Kédougou)',
  'Tambacounda': 'Sud-Est (Tambacounda, Kédougou)',
  'Kédougou': 'Sud-Est (Tambacounda, Kédougou)',
  'Sud-Est': 'Sud-Est (Tambacounda, Kédougou)',

  // Nord
  'Nord (Saint-Louis)': 'Nord (Saint-Louis)',
  'Saint-Louis': 'Nord (Saint-Louis)',
  'Nord': 'Nord (Saint-Louis)',

  // Nord-Est
  'Nord-Est (Matam)': 'Nord-Est (Matam)',
  'Matam': 'Nord-Est (Matam)',
  'Nord-Est': 'Nord-Est (Matam)',

  // Dakar et Thiès restent inchangés
  'Dakar': 'Dakar',
  'Thiès': 'Thiès'
};

/**
 * Normalise un nom de pôle vers le format officiel
 * @param {string} pole - Le nom du pôle à normaliser
 * @returns {string} - Le nom normalisé du pôle
 */
export function normalizePole(pole) {
  if (!pole) return null;

  // Trim et normalisation
  const trimmed = pole.trim();

  // Retourner le mapping ou la valeur d'origine si déjà normalisée
  return POLE_MAPPING[trimmed] || trimmed;
}

/**
 * Extrait tous les pôles uniques d'une liste de projets
 * et les normalise vers les pôles officiels
 * @param {Array} projects - Liste des projets
 * @returns {Array} - Liste triée des pôles uniques normalisés
 */
export function extractUniquePoles(projects) {
  const poles = new Set();

  projects.forEach(project => {
    if (project.poles) {
      // Un projet peut avoir plusieurs pôles séparés par des virgules
      const projectPoles = project.poles.split(',').map(p => p.trim());
      projectPoles.forEach(pole => {
        const normalized = normalizePole(pole);
        if (normalized) {
          poles.add(normalized);
        }
      });
    }
  });

  return [...poles].sort();
}
