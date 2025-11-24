# Guide de Déploiement PLASMAP sur Ubuntu

---

## ÉTAPE 0 : Se connecter au serveur

Une fois devant le serveur Ubuntu à l'ANSD :

```bash
# Si tu as un écran/clavier branché directement, tu verras un prompt de connexion
# Sinon, depuis ton PC, connecte-toi en SSH :
ssh utilisateur@adresse-ip-du-serveur
```

Tu verras quelque chose comme :
```
utilisateur@serveur:~$
```

Le `~` signifie que tu es dans ton dossier personnel.

---

## ÉTAPE 1 : Mettre à jour le système

```bash
sudo apt update
```
> Tape ton mot de passe quand demandé (tu ne verras pas les caractères, c'est normal)

```bash
sudo apt upgrade -y
```
> Le `-y` répond "oui" automatiquement aux questions

---

## ÉTAPE 2 : Installer les logiciels nécessaires

Copie et colle cette commande en entier :

```bash
sudo apt install -y python3 python3-pip python3-venv nodejs npm git nginx curl
```

Vérifie que tout est installé :
```bash
python3 --version
node --version
npm --version
git --version
nginx -v
```

Tu devrais voir les versions s'afficher pour chaque commande.

---

## ÉTAPE 3 : Créer le dossier pour l'application

```bash
sudo mkdir -p /var/www/plasmap
```

Donner les droits à ton utilisateur :
```bash
sudo chown -R $USER:$USER /var/www/plasmap
```

Se déplacer dans ce dossier :
```bash
cd /var/www/plasmap
```

> Tu verras maintenant : `utilisateur@serveur:/var/www/plasmap$`

---

## ÉTAPE 4 : Télécharger le code

### Option A : Avec Git (si internet disponible)

```bash
git clone https://github.com/absakho-source/maturation.git .
```

> Le `.` à la fin est important ! Il dit de cloner dans le dossier actuel.

### Option B : Avec clé USB (si pas d'internet)

1. Branche ta clé USB
2. Monte la clé :
```bash
sudo mkdir -p /mnt/usb
sudo mount /dev/sdb1 /mnt/usb
```
> Note : `/dev/sdb1` peut être différent. Tape `lsblk` pour voir les disques.

3. Copie les fichiers :
```bash
cp -r /mnt/usb/maturation/* /var/www/plasmap/
```

4. Démonte la clé :
```bash
sudo umount /mnt/usb
```

---

## ÉTAPE 5 : Configurer le Backend

### 5.1 Aller dans le dossier backend
```bash
cd /var/www/plasmap/backend
```

### 5.2 Créer l'environnement Python
```bash
python3 -m venv venv
```

### 5.3 Activer l'environnement
```bash
source venv/bin/activate
```

> Tu verras `(venv)` apparaître au début de la ligne. Ça veut dire que l'environnement est activé.

### 5.4 Installer les dépendances Python
```bash
pip install -r requirements.txt
```

> Ça peut prendre quelques minutes. Attends que ça finisse.

### 5.5 Créer les dossiers nécessaires
```bash
mkdir -p uploads static/uploads
```

### 5.6 Initialiser la base de données
```bash
python -c "from db import db; from app import app;
with app.app_context():
    db.create_all()
    print('Base de données créée!')"
```

### 5.7 Exécuter les migrations
```bash
python add_missing_user_columns.py
python add_visibility_column.py
python create_ministeres_table.py
python init_demo_data.py
```

### 5.8 Tester que le backend fonctionne
```bash
python app.py
```

Tu devrais voir :
```
 * Running on http://0.0.0.0:5000
```

Appuie sur `Ctrl+C` pour arrêter.

### 5.9 Désactiver l'environnement Python
```bash
deactivate
```

---

## ÉTAPE 6 : Configurer le Frontend

### 6.1 Aller dans le dossier frontend
```bash
cd /var/www/plasmap/frontend
```

### 6.2 Installer les dépendances Node
```bash
npm install
```

> Ça peut prendre plusieurs minutes.

### 6.3 Construire l'application
```bash
npm run build
```

Tu verras un message de succès et un dossier `dist` sera créé.

---

## ÉTAPE 7 : Créer le service systemd pour le backend

### 7.1 Créer le fichier de service
```bash
sudo nano /etc/systemd/system/plasmap-backend.service
```

> `nano` est un éditeur de texte. Tu vas voir un écran noir avec le curseur.

### 7.2 Copier ce contenu

Tape ou colle exactement ceci :

```ini
[Unit]
Description=PLASMAP Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/plasmap/backend
Environment="PATH=/var/www/plasmap/backend/venv/bin"
ExecStart=/var/www/plasmap/backend/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 7.3 Sauvegarder et quitter nano
1. Appuie sur `Ctrl+O` (la lettre O)
2. Appuie sur `Entrée` pour confirmer
3. Appuie sur `Ctrl+X` pour quitter

### 7.4 Activer et démarrer le service
```bash
sudo systemctl daemon-reload
sudo systemctl enable plasmap-backend
sudo systemctl start plasmap-backend
```

### 7.5 Vérifier que ça fonctionne
```bash
sudo systemctl status plasmap-backend
```

Tu devrais voir `active (running)` en vert.

---

## ÉTAPE 8 : Configurer Nginx (serveur web)

### 8.1 Créer le fichier de configuration
```bash
sudo nano /etc/nginx/sites-available/plasmap
```

### 8.2 Copier ce contenu

**IMPORTANT** : Remplace `ADRESSE_IP_DU_SERVEUR` par l'adresse IP réelle du serveur (ex: 192.168.1.100)

```nginx
server {
    listen 80;
    server_name ADRESSE_IP_DU_SERVEUR;

    # Taille max des fichiers uploadés (100 MB)
    client_max_body_size 100M;

    # Frontend - fichiers statiques
    location / {
        root /var/www/plasmap/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend - API
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Fichiers uploadés
    location /uploads {
        alias /var/www/plasmap/backend/uploads;
    }
}
```

### 8.3 Sauvegarder et quitter
`Ctrl+O`, `Entrée`, `Ctrl+X`

### 8.4 Activer le site
```bash
sudo ln -s /etc/nginx/sites-available/plasmap /etc/nginx/sites-enabled/
```

### 8.5 Désactiver le site par défaut
```bash
sudo rm /etc/nginx/sites-enabled/default
```

### 8.6 Tester la configuration
```bash
sudo nginx -t
```

Tu devrais voir :
```
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 8.7 Redémarrer Nginx
```bash
sudo systemctl restart nginx
```

---

## ÉTAPE 9 : Configurer les permissions

```bash
sudo chown -R www-data:www-data /var/www/plasmap
sudo chmod -R 755 /var/www/plasmap
sudo chmod -R 775 /var/www/plasmap/backend/uploads
```

---

## ÉTAPE 10 : Configurer le pare-feu

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

Tape `y` quand demandé.

---

## ÉTAPE 11 : Tester l'application

### Depuis le serveur
```bash
curl http://localhost/api/health
```

### Depuis un autre PC sur le réseau
Ouvre un navigateur et va sur :
```
http://ADRESSE_IP_DU_SERVEUR
```

Tu devrais voir la page de connexion PLASMAP !

---

## Identifiants par défaut

| Rôle | Username | Mot de passe |
|------|----------|--------------|
| Admin | admin | admin123 |
| Secrétariat SCT | secretariat | secret123 |
| Évaluateur | evaluateur1 | eval123 |
| Soumissionnaire | soumissionnaire | soum123 |

---

## Commandes utiles à retenir

### Voir les logs du backend
```bash
sudo journalctl -u plasmap-backend -f
```
> `-f` pour suivre en temps réel. `Ctrl+C` pour arrêter.

### Redémarrer le backend
```bash
sudo systemctl restart plasmap-backend
```

### Redémarrer Nginx
```bash
sudo systemctl restart nginx
```

### Voir l'état des services
```bash
sudo systemctl status plasmap-backend
sudo systemctl status nginx
```

### Mettre à jour le code (si Git)
```bash
cd /var/www/plasmap
git pull origin main
sudo systemctl restart plasmap-backend
```

---

## En cas de problème

### Le backend ne démarre pas
```bash
sudo journalctl -u plasmap-backend -n 50
```
Regarde les erreurs affichées.

### Nginx affiche une erreur
```bash
sudo tail -f /var/log/nginx/error.log
```

### Page blanche
Vérifie que le build frontend existe :
```bash
ls -la /var/www/plasmap/frontend/dist
```

### Erreur 502 Bad Gateway
Le backend n'est pas démarré :
```bash
sudo systemctl start plasmap-backend
```

### Erreur de permission sur uploads
```bash
sudo chown -R www-data:www-data /var/www/plasmap/backend/uploads
sudo chmod -R 775 /var/www/plasmap/backend/uploads
```

---

## Checklist avant de partir

- [ ] L'application est accessible via navigateur
- [ ] La connexion admin fonctionne
- [ ] On peut soumettre un projet
- [ ] Les fichiers s'uploadent correctement
- [ ] Noter l'adresse IP du serveur
- [ ] Noter les identifiants admin changés

---

## Contact support

En cas de problème après le déploiement :
- Email : [ton email]
- Téléphone : [ton numéro]
