from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/')
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

