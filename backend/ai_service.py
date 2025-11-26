"""
Service d'IA générative pour rapports élaborés
Utilise Claude API d'Anthropic pour générer des analyses avancées

INSTALLATION (quand vous voudrez l'activer):
    pip install anthropic

CONFIGURATION:
    export ENABLE_AI=true
    export ANTHROPIC_API_KEY=sk-ant-xxxxx
"""

from ai_config import is_ai_available, AI_MODEL, AI_MAX_TOKENS, AI_TEMPERATURE
import json


def generer_rapport_avec_ia(donnees_statistiques):
    """
    Génère un rapport élaboré avec analyse IA

    Args:
        donnees_statistiques: dict contenant les stats agrégées

    Returns:
        dict avec les sections du rapport générées par IA
    """
    if not is_ai_available():
        return None

    try:
        import anthropic

        client = anthropic.Anthropic()

        # Construire le prompt avec les données
        prompt = _construire_prompt_rapport(donnees_statistiques)

        # Appel à Claude
        message = client.messages.create(
            model=AI_MODEL,
            max_tokens=AI_MAX_TOKENS,
            temperature=AI_TEMPERATURE,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parser la réponse
        contenu = message.content[0].text
        rapport = _parser_reponse_ia(contenu)

        print(f"[AI] Rapport généré avec succès via {AI_MODEL}")
        return rapport

    except ImportError:
        print("[AI] Module 'anthropic' non installé. Installez avec: pip install anthropic")
        return None
    except Exception as e:
        print(f"[AI] Erreur lors de la génération: {e}")
        import traceback
        traceback.print_exc()
        return None


def _construire_prompt_rapport(stats):
    """Construit le prompt optimisé pour Claude"""

    prompt = f"""Tu es un expert en analyse de politiques publiques au Sénégal, spécialisé dans l'évaluation de projets de développement.

Analyse les données suivantes de la plateforme PLASMAP (Plateforme de Soumission et Maturation des Projets) et génère un rapport élaboré destiné aux décideurs de haut niveau (Présidence SCT, Comité d'orientation).

## DONNÉES STATISTIQUES

**Total de projets:** {stats.get('total_projets', 0)}
**Coût total demandé:** {stats.get('cout_total', 0):,.0f} FCFA
**Coût moyen par projet:** {stats.get('cout_moyen', 0):,.0f} FCFA

**Répartition par statut:**
{json.dumps(stats.get('statuts', {}), indent=2, ensure_ascii=False)}

**Répartition par secteur:**
{json.dumps(stats.get('secteurs', {}), indent=2, ensure_ascii=False)}

**Répartition par pôle territorial:**
{json.dumps(stats.get('poles', {}), indent=2, ensure_ascii=False)}

**Coûts par secteur (FCFA):**
{json.dumps(stats.get('cout_par_secteur', {}), indent=2, ensure_ascii=False)}

**Coûts par pôle (FCFA):**
{json.dumps(stats.get('cout_par_pole', {}), indent=2, ensure_ascii=False)}

## INSTRUCTIONS

Génère un rapport structuré en français avec les sections suivantes:

### 1. RÉSUMÉ EXÉCUTIF (2-3 paragraphes)
- Vue d'ensemble synthétique pour décideurs pressés
- Chiffres clés et messages principaux
- Ton professionnel adapté au contexte sénégalais

### 2. ANALYSE DES TENDANCES (5-7 paragraphes)
- Identifier les secteurs prioritaires et leur pertinence
- Analyser la répartition territoriale (équilibre/déséquilibre)
- Évaluer les niveaux d'investissement par secteur
- Identifier les corrélations intéressantes

### 3. INSIGHTS STRATÉGIQUES (bullet points)
- 5-7 observations clés non-évidentes
- Chaque insight doit être actionnable
- Focus sur les déséquilibres, opportunités, risques

### 4. RECOMMANDATIONS (bullet points numérotés)
- 5-7 recommandations concrètes et priorisées
- Alignées sur la politique de territorialisation
- Réalistes et basées sur les données

### 5. INDICATEURS D'ALERTE (si applicable)
- Signaler les pôles sous-représentés
- Identifier les secteurs sur-concentrés
- Détecter les anomalies dans les coûts

Format de réponse: JSON structuré avec les clés: resume_executif, analyse_tendances, insights, recommandations, alertes

Sois précis, factuel et nuancé. Utilise les termes appropriés au contexte sénégalais.
"""

    return prompt


def _parser_reponse_ia(texte):
    """Parse la réponse de Claude"""
    try:
        # Si Claude retourne du JSON pur
        if texte.strip().startswith('{'):
            return json.loads(texte)

        # Sinon, extraire les sections manuellement
        rapport = {
            'resume_executif': '',
            'analyse_tendances': '',
            'insights': [],
            'recommandations': [],
            'alertes': []
        }

        # Parser les sections (simplifié - à améliorer selon format réel)
        sections = texte.split('###')
        for section in sections:
            if 'RÉSUMÉ EXÉCUTIF' in section:
                rapport['resume_executif'] = section.split('\n', 1)[1].strip()
            elif 'ANALYSE DES TENDANCES' in section:
                rapport['analyse_tendances'] = section.split('\n', 1)[1].strip()
            # ... autres sections

        return rapport

    except Exception as e:
        print(f"[AI] Erreur parsing: {e}")
        return {'texte_brut': texte}


def test_connexion_ia():
    """
    Teste la connexion à l'API Claude
    À utiliser pour vérifier la configuration
    """
    if not is_ai_available():
        return {
            'success': False,
            'error': 'IA non configurée (ENABLE_AI=false ou API key manquante)'
        }

    try:
        import anthropic
        client = anthropic.Anthropic()

        message = client.messages.create(
            model=AI_MODEL,
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": "Réponds simplement: OK"
            }]
        )

        return {
            'success': True,
            'model': AI_MODEL,
            'response': message.content[0].text
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
