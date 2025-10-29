#!/bin/bash
set -ex

echo "--- Starting Audio Converter App ---"

# Use the connection pooler hostname
echo "Testing database connection..."
if pg_isready -h aws-0-us-west-1.pooler.supabase.co -p 5432 -U postgres -d postgres -t 10; then
    echo "✅ Database connection successful"
else
    echo "⚠️  Database connection failed, but continuing..."
fi

echo "Building Tailwind CSS..."
python manage.py tailwind build --no-input || echo "Tailwind build failed, continuing..."

echo "Collecting static files..."
python manage.py collectstatic --noinput || echo "Collectstatic failed, continuing..."

echo "Running database migrations..."
python manage.py migrate --noinput || echo "Migrations failed, continuing..."

# Create superuser if environment variables exist
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
if email and password and not User.objects.filter(email=email).exists():
    User.objects.create_superuser(email=email, password=password)
    print('Superuser created successfully')
else:
    print('Superuser already exists or credentials missing')
" || echo "Superuser creation failed, continuing..."
fi

echo "Starting Gunicorn server..."
# Use $PORT environment variable provided by Render
exec gunicorn audio_converter.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
# set -ex # Keep this for verbose debugging during initial full run

# echo "--- Script started: wait-for-db.sh ---"


# export DATABASE_URL="postgresql://postgres:[OTYCz5lBN26AofiM]@db.afzclrvsjnhbwgoebqpr.supabase.co:5432/postgres"

# echo "Waiting for database..."
# until pg_isready -d "$DATABASE_URL" >/dev/null 2>&1; do
#   sleep 2
# done

# echo "Database is ready."

# echo "Running Tailwind build..."
# # Ensure SECRET_KEY and DEBUG are set in Render's environment variables.
# SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py tailwind build --no-input || { echo "Tailwind build failed! Continuing anyway."; }

# echo "Collecting static files..."
# SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py collectstatic --noinput || { echo "Collectstatic failed! Continuing anyway."; }

# echo "Running migrations..."
# SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py migrate --noinput || { echo "Migrations failed! This is critical!"; exit 1; }

# # Create superuser if env vars present
# if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
#   echo "Ensuring superuser exists..."
#   SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py shell <<'PYCODE'
# import os
# from django.contrib.auth import get_user_model
# from decouple import config # <--- IMPORTANT: This import is necessary!

# User = get_user_model()

# email = config("DJANGO_SUPERUSER_EMAIL", default=None)
# password = config("DJANGO_SUPERUSER_PASSWORD", default=None)
# username = email.split('@')[0] if email else "admin"

# if email and password and not User.objects.filter(email=email).exists():
#     User.objects.create_superuser(username=username, email=email, password=password)
#     print(f"Created superuser: {email}")
# else:
#     print("Superuser exists or email/password missing; skipping.")
# PYCODE
# fi

# echo "Starting Gunicorn..."
# # This will exec Gunicorn with the arguments passed to wait-for-db.sh from the Dockerfile CMD.
# exec "$@"








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
