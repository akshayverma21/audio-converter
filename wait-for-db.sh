
#!/usr/bin/env bash
set -ex # Keep this for verbose debugging

echo "--- Script started: wait-for-db.sh ---"
echo "--- Testing initial script execution only ---"

# Temporarily comment out all functional parts
# echo "Waiting for database..."
# until pg_isready -d "$DATABASE_URL" >/dev/null 2>&1; do
#   sleep 2
# done
#
# echo "Database is ready."
#
# echo "Running Tailwind build..."
# SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py tailwind build --no-input || { echo "Tailwind build failed!"; exit 1; }
#
# echo "Collecting static files..."
# SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py collectstatic --noinput || { echo "Collectstatic failed!"; exit 1; }
#
# echo "Running migrations..."
# SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py migrate --noinput || { echo "Migrations failed!"; exit 1; }
#
# if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
#   echo "Ensuring superuser exists..."
#   SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py shell <<'PYCODE'
# import os
# from django.contrib.auth import get_user_model
# from decouple import config
#
# User = get_user_model()
#
# email = config("DJANGO_SUPERUSER_EMAIL", default=None)
# password = config("DJANGO_SUPERUSER_PASSWORD", default=None)
# username = email.split('@')[0] if email else "admin"
#
# if email and password and not User.objects.filter(email=email).exists():
#     User.objects.create_superuser(username=username, email=email, password=password)
#     print(f"Created superuser: {email}")
# else:
#     print("Superuser exists or email/password missing; skipping.")
# PYCODE
# fi

# Keep the exec line, as it needs to run something
echo "Starting Gunicorn placeholder (script truncated for test)..."
exec SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" "$@"

# #!/usr/bin/env bash
# set -ex # <--- CHANGED: Added 'x' to enable command tracing

# echo "--- Script started: wait-for-db.sh ---" # <--- NEW: Early debug message

# echo "Waiting for database..."
# until pg_isready -d "$DATABASE_URL" >/dev/null 2>&1; do
#   sleep 2
# done

# echo "Database is ready."

# echo "Running Tailwind build..."
# # Ensure these environment variables are actually set in Render!
# SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py tailwind build --no-input || { echo "Tailwind build failed!"; exit 1; } # <--- Added error handling

# echo "Collecting static files..."
# SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py collectstatic --noinput || { echo "Collectstatic failed!"; exit 1; } # <--- Added error handling

# echo "Running migrations..."
# SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py migrate --noinput || { echo "Migrations failed!"; exit 1; } # <--- Added error handling

# # Create superuser if env vars present
# if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
#   echo "Ensuring superuser exists..."
#   SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py shell <<'PYCODE'
# import os
# from django.contrib.auth import get_user_model
# from decouple import config

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
# # Ensure Gunicorn also inherits the necessary environment variables
# exec SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" "$@"








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
