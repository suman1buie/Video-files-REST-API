import os
import boto3
import tempfile
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
        res, s3_file_url = upload_video_to_s3(file, video_file_path)
        
        sign_url =generate_presigned_url(os.getenv('S3_BUCKET'), video_file_path)
        clip = VideoFileClip(sign_url)
        duration = clip.duration
        clip.close()
        
        if res:
            return video_file_path, duration
        
        return "", 0
    except Exception as e:
        return "", 0


def trim_video(video, start_time, end_time):
    """
    Trims a video file from the given start time to the end time and save theb video object with new file path.

    """
    try:
        video_file_path = video.file_url
        video_file_name = video_file_path.split('/')[-1]
        image_url = generate_presigned_url(os.getenv('S3_BUCKET'), video_file_name)
        if image_url:
            trimmed_clip = VideoFileClip(image_url)
            if trimmed_clip.duration < end_time:
                trimmed_clip.close()
                return False, "End time is too short"
        
            trimmed_clip = trimmed_clip.subclip(start_time, end_time)
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
                trimmed_clip.write_videofile(tmp_file.name, codec="libx264")
                tmp_file.seek(0)
                trimmed_data = tmp_file.read()
                size = os.path.getsize(tmp_file.name)
                duration = trimmed_clip.duration
                trimmed_path = f"trimmed_{video_file_name}"
                res, file_url = upload_video_to_s3(ContentFile(trimmed_data), trimmed_path)
                
                delete_video_file(os.getenv('S3_BUCKET'), video.file_url)
                video.file_url = trimmed_path
                trimmed_clip.close()
                video.video_size = size
                video.video_duration = duration
                video.save()
            
                return True, trimmed_path
            
        return False, "Unable to find video"
    except Exception as e:
        return False, str(e)


def merge_multiple_videos(videos, merged_video_title):
    """
    Merges multiple video files into a single video file.

    """
    try:
        clips = []

        for video in videos:
            video_file_name = video.file_url.split('/')[-1]
            video_sign_url = generate_presigned_url(os.getenv('S3_BUCKET'),video_file_name)
            clip = VideoFileClip(video_sign_url)
            clips.append(clip)

        merged_clip = concatenate_videoclips(clips, method="compose")
        
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
            merged_clip.write_videofile(tmp_file.name, codec="libx264")
            tmp_file.seek(0)
            merged_data = tmp_file.read()
            merged_path = f"merge_video_{get_random_string(length=10)}.mp4"
            res, file_url = upload_video_to_s3(ContentFile(merged_data), merged_path)
            size = os.path.getsize(tmp_file.name)
        
            merged_video = Video.objects.create(
                video_title=merged_video_title,
                file_url=merged_path,
                video_size=size,
                video_duration=merged_clip.duration,
            )
            merged_clip.close()
            for video in videos:
                delete_video_file(os.getenv('S3_BUCKET'), video.file_url)
                video.delete()

            return merged_video

        return None        
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
        s3_file_url = f"https://{os.getenv('S3_BUCKET')}.s3.{os.getenv('S3_REGION')}.amazonaws.com/{file_path}"
        return True, s3_file_url
    except Exception as e:
        return False, str(e)


def generate_presigned_url(bucket_name, key, expiration=3600):
    try:
        s3 = boto3.client(
            's3',
            region_name=os.getenv('S3_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
        )
        return s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=expiration
        )
    except Exception as e:
        return None


def delete_video_file(bucket_name, file_name):
    s3 = boto3.client(
        's3',
        region_name=os.getenv('S3_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
    )
    
    try:
        s3.delete_object(Bucket=bucket_name, Key=file_name)
        return True
    except Exception as e:
        return False