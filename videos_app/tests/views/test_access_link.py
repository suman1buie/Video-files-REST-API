from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from videos_app.models import Video, SharedLink
from django.urls import reverse
from django.conf import settings
import json


class TestAccessSharedLinkView(APITestCase):
    
    def setUp(self):
        self.video = Video.objects.create(
            video_title="Test Video",
            video_size=10 * 1024 * 1024,
            video_duration=300,
            file_url="test_video.mp4"
        )
        
        self.shared_link = SharedLink.objects.create(
            video=self.video,
            token="valid_token",
            expiry="2024-12-31T23:59:59Z"
        )
        
        self.access_url = reverse('access-shared-link-api', args=[self.video.pk, self.shared_link.token])

    @patch('videos_app.views.generate_presigned_url')
    def test_access_shared_link_success(self, mock_generate_presigned_url):
        mock_generate_presigned_url.return_value = "https://s3.example.com/test_video.mp4?signature=xyz"
        
        response = self.client.get(self.access_url, HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response._container[0].decode('utf-8'))
        self.assertIn('video_title', data)
        self.assertEqual(data['video_title'], self.video.video_title)
        self.assertIn('signed_video_url', data)
        self.assertEqual(data['signed_video_url'], "https://s3.example.com/test_video.mp4?signature=xyz")
        self.assertIn('expires_at', data)
        self.assertEqual(data['expires_at'], self.shared_link.expiry)

    @patch('videos_app.views.generate_presigned_url')
    def test_expired_link(self, mock_generate_presigned_url):
        self.shared_link.expiry = "2020-12-31T23:59:59Z"
        self.shared_link.save()
        
        response = self.client.get(self.access_url, HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response._container[0].decode('utf-8'))
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'This link has expired.')

    def test_link_not_found(self):
        invalid_url = reverse('access-shared-link-api', args=[self.video.pk, "invalid_token"])
        response = self.client.get(invalid_url,  HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response._container[0].decode('utf-8'))
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'No SharedLink matches the given query.')

    @patch('videos_app.views.generate_presigned_url')
    def test_unexpected_error(self, mock_generate_presigned_url):
        mock_generate_presigned_url.side_effect = Exception("Unexpected error")
        response = self.client.get(self.access_url, HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = json.loads(response._container[0].decode('utf-8'))
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Unexpected error')
