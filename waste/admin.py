from django.contrib import admin
from .models import Citizen, Company, Report
from .models import Bin

admin.site.register(Citizen)
from django.contrib.auth.hashers import make_password

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'address')
    search_fields = ('name', 'contact_email')

    def save_model(self, request, obj, form, change):
        # Hash the password if it's provided and not already hashed
        if obj.password and not obj.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.register(Report)



@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'status', 'types')
    search_fields = ('name', 'address', 'types')
    list_filter = ('status',)

from .models import RecyclingCenter

@admin.register(RecyclingCenter)
class RecyclingCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'accepted_waste_types', 'contact')
    search_fields = ('name', 'address', 'accepted_waste_types')
