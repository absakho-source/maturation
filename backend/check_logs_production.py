#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour vérifier les logs de connexion en production
"""

import sys
from app import app, db
from models import ConnexionLog
from datetime import datetime

def check_logs():
    with app.app_context():
        print("=== DIAGNOSTIC DES LOGS DE CONNEXION ===\n")

        # Compter les logs
        total_logs = ConnexionLog.query.count()
        print(f"Nombre total de logs: {total_logs}")

        if total_logs == 0:
            print("\n⚠️ Aucun log de connexion trouvé dans la base de données.")
            print("Solution: Connectez-vous à l'application pour créer un nouveau log.")
            return

        # Afficher les 5 derniers logs
        print("\n=== Les 5 derniers logs ===")
        recent_logs = ConnexionLog.query.order_by(ConnexionLog.date_connexion.desc()).limit(5).all()

        for log in recent_logs:
            print(f"\nLog ID: {log.id}")
            print(f"  Username: {log.username}")
            print(f"  Display Name: {log.display_name}")
            print(f"  Role: {log.role}")
            print(f"  Date Connexion: {log.date_connexion} (type: {type(log.date_connexion).__name__})")
            print(f"  Adresse IP: {log.adresse_ip}")
            print(f"  User Agent: {log.user_agent[:50] if log.user_agent else 'N/A'}...")
            print(f"  Statut: {log.statut}")

            # Tester la conversion en dict
            try:
                log_dict = log.to_dict()
                print(f"  to_dict() date_connexion: {log_dict['date_connexion']}")
                print(f"  to_dict() adresse_ip: {log_dict['adresse_ip']}")
            except Exception as e:
                print(f"  ⚠️ Erreur lors de to_dict(): {e}")

        print("\n=== FIN DU DIAGNOSTIC ===")

if __name__ == "__main__":
    check_logs()
