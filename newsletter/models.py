from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Newsletter(models.Model):
    title = models.CharField(max_length=200, default="Streams of Faith")
    volume = models.PositiveIntegerField(default=1)
    month = models.CharField(max_length=20, blank=True)
    publish_date = models.DateField(default=timezone.now)
    main_content = models.TextField(help_text="Main writeup of the month (plain text or HTML)")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-publish_date']

    def save(self, *args, **kwargs):
        if not self.month:
            self.month = timezone.now().strftime('%B')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - Volume {self.volume} ({self.month})"


class NewsletterSection(models.Model):
    newsletter = models.ForeignKey(
        Newsletter,
        related_name='sections',
        on_delete=models.CASCADE
    )
    heading = models.CharField(
        max_length=200,
        blank=True,  # optional
        null=True,
        help_text="Optional section heading"
    )
    content = models.TextField(
        blank=True,
        help_text="You can use HTML here or plain text"
    )
    image = models.ImageField(
        upload_to='newsletter_images/',
        blank=True,
        null=True
    )
    link = models.URLField(
        blank=True,
        null=True,
        help_text="Optional link at the bottom of the section"
    )
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.heading if self.heading else f"Section {self.order}"
