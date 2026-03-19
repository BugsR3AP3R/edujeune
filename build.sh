#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  build.sh  —  exécuté par Render à chaque déploiement
# ─────────────────────────────────────────────────────────────
set -o errexit   # stoppe si une commande échoue

echo "📦  Installation des dépendances..."
pip install -r requirements.txt

echo "📁  Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "🗄️  Migrations de la base de données..."
python manage.py migrate

echo "🌱  Chargement des données de démo..."
python manage.py seed_data

echo "✅  Build terminé !"
