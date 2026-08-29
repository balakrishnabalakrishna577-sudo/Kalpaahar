#!/usr/bin/env bash
# Render build script for KalpAahar Django backend
set -o errexit

cd kalpaahar_backend

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_ebooks

# Create superuser automatically if it does not already exist
python manage.py shell -c "
from accounts.models import User
if not User.objects.filter(email='admin@kalpaahar.in').exists():
    User.objects.create_superuser(
        email='admin@kalpaahar.in',
        password='Kalpaahar@Admin2026',
        name='Admin'
    )
    print('Superuser created')
else:
    print('Superuser already exists')
"