import os
import django
from django.contrib.auth.hashers import make_password, is_password_usable

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecogreen.settings')
django.setup()

from waste.models import Company

def hash_existing_passwords():
    companies = Company.objects.all()
    count = 0
    for company in companies:
        if company.password and not company.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            print(f"Hashing password for company: {company.name}")
            company.password = make_password(company.password)
            company.save()
            count += 1
    print(f"Successfully hashed passwords for {count} companies.")

if __name__ == "__main__":
    hash_existing_passwords()
