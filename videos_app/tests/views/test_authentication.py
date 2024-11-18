from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from videos_app.models import Video

class TestVideoUploadView(APITestCase):
    @patch('videos_app.views.uplod_video')
    def test_video_upload_success(self, mock_uplod_video):
        mock_uplod_video.return_value = ("/path/to/video.mp4", 300)
        response = self.client.post(
            "/api/v1.0/videos/upload/",
            {'file': "", 'title': 'Test Video'},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        

    @patch('videos_app.views.uplod_video')
    def test_no_file_uploaded(self, mock_uplod_video):
        response = self.client.post("/api/v1.0/videos/upload/", {}, format='multipart', HTTP_AUTHORIZATION=f'Token judhd')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)