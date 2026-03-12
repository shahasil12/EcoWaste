#!/bin/bash
set -e
echo "Building project..."
pip install -r requirements.txt --break-system-packages
python3 manage.py collectstatic --noinput --clear
python3 manage.py migrate
python3 create_superuser.py
