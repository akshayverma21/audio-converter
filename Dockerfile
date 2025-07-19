# ---------- Base Image ----------
FROM python:3.12-slim
# Python runtime env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---------- System Dependencies ----------
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    build-essential \
    libmagic1 \
    postgresql-client \
    nodejs \
    npm \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# ---------- App Directory ----------
WORKDIR /app

# ---------- Python Dependencies ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Node.js Dependencies ----------
COPY theme/static_src/package.json theme/static_src/
WORKDIR /app/theme/static_src
RUN npm install && npm cache clean --force

# ---------- App Code ----------
WORKDIR /app
COPY . .
RUN dos2unix wait-for-db.sh

# ---------- Build Static Assets ----------
ENV DJANGO_SECRET_KEY_BUILD="a_dummy_secret_key_for_docker_build_only_replace_this_with_a_real_one_in_render_env"
RUN DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY_BUILD python manage.py tailwind build
RUN DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY_BUILD python manage.py collectstatic --noinput

# ---------- Port ----------
EXPOSE 8000

# ---------- Entrypoint ----------
CMD ["./wait-for-db.sh", "gunicorn", "audio_converter.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]










# # ---------- Base Image ----------
# FROM python:3.12-slim
# # Python runtime env
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# # ---------- System Dependencies ----------
# # postgresql-client for pg_isready; node & npm for tailwind; curl for diagnostics
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libreoffice \
#     libreoffice-writer \
#     libreoffice-calc \
#     libreoffice-impress \
#     build-essential \
#     libmagic1 \
#     postgresql-client \
#     nodejs \
#     npm \
#     dos2unix \
#     && rm -rf /var/lib/apt/lists/*

# # ---------- App Directory ----------
# WORKDIR /app

# # ---------- Python Dependencies ----------
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # ---------- App Code ----------
# COPY . .

# # Normalize line endings on our entry script (in case committed from Windows)
# RUN dos2unix wait-for-db.sh || true

# # Change directory to where package.json is located for npm install
# WORKDIR /app/theme/static_src
# RUN npm install || true

# # Change back to the main app directory for Django commands
# WORKDIR /app

# # --- FIX FOR SECRET_KEY ERROR STARTS HERE ---
# # Set a dummy SECRET_KEY for Django manage.py commands during the build phase.
# # This value is only used during the Docker build and will be overridden by
# # Render's environment variable at runtime.
# ENV DJANGO_SECRET_KEY_BUILD="a_dummy_secret_key_for_docker_build_only_replace_this_with_a_real_one_in_render_env"

# # Tailwind build (if you use django-tailwind or similar; safe to ignore failure)
# # Pass the dummy SECRET_KEY for the build commands
# RUN DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY_BUILD python manage.py tailwind build || true

# # ---------- Static Assets ----------
# # Pass the dummy SECRET_KEY for the collectstatic command
# RUN DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY_BUILD python manage.py collectstatic --noinput || true
# # --- FIX FOR SECRET_KEY ERROR ENDS HERE ---

# # ---------- Port ----------
# EXPOSE 8000
# -------


# # ---------- Entrypoint ----------

# CMD ["./wait-for-db.sh", "gunicorn", "audio_converter.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
