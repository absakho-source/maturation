-- Migration : Ajout des champs pour le système de validation des comptes
-- Date : 2025-11-03

-- Note: display_name existe déjà, on l'ignore

-- Ajouter les nouveaux champs à la table users (SQLite ne supporte pas IF NOT EXISTS dans ALTER TABLE)
ALTER TABLE users ADD COLUMN telephone VARCHAR(20);
ALTER TABLE users ADD COLUMN fonction VARCHAR(255);
ALTER TABLE users ADD COLUMN type_structure VARCHAR(50);
ALTER TABLE users ADD COLUMN nom_structure VARCHAR(255);
ALTER TABLE users ADD COLUMN justificatif_path VARCHAR(500);
ALTER TABLE users ADD COLUMN statut_compte VARCHAR(50) DEFAULT 'non_verifie';
ALTER TABLE users ADD COLUMN date_verification TIMESTAMP;
ALTER TABLE users ADD COLUMN verifie_par VARCHAR(100);
ALTER TABLE users ADD COLUMN date_creation TIMESTAMP;

-- Créer un index pour améliorer les performances des requêtes
CREATE INDEX IF NOT EXISTS idx_users_statut_compte ON users(statut_compte);
CREATE INDEX IF NOT EXISTS idx_users_type_structure ON users(type_structure);
