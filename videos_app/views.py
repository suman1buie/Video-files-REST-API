import os

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import VideoSerializer
from .models import Video
from .utils import uplod_video
from .const import MAX_SIZE_MB, MIN_SIZE_MB, MIN_VIDEO_DURATION_MINUTE, MAX_VIDEO_DURATION_MINUTE


class VideoUploadView(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            video_size = file.size
            max_video_size = MAX_SIZE_MB * 1024 * 1024
            min_video_size = MIN_SIZE_MB * 1024 * 1024
            
            if video_size > max_video_size or video_size < min_video_size:
                return Response({'error': f'Video size should be between {MIN_SIZE_MB}MB and {MAX_SIZE_MB}MB'}, status=status.HTTP_400_BAD_REQUEST)

            video_file_path, duration = uplod_video(file)
            
            if duration < MIN_VIDEO_DURATION_MINUTE * 60 and duration > MAX_VIDEO_DURATION_MINUTE * 60:
                os.remove(video_file_path)
                return Response({'error': f'Video duration should be between {MIN_VIDEO_DURATION_MINUTE} minutes and {MAX_VIDEO_DURATION_MINUTE} minutes'}, status=status.HTTP_400_BAD_REQUEST)
            
            video = Video.objects.create(
                video_title=request.data.get('title', 'Untitled'),
                file_url=video_file_path,
                video_size=video_size,
                video_duration=duration,
            )
            serializer = VideoSerializer(video)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            os.remove(video_file_path)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)