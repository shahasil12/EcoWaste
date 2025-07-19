from django.urls import path
from . import views  

urlpatterns = [
    path('', views.home, name='home'),
    path('citizen',views.citizen,name='citizen'),
    path('register_user',views.register_user,name='register_user'),
    path('citizen_login',views.citizen_login,name='citizen_login'),
    path('citizen_home',views.citizen_home,name='citizen_home'),
    path('report/', views.report_waste, name='report_waste'),
    path('citizen_report/',views.citizen_report,name='citizen_report'),
    path('citizen/logout/', views.citizen_logout, name='citizen_logout'),
    path('citizen/profile/', views.citizen_profile, name='citizen_profile'),
   path('company_dashboard/<int:company_id>/', views.company_dashboard, name='company_dashboard'),
   path('company_login/', views.company_login, name='company_login'),
   path('company/resolve_report/<int:report_id>/', views.company_resolve_report, name='company_resolve_report'),
   path('company/logout/', views.company_logout, name='company_logout'),
   path('company/forgot-password/', views.company_forgot_password, name='company_forgot_password'),
   path('company/reset-password/', views.company_reset_password, name='company_reset_password'),
   path('bins-json/', views.bins_json, name='bins-json'),
]   
