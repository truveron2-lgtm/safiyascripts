from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Article(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.TextField(max_length=300)
    full_description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='article_images/', blank=True, null=True)
    date_posted = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(Article, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.name} on {self.article}"

    def is_reply(self):
        return self.parent is not None


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)  # ✅ rename this
    def __str__(self):
        return self.email
