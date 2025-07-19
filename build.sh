#!/usr/bin/env bash
# Exit on error
set -o errexit


pip install -r requirements.txt

# Install Node.js (required for Tailwind CLI)
# curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
# apt-get install -y nodejs

# Install Node.js dependencies (e.g., Tailwind CSS)
npm install

# Compile Tailwind CSS
# npx tailwindcss -i ./src/input.css -o ./static/css/output.css --minify #just for test
# # python manage.py tailwind init #new
# python manage.py tailwind install #new
# # npx tailwindcss
# python manage.py tailwind install --no-package-lock #new
python manage.py tailwind build
# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate
