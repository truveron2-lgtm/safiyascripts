from django.db import models

class AboutPage(models.Model):
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"About Page (Last updated: {self.last_updated.strftime('%Y-%m-%d')})"
