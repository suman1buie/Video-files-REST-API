from django.db import models
from django.utils import timezone


class Video(models.Model):
    video_title = models.CharField(max_length=255)
    file_url = models.CharField(max_length=250)
    video_size = models.PositiveIntegerField()
    video_duration = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return self.video_title


class SharedLink(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    expiry = models.DateTimeField()
    
    def __str__(self):
        return f"Link for {self.video.video_title} (expires at {self.expiry})"
    
    def is_expired(self):
        return timezone.now() > self.expiry