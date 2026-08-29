#!/usr/bin/env bash
# Render build script for KalpAahar Django backend
set -o errexit

cd kalpaahar_backend

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_ebooks