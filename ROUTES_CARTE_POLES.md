# Calque Routier - Carte des Pôles Territoriaux

## Résumé

Ajout d'un calque de routes réalistes sur la carte des pôles territoriaux du Sénégal, utilisant les données OpenStreetMap pour afficher un réseau routier complet et précis.

## Date d'implémentation

3 décembre 2025

## Fonctionnalité

### Description

La carte des pôles territoriaux affiche maintenant un réseau routier complet du Sénégal avec des tracés réalistes suivant la géométrie réelle des routes (polylignes courbes) au lieu de lignes droites.

### Source des Données

- **Origine** : OpenStreetMap (OSM)
- **Méthode d'extraction** : API Overpass
- **Requête utilisée** :
```
[out:json];
area["ISO3166-1"="SN"];
way["highway"~"motorway|trunk|primary|secondary|tertiary"](area);
out geom;
```

### Statistiques

- **Total de routes** : 8 087 segments
- **Taille du fichier** : 6.7 MB (complet), 596 KB (échantillon)
- **Classification** :
  - Autoroutes : 157 segments
  - Routes nationales : 2 310 segments
  - Routes départementales : 1 472 segments
  - Routes locales : 4 148 segments

## Fichiers Créés

### 1. `frontend/public/senegal_roads_full.json`
- **Taille** : 6.7 MB
- **Contenu** : 8 087 routes complètes avec géométries réelles
- **Format** :
```json
[
  {
    "id": "road_8113165",
    "type": "nationale|departementale|locale|autoroute",
    "coordinates": [
      [-17.4665556, 14.7178554],
      [-17.4666456, 14.7178158],
      ...
    ]
  }
]
```

### 2. `frontend/public/senegal_roads_sample.json`
- **Taille** : 596 KB
- **Contenu** : 200 routes pour tests
- **Usage** : Tests de performance et développement

### 3. `frontend/public/senegal_roads.json`
- **Taille** : 8 KB
- **Contenu** : 6 routes principales (ancien format GeoJSON)
- **Statut** : Conservé pour compatibilité, non utilisé

## Implémentation Technique

### Composant Modifié

**Fichier** : `frontend/src/components/CartePolesTerritoriaux.vue`

### Changements Apportés

#### 1. Template SVG (lignes 136-151)
```vue
<!-- COUCHE 3: Routes principales -->
<g class="roads-layer">
  <g v-for="road in roadSegments" :key="road.id">
    <polyline
      :points="getRoadPolylinePoints(road.coordinates)"
      :stroke="getRoadColor(road.type)"
      :stroke-width="getRoadWidth(road.type)"
      :stroke-opacity="getRoadOpacity(road.type)"
      fill="none"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </g>
</g>
```

**Avant** : Utilisation de `<line>` pour lignes droites
**Après** : Utilisation de `<polyline>` pour tracés courbes

#### 2. Data Section (ligne 276)
```javascript
data() {
  return {
    // ...
    roadSegments: [] // Chargé depuis JSON
  }
}
```

**Avant** : 43 routes hardcodées (rectilignes)
**Après** : Array vide rempli dynamiquement depuis JSON

#### 3. Mounted Hook (lignes 428-432)
```javascript
async mounted() {
  await this.loadGeojsonData()
  await this.loadRoadsData()  // NOUVEAU
  await this.loadStats()
}
```

#### 4. Nouvelle Méthode de Chargement (lignes 446-456)
```javascript
async loadRoadsData() {
  try {
    const response = await fetch('/senegal_roads_full.json')
    const roads = await response.json()
    this.roadSegments = roads
    console.log(`✅ ${roads.length} routes chargées`)
  } catch (error) {
    console.error('❌ Erreur chargement routes:', error)
    this.roadSegments = []
  }
}
```

#### 5. Helper Methods (lignes 458-495)

**a) Conversion Coordonnées → Points SVG**
```javascript
getRoadPolylinePoints(coordinates) {
  if (!coordinates || coordinates.length === 0) return ''
  return coordinates.map(([lon, lat]) =>
    `${this.lonToX(lon)},${this.latToY(lat)}`
  ).join(' ')
}
```

**b) Couleur par Type**
```javascript
getRoadColor(type) {
  const colors = {
    'autoroute': '#8b4513',      // Marron foncé
    'nationale': '#8b4513',       // Marron
    'departementale': '#a0826d',  // Marron clair
    'locale': '#c4a57b'           // Marron très clair
  }
  return colors[type] || '#c4a57b'
}
```

**c) Épaisseur par Type**
```javascript
getRoadWidth(type) {
  const widths = {
    'autoroute': 2.5,
    'nationale': 2,
    'departementale': 1,
    'locale': 0.5
  }
  return widths[type] || 0.5
}
```

**d) Opacité par Type**
```javascript
getRoadOpacity(type) {
  const opacities = {
    'autoroute': 0.8,
    'nationale': 0.7,
    'departementale': 0.5,
    'locale': 0.3
  }
  return opacities[type] || 0.3
}
```

## Style Visuel

### Palette de Couleurs

| Type | Couleur | Code Hex | Épaisseur | Opacité |
|------|---------|----------|-----------|---------|
| Autoroute | Marron foncé | #8b4513 | 2.5 | 0.8 |
| Nationale | Marron | #8b4513 | 2.0 | 0.7 |
| Départementale | Marron clair | #a0826d | 1.0 | 0.5 |
| Locale | Marron très clair | #c4a57b | 0.5 | 0.3 |

### Hiérarchie Visuelle

1. **Routes locales** (4148) - Tracés fins et transparents en arrière-plan
2. **Routes départementales** (1472) - Tracés moyens, plus visibles
3. **Routes nationales** (2310) - Tracés épais et bien visibles
4. **Autoroutes** (157) - Tracés les plus épais et opaques

## Ordre des Couches SVG

```
1. Fond de carte (mer/océan)
2. Pôles territoriaux (remplissage coloré)
3. Routes (NOUVELLE COUCHE)
   ├── Routes locales (dessous)
   ├── Routes départementales
   ├── Routes nationales
   └── Autoroutes (dessus)
4. Contours des pôles (stroke)
5. Labels des pôles (texte)
```

## Performance

### Rendu Initial

- **8 087 polylines SVG** à générer
- **~150 000 points** à transformer (lon/lat → x/y)
- **Temps de chargement estimé** : 1-3 secondes (selon navigateur)

### Optimisations Possibles (si nécessaire)

1. **Simplification géométrique** : Réduire le nombre de points par polyline
2. **LOD (Level of Detail)** : Charger routes par niveaux de zoom
3. **Clustering** : Grouper routes proches
4. **Canvas au lieu de SVG** : Utiliser `<canvas>` pour meilleures performances

## Tests

### Tests Locaux Requis

1. Ouvrir http://localhost:5173
2. Naviguer vers la carte des pôles territoriaux
3. Vérifier que les routes s'affichent avec des tracés courbes
4. Vérifier la hiérarchie visuelle (routes locales plus claires, nationales plus foncées)
5. Tester la performance (fluidité des interactions)

### Console Attendue

```
✅ Données GeoJSON chargées: {...}
✅ 8087 routes chargées
✅ Stats des pôles mises à jour: {...}
```

## Déploiement

### Prérequis

Les fichiers JSON doivent être accessibles dans le dossier `public/` du frontend déployé :
- ✅ `senegal_roads_full.json` (6.7 MB)
- ✅ `senegal_roads_sample.json` (596 KB)
- ✅ `senegal_roads.json` (8 KB, legacy)

### Étapes

1. **Pousser vers GitHub** :
```bash
git push origin main
```

2. **Déployer sur Render** :
```bash
ssh root@164.92.255.58 "cd /root/maturation && git pull origin main && pkill -f 'npm.*dev' && cd frontend && nohup npm run dev > frontend.log 2>&1 &"
```

3. **Vérifier** :
- Accéder à la carte des pôles
- Console du navigateur doit afficher "✅ 8087 routes chargées"
- Routes doivent être visibles avec tracés réalistes

## Maintenance

### Mise à Jour des Données Routières

Pour mettre à jour les routes depuis OSM :

1. **Requête Overpass API** :
```bash
curl "https://overpass-api.de/api/interpreter" \
  --data-urlencode 'data=[out:json];area["ISO3166-1"="SN"];way["highway"~"motorway|trunk|primary|secondary|tertiary"](area);out geom;' \
  -o /tmp/osm_roads.json
```

2. **Conversion Python** :
```python
import json

# Charger OSM
with open('/tmp/osm_roads.json', 'r') as f:
    osm = json.load(f)

# Convertir
roads = []
types = {
    'motorway': 'autoroute',
    'trunk': 'nationale',
    'primary': 'nationale',
    'secondary': 'departementale',
    'tertiary': 'locale'
}

for el in osm.get('elements', []):
    if el.get('type') == 'way' and 'geometry' in el:
        highway = el.get('tags', {}).get('highway', '')
        road_type = types.get(highway, 'locale')
        coords = [[n['lon'], n['lat']] for n in el['geometry']]

        if len(coords) >= 2:
            roads.append({
                'id': f"road_{el['id']}",
                'type': road_type,
                'coordinates': coords
            })

# Sauvegarder
with open('frontend/public/senegal_roads_full.json', 'w') as f:
    json.dump(roads, f)
```

3. **Commit et déployer** :
```bash
git add frontend/public/senegal_roads_full.json
git commit -m "Mise à jour données routières OSM"
git push origin main
```

### Performance Tuning

Si le rendu est lent (>3 secondes) :

1. **Option 1** : Utiliser `senegal_roads_sample.json` (200 routes)
```javascript
const response = await fetch('/senegal_roads_sample.json')
```

2. **Option 2** : Filtrer par type
```javascript
this.roadSegments = roads.filter(r =>
  ['autoroute', 'nationale'].includes(r.type)
)
```

3. **Option 3** : Simplifier les coordonnées
```python
# Garder 1 point sur 3
coords = coords[::3]
```

## Historique des Versions

### Version 1.0 - Lignes Droites (avant 3 déc 2025)
- 43 routes hardcodées
- Lignes droites entre points A et B
- Format : `{ name, start, end, type }`

### Version 2.0 - Tracés Réalistes (3 déc 2025)
- 8 087 routes depuis OSM
- Polylignes courbes suivant géométrie réelle
- Format : `{ id, type, coordinates: [[lon, lat], ...] }`

## Support

Pour questions ou problèmes :
1. Vérifier console navigateur pour messages d'erreur
2. Vérifier que fichier JSON est accessible : `http://localhost:5173/senegal_roads_full.json`
3. Vérifier taille fichier : `du -h frontend/public/senegal_roads_full.json`
4. Consulter logs frontend : `tail -f frontend/frontend.log`

## Commit Git

**SHA** : 9f107fc
**Message** : "Ajout calque routier réaliste sur carte des pôles territoriaux"
**Fichiers modifiés** :
- `frontend/src/components/CartePolesTerritoriaux.vue` (+43 lignes, -79 lignes)
- `frontend/public/senegal_roads_full.json` (nouveau, 6.7 MB)
- `frontend/public/senegal_roads_sample.json` (nouveau, 596 KB)
- `frontend/public/senegal_roads.json` (nouveau, 8 KB)

---

**Documentation créée le** : 3 décembre 2025
**Dernière mise à jour** : 3 décembre 2025
