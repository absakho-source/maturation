# Guide d'Installation Serveur - Plateforme de Soumission de Projets

## Spécifications Serveur Requises

### 1. Système d'exploitation

**✅ RECOMMANDÉ : Ubuntu Server 22.04 LTS ou 24.04 LTS**

**Pourquoi Ubuntu ?**
- Support long terme (5 ans)
- Excellente compatibilité avec Python, Node.js, PostgreSQL
- Grande communauté et documentation
- Mises à jour de sécurité régulières
- Gratuit et open-source

**Alternatives acceptables :**
- Debian 12 (Bookworm)
- CentOS Stream 9 / Rocky Linux 9

**❌ NON RECOMMANDÉ :**
- Windows Server (problèmes de compatibilité avec les dépendances Python/Node.js)
- Ubuntu Desktop (trop de services inutiles)

---

### 2. Configuration Matérielle

#### **Option A : Production Légère (< 100 utilisateurs simultanés)**

```
CPU      : 2 cœurs (2 vCPUs)
RAM      : 4 GB
Disque   : 50 GB SSD
Réseau   : 100 Mbps
```

**Cas d'usage :** Équipe interne, 20-50 projets/an, < 100 utilisateurs actifs

**Coût estimé :** 10-20 €/mois (VPS) ou serveur physique ~500 €

---

#### **Option B : Production Standard (100-500 utilisateurs simultanés) ⭐ RECOMMANDÉ**

```
CPU      : 4 cœurs (4 vCPUs)
          Processeur : Intel Xeon, AMD EPYC, ou équivalent
RAM      : 8 GB DDR4
Disque   : 100 GB SSD NVMe (lecture ≥ 3000 MB/s)
Réseau   : 500 Mbps minimum, 1 Gbps recommandé
```

**Cas d'usage :** Plateforme nationale, 100-500 projets/an, plusieurs ministères

**Coût estimé :** 30-50 €/mois (VPS) ou serveur physique ~1500 €

---

#### **Option C : Production Haute Disponibilité (> 500 utilisateurs simultanés)**

```
CPU      : 8 cœurs (8 vCPUs)
          Processeur : Intel Xeon Gold, AMD EPYC 7xx3
RAM      : 16 GB DDR4 ECC
Disque   : 250 GB SSD NVMe RAID 1 (redondance)
Réseau   : 1 Gbps garanti
Backup   : Disque supplémentaire 500 GB pour sauvegardes
```

**Cas d'usage :** Plateforme multi-pays, milliers de projets, haute criticité

**Coût estimé :** 80-150 €/mois (VPS) ou serveur physique ~3000-5000 €

---

### 3. Espace Disque Détaillé

| Composant | Taille | Description |
|-----------|--------|-------------|
| Système Ubuntu | 10 GB | OS + logiciels système |
| Application (code) | 500 MB | Backend Flask + Frontend Vue.js |
| Base de données | 5-50 GB | Dépend du volume de projets |
| Fichiers uploadés (PDFs) | 10-100 GB | Documents des projets (estimé 2 MB/projet) |
| Logs | 5 GB | Logs applicatifs + système |
| Sauvegardes | 20-100 GB | Dumps SQL quotidiens + fichiers |
| Swap | 4-8 GB | Mémoire swap (2x RAM si RAM < 4GB) |
| **TOTAL RECOMMANDÉ** | **100-250 GB** | Selon charge attendue |

**💡 Conseil :** Prévoir un disque externe ou NAS pour les sauvegardes

---

### 4. Logiciels à Installer

#### **Système de base**
```bash
- Ubuntu Server 22.04 LTS (minimal install)
- OpenSSH Server
- UFW (firewall)
- Fail2ban (protection SSH)
```

#### **Environnement d'exécution**
```bash
- Python 3.10 ou 3.11
- pip (gestionnaire paquets Python)
- virtualenv
- Node.js 20.x LTS
- npm 10.x
```

#### **Base de données**
```bash
Option A (Production) : PostgreSQL 14+
Option B (Légère)     : SQLite 3 (déjà inclus avec Python)
```

**💡 Recommandation :** PostgreSQL pour > 50 utilisateurs simultanés

#### **Serveur Web**
```bash
- Nginx 1.24+ (reverse proxy + serveur statique)
- Certbot (certificats SSL Let's Encrypt)
```

#### **Gestionnaires de processus**
```bash
- Systemd (backend Flask)
- PM2 (frontend Node.js en dev) ou servir via Nginx en production
```

#### **Outils de monitoring (optionnel)**
```bash
- htop (monitoring CPU/RAM)
- netdata (monitoring temps réel)
- logrotate (rotation logs automatique)
```

---

### 5. Réseau et Sécurité

#### **Ports à ouvrir**

| Port | Service | Accès | Règle Firewall |
|------|---------|-------|----------------|
| 22 | SSH | Admin uniquement | Restreindre par IP si possible |
| 80 | HTTP | Public | Redirection automatique vers 443 |
| 443 | HTTPS | Public | Seul port public ouvert |
| 5432 | PostgreSQL | Localhost | ❌ Ne JAMAIS exposer publiquement |

#### **Configuration Firewall (UFW)**
```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH (restreindre par IP si possible)
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

#### **Sécurité obligatoire**

✅ **Niveau 1 (Minimal)**
- Certificat SSL/TLS (Let's Encrypt gratuit)
- Firewall UFW activé
- SSH par clé uniquement (désactiver authentification par mot de passe)
- Utilisateur non-root pour exécuter l'application
- Mises à jour automatiques de sécurité

✅ **Niveau 2 (Recommandé)**
- Fail2ban (blocage automatique après tentatives SSH/HTTP échouées)
- Sauvegardes automatiques quotidiennes
- Monitoring des logs
- Rate limiting sur Nginx
- HSTS (HTTP Strict Transport Security)

✅ **Niveau 3 (Haute sécurité)**
- VPN pour accès administrateur
- WAF (Web Application Firewall) - ex: ModSecurity
- IDS/IPS (ex: Suricata)
- Audit de sécurité trimestriel
- Séparation réseau (DMZ)

---

### 6. Architecture de Déploiement

```
Internet
   ↓
[Firewall UFW]
   ↓
[Nginx :443] ← Certificat SSL Let's Encrypt
   ↓                                    ↓
[Backend Flask :5000]          [Frontend Vue.js]
(gunicorn/waitress)            (fichiers statiques)
   ↓
[PostgreSQL :5432]
(localhost uniquement)
   ↓
[Disque de sauvegarde]
(dumps quotidiens)
```

**Processus de fonctionnement :**
1. Utilisateur accède à `https://plateforme.gouv.sn`
2. Nginx reçoit la requête HTTPS (port 443)
3. Si c'est une requête API (`/api/*`) → proxy vers Flask (port 5000)
4. Si c'est une page web → servir fichiers statiques Vue.js
5. Backend Flask interroge PostgreSQL (localhost:5432)
6. Réponse renvoyée via Nginx → utilisateur

---

### 7. Estimation Budget

#### **Hébergement VPS (Serveur virtuel)**

| Fournisseur | Configuration | Prix/mois | Localisation |
|-------------|---------------|-----------|--------------|
| **OVH** | 4 vCPU, 8GB, 80GB SSD | 20-30 € | France/Canada |
| **DigitalOcean** | 4 vCPU, 8GB, 160GB SSD | 48 $ | Amsterdam/Londres |
| **Contabo** | 6 vCPU, 16GB, 400GB SSD | 13 € | Allemagne |
| **Hetzner** | 4 vCPU, 8GB, 160GB SSD | 20 € | Allemagne/Finlande |
| **Linode** | 4 vCPU, 8GB, 160GB SSD | 48 $ | Mondial |

**💡 Pour le Sénégal/Afrique :** OVH (datacenter Afrique du Sud) ou DigitalOcean (Londres) pour latence réduite

#### **Serveur dédié physique (sur site)**

| Type | Configuration | Prix | Avantages |
|------|---------------|------|-----------|
| **Mini PC** | Intel i5, 16GB, 500GB SSD | 500-800 € | Faible consommation |
| **Serveur tour** | Xeon 4-core, 32GB, 1TB SSD | 1500-2500 € | Évolutif |
| **Serveur rack** | Xeon 8-core, 64GB, 2TB RAID | 3000-5000 € | Professionnel |

**Coûts supplémentaires (serveur physique) :**
- Électricité : 50-150 €/an
- Onduleur (UPS) : 200-500 € (protection coupures)
- Connexion internet fibre : 50-200 €/mois
- Climatisation (datacenter) : Variable
- Maintenance : Temps administrateur

---

### 8. Connexion Internet Requise

**Minimum :**
- **Bande passante** : 100 Mbps symétrique
- **Latence** : < 50 ms vers les utilisateurs
- **Disponibilité** : 99.9% uptime

**Recommandé :**
- **Bande passante** : 500 Mbps - 1 Gbps
- **IP fixe** : Obligatoire pour DNS
- **Connexion redondante** : 2 FAI différents (failover automatique)

**💡 Pour datacenter sur site :** Prévoir connexion fibre professionnelle avec SLA

---

### 9. Sauvegardes

#### **Stratégie 3-2-1**
- **3** copies des données
- **2** supports différents (disque local + cloud/externe)
- **1** copie hors site

#### **Fréquence recommandée**
```
Base de données : Dump SQL quotidien (3h du matin)
Fichiers uploadés : Rsync quotidien
Configuration : Backup hebdomadaire
Logs : Rotation quotidienne (garder 30 jours)
```

#### **Rétention**
```
Quotidien  : 7 jours
Hebdomadaire : 4 semaines
Mensuel : 12 mois
Annuel : 5 ans (conformité légale)
```

#### **Script de sauvegarde automatique** (fourni dans le package d'installation)

---

### 10. Temps d'Installation Estimé

**Installation manuelle complète :**
- Configuration serveur Ubuntu : 1-2 heures
- Installation dépendances : 30 min
- Déploiement application : 1 heure
- Configuration Nginx + SSL : 30 min
- Tests et validation : 1 heure
- **TOTAL : 4-5 heures** (administrateur expérimenté)

**Installation automatisée (avec script fourni) :**
- **30 minutes** (+ temps de téléchargement paquets)

---

### 11. Prérequis Administrateur

**Compétences requises :**
- ✅ Administration Linux de base (ligne de commande)
- ✅ Notions réseau (DNS, pare-feu, ports)
- ✅ Configuration SSH
- ⚠️ Notions de sécurité (optionnel mais recommandé)

**Si vous n'avez pas d'administrateur système :**
- Je peux fournir un script d'installation automatique
- Documentation pas-à-pas avec captures d'écran
- Support à distance possible

---

## Recommandation Finale

### **Pour la DGPPE (Sénégal) :**

**Solution recommandée :** VPS OVH 4 vCPU / 8GB RAM / 100GB SSD

**Justification :**
- ✅ Datacenter en Afrique du Sud (faible latence)
- ✅ Conformité RGPD (données hébergées en Afrique)
- ✅ Support 24/7 en français
- ✅ Rapport qualité/prix excellent
- ✅ Évolutif facilement
- ✅ Sauvegardes automatiques disponibles
- ✅ Paiement en euros

**Coût total annuel estimé :**
```
Serveur VPS OVH : 25 €/mois × 12 = 300 €/an
Domaine .sn : 15 000 FCFA/an ≈ 23 €/an
Certificat SSL : Gratuit (Let's Encrypt)
-------------------------------------------
TOTAL : ~325 €/an (~213 000 FCFA/an)
```

**Alternative (serveur physique sur site) :**
- Coût initial : 1500-2000 € (serveur)
- Coût récurrent : 100-200 €/an (électricité + internet)
- Avantage : Contrôle total, données 100% locales
- Inconvénient : Nécessite administrateur sur place, risque de coupure électrique

---

## Prochaines Étapes

1. **Décision :** VPS hébergé ou serveur physique sur site ?
2. **Fournisseur :** Quel hébergeur préférez-vous ?
3. **Préparation :** Je crée le script d'installation automatique
4. **Déploiement :** Installation guidée pas-à-pas
5. **Formation :** Documentation administrateur

**Voulez-vous que je prépare :**
- ✅ Script d'installation automatique (1 commande)
- ✅ Documentation pas-à-pas avec screenshots
- ✅ Script de sauvegarde automatique
- ✅ Configuration Nginx optimisée
- ✅ Monitoring et alertes

**Question :** Avez-vous déjà un serveur disponible ou voulez-vous des recommandations spécifiques pour un hébergeur au Sénégal ?
