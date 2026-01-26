#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Ensure superuser 'admin' exists with correct password and permissions
python manage.py shell -c "from django.contrib.auth.models import User; u, created = User.objects.get_or_create(username='admin'); u.set_password('password123'); u.is_superuser = True; u.is_staff = True; u.save(); print('Superuser updated/created')"
