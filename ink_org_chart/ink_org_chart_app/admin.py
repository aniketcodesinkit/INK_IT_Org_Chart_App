from django.contrib import admin
from .models import Employee
from .models import Certification
# Register your models here.

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'get_managers', 'office_location', 'employment_type')
    search_fields = ('name', 'title', 'managers__name', 'office_location')
    list_filter = ('employment_type', 'office_location')

    # Custom method to display managers
    def get_managers(self, obj):
        return ", ".join([manager.name for manager in obj.managers.all()])
    get_managers.short_description = 'Managers'

admin.site.register(Employee, EmployeeAdmin)

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )  # Update fields as per your model
    search_fields = ('name',)
    list_filter = ('name',)