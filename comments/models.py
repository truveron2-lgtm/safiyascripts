from django.db import models
from articles.models import Comment, Article
from django.contrib.auth.models import User

# Optional: You can create a proxy model to simplify admin queries
class NewComment(Comment):
    class Meta:
        proxy = True
        verbose_name = "New Comment"
        verbose_name_plural = "New Comments"
