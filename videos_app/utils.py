import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from django.utils.crypto import get_random_string
from django.conf import settings


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
