from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from videos_app.models import Video
from django.conf import settings


class TestVideoUploadView(APITestCase):
    def setUp(self):
        self.upload_url = '/api/v1.0/videos/upload/'
        dummy_content = b"a" * (6 * 1024 * 1024)
        self.valid_video = SimpleUploadedFile(
            "test_video.mp4", dummy_content, content_type="video/mp4"
        )
        self.max_video_size = 50
        self.min_video_size = 5
        self.min_duration = 1
        self.max_duration = 25

    @patch('videos_app.views.MAX_SIZE_MB', 50)
    @patch('videos_app.views.MIN_SIZE_MB', 5)
    @patch('videos_app.views.MIN_VIDEO_DURATION_MINUTE', 1)
    @patch('videos_app.views.MAX_VIDEO_DURATION_MINUTE', 10)
    @patch('videos_app.views.uplod_video')
    def test_video_upload_success(self, mock_uplod_video):
        mock_uplod_video.return_value = {"error": "", "duration" : 300, 'file_path' : "/path/to/video.mp4"}
        response = self.client.post(
            self.upload_url,
            {'file': self.valid_video, 'title': 'Test Video'},
            format='multipart',
            HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}'
        )
           
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('file_url', response.data)
        self.assertEqual(Video.objects.count(), 1)

    @patch('videos_app.views.uplod_video')
    def test_no_file_uploaded(self, mock_uplod_video):
        response = self.client.post(self.upload_url, {}, format='multipart', HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'No file uploaded')
        self.assertEqual(Video.objects.count(), 0)

    @patch('videos_app.views.uplod_video')
    def test_video_file_too_large(self, mock_uplod_video):
        large_video = SimpleUploadedFile(
            "large_video.mp4",
            b"a" * (self.max_video_size * 1024 * 1024 + 1),
            content_type="video/mp4"
        )
        response = self.client.post(self.upload_url, {'file': large_video}, format='multipart', HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Video size should be between', response.data['error'])
        self.assertEqual(Video.objects.count(), 0)


    @patch('videos_app.views.uplod_video')
    def test_upload_exception_handling(self, mock_uplod_video):
        mock_uplod_video.side_effect = Exception("Mocked upload error")

        response = self.client.post(
            self.upload_url,
            {'file': self.valid_video, 'title': 'Test Video'},
            format='multipart',
            HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Mocked upload error')
        self.assertEqual(Video.objects.count(), 0)

    @patch('videos_app.views.uplod_video')
    def test_upload_exception_handling(self, mock_uplod_video):
        mock_uplod_video.side_effect = Exception("Mocked upload error")

        wrong_format = SimpleUploadedFile(
            "large_video.mp3",
            b"a" * (6 * 1024 * 1024),
            content_type="video/mp4"
        )
        
        response = self.client.post(
            self.upload_url,
            {'file': wrong_format, 'title': 'not a video file'},
            format='multipart',
            HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid file format')
        self.assertEqual(Video.objects.count(), 0)