import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from django.utils.crypto import get_random_string


def uplod_video(file):
    """
    Uploads a video file to the server and returns the video duration.

    """
    video_name = file._name.split('.')[0] + get_random_string(10)
    video_file_path = os.path.join('videos', f'{video_name}.mp4')
    
    with open(video_file_path, 'wb') as temp_file:
        for chunk in file.chunks():
                temp_file.write(chunk)            

    clip = VideoFileClip(video_file_path)
    duration = clip.duration
    
    return video_file_path, duration
