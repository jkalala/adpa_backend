#!/bin/bash

set -e

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
    sleep 1
done
echo "PostgreSQL is up!"

echo "Applying database migrations..."
python manage.py migrate

echo "Creating superuser if not exists..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser('admin@example.com', 'admin123', first_name='Admin', last_name='User')
END

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000