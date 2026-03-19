#!/usr/bin/env bash
set -o errexit

echo "📦  Installation des dépendances..."
pip install -r requirements.txt

echo "🔧  Création des migrations..."
python manage.py makemigrations users
python manage.py makemigrations courses
python manage.py makemigrations quiz
python manage.py makemigrations chat
python manage.py makemigrations live

echo "🗄️  Application des migrations..."
python manage.py migrate

echo "📁  Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "🌱  Chargement des données de démo..."
python manage.py seed_data

echo "✅  Build terminé !"
