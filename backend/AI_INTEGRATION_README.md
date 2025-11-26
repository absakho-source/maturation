# 🤖 Intégration IA pour Rapports Élaborés

## État actuel

L'infrastructure est **préparée** mais **l'IA n'est pas activée**. Le système utilise actuellement l'analyse statistique classique.

## Architecture

```
📦 Backend
├── ai_config.py           # Configuration IA (variables d'environnement)
├── ai_service.py          # Service d'appel à Claude API
├── ai_rapport_generator.py # Générateur hybride (IA ou classique)
└── AI_INTEGRATION_README.md # Ce fichier
```

### Fonctionnement

Le système est **hybride** et choisit automatiquement:

- ✅ **Si `ENABLE_AI=true` ET API key configurée**: Utilise Claude API
- ✅ **Sinon**: Utilise l'analyse statistique classique (actuel)

Aucun impact sur le fonctionnement actuel - tout continue de marcher normalement.

---

## 🚀 Comment activer l'IA (quand vous voudrez)

### Étape 1: Obtenir une clé API Claude

1. Créer un compte sur [https://console.anthropic.com](https://console.anthropic.com)
2. Aller dans "API Keys"
3. Créer une nouvelle clé (commence par `sk-ant-`)
4. **Important**: Ajouter du crédit sur le compte (carte bancaire)

**Coût estimé**: ~0,50-2$ par rapport généré (selon longueur)

### Étape 2: Installer la bibliothèque Python

```bash
cd backend
source venv/bin/activate  # Si vous utilisez un venv
pip install anthropic
```

### Étape 3: Configurer les variables d'environnement

#### En local (développement):

```bash
export ENABLE_AI=true
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

Ou créer un fichier `.env` (ne pas commit!):
```env
ENABLE_AI=true
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
AI_MODEL=claude-3-5-sonnet-20241022
AI_MAX_TOKENS=4096
AI_TEMPERATURE=0.7
```

#### Sur Render (production):

Dans le dashboard Render:
1. Aller dans votre service backend
2. Environment → Environment Variables
3. Ajouter:
   - `ENABLE_AI` = `true`
   - `ANTHROPIC_API_KEY` = `sk-ant-xxxxx`
4. Redémarrer le service

### Étape 4: Tester

```bash
cd backend
python3 -c "
from ai_service import test_connexion_ia
resultat = test_connexion_ia()
print(resultat)
"
```

Vous devriez voir:
```
{
  'success': True,
  'model': 'claude-3-5-sonnet-20241022',
  'response': 'OK'
}
```

### Étape 5: Générer un rapport test

Allez dans l'interface, cliquez sur **"Rapport Élaboré"** dans PresidenceSCT ou PresidenceComite.

Le rapport sera maintenant généré par Claude! 🎉

Dans les logs backend, vous verrez:
```
[RAPPORT] 🤖 Génération avec IA (Claude API)...
[AI] Rapport généré avec succès via claude-3-5-sonnet-20241022
[RAPPORT] ✅ Rapport IA généré avec succès
```

---

## 📊 Comparaison IA vs Classique

| Fonctionnalité | Version Classique (actuelle) | Version IA (future) |
|----------------|------------------------------|---------------------|
| Résumé exécutif | Template fixe avec stats | Rédaction naturelle contextualisée |
| Analyse tendances | Calculs prédéfinis | Détection patterns complexes |
| Insights | 4-5 règles if/else | 5-7 observations nuancées |
| Recommandations | ❌ Pas disponible | ✅ 5-7 recommandations stratégiques |
| Alertes | ❌ Pas disponible | ✅ Détection anomalies automatique |
| Coût | 0€ | ~1-2$ par rapport |
| Vitesse | <1s | 3-8s |
| Personnalisation | Faible | Très élevée |

---

## 🔧 Configuration avancée

### Variables d'environnement disponibles

```bash
# Activer/désactiver l'IA
ENABLE_AI=true|false

# Clé API Anthropic (obligatoire si ENABLE_AI=true)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Modèle à utiliser (optionnel)
AI_MODEL=claude-3-5-sonnet-20241022  # Recommandé (équilibre coût/qualité)
# AI_MODEL=claude-3-opus-20240229     # Meilleur qualité mais plus cher
# AI_MODEL=claude-3-haiku-20240307    # Moins cher mais qualité inférieure

# Longueur max de la réponse (optionnel)
AI_MAX_TOKENS=4096  # Défaut (suffisant pour rapport complet)

# Température (créativité) (optionnel)
AI_TEMPERATURE=0.7  # Défaut (0.0 = déterministe, 1.0 = créatif)
```

### Modifier le prompt

Si vous voulez personnaliser les rapports générés par l'IA, éditez:
- **Fichier**: `backend/ai_service.py`
- **Fonction**: `_construire_prompt_rapport()`

Vous pouvez modifier:
- Le ton (formel, informel, technique...)
- Les sections demandées
- Le format de sortie (JSON, Markdown...)
- Les exemples et guidelines

---

## 🧪 Mode test / debug

Pour tester l'IA sans impacter la production, vous pouvez créer une route de test:

```python
# Dans app.py
@app.route("/api/test-ia", methods=["GET"])
def test_ia():
    from ai_config import get_ai_status
    from ai_service import test_connexion_ia

    return jsonify({
        'config': get_ai_status(),
        'test_connexion': test_connexion_ia()
    })
```

Puis appeler: `GET /api/test-ia`

---

## ❓ FAQ

### L'IA est-elle obligatoire?

Non. Le système fonctionne parfaitement sans IA. C'est une fonctionnalité optionnelle.

### Que se passe-t-il si l'API Claude est en panne?

Le système détecte l'erreur et bascule automatiquement sur la version statistique classique. **Aucun crash**.

### Peut-on utiliser un autre modèle (GPT-4, Gemini)?

Oui, il faudrait adapter `ai_service.py` pour utiliser l'API OpenAI ou Google. L'architecture est flexible.

### Les données sont-elles envoyées à Anthropic?

Oui, les **statistiques agrégées** (nombres, pourcentages) sont envoyées à l'API Claude pour analyse.

**Aucune donnée personnelle** n'est envoyée (pas de noms, emails, etc.).

Selon les [Conditions d'utilisation d'Anthropic](https://www.anthropic.com/legal/commercial-terms), les données ne sont **pas utilisées pour entraîner** les modèles.

### Combien ça coûte?

Avec Claude 3.5 Sonnet:
- Input: $3 / 1M tokens (~750k mots)
- Output: $15 / 1M tokens

**Estimation par rapport** (avec ~2000 tokens input + 2000 tokens output):
- Coût: ~$0.04 (environ 25 FCFA)

Très abordable pour des rapports élaborés de haute qualité.

---

## 📝 Checklist d'activation

- [ ] Créer compte Anthropic
- [ ] Obtenir API key
- [ ] Ajouter crédit sur le compte
- [ ] Installer `pip install anthropic`
- [ ] Configurer `ENABLE_AI=true`
- [ ] Configurer `ANTHROPIC_API_KEY=sk-ant-xxx`
- [ ] Tester connexion (`test_connexion_ia()`)
- [ ] Générer un rapport test
- [ ] Vérifier les logs
- [ ] Valider la qualité du rapport
- [ ] Déployer en production

---

## 🎯 Recommandations

1. **Testez d'abord en local** avant d'activer en production
2. **Surveillez les coûts** via le dashboard Anthropic
3. **Comparez les rapports** IA vs classiques avant de vous décider
4. **Gardez un budget** de 20-50$ pour commencer
5. **Désactivez si besoin** en mettant `ENABLE_AI=false`

---

## 📞 Support

Pour toute question sur l'intégration IA, contactez l'équipe de développement ou consultez:
- Documentation Claude API: https://docs.anthropic.com
- Pricing: https://www.anthropic.com/pricing
