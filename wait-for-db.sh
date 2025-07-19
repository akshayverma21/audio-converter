
#!/usr/bin/env bash
set -e # Exit immediately if a command exits with a non-zero status

echo "Waiting for database..."
until pg_isready -d "$DATABASE_URL" >/dev/null 2>&1; do
  sleep 2
done

echo "Database is ready."

# --- Corrected: Removed 'RUN' and added env var passing ---
# These commands now run as plain shell commands at runtime.
# SECRET_KEY and DEBUG environment variables are provided by Render at runtime.
echo "Running Tailwind build..."
SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py tailwind build --no-input || true

echo "Collecting static files..."
SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py collectstatic --noinput || true
# --- End Corrected ---

echo "Running migrations..."
SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py migrate --noinput

# Create superuser if env vars present
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Ensuring superuser exists..."
  # CRITICAL FIX: Added 'from decouple import config' inside the PYCODE block.
  # Added SECRET_KEY and DEBUG prefix here too for consistency, though shell might inherit for internal calls.
  SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" python manage.py shell <<'PYCODE'
import os
from django.contrib.auth import get_user_model
from decouple import config # <--- NEW: Import config function

User = get_user_model()

# Ensure these environment variables (DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD)
# are set in Render's environment variables for your service!
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
# Ensure Gunicorn also inherits the necessary environment variables
exec SECRET_KEY="$SECRET_KEY" DEBUG="$DEBUG" "$@"














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
