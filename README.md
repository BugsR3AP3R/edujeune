# 🎓 EduJeunes — Plateforme Éducative

Plateforme éducative complète construite avec **Django 4.2 + Bootstrap 5 + Django Channels**.

---

## 🚀 Installation rapide (5 étapes)

### 1. Crée un environnement virtuel
```bash
python -m venv venv
# Windows :
venv\Scripts\activate
# Mac/Linux :
source venv/bin/activate
```

### 2. Installe les dépendances
```bash
pip install -r requirements.txt
```

### 3. Applique les migrations
```bash
python manage.py migrate
```

### 4. Remplis la base avec les données de démo
```bash
python manage.py seed_data
```

### 5. Lance le serveur
```bash
python manage.py runserver
```

Ouvre **http://127.0.0.1:8000** dans ton navigateur.

---

## 🔑 Comptes de démonstration

| Rôle       | Utilisateur       | Mot de passe |
|------------|-------------------|--------------|
| Professeure | `prof_marie`      | `pass1234`   |
| Professeur | `prof_pierre`     | `pass1234`   |
| Professeure | `prof_anne`       | `pass1234`   |
| Étudiant   | `etudiant_jean`   | `pass1234`   |
| Étudiante  | `etudiant_sarah`  | `pass1234`   |
| Étudiant   | `etudiant_paul`   | `pass1234`   |
| Admin      | `admin`           | `admin1234`  |

---

## ✨ Fonctionnalités

### 👩‍🎓 Pour les étudiants
- Inscription avec rôle Étudiant ou Professeur
- Explorer et s'inscrire aux cours (gratuits & payants)
- Leçons vidéo (YouTube/upload), audio, texte
- Suivi de progression par cours
- Quiz chronométrés avec corrections détaillées
- Classroom en temps réel (WebSocket)
- Accès aux sessions live et rediffusions

### 👩‍🏫 Pour les professeurs
- Créer des cours avec image de couverture
- Ajouter des modules et leçons depuis la page Gérer
- Leçons vidéo (lien YouTube/Vimeo ou upload fichier)
- Leçons audio (upload) ou texte riche
- Publier / dépublier un cours en un clic
- Verrouiller des modules
- Programmer des sessions live
- Démarrer/terminer un live en temps réel
- Voir les statistiques (inscrits, note moyenne)

### 🛠️ Technique
- **Django 4.2** — framework principal
- **Django Channels** — WebSockets (chat, live)
- **Bootstrap 5.3** + Bootstrap Icons
- **SQLite** (dev) → PostgreSQL prêt pour la prod
- Design sombre moderne (thème orange #FF6B2B)
- Responsive mobile-first

---

## 📁 Structure du projet

```
eduj/
├── eduplatform/     # Config Django (settings, urls, views principales)
├── users/           # Modèle utilisateur personnalisé
├── courses/         # Cours, modules, leçons, inscriptions, avis
│   └── management/
│       └── commands/
│           └── seed_data.py   ← Données de démo
├── quiz/            # Quiz, questions, choix, tentatives
├── chat/            # Classroom WebSocket par cours
├── live/            # Sessions live WebSocket
├── templates/       # 20+ templates HTML Bootstrap
├── static/          # CSS, JS, images
└── media/           # Fichiers uploadés
```

---

## 🌐 Déploiement en production

```bash
# 1. Modifier settings.py
DEBUG = False
SECRET_KEY = 'nouvelle-clé-secrète-très-longue'
ALLOWED_HOSTS = ['tondomaine.com']

# 2. Configurer PostgreSQL dans DATABASES

# 3. Configurer Redis pour les channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {'hosts': [('127.0.0.1', 6379)]},
    }
}

# 4. Collecter les fichiers statiques
python manage.py collectstatic

# 5. Lancer avec Daphne (ASGI)
daphne -b 0.0.0.0 -p 8000 eduplatform.asgi:application
```
