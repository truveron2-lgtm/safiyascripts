from django.apps import apps
from django.contrib.sitemaps import Sitemap
from django.contrib.sites.models import Site

class AutoSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        items = []
        excluded_apps = ["auth", "admin", "sessions", "contenttypes", "account"]  # exclude these
        for model in apps.get_models():
            if model._meta.app_label in excluded_apps:
                continue
            try:
                objs = model.objects.all()
                for obj in objs:
                    items.append((model, obj.pk))
            except:
                pass
        return items

    def location(self, item):
        model, pk = item
        # get the current site domain
        site = Site.objects.get_current()
        return f"https://{site.domain}/{model._meta.model_name}/{pk}/"
