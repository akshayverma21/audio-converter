# ---------- Base Image ----------
FROM python:3.12-slim
# Python runtime env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---------- System Dependencies ----------
# postgresql-client for pg_isready; node & npm for tailwind; curl for diagnostics
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

# ---------- App Code ----------
COPY . .

# Normalize line endings on our entry script (in case committed from Windows)
RUN dos2unix wait-for-db.sh || true

# --- FIX FOR NPM INSTALL ERROR STARTS HERE ---
# Change directory to where package.json is located for npm install
WORKDIR /app/theme/static_src
RUN npm install || true
# --- FIX FOR NPM INSTALL ERROR ENDS HERE ---

# Change back to the main app directory for Django commands
WORKDIR /app

# Tailwind build (if you use django-tailwind or similar; safe to ignore failure)
# This command should run from /app, and it will look for the tailwind config in theme/static_src

# ---------- Static Assets ----------

# ---------- Port ----------
EXPOSE 8000

# # ---------- Entrypoint ----------
CMD ["/bin/bash", "-c", "echo 'CMD starting via bash -c'; ls -la /app/wait-for-db.sh; exec ./wait-for-db.sh \"$@\"", "bash", "gunicorn", "audio_converter.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
# CMD ["/bin/bash", "-c", "echo '!!! Render test: If you see this, basic container startup works !!!'; sleep 300"]
