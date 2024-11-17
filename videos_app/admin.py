from django.contrib import admin
from .models import Video, SharedLink, VideoProcessingJob



admin.site.register(Video)
admin.site.register(SharedLink)
admin.site.register(VideoProcessingJob)
