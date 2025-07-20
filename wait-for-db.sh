#!/usr/bin/env bash
set -e

echo "Waiting for database..."
until pg_isready -d "$DATABASE_URL" >/dev/null 2>&1; do
  sleep 2
done
# RUN python manage.py tailwind build || true

# # ---------- Static Assets ----------
# RUN python manage.py collectstatic --noinput || true

echo "Database is ready. Running migrations..."
python manage.py migrate --noinput

# Create superuser if env vars present
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Ensuring superuser exists..."
  python manage.py shell <<'PYCODE'
import os
from django.contrib.auth import get_user_model
User = get_user_model()

email = config("DJANGO_SUPERUSER_EMAIL")
password = config("DJANGO_SUPERUSER_PASSWORD")
username = email.split('@')[0] if email else "admin"

if email and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created superuser: {email}")
else:
    print("Superuser exists or email missing; skipping.")
PYCODE
fi

echo "Starting Gunicorn..."
exec "$@"
