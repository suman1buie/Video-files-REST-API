from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from videos_app.models import Video, SharedLink



class VideoModelTest(TestCase):
    
    def setUp(self):
        self.video = Video.objects.create(
            video_title="video title for test",
            file_url="http://aws-s3.com/video.mp4",
            video_size=1024 * 1024 * 6,
            video_duration=12.6
        )

    def test_video_creation(self):
        self.assertEqual(self.video.video_title, "video title for test")
        self.assertEqual(self.video.file_url, "http://aws-s3.com/video.mp4")
        self.assertEqual(self.video.video_size, 1024 * 1024 * 6)
        self.assertEqual(self.video.video_duration, 12.6)

    def test_video_str(self):
        self.assertEqual(str(self.video), "video title for test")


class SharedLinkModelTest(TestCase):

    def setUp(self):
        self.video = Video.objects.create(
            video_title="Test Video",
            file_url="http://s3.aws.com/video.mp4",
            video_size=1024 * 1024 * 10,
            video_duration=120.0
        )
        self.shared_link = SharedLink.objects.create(
            video=self.video,
            token="token2334##jjdj",
            expiry=timezone.now() + timedelta(days=1)
        )

    def test_shared_link_creation(self):
        self.assertEqual(self.shared_link.token, "token2334##jjdj")
        self.assertEqual(self.shared_link.video, self.video)
        self.assertGreater(self.shared_link.expiry, timezone.now())

    def test_is_expired_not_expired(self):
        self.assertFalse(self.shared_link.is_expired())

    def test_is_expired_expired(self):
        expired_link = SharedLink.objects.create(
            video=self.video,
            token="expired_token_123",
            expiry=timezone.now() - timedelta(days=1)
        )
        self.assertTrue(expired_link.is_expired())

    def test_shared_link_str(self):
        self.assertEqual(str(self.shared_link), "Link for Test Video (expires at {})".format(self.shared_link.expiry))
