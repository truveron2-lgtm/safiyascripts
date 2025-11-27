# backup/urls.py
from django.urls import path
from . import views

app_name = 'backup'

urlpatterns = [
    path('', views.backup_restore_home, name='backup_home'),
    # Note: backup and restore are POST endpoints triggered from the same form in the template.
    path('backup/', views.backup_view, name='backup'),
    path('restore/', views.restore_view, name='restore'),
]
