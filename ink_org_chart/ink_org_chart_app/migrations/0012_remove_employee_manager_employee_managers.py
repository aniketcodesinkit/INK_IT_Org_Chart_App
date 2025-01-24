# Generated by Django 5.1.3 on 2025-01-23 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ink_org_chart_app', '0011_remove_employee_employee_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='manager',
        ),
        migrations.AddField(
            model_name='employee',
            name='managers',
            field=models.ManyToManyField(blank=True, related_name='subordinates', to='ink_org_chart_app.employee'),
        ),
    ]
