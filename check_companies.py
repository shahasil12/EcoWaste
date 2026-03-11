import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecogreen.settings')
django.setup()

from waste.models import Company

companies = Company.objects.all()
for c in companies:
    print(f"ID: {c.id}, Name: '{c.name}', Password(hashed?): '{c.password}', Email: '{c.contact_email}'")
