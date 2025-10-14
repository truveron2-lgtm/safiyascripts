from django.db import models
from django.utils import timezone

class Visitor(models.Model):
    ip_address = models.GenericIPAddressField()
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.ip_address} - {self.country or 'Unknown'}"

class PageView(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='page_views')
    page_name = models.CharField(max_length=200)
    url = models.URLField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.page_name} visited by {self.visitor.ip_address}"
