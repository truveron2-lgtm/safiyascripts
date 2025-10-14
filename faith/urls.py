from django.urls import path
from . import views

app_name = 'faith'

urlpatterns = [
    path('', views.faith_public, name='faith_public'),          # Public page
    path('add/', views.faith_add, name='faith_add'),           # Admin add
    path('list/', views.faith_list, name='faith_list'),        # Admin list
    path('<int:pk>/delete/', views.faith_delete, name='faith_delete'),  # Admin delete
    path('<int:pk>/edit/', views.faith_edit, name='faith_edit'),

]
