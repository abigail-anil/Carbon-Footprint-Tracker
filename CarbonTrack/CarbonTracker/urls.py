from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculate_emission, name='calculate_emission'),
    path('delete_emission/', views.delete_emission, name='delete_emission'),
    path('reports/', views.emission_reports, name='emission_reports'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('settings/', views.settings_view, name='settings'),
]