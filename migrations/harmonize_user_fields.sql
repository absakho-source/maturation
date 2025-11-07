-- Migration : Harmonisation des champs utilisateur
-- Date : 2025-11-04
-- Description : Remplace les champs séparés prenom/nom par un champ unique nom_complet
--                Supprime le champ structure en doublon avec nom_structure

-- Créer une nouvelle table avec la structure corrigée
CREATE TABLE users_new (
  id INTEGER PRIMARY KEY,
  username VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(100) NOT NULL,
  role VARCHAR(50) NOT NULL,
  display_name VARCHAR(100),
  nom_complet VARCHAR(200),
  fonction VARCHAR(255),
  type_structure VARCHAR(50),
  nom_structure VARCHAR(255),
  justificatif_path VARCHAR(500),
  statut_compte VARCHAR(50) DEFAULT 'non_verifie',
  date_verification TIMESTAMP,
  verifie_par VARCHAR(100),
  telephone VARCHAR(20),
  date_creation TIMESTAMP
);

-- Copier les données existantes en fusionnant prenom et nom en nom_complet
INSERT INTO users_new (
  id, username, password, role, display_name, nom_complet,
  fonction, type_structure, nom_structure, justificatif_path,
  statut_compte, date_verification, verifie_par, telephone, date_creation
)
SELECT
  id, username, password, role, display_name,
  CASE
    WHEN prenom IS NOT NULL AND nom IS NOT NULL THEN prenom || ' ' || nom
    WHEN nom IS NOT NULL THEN nom
    WHEN prenom IS NOT NULL THEN prenom
    ELSE NULL
  END as nom_complet,
  fonction, type_structure, nom_structure, justificatif_path,
  statut_compte, date_verification, verifie_par, telephone, date_creation
FROM users;

-- Supprimer l'ancienne table et renommer la nouvelle
DROP TABLE users;
ALTER TABLE users_new RENAME TO users;
