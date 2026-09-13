#!/bin/sh
set -e

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Checking if initial demo data is needed..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')
django.setup()
from music.models import Album
from django.core.management import call_command
if Album.objects.count() == 0:
    print('Database is empty. Populating demo albums & songs...')
    call_command('seed_demo')
else:
    print(f'Database already contains {Album.objects.count()} album(s). Skipping seed.')
"

PORT="${PORT:-8000}"
WORKERS="${WEB_CONCURRENCY:-2}"

echo "==> Starting Gunicorn server on port ${PORT} with ${WORKERS} worker(s)..."
exec gunicorn website.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --workers "${WORKERS}" \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
