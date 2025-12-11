#!/bin/bash
# Script de build avec nettoyage du cache Vite
# Force un rebuild complet pour Render
# Build version: 1.0.39 - 2025-12-11 - Move Fatick left x: -0.15, y: -0.30

echo "🧹 Nettoyage du cache Vite et du dossier dist..."
rm -rf dist
rm -rf node_modules/.vite
echo "✅ Cache nettoyé"

echo "📦 Installation des dépendances..."
npm install

echo "🏗️  Build du projet..."
npm run build

echo "✅ Build terminé avec succès!"
