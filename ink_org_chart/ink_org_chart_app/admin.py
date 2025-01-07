from django.contrib import admin
from .models import Employee
from .models import Certification
# Register your models here.

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'manager', 'office_location', 'employment_type')
    search_fields = ('name', 'title', 'manager__name', 'office_location')
    list_filter = ('employment_type', 'office_location')

admin.site.register(Employee, EmployeeAdmin)

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )  # Update fields as per your model
    search_fields = ('name',)
    list_filter = ('name',)