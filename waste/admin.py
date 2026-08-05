from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import Citizen, Company, Report, Bin, BinReport, Worker, PickupRequest, RecyclingCenter

@admin.register(Citizen)
class CitizenAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone', 'place', 'points')
    search_fields = ('username', 'phone', 'place')
    list_filter = ('place',)

    def save_model(self, request, obj, form, change):
        if obj.password and not obj.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_email', 'address')
    search_fields = ('name', 'contact_email')

    def save_model(self, request, obj, form, change):
        if obj.password and not obj.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reported_by', 'waste_type', 'status', 'place', 'assigned_company', 'created_at')
    search_fields = ('place', 'waste_type', 'status')
    list_filter = ('status', 'waste_type', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude', 'status', 'types', 'full_reports_count')
    search_fields = ('name', 'address', 'types')
    list_filter = ('status',)

@admin.register(BinReport)
class BinReportAdmin(admin.ModelAdmin):
    list_display = ('bin', 'reported_by', 'reported_at')
    list_filter = ('reported_at',)
    readonly_fields = ('reported_at',)

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone', 'vehicle_number')
    search_fields = ('username', 'phone', 'vehicle_number')

    def save_model(self, request, obj, form, change):
        if obj.password and not obj.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'citizen', 'waste_type', 'status', 'pickup_date', 'assigned_worker', 'preferred_company', 'created_at')
    list_filter = ('status', 'waste_type', 'pickup_date', 'created_at')
    search_fields = ('citizen__username', 'address')
    readonly_fields = ('created_at',)

@admin.register(RecyclingCenter)
class RecyclingCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude', 'accepted_waste_types', 'contact')
    search_fields = ('name', 'address', 'accepted_waste_types')
