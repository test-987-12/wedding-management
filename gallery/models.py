from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from weddings.models import Wedding

class MediaCategory(models.Model):
    """Categories for organizing media files"""
    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE, related_name='media_categories')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Media Categories"

    def __str__(self):
        return f"{self.name} - {self.wedding}"

class Media(models.Model):
    """Media model for photos and videos"""
    MEDIA_TYPES = (
        ('photo', 'Photo'),
        ('video', 'Video'),
    )

    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE, related_name='media')
    category = models.ForeignKey(MediaCategory, on_delete=models.SET_NULL, related_name='media_items', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='photo')
    file = models.FileField(upload_to='wedding_media/')
    thumbnail = models.ImageField(upload_to='wedding_media/thumbnails/', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_media')
    is_featured = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Media"

    def __str__(self):
        return f"{self.title} - {self.wedding}"

    @property
    def is_photo(self):
        return self.media_type == 'photo'

    @property
    def is_video(self):
        return self.media_type == 'video'

class MediaComment(models.Model):
    """Comments on media items"""
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.media.title} by {self.user.username}"

class MediaLike(models.Model):
    """Likes on media items"""
    media = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('media', 'user')

    def __str__(self):
        return f"Like on {self.media.title} by {self.user.username}"
