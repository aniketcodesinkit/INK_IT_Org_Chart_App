from django.db import models

class Employee(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Intern', 'Intern'),
    ]

    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    manager = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='subordinates'
    )
    office_location = models.CharField(max_length=100)
    employment_type = models.CharField(
        max_length=20, 
        choices=EMPLOYMENT_TYPE_CHOICES, 
        default='Full-time'
    )
    image = models.ImageField(upload_to='employee_images/', null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.title})"

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
