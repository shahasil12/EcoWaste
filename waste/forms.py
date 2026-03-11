from django import forms
from django.core.validators import RegexValidator

from .models import Report

class UserForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'id': 'regUsername'}))
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={'id': 'regPassword'}))
    phone = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', message="Enter a valid 10-digit phone number")],
        widget=forms.TextInput(attrs={'id': 'regPhone'})
    )
    place = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'id': 'regPlace'}))


class Citizen_login(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'id': 'loginUsername'}))
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={'id': 'loginPassword'}))




class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'place',
            'latitude',
            'longitude',
            'waste_type',
            'fee',
            'image',
        ]
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }



class CompanyLoginForm(forms.Form):
    name = forms.CharField(label="Company Name", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

from .models import PickupRequest, Company

class PickupRequestForm(forms.ModelForm):
    preferred_company = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=False,
        empty_label="-- Any Available Company --",
        label="Preferred Company",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = PickupRequest
        fields = ['waste_type', 'address', 'latitude', 'longitude', 'pickup_date', 'preferred_company']
        widgets = {
            'pickup_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'waste_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class WorkerLoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)
