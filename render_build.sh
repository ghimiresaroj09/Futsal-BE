#!/usr/bin/env bash
# Render build step. Runs on every deploy, before the start command.
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
