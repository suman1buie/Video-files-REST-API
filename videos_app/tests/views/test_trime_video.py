from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from videos_app.models import Video
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

class TestVideoTrimView(APITestCase):
    def setUp(self):
        self.video = Video.objects.create(
            video_title="Test Video",
            video_size=10 * 1024 * 1024,
            video_duration=30,
            file_url="test_video.mp4"
        )
        self.trim_url = f'/api/v1.0/videos/{self.video.pk}/trim/'

    @patch('videos_app.views.trim_video')
    def test_video_trim_success(self, mock_trim_video):
        mock_trim_video.return_value = True, "/path/to/trimmed_video.mp4"
        
        response = self.client.post(
            self.trim_url,
            {'start': 6, 'end': 12},
            format='json',
            HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Video trimmed successfully')
        self.assertEqual(response.data['trimmed_video'], '/path/to/trimmed_video.mp4')

    def test_video_not_found(self):
        invalid_url = '/api/v1.0/videos/999/trim/'
        response = self.client.post(invalid_url, {'start': 60, 'end': 120}, format='json',HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Video not found')

    @patch('videos_app.views.trim_video')
    def test_invalid_start_time(self, mock_trim_video):
        mock_trim_video.return_value = False, "End time is too short"
        
        response = self.client.post(
            self.trim_url,
            {'start': 10, 'end': 120},
            format='json',
            HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "End time is too short")

    @patch('videos_app.views.trim_video')
    def test_video_trim_unexpected_error(self, mock_trim_video):
        res, mock_trim_video.side_effect = False, Exception("Unexpected error during trimming")

        response = self.client.post(
            self.trim_url,
            {'start': 60, 'end': 120},
            format='json',
            HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Unexpected error during trimming')

