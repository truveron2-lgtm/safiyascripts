from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('', views.new_comments_list, name='new_comments_list'),
]
