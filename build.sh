#!/bin/bash
echo "Building project..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
python3 manage.py migrate
