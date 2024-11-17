from django.db import models


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
        return f"Link for {self.video.title} (expires at {self.expiry})"


class VideoProcessingJob(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    video = models.ForeignKey('Video', on_delete=models.CASCADE, related_name='processing_jobs')
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.video.title} - {self.status}"