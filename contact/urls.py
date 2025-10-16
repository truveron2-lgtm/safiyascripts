from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.contact_view, name='contact'),
    path('admin/list/', views.contact_list, name='contact_list'),
    path('admin/view/<int:pk>/', views.contact_detail, name='contact_detail'),
    path('admin/delete/<int:pk>/', views.contact_delete, name='contact_delete'),
]
