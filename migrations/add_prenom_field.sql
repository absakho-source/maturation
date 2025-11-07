-- Migration : Ajout du champ prenom pour séparer prénom et nom
-- Date : 2025-11-03

-- Ajouter le champ prenom à la table users
ALTER TABLE users ADD COLUMN prenom VARCHAR(100);

-- Note: Le champ nom existe déjà dans le modèle
