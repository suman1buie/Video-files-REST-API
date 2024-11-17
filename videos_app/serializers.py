from rest_framework import serializers
from .models import Video, SharedLink


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'video_title', 'file_url', 'video_size', 'video_duration', 'uploaded_at']


# class SharedLinkSerializer(serializers.ModelSerializer):
#     video_title = serializers.ReadOnlyField(source='video.title')
#     video = serializers.SerializerMethodField()
    
#     class Meta:
#         model = SharedLink
#         fields = ['id', 'video', 'video_title', 'token', 'expiry']

#     def get_video(self, obj):
#         return {
#             'id': obj.video.id,
#             'video_link': obj.video.file_url
#         }