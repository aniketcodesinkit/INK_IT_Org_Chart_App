# Generated by Django 5.1.3 on 2024-12-11 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ink_org_chart_app', '0009_employee_employee_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='employee_id',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
