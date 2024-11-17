from rest_framework import serializers
from .models import Video, SharedLink


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'file', 'size', 'duration', 'uploaded_at']


class SharedLinkSerializer(serializers.ModelSerializer):
    video_title = serializers.ReadOnlyField(source='video.title')

    class Meta:
        model = SharedLink
        fields = ['id', 'video', 'video_title', 'token', 'expiry']
