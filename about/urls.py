from django.urls import path
from . import views

app_name = 'about'

urlpatterns = [
    path('', views.about_public, name='about_public'),  # Public page
    path('edit/', views.about_edit, name='about_edit'), # Admin edit
]
