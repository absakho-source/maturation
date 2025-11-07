#!/usr/bin/env python3
"""
Serveur de test minimal pour la fiche d'évaluation
"""
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/projects/<int:project_id>/presentation', methods=['GET'])
def test_presentation(project_id):
    """Route de test pour la présentation"""
    return jsonify({
        'id': project_id,
        'titre': f'Projet test {project_id}',
        'secteur': 'Secteur test',
        'description': 'Description test',
        'cout_estimatif': 1000000000,
        'message': 'Route fonctionne!'
    })

@app.route('/api/users/profile', methods=['GET'])
def test_profile():
    """Route de test pour le profil utilisateur"""
    return jsonify({
        'nom': 'Évaluateur Test',
        'email': 'test@dgppe.sn',
        'role': 'evaluateur'
    })

if __name__ == '__main__':
    print("🚀 Serveur de test démarré sur http://127.0.0.1:5002")
    app.run(debug=False, host='127.0.0.1', port=5002)