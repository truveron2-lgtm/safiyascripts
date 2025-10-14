from django.urls import path
from . import views

app_name = 'report'

urlpatterns = [
    path('dashboard/', views.report_dashboard, name='dashboard'),
]
