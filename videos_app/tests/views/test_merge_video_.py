from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
from videos_app.models import Video
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings


class TestVideoMergeView(APITestCase):
    def setUp(self):
        from videos_app.views import merge_multiple_videos
        self.video_1 = Video.objects.create(
            video_title="Video 1",
            video_size=10 * 1024 * 1024,
            video_duration=300,
            file_url="video_1.mp4"
        )
        self.video_2 = Video.objects.create(
            video_title="Video 2",
            video_size=10 * 1024 * 1024,
            video_duration=200,
            file_url="video_2.mp4"
        )
        self.merge_url = '/api/v1.0/videos/merge/'

    @patch('videos_app.views.merge_multiple_videos')
    def test_video_merge_success(self, mock_merge_multiple_videos):
        mock_merge_multiple_videos.return_value = Video.objects.create(
            video_title="Merged Video",
            video_size=20 * 1024 * 1024,
            video_duration=500,
            file_url="merged_video.mp4"
        )
        
        response = self.client.post(
            self.merge_url,
            {'video_ids': [self.video_1.pk, self.video_2.pk], 'video_title': 'Merged Video'},
            format='json',
            HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('video_title', response.data)
        self.assertEqual(response.data['video_title'], 'Merged Video')
        self.assertEqual(response.data['file_url'], 'merged_video.mp4')

    def test_not_enough_videos(self):
        response = self.client.post(
            self.merge_url,
            {'video_ids': [self.video_1.pk]},
            format='json',
            HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'At least two videos are required to merge.')

    def test_some_videos_not_found(self):
        response = self.client.post(
            self.merge_url,
            {'video_ids': [self.video_1.pk, 999], 'video_title': 'Merged Video'},
            format='json',
            HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}'
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Some videos do not exist.')

    @patch('videos_app.views.merge_multiple_videos')
    def test_failed_to_merge_videos(self, mock_merge_multiple_videos):
        mock_merge_multiple_videos.return_value = None
        
        response = self.client.post(
            self.merge_url,
            {'video_ids': [self.video_1.pk, self.video_2.pk], 'video_title': 'Merged Video'},
            format='json',
            HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Failed to merge the videos.')

    @patch('videos_app.views.merge_multiple_videos')
    def test_general_exception(self, mock_merge_multiple_videos):
        mock_merge_multiple_videos.side_effect = Exception("Unexpected error during merging")
        
        response = self.client.post(
            self.merge_url,
            {'video_ids': [self.video_1.pk, self.video_2.pk], 'video_title': 'Merged Video'},
            format='json',
            HTTP_AUTHORIZATION=f'Token {settings.API_TOKEN}'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Unexpected error during merging')

