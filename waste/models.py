from django.db import models
from django.contrib import admin

class Citizen(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=30)
    place = models.CharField(max_length=20)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.username

class Company(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100,null=True)
    address = models.CharField(max_length=200)
    contact_email = models.EmailField()

    def __str__(self):
        return self.name

class Report(models.Model):
    reported_by = models.ForeignKey(Citizen, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now=True)
    place = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    WASTE_TYPE_CHOICES = [
        ('Plastic', 'Plastic'),
        ('Organic', 'Organic'),
        ('E-waste', 'E-waste'),
        ('Metal', 'Metal'),
        ('Glass', 'Glass'),
        ('Other', 'Other'),
    ]
    waste_type = models.CharField(max_length=100, choices=WASTE_TYPE_CHOICES)
    fee = models.IntegerField()
    image = models.ImageField(upload_to='waste_image/')
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        if self.reported_by:
            return f"Report by {self.reported_by.username} at {self.place}"
        return f"Report at {self.place}"


class Bin(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=200)
    status = models.CharField(max_length=30, choices=[('Available', 'Available'), ('Full', 'Full')])
    types = models.CharField(max_length=200)  

    def __str__(self):
        return self.name

class Worker(models.Model):
    # Added this now so we can use it in PickupRequest
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=30)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Worker: {self.username}"

class PickupRequest(models.Model):
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    WASTE_TYPE_CHOICES = [
        ('General', 'General'),
        ('Plastic', 'Plastic'),
        ('Organic', 'Organic'),
        ('E-waste', 'E-waste'),
        ('Metal', 'Metal'),
    ]
    waste_type = models.CharField(max_length=50, choices=WASTE_TYPE_CHOICES)
    address = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    pickup_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Assigned', 'Assigned'),
        ('Completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_worker = models.ForeignKey(Worker, null=True, blank=True, on_delete=models.SET_NULL)
    preferred_company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, related_name='pickup_requests')


class RecyclingCenter(models.Model):
    name = models.CharField(max_length=150)
    address = models.TextField()
    accepted_waste_types = models.CharField(max_length=200, help_text="e.g. Plastic, E-waste, Metal")
    contact = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name
