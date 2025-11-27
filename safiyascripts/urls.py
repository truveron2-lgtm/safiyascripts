"""
URL configuration for safiyascripts project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from .sitemaps import AutoSitemap
from .views import universal_detail


sitemaps = {
    'auto': AutoSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('account/', include('account.urls', namespace='account')),
    path('articles/', include(('articles.urls', 'articles'), namespace='articles')),
    path('books/', include('books.urls')),
    path('about/', include('about.urls')),
    path('faith/', include('faith.urls')),
    path('stats/', include('stats.urls')),
    path('report/', include('report.urls')),
    path('contact/', include('contact.urls')),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
       # Comments app
    path('comments/', include('comments.urls', namespace='comments')),  # <-- our new app
    path('newsletter/', include(('newsletter.urls', 'newsletter'), namespace='newsletter')),

    path("<str:model_name>/<int:pk>/", universal_detail, name="universal_detail"),
    path('backup/', include('backup.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)