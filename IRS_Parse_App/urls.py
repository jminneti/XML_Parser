from django.urls import path

from . import views

urlpatterns = [
    path('', views.IRS_Parse_App_View, name='IRS_Parse_App_URL'),
    path('parse/', views.parse_View, name='parse_URL'),
    path('validation/', views.validation_View, name='validation_URL'),
    
]