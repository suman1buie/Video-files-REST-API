import os
from django.utils.crypto import get_random_string
from datetime import timedelta, datetime
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import VideoSerializer
from .models import Video, SharedLink
from .utils import uplod_video, trim_video, merge_multiple_videos, generate_token, generate_presigned_url, is_video_file
from .const import MAX_SIZE_MB, MIN_SIZE_MB, MIN_VIDEO_DURATION_MINUTE, MAX_VIDEO_DURATION_MINUTE
from video_api.urls import v1


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

            if not is_video_file(file._name):
                return Response({'error': 'Invalid file format'}, status=status.HTTP_400_BAD_REQUEST)
            
            video_file_path, duration = uplod_video(file)
            if video_file_path == '':
                return Response({'error': 'Failed to upload video'}, status=status.HTTP_400_BAD_REQUEST)
                
            if duration < MIN_VIDEO_DURATION_MINUTE * 60 and duration > MAX_VIDEO_DURATION_MINUTE * 60:
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
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

 
class VideoTrimView(APIView):
    def post(self, request, pk):
        try:
            video = Video.objects.get(pk=pk)
            start = float(request.data.get('start', 0))
            end = float(request.data.get('end', video.video_duration))
            resp, meesage = trim_video(video, start, end)
            if resp:
                return Response({'message': 'Video trimmed successfully', 'trimmed_video': meesage})
            else:
                return Response({'error': meesage}, status=status.HTTP_400_BAD_REQUEST)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LinkShareView(APIView):
    def post(self, request, pk):
        """Generate a shared link for a video"""
        try:
            video = Video.objects.get(pk=pk)
            token = generate_token(video.id)
            expiry_time = timezone.now() + timedelta(hours=1)

            shared_link = SharedLink.objects.create(
                video=video,
                token=token,
                expiry=expiry_time
            )

            link = f"{request.build_absolute_uri('/')[:-1]}/api/{v1}/videos/{video.id}/share/{token}/"
            return Response({
                "message": "Link generated successfully",
                "link": link,
                "expires_at": shared_link.expiry
            }, status=status.HTTP_201_CREATED)

        except Video.DoesNotExist:
            return Response({"error": "Video not found"}, status=status.HTTP_404_NOT_FOUND)
        

class AccessSharedLinkView(APIView):
    def get(self, request, video_id, token):
        try:
            shared_link = get_object_or_404(SharedLink, video_id=video_id, token=token)
            if shared_link.is_expired():
                return JsonResponse({"error": "This link has expired."}, status=status.HTTP_400_BAD_REQUEST)
            
            access_link = generate_presigned_url(os.getenv('S3_BUCKET'), shared_link.video.file_url, expiration=3600)
            
            return JsonResponse({
                "video_title": shared_link.video.video_title,
                "signed_video_url": access_link,
                "expires_at": shared_link.expiry
            })

        except SharedLink.DoesNotExist:
            return JsonResponse({"error": "Link not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VideoMergeView(APIView):
    def post(self, request):
        try:
            video_ids = request.data.get('video_ids', [])
            merged_video_title = request.data.get('video_title', "merged_video_title")
            
            if len(video_ids) < 2:
                return Response({"error": "At least two videos are required to merge."}, status=status.HTTP_400_BAD_REQUEST)

            videos = Video.objects.filter(id__in=video_ids)
            
            if len(videos) != len(video_ids):
                return Response({"error": "Some videos do not exist."}, status=status.HTTP_404_NOT_FOUND)

            merged_video = merge_multiple_videos(videos, merged_video_title)
            if merged_video:
                serializer = VideoSerializer(merged_video)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Failed to merge the videos."}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)