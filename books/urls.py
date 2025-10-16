from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('manage/', views.book_table_list, name='book_table_list'),
    path('add/', views.add_book, name='add_book'),
    path('edit/<int:pk>/', views.edit_book, name='edit_book'),
    path('delete/<int:pk>/', views.delete_book, name='delete_book'),
]
