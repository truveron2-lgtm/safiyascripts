from django.urls import path
from . import views

app_name = 'stats'

urlpatterns = [
    path('dashboard/', views.stats_dashboard, name='dashboard'),
]
