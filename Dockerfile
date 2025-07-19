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


# COPY package*.json ./
RUN npm install || true
# RUN npm run build || true


# ---------- Port ----------
EXPOSE 8000

# ---------- Entrypoint ----------
CMD ["./wait-for-db.sh", "gunicorn", "audio_converter.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
