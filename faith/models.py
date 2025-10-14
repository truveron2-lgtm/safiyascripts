from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class FaithText(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
