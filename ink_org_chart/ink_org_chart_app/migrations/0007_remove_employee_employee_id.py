# Generated by Django 5.1.3 on 2024-12-03 03:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ink_org_chart_app', '0006_employee_employee_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='employee_id',
        ),
    ]
