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

    # ✅ Public pages
    path('public/', views.article_list_public, name='article_list_public'),
    path('public/<int:pk>/', views.article_detail_public, name='article_detail_public'),

        # ✅ Subscription
    path('subscribe/', views.subscribe, name='subscribe'),


]
