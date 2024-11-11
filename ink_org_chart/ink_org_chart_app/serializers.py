# serializers.py
from rest_framework import serializers
from .models import Employee
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'title', 'office_location', 'employment_type', 'manager', 'image']
        depth = 1  # To include manager details in a nested way if needed



class AddEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['name', 'title', 'manager', 'office_location', 'employment_type', 'image']  # Define the fields you want as parameters
