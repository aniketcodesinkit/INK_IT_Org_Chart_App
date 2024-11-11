from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
import logging
logger = logging.getLogger(__name__)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import UserSerializer, EmployeeSerializer, AddEmployeeSerializer
from rest_framework.schemas import AutoSchema

# Home page (index)
@login_required
def index(request):
    return render(request, 'ink_org_chart_app/index.html')

def register_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'User already exists. Please login.')
                return redirect('login')
            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                messages.success(request, 'Account created successfully. Please login.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

    return render(request, 'ink_org_chart_app/register.html')


def login_user(request):
    if request.method == 'GET':
        # Clear existing messages on GET request to avoid showing unwanted messages
        storage = messages.get_messages(request)
        storage.used = True  # This will mark all messages as read/used

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('index')  # Redirect to index after login
        else:
            messages.error(request, 'Invalid username or password.')
            return redirect('login')

    return render(request, 'ink_org_chart_app/login.html')  # Render the login page


def logout_user(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

# Add Employee
def add_employee(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        title = request.POST.get('title')
        manager_id = request.POST.get('manager')
        office_location = request.POST.get('office_location')
        employment_type = request.POST.get('employment_type')
        
        # Handle image upload with request.FILES
        image = request.FILES.get('image')  # Changed from request.POST to request.FILES

        # Get the manager if selected, otherwise set None
        manager = Employee.objects.get(id=manager_id) if manager_id else None
        
        # Create a new employee with the provided data
        Employee.objects.create(
            name=name,
            title=title,
            manager=manager,
            office_location=office_location,
            employment_type=employment_type,
            image=image  # Save the uploaded image
        )
        
        # Redirect to the employee list page after successful creation
        return redirect('employee_list')

    # If GET request, render the form with the list of employees to select manager
    employees = Employee.objects.all()  # To list managers in the dropdown
    return render(request, 'ink_org_chart_app/add_employee.html', {'employees': employees})

# Employee list
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'ink_org_chart_app/employee_list.html', {'employees': employees})

# Edit employee
def edit_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee.name = request.POST.get('name')
        employee.title = request.POST.get('title')
        manager_id = request.POST.get('manager')
        employee.office_location = request.POST.get('office_location')
        employee.employment_type = request.POST.get('employment_type')
        employee.image = request.POST.get('image')

        if 'image' in request.FILES:
            employee.image = request.FILES['image']
        
        if manager_id:
            employee.manager = Employee.objects.get(id=manager_id)
        else:
            employee.manager = None

        employee.save()
        return redirect('employee_list')
    
    employees = Employee.objects.all()
    return render(request, 'ink_org_chart_app/edit_employee.html', {'employee': employee, 'employees': employees})

# Delete employee
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    return redirect('employee_list')

# Function to build the hierarchy recursively
def build_hierarchy(employee):
    """Recursively build the hierarchy of employees."""
    subordinates = employee.subordinates.all()  # Fetch subordinates (those who report to the current employee)

    return {
        'name': employee.name,
        'title': employee.title,
        'office_location': employee.office_location,
        'employment_type': employee.employment_type,
        'image': employee.image.url if employee.image else '',  # Use image URL if available, otherwise empty
        'children': [build_hierarchy(subordinate) for subordinate in subordinates]  # Recursively fetch subordinates
    }

def org_chart(request):
    """Fetch and structure employee data into a hierarchy for the org chart."""
    # Get the root employee(s) who do not have a manager (usually CEO, etc.)
    root_employees = Employee.objects.filter(manager__isnull=True)

    # Build hierarchy for each root employee
    data = [build_hierarchy(employee) for employee in root_employees]

    # Pass hierarchical data to the template, serialized to JSON
    return render(request, 'ink_org_chart_app/org_chart.html', {'data': json.dumps(data)})


# ---------------------------------- Swagger API -----------------------------------------

# Register User API
class RegisterUserApiView(APIView):
    permission_classes = [AllowAny]
    schema = AutoSchema()

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            if User.objects.filter(username=username).exists():
                return Response({'error': 'User already exists. Please login.'}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create_user(username=username, password=password)
            return Response({'success': 'Account created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login User API
class LoginUserApiView(APIView):
    permission_classes = [AllowAny]
    schema = AutoSchema()

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return Response({'success': 'Login successful'}, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Employee List API
class EmployeeListApiView(APIView):
    permission_classes = [IsAuthenticated]
    schema = AutoSchema()

    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)
    
# Logout User API
class LogoutUserApiView(APIView):
    permission_classes = [IsAuthenticated]
    schema = AutoSchema()

    def post(self, request):
        logout(request)
        return Response({'info': 'You have been logged out'}, status=status.HTTP_200_OK)


# Add Employee API
class AddEmployeeApiView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=AddEmployeeSerializer,
        responses={201: AddEmployeeSerializer, 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = AddEmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Edit Employee API
class EditEmployeeApiView(APIView):
    permission_classes = [IsAuthenticated]
    schema = AutoSchema()

    @swagger_auto_schema(
        request_body=EmployeeSerializer,
        responses={201: EmployeeSerializer, 400: 'Bad Request'}
    )

    def put(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'Employee updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Employee API
class DeleteEmployeeApiView(APIView):
    permission_classes = [IsAuthenticated]
    schema = AutoSchema()

    def delete(self, request, pk):
        employee = get_object_or_404(Employee, pk=pk)
        employee.delete()
        return Response({'success': 'Employee deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# Organization Chart API
class OrgChartApiView(APIView):
    permission_classes = [IsAuthenticated]
    schema = AutoSchema()

    def get(self, request):
        root_employees = Employee.objects.filter(manager__isnull=True)
        data = [self.build_hierarchy(employee) for employee in root_employees]
        return Response(data)

    def build_hierarchy(self, employee):
        subordinates = employee.subordinates.all()
        return {
            'name': employee.name,
            'title': employee.title,
            'office_location': employee.office_location,
            'employment_type': employee.employment_type,
            'image': employee.image.url if employee.image else '',
            'children': [self.build_hierarchy(subordinate) for subordinate in subordinates]
        }
