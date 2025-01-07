from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Project

from .models import Certification
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
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now, timedelta
from .models import SharedLink
from django.http import JsonResponse,  HttpResponseForbidden


# Home page (index)
# @login_required
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
        # employee_id = request.POST.get('employee_id')
        name = request.POST.get('name')
        title = request.POST.get('title')
        manager_id = request.POST.get('manager')
        office_location = request.POST.get('office_location')
        employment_type = request.POST.get('employment_type')
        job_description = request.POST.get('job_description')
        department = request.POST.get('department')
        date_of_joining = request.POST.get('date_of_joining')

        # Handle image upload
        image = request.FILES.get('image')

        # Handle resume/CV upload
        resume = request.FILES.get('resume')

        # Get the manager if selected, otherwise set to None
        manager = Employee.objects.get(id=manager_id) if manager_id else None

        # Create the employee object
        employee = Employee.objects.create(
            # employee_id = employee_id,
            name=name,
            title=title,
            manager=manager,
            office_location=office_location,
            employment_type=employment_type,
            image=image,
            resume=resume,
            job_description=job_description,
            department=department,
            date_of_joining=date_of_joining 
        )

        # Handle certifications
        certifications = request.POST.getlist('certifications[]')  # Handle multiple certifications
        if certifications:
            for cert_name in certifications:
                if cert_name.strip():  # Avoid empty certifications
                    Certification.objects.create(employee=employee, name=cert_name.strip())

        # Redirect to the employee list page after successful creation
        return redirect('employee_list')

    # For GET requests, render the form with the list of employees to select the manager
    employees = Employee.objects.all()
    return render(request, 'ink_org_chart_app/add_employee.html', {'employees': employees})

# Edit Employee
def edit_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee.employee_id = request.POST.get('employee_id')
        employee.name = request.POST.get('name')
        employee.title = request.POST.get('title')
        manager_id = request.POST.get('manager')
        employee.office_location = request.POST.get('office_location')
        employee.employment_type = request.POST.get('employment_type')
        employee.job_description = request.POST.get('job_description')
        employee.department = request.POST.get('department')
        
        # Update image and cv files if provided
        if 'image' in request.FILES:
            employee.image = request.FILES['image']
        if 'cv' in request.FILES:
            employee.cv = request.FILES['cv']
        
        # Set the manager if provided, otherwise set None
        if manager_id:
            employee.manager = Employee.objects.get(id=manager_id)
        else:
            employee.manager = None

        employee.save()

        # Handle certifications: Delete existing certifications and add new ones
        employee.certifications.all().delete()  # Clear all existing certifications
        certifications = request.POST.getlist('certifications[]')  # Handle multiple certifications
        if certifications:
            for cert_name in certifications:
                if cert_name.strip():  # Avoid empty certifications
                    Certification.objects.create(employee=employee, name=cert_name.strip())

        # Redirect to the employee list page after successful update
        return redirect('employee_list')
    
    employees = Employee.objects.all()
    return render(request, 'ink_org_chart_app/edit_employee.html', {'employee': employee, 'employees': employees})

# Delete Employee
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.delete()
    return redirect('employee_list')

# Employee list view
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'ink_org_chart_app/employee_list.html', {'employees': employees})

# Function to build the hierarchy recursively
def build_hierarchy(employee):
    """Recursively build the hierarchy of employees."""
    subordinates = employee.subordinates.all()  # Fetch subordinates (those who report to the current employee)

    return {
        "id": employee.id,
        'name': employee.name,
        'title': employee.title,
        'office_location': employee.office_location,
        'employment_type': employee.employment_type,
        "manager": employee.manager.name if employee.manager else None,
        'image': employee.image.url if employee.image else '',  # Use image URL if available, otherwise empty
        'children': [build_hierarchy(subordinate) for subordinate in subordinates]  # Recursively fetch subordinates
    }

def create_project(request):
    """
    Handle the creation of a new project.
    """
    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        employee_ids = request.POST.getlist('employees')

        if name:  # Validate project name
            project = Project.objects.create(name=name, description=description)
            project.employees.set(employee_ids)
            return redirect('project_list')

    all_employees = Employee.objects.all()
    return render(request, 'ink_org_chart_app/create_project.html', {
        'all_employees': all_employees
    })

def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    all_employees = Employee.objects.all()
    assigned_employees = project.employees.all()

    if request.method == "POST":
        name = request.POST.get('name')
        description = request.POST.get('description')
        employee_ids = request.POST.getlist('employees')

        if name:
            project.name = name
            project.description = description
            project.employees.set(employee_ids)
            project.save()
            return redirect('project_list')

    return render(request, 'ink_org_chart_app/edit_project.html', {
        'project': project,
        'all_employees': all_employees,
        'assigned_employees': assigned_employees,
    })

def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        project.delete()
        return redirect('project_list')

# Project List Page
def project_list(request):
    """
    Display all projects with a search filter.
    """
    search_query = request.GET.get('q', '')  # Search query from GET parameters
    projects = Project.objects.all()

    if search_query:
        projects = projects.filter(name__icontains=search_query)  # Filter projects by name

    return render(request, 'ink_org_chart_app/project_list.html', {
        'projects': projects,
        'search_query': search_query
    })

# Project Detail Page
def project_detail(request, project_id):
    """
    Display details of a specific project and its employees.
    """
    project = get_object_or_404(Project, id=project_id)
    employees = project.employees.all()

    return render(request, 'ink_org_chart_app/project_detail.html', {
        'project': project,
        'employees': employees
    })

def get_project_employees(request, project_id):
    """
    Returns the employees associated with the selected project in JSON format.
    """
    project = get_object_or_404(Project, id=project_id)
    employees = project.employees.all()

    # Serialize employees data
    data = {
        'employees': [
            {
                'name': emp.name,
                'title': emp.title,
                'department': emp.department,
                'image_url': emp.image.url if emp.image else '',  # Handle missing image
            }
            for emp in employees
        ]
    }
    return JsonResponse(data)

def org_chart(request):
    # Fetch all unique departments
    departments = Employee.objects.values_list('department', flat=True).distinct()

    # Get the selected department from the request (default to 'all')
    selected_department = request.GET.get('department', 'all')

    # Filter employees based on the selected department
    if selected_department == 'all':
        employees = Employee.objects.all()
    else:
        employees = Employee.objects.filter(department=selected_department)

    # Process data into the hierarchical structure
    employees_data = []
    for emp in employees:
        employees_data.append({
            'id': emp.id,
            'name': emp.name,
            'title': emp.title,
            'manager_id': emp.manager_id,
            'image': emp.image.url if emp.image and hasattr(emp.image, 'url') else None,
            'department': emp.department,
            'department': emp.department,
            "office_location": emp.office_location 
        })

    # Build hierarchical JSON data for the org chart
    def build_hierarchy(employee_list, manager_id=None):
        hierarchy = []
        for emp in employee_list:
            if emp['manager_id'] == manager_id:
                children = build_hierarchy(employee_list, emp['id'])
                hierarchy.append({**emp, 'children': children})
        return hierarchy

    org_chart_data = build_hierarchy(employees_data)

    return render(request, 'ink_org_chart_app/org_chart.html', {
        'data': json.dumps(org_chart_data),  # Pass as JSON to the template
        'departments': departments,
        'selected_department': selected_department,
    })

# Employee Detail View
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    certifications = employee.certifications.all()  # Fetch all certifications for the employee
    return render(request, 'ink_org_chart_app/employee_detail.html', {'employee': employee, 'certifications': certifications})

def public_org_chart_view(request, token):
    # Find the shared link
    shared_link = get_object_or_404(SharedLink, token=token)

    # Validate the link
    if not shared_link.is_valid():
        return HttpResponseForbidden("This link is expired or invalid.")
    
    # Render the org chart (minimal view)
    return render(request, 'ink_org_chart_app/org_chart_public.html', {"org_chart_data": shared_link.shared_data})


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
                # Generate refresh and access tokens
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Employee List API
class EmployeeListApiView(APIView):
    permission_classes = [IsAuthenticated]
    schema = AutoSchema()

    @swagger_auto_schema(
        operation_description="Get list of employees (requires Bearer Token)",
        responses={200: "List of employees"},
        security=[{'Bearer': []}], # Link the Bearer Token
        
    )
    
    def get(self, request):
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)
    
# Logout User API
class LogoutUserApiView(APIView):
    permission_classes = [IsAuthenticated]
    schema = AutoSchema()

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the refresh token
            return Response({"info": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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


class GenerateShareableLink(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Set expiration time for the link (e.g., 1 hour from now)
        expiration_time = now() + timedelta(hours=1)
        
        # Create a new shared link
        shared_link = SharedLink.objects.create(
            expires_at=expiration_time,
            shared_data={},  # Optionally, pass specific org chart data
        )
        
        # Generate the link
        shareable_url = f"{request.scheme}://{request.get_host()}/public/org_chart/{shared_link.token}/"
        
        return JsonResponse({
            "success": True,
            "shareable_url": shareable_url,
            "expires_at": shared_link.expires_at,
        })