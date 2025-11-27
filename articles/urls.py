from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('home-summary/', views.article_summary_home, name='article_summary_home'),
    path('', views.article_list, name='article_list'),
    path('<int:pk>/', views.article_detail, name='article_detail'),
    path('create/', views.article_create, name='article_create'),
    path('<int:pk>/edit/', views.article_edit, name='article_edit'),
    path('<int:pk>/delete/', views.article_delete, name='article_delete'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('subscribers/', views.subscribers_list, name='subscribers_list'),
    path("article/<int:pk>/regen-audio/", views.regenerate_audio, name="regenerate_audio"),
    path('subscribers/add/', views.add_subscriber, name='add_subscriber'),
    path('subscribers/<int:pk>/delete/', views.delete_subscriber, name='delete_subscriber'),




    # ✅ Public pages
    path('public/', views.article_list_public, name='article_list_public'),
    path('public/<int:pk>/', views.article_detail_public, name='article_detail_public'),

        # ✅ Subscription
    path('subscribe/', views.subscribe, name='subscribe'),
    path('<int:pk>/reply/', views.admin_reply_comment, name='admin_reply_comment'),


]
