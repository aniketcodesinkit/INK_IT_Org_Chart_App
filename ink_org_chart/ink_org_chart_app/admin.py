from django.contrib import admin
from .models import Employee

# Register your models here.

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'manager', 'office_location', 'employment_type')
    search_fields = ('name', 'title', 'manager__name', 'office_location')
    list_filter = ('employment_type', 'office_location')

admin.site.register(Employee, EmployeeAdmin)

