from django import forms
from django.core.validators import RegexValidator

from .models import Report

class UserForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20, widget=forms.PasswordInput)
    phone = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', message="Enter a valid 10-digit phone number")]
    )
    place = forms.CharField(max_length=20)


class Citizen_login(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=20, widget=forms.PasswordInput)




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
