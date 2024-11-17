import os
import boto3
import hashlib
from django.core.files.base import ContentFile
from moviepy.editor import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from django.utils.crypto import get_random_string
from django.conf import settings
from datetime import timedelta, datetime
from dotenv import load_dotenv

from .models import Video


def generate_token(video_id):
    random_string = get_random_string(length=32)
    token = hashlib.sha256(f"{video_id}{random_string}".encode('utf-8')).hexdigest()
    return token


def uplod_video(file):
    """
    Uploads a video file to the server and returns the video duration.

    """
    try:
        video_name = file._name.split('.')[0] + get_random_string(10)
        video_file_path = f'{video_name}.mp4'
        res, file_url = upload_video_to_s3(file, video_file_path)
        
        clip = VideoFileClip(file_url)
        duration = clip.duration
        clip.close()
        
        if res:
            return file_url, duration
        
        return "", 0
    except Exception as e:
        return "", 0


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


def upload_video_to_s3(file, file_path):
    if file_path == '':
        return False, 'No selected file'
    try:
        load_dotenv()
        s3_client = boto3.client(
            's3',
            region_name=os.getenv('S3_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
        )
        s3_client.upload_fileobj(
            file.file,
            os.getenv('S3_BUCKET'),
            file_path,
        )
        file_url = f"https://{os.getenv('S3_BUCKET')}.s3.{os.getenv('S3_REGION')}.amazonaws.com/{file_path}"
        return True, file_url
    except Exception as e:
        return False, str(e)


def generate_presigned_url(bucket_name, key, expiration=3600):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=expiration
    )