# Configuration Reverse Proxy SONATEL
## Pour l'intégration de la plateforme de maturation sur www.dgppe.sn/maturation

---

## Contexte

La plateforme de soumission de projets de maturation de la DGPPE sera hébergée sur un **serveur Ubuntu 22.04 LTS ANSD**, mais doit être accessible via l'URL :

**`https://www.dgppe.sn/maturation`**

Le domaine `www.dgppe.sn` étant géré par la SONATEL, il est nécessaire de configurer un **reverse proxy** depuis le serveur SONATEL vers le serveur Ubuntu ANSD.

---

## Architecture

```
Utilisateur
    ↓
https://www.dgppe.sn/maturation
    ↓
[Serveur SONATEL - www.dgppe.sn (Nginx)]
    ↓ (reverse proxy HTTP)
http://<IP_SERVEUR_ANSD>
    ↓
[Serveur Ubuntu ANSD - Nginx - Plateforme Maturation]
```

**Flux de requêtes :**
1. Utilisateur accède à `https://www.dgppe.sn/maturation/...`
2. Serveur SONATEL reçoit la requête HTTPS
3. SONATEL fait un reverse proxy vers le serveur ANSD (HTTP ou HTTPS interne)
4. Serveur ANSD traite la requête et renvoie la réponse
5. SONATEL renvoie la réponse à l'utilisateur

---

## Configuration Nginx (sur serveur SONATEL)

### Option 1 : Reverse Proxy HTTP (RECOMMANDÉ - plus simple)

Le serveur ANSD écoute en HTTP sur le port 80, SONATEL gère le SSL :

```nginx
# Fichier : /etc/nginx/sites-available/dgppe.sn
# Sur le serveur SONATEL www.dgppe.sn

server {
    listen 443 ssl http2;
    server_name www.dgppe.sn;

    # Certificats SSL (existants sur serveur SONATEL)
    ssl_certificate /etc/ssl/certs/dgppe.sn.crt;
    ssl_certificate_key /etc/ssl/private/dgppe.sn.key;
    ssl_protocols TLSv1.2 TLSv1.3;

    # Configuration existante pour le reste du site www.dgppe.sn
    # ...

    # NOUVEAU : Reverse proxy pour /maturation
    location /maturation/ {
        # Proxy vers serveur ANSD
        proxy_pass http://<IP_SERVEUR_ANSD>/;

        # Headers pour préserver l'information client
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;

        # Timeouts (ajuster selon besoins)
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffers (optimisation performance)
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;

        # WebSocket support (si nécessaire)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Proxy pour les requêtes API (important pour CORS)
    location /maturation/api/ {
        proxy_pass http://<IP_SERVEUR_ANSD>/api/;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;

        # CORS headers (si nécessaire)
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;

        # OPTIONS preflight
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
}

# Redirection HTTP vers HTTPS
server {
    listen 80;
    server_name www.dgppe.sn;
    return 301 https://$server_name$request_uri;
}
```

**À remplacer :**
- `<IP_SERVEUR_ANSD>` : L'IP publique du serveur ANSD (fournie par l'ANSD)

---

### Option 2 : Reverse Proxy HTTPS (si serveur ANSD a son propre SSL)

Si le serveur ANSD écoute en HTTPS avec son propre certificat :

```nginx
location /maturation/ {
    proxy_pass https://<IP_SERVEUR_ANSD>/;

    # Désactiver vérification SSL (certificat auto-signé sur ANSD)
    proxy_ssl_verify off;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
}
```

**⚠️ Note :** Option 1 (HTTP) est plus simple et suffisante, car le trafic entre SONATEL et ANSD peut rester en HTTP interne.

---

## Configuration Apache (alternative si SONATEL utilise Apache)

Si le serveur `www.dgppe.sn` utilise Apache au lieu de Nginx :

```apache
# Fichier : /etc/apache2/sites-available/dgppe.sn.conf
# Sur le serveur SONATEL www.dgppe.sn

<VirtualHost *:443>
    ServerName www.dgppe.sn

    # SSL Configuration (existante)
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/dgppe.sn.crt
    SSLCertificateKeyFile /etc/ssl/private/dgppe.sn.key

    # Configuration existante du site
    # ...

    # NOUVEAU : Reverse proxy pour /maturation
    ProxyPreserveHost On
    ProxyRequests Off

    # Activer modules requis
    # a2enmod proxy proxy_http headers

    # Reverse proxy vers serveur ANSD
    ProxyPass /maturation http://<IP_SERVEUR_ANSD>/
    ProxyPassReverse /maturation http://<IP_SERVEUR_ANSD>/

    # Headers
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-Port "443"
    RequestHeader set X-Forwarded-Host "www.dgppe.sn"

    # Timeouts
    ProxyTimeout 60
</VirtualHost>

# Redirection HTTP vers HTTPS
<VirtualHost *:80>
    ServerName www.dgppe.sn
    Redirect permanent / https://www.dgppe.sn/
</VirtualHost>
```

**Modules Apache requis :**
```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod headers
sudo systemctl restart apache2
```

---

## Tests de Validation

Une fois la configuration en place, tester :

### 1. Test basique de connectivité

```bash
# Depuis le serveur SONATEL, tester l'accès au serveur ANSD
curl -I http://<IP_SERVEUR_ANSD>

# Devrait retourner HTTP 200 OK
```

### 2. Test du reverse proxy

```bash
# Depuis n'importe quel ordinateur
curl -I https://www.dgppe.sn/maturation

# Devrait retourner HTTP 200 OK (pas 404 ou 502)
```

### 3. Test dans le navigateur

Ouvrir dans un navigateur :
```
https://www.dgppe.sn/maturation
```

**Attendu :** Page d'accueil de la plateforme de maturation (page de login)

---

## Vérification de la Configuration

### Sur le serveur SONATEL (après configuration)

```bash
# Vérifier la syntaxe Nginx
sudo nginx -t

# Recharger Nginx
sudo systemctl reload nginx

# Vérifier les logs en temps réel
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Sur le serveur ANSD

```bash
# Vérifier que Nginx écoute sur le port 80
sudo ss -tlnp | grep :80

# Vérifier les logs
sudo tail -f /var/log/nginx/access.log
```

---

## Problèmes Courants et Solutions

### Erreur 502 Bad Gateway

**Cause :** Le serveur ANSD n'est pas accessible ou ne répond pas

**Solutions :**
1. Vérifier que le serveur ANSD est démarré
2. Vérifier le firewall ANSD autorise l'IP du serveur SONATEL
3. Vérifier l'IP du serveur ANSD dans la config Nginx SONATEL
4. Tester la connectivité : `curl http://<IP_SERVEUR_ANSD>` depuis SONATEL

### Erreur 504 Gateway Timeout

**Cause :** Le serveur ANSD prend trop de temps à répondre

**Solutions :**
1. Augmenter les timeouts dans la config Nginx :
```nginx
proxy_connect_timeout 120s;
proxy_send_timeout 120s;
proxy_read_timeout 120s;
```

### Erreur 404 Not Found

**Cause :** Le chemin `/maturation` n'est pas correctement routé

**Solutions :**
1. Vérifier que `proxy_pass` se termine par `/` : `http://<IP>/`
2. Vérifier que la config a été rechargée : `sudo nginx -t && sudo systemctl reload nginx`

### Problèmes de CSS/JS (page sans style)

**Cause :** Les chemins relatifs des assets ne sont pas corrects

**Solutions :**
1. Vérifier que l'application Vue.js a été compilée avec `publicPath: '/maturation/'`
2. Ajouter dans la config Nginx SONATEL :
```nginx
location /maturation/static/ {
    proxy_pass http://<IP_SERVEUR_ANSD>/static/;
}
```

---

## Sécurité

### Restriction d'accès par IP (optionnel)

Si vous voulez restreindre l'accès à certaines IP :

```nginx
location /maturation/ {
    # Autoriser seulement certaines IP
    allow 196.1.0.0/16;      # Exemple : plage IP Sénégal
    allow 41.82.0.0/16;      # Exemple : autre plage
    deny all;

    proxy_pass http://<IP_SERVEUR_ANSD>/;
    # ... reste de la config
}
```

### Rate Limiting (protection DDoS)

```nginx
# En haut du fichier nginx.conf
limit_req_zone $binary_remote_addr zone=maturation:10m rate=10r/s;

# Dans location /maturation/
location /maturation/ {
    limit_req zone=maturation burst=20 nodelay;

    proxy_pass http://<IP_SERVEUR_ANSD>/;
    # ... reste de la config
}
```

---

## Monitoring

### Logs à surveiller sur SONATEL

```bash
# Accès à /maturation
grep "/maturation" /var/log/nginx/access.log

# Erreurs reverse proxy
grep "proxy" /var/log/nginx/error.log
```

### Métriques importantes

- Nombre de requêtes vers `/maturation` par minute
- Temps de réponse moyen (devrait être < 2 secondes)
- Taux d'erreur 502/504 (devrait être < 1%)

---

## Contact et Support

### DGPPE
**Responsable technique :**
- Email : [À compléter]
- Téléphone : [À compléter]

### ANSD
**Administrateur serveur :**
- Email : [À compléter]
- Téléphone : [À compléter]

### SONATEL
**Administrateur www.dgppe.sn :**
- Email : [À compléter]
- Téléphone : [À compléter]

---

## Checklist de Configuration

**À faire par la SONATEL :**

```
□ Identifier le serveur hébergeant www.dgppe.sn
□ Déterminer le serveur web utilisé (Nginx ou Apache)
□ Récupérer l'IP publique du serveur ANSD
□ Ajouter la configuration reverse proxy dans le vhost www.dgppe.sn
□ Tester la syntaxe de la configuration (nginx -t ou apachectl -t)
□ Recharger le serveur web
□ Tester l'accès depuis SONATEL : curl http://<IP_ANSD>
□ Tester l'accès public : https://www.dgppe.sn/maturation
□ Vérifier les logs nginx/apache
□ Confirmer à la DGPPE que la configuration est opérationnelle
```

---

## Résumé Configuration Minimale

**Pour SONATEL (Nginx) :**

```nginx
# Dans /etc/nginx/sites-available/dgppe.sn
location /maturation/ {
    proxy_pass http://<IP_SERVEUR_ANSD>/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**Commandes :**
```bash
# Tester config
sudo nginx -t

# Recharger
sudo systemctl reload nginx

# Vérifier
curl -I https://www.dgppe.sn/maturation
```

**C'est tout !** 🎉

---

**Date :** 2025-01-19
**Version :** 1.0
**Statut :** Prêt pour transmission à SONATEL
