#!/usr/bin/env bash
# Build script for Render deployment

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput --clear

echo "Build completed successfully!"