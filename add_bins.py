import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecogreen.settings')
django.setup()

from waste.models import Bin

bins_data = [
    {
        "name": "Central Park Bin",
        "latitude": 9.9312,
        "longitude": 76.2673,
        "address": "Marine Drive, Kochi",
        "status": "Available",
        "types": "Plastic, Paper, Metal"
    },
    {
        "name": "Tech Hub Bin",
        "latitude": 10.0261,
        "longitude": 76.3086,
        "address": "Infopark, Kakkanad",
        "status": "Available",
        "types": "E-waste, Metal"
    },
    {
        "name": "Market Square Bin",
        "latitude": 9.9760,
        "longitude": 76.2861,
        "address": "Broadway, Ernakulam",
        "status": "Full",
        "types": "Organic, Plastic"
    },
    {
        "name": "Metro Station Bin",
        "latitude": 10.0104,
        "longitude": 76.3134,
        "address": "Edappally Metro Station",
        "status": "Available",
        "types": "Plastic, Paper"
    }
]

for b_data in bins_data:
    Bin.objects.get_or_create(
        name=b_data["name"],
        defaults={
            "latitude": b_data["latitude"],
            "longitude": b_data["longitude"],
            "address": b_data["address"],
            "status": b_data["status"],
            "types": b_data["types"]
        }
    )

print(f"Successfully added {len(bins_data)} sample bins.")
