# ---------- Base Image ----------
FROM python:3.12-slim

# Python runtime env
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---------- System Dependencies ----------
# Install postgresql-client, nodejs, npm, and other dependencies
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

# Normalize line endings for scripts
RUN dos2unix wait-for-db.sh || true

# ---------- Tailwind Setup ----------
# Run npm install in the theme directory where package.json exists
WORKDIR /app/theme
RUN npm install || true
RUN python /app/manage.py tailwind build || true

# ---------- Static Assets ----------
WORKDIR /app
RUN python manage.py collectstatic --noinput

# ---------- Port ----------
EXPOSE 8000

# ---------- Entrypoint ----------
CMD ["./wait-for-db.sh", "gunicorn", "audio_converter.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
