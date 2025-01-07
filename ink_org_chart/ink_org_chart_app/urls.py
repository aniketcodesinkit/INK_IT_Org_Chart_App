from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from . import views
from .views import (
    RegisterUserApiView, LoginUserApiView, LogoutUserApiView, 
    EmployeeListApiView, AddEmployeeApiView, EditEmployeeApiView, 
    DeleteEmployeeApiView, OrgChartApiView, GenerateShareableLink, public_org_chart_view
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', views.login_user, name='login'),  
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('index/', views.index, name='index'),
    path('employee_list/', views.employee_list, name='employee_list'), 
    path('add/', views.add_employee, name='add_employee'),
    path('list/', views.employee_list, name='employee_list'),
    path('edit/<int:pk>/', views.edit_employee, name='edit_employee'),
    path('delete/<int:pk>/', views.delete_employee, name='delete_employee'),
    path('employee/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('project_list/', views.project_list, name='project_list'),  # List all projects
    path('project_detail/<int:project_id>/', views.project_detail, name='project_detail'),  # View project details
    path('project/create/', views.create_project, name='create_project'),  # Create project
    path('edit_project/<int:project_id>/', views.edit_project, name='edit_project'),  # Edit project
    path('project/delete/<int:project_id>/', views.delete_project, name='delete_project'),  # Delete project
    path('get_project_employees/<int:project_id>/', views.get_project_employees, name='get_project_employees'),
    path('create_project/', views.create_project, name='create_project'),
    path('org_chart/', views.org_chart, name='org_chart'),
    path('api/register/', RegisterUserApiView.as_view(), name='api-register'),
    path('api/login/', LoginUserApiView.as_view(), name='api-login'),
    path('api/logout/', LogoutUserApiView.as_view(), name='api-logout'),
    path('api/employee_list/', EmployeeListApiView.as_view(), name='api-employee-list'),
    path('api/add_employee/', AddEmployeeApiView.as_view(), name='api-add-employee'),
    path('api/edit_employee/<int:pk>/', EditEmployeeApiView.as_view(), name='api-edit-employee'),
    path('api/delete_employee/<int:pk>/', DeleteEmployeeApiView.as_view(), name='api-delete-employee'),
    path('api/org_chart/', OrgChartApiView.as_view(), name='api-org-chart'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/generate_shareable_link/', GenerateShareableLink.as_view(), name='generate_shareable_link'),
    path('public/org_chart/<uuid:token>/', public_org_chart_view, name='public_org_chart'),
    
]
