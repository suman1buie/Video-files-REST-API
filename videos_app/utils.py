import os
import hashlib
from django.core.files.base import ContentFile
from moviepy.editor import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from django.utils.crypto import get_random_string
from django.conf import settings
from datetime import timedelta, datetime
from .models import Video


def generate_token(video_id):
    random_string = get_random_string(length=32)
    token = hashlib.sha256(f"{video_id}{random_string}".encode('utf-8')).hexdigest()
    return token


def uplod_video(file):
    """
    Uploads a video file to the server and returns the video duration.

    """
    video_name = file._name.split('.')[0] + get_random_string(10)
    video_file_path = os.path.join(settings.MEDIA_ROOT, f'{video_name}.mp4')
    
    with open(video_file_path, 'wb') as temp_file:
        for chunk in file.chunks():
                temp_file.write(chunk)            

    clip = VideoFileClip(video_file_path)
    duration = clip.duration
    
    return video_file_path, duration


def trim_video(video, start_time, end_time):
    """
    Trims a video file from the given start time to the end time and save theb video object with new file path.

    """
    video_file_path = video.file_url
    video_file_name = video_file_path.split('/')[-1]
    clip = VideoFileClip(video_file_path).subclip(start_time, end_time)
    trimmed_path = f"{settings.MEDIA_ROOT}/trimmed_{video_file_name}"
    clip.write_videofile(trimmed_path, codec="libx264")
    
    os.remove(video.file_url)
    video.file_url = trimmed_path
    video.save()
    
    return trimmed_path


def merge_multiple_videos(videos, merged_video_title):
    """
    Merges multiple video files into a single video file.

    """
    try:
        clips = []

        for video in videos:
            clip = VideoFileClip(video.file_url)
            clips.append(clip)

        merged_clip = concatenate_videoclips(clips, method="compose")

        merged_path = f"{settings.MEDIA_ROOT}/merge_video_{get_random_string(length=10)}.mp4"
        merged_clip.write_videofile(merged_path, codec="libx264")
        breakpoint()
        merged_video = Video.objects.create(
            video_title=merged_video_title,
            file_url=merged_path,
            video_size=os.path.getsize(merged_path),
            video_duration=merged_clip.duration,
        )
        
        for video in videos:
            os.remove(video.file_url)
            video.delete()

        return merged_video
        
    except Exception as e:
        print(f"Error merging videos: {str(e)}")
        return None