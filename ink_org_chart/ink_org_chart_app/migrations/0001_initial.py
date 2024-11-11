# Generated by Django 5.1.1 on 2024-10-21 05:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=100)),
                ('office_location', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to='employee_images/')),
                ('date_of_joining', models.DateField(blank=True, null=True)),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subordinates', to='ink_org_chart_app.employee')),
            ],
        ),
    ]
