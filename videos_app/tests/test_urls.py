from django.test import TestCase
from django.urls import reverse, resolve



class TestVideoProcessing(TestCase):
    
    def test_video_upload_url_is_resolved(self):
        from videos_app.views import VideoUploadView
        url = reverse('video-upload-api')
        self.assertEqual(resolve(url).func.view_class, VideoUploadView)
        

    def test_video_merge_url_is_resolved(self):
        from videos_app.views import VideoMergeView
        url = reverse('video-merge-api')
        self.assertEqual(resolve(url).func.view_class, VideoMergeView)
        
        
    def test_video_trim_url_is_resolved(self):
        from videos_app.views import VideoTrimView
        url = reverse('video-trim-api', args=[1])
        self.assertEqual(resolve(url).func.view_class, VideoTrimView)
        
        
    def test_share_url_is_resolved(self):
        from videos_app.views import LinkShareView
        url = reverse('video-share-api', args=[1])
        self.assertEqual(resolve(url).func.view_class, LinkShareView)
        

    def test_share_video_link_is_resolved(self):
        from videos_app.views import AccessSharedLinkView
        url = reverse('access-shared-link-api', args=[1,"_token"])
        self.assertEqual(resolve(url).func.view_class, AccessSharedLinkView)