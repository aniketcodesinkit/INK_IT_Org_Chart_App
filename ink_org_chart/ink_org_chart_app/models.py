from __future__ import annotations
from django.db import models
from django.utils.timezone import now
import uuid

class Certification(models.Model):
       employee = models.ForeignKey('Employee', related_name='certifications', on_delete=models.CASCADE)
       name = models.CharField(max_length=200)
       issued_by = models.CharField(max_length=200, null=True, blank=True)
       issue_date = models.DateField(null=True, blank=True)

class Employee(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Intern', 'Intern'),
    ]

    # employee_id = models.CharField(max_length=20, unique=True)
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

    # certifications = models.TextField(null=True, blank=True)
    job_description = models.TextField(null=True, blank=True)
    resume = models.FileField(upload_to='employee_resumes/', null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)

   
    def __str__(self):
        return f"{self.name} ({self.title})"

    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    employees = models.ManyToManyField(Employee, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SharedLink(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    shared_data = models.JSONField()  # Store org chart data or a reference to it
    
    def is_valid(self):
        return self.is_active and self.expires_at > now()