#!/bin/bash
# Script de build avec nettoyage du cache Vite
# Force un rebuild complet pour Render
# Build version: 1.0.23 - 2025-12-10 18:00 - Zero loading time

echo "🧹 Nettoyage du cache Vite et du dossier dist..."
rm -rf dist
rm -rf node_modules/.vite
echo "✅ Cache nettoyé"

echo "📦 Installation des dépendances..."
npm install

echo "🏗️  Build du projet..."
npm run build

echo "✅ Build terminé avec succès!"
