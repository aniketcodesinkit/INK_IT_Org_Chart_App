# serializers.py
from rest_framework import serializers
from .models import Employee
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

# Serializer for user registration
class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'password': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


# Serializer for login 
class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)




class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'title', 'office_location', 'employment_type', 'manager', 'image']
        depth = 1  # To include manager details in a nested way if needed



class AddEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['name', 'title', 'manager', 'office_location', 'employment_type', 'image']  # Define the fields you want as parameters

