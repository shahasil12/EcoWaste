import os
import django
from django.test import Client
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecogreen.settings')
django.setup()

from waste.models import Company

def verify_company_login():
    client = Client()
    # Test with one of the companies
    company_name = 'tata'
    password = 'tcs1234'
    
    print(f"Attempting login for company: {company_name}")
    response = client.post(reverse('company_login'), {'name': company_name, 'password': password})
    
    if response.status_code == 302:
        print("Login successful! Redirected as expected.")
        # Check if company_id is in session
        if client.session.get('company_id'):
            print(f"Company ID {client.session['company_id']} found in session.")
            return True
        else:
            print("Login failed: company_id not in session.")
            return False
    else:
        print(f"Login failed with status code: {response.status_code}")
        return False

if __name__ == "__main__":
    if verify_company_login():
        print("Verification PASSED")
    else:
        print("Verification FAILED")
        exit(1)
