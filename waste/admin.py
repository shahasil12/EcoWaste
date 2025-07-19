from django.contrib import admin
from .models import Citizen, Company, Report
from .models import Bin

admin.site.register(Citizen)
admin.site.register(Company)
admin.site.register(Report)



@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'status', 'types')
    search_fields = ('name', 'address', 'types')
    list_filter = ('status',)
