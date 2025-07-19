from django.db import models
from django.contrib import admin

class Citizen(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=30)
    place = models.CharField(max_length=20)

class Company(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100,null=True)
    address = models.CharField(max_length=200)
    contact_email = models.EmailField()

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


class Bin(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=200)
    status = models.CharField(max_length=30, choices=[('Available', 'Available'), ('Full', 'Full')])
    types = models.CharField(max_length=200)  

    def __str__(self):
        return self.name
