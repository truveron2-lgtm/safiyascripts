from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    path('create/', views.create_newsletter, name='create_newsletter'),
    path('<int:newsletter_id>/sections/', views.add_sections, name='add_sections'),
    path('<int:newsletter_id>/preview/', views.preview_newsletter, name='preview_newsletter'),
    path('<int:newsletter_id>/send/', views.send_newsletter, name='send_newsletter'),
    path('<int:newsletter_id>/start-send/', views.start_send_background, name='start_send_background'),
    path('<int:newsletter_id>/send-progress/', views.sending_progress, name='sending_progress'),
    path('<int:newsletter_id>/sent/', views.sent_confirmation, name='sent_confirmation'),
]
