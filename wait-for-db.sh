#!/bin/bash
set -ex # Keep this for verbose debugging during initial full run

echo "--- Script started: wait-for-db.sh ---"


echo "Waiting for database..."
until pg_isready -d "$DATABASE_URL" >/dev/null 2>&1; do
  sleep 2
done

echo "Database is ready."

echo "Running Tailwind build..."
# Ensure SECRET_KEY and DEBUG are set in Render's environment variables.
SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py tailwind build --no-input || { echo "Tailwind build failed! Continuing anyway."; }

echo "Collecting static files..."
SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py collectstatic --noinput || { echo "Collectstatic failed! Continuing anyway."; }

echo "Running migrations..."
SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py migrate --noinput || { echo "Migrations failed! This is critical!"; exit 1; }

# Create superuser if env vars present
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Ensuring superuser exists..."
  SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py shell <<'PYCODE'
import os
from django.contrib.auth import get_user_model
from decouple import config # <--- IMPORTANT: This import is necessary!

User = get_user_model()

email = config("DJANGO_SUPERUSER_EMAIL", default=None)
password = config("DJANGO_SUPERUSER_PASSWORD", default=None)
username = email.split('@')[0] if email else "admin"

if email and password and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created superuser: {email}")
else:
    print("Superuser exists or email/password missing; skipping.")
PYCODE
fi

echo "Starting Gunicorn..."
# This will exec Gunicorn with the arguments passed to wait-for-db.sh from the Dockerfile CMD.
exec "$@"








# #!/usr/bin/env bash
# set -e

# echo "Waiting for database..."
# until pg_isready -d "$DATABASE_URL" >/dev/null 2>&1; do
#   sleep 2
# done
# RUN python manage.py tailwind build || true

# # ---------- Static Assets ----------
# RUN python manage.py collectstatic --noinput || true

# echo "Database is ready. Running migrations..."
# python manage.py migrate --noinput

# # Create superuser if env vars present
# if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
#   echo "Ensuring superuser exists..."
#   python manage.py shell <<'PYCODE'
# import os
# from django.contrib.auth import get_user_model
# User = get_user_model()

# email = config("DJANGO_SUPERUSER_EMAIL")
# password = config("DJANGO_SUPERUSER_PASSWORD")
# username = email.split('@')[0] if email else "admin"

# if email and not User.objects.filter(email=email).exists():
#     User.objects.create_superuser(username=username, email=email, password=password)
#     print(f"Created superuser: {email}")
# else:
#     print("Superuser exists or email missing; skipping.")
# PYCODE
# fi

# echo "Starting Gunicorn..."
# exec "$@"
