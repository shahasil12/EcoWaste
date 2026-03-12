import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecogreen.settings')
django.setup()

User = get_user_model()
username = 'shahasil'
email = 'shahasil@example.com' # Placeholder
password = 'admin'

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser {username}...")
    User.objects.create_superuser(username, email, password)
    print("Superuser created successfully.")
else:
    print(f"Superuser {username} already exists.")
