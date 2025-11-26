"""
Configuration pour l'intégration future d'IA générative (Claude API)
À activer quand nécessaire en définissant ENABLE_AI=True et ANTHROPIC_API_KEY
"""

import os

# Configuration IA
ENABLE_AI = os.environ.get('ENABLE_AI', 'false').lower() == 'true'
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
AI_MODEL = os.environ.get('AI_MODEL', 'claude-3-5-sonnet-20241022')  # Modèle recommandé
AI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', '4096'))
AI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', '0.7'))

# Vérifier si l'IA est disponible
def is_ai_available():
    """Vérifie si l'IA générative est configurée et disponible"""
    if not ENABLE_AI:
        return False
    if not ANTHROPIC_API_KEY:
        print("[AI] ENABLE_AI=true mais ANTHROPIC_API_KEY non définie")
        return False
    return True

def get_ai_status():
    """Retourne le statut de configuration de l'IA"""
    return {
        'enabled': ENABLE_AI,
        'configured': bool(ANTHROPIC_API_KEY),
        'available': is_ai_available(),
        'model': AI_MODEL if is_ai_available() else None
    }
