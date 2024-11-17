from django.urls import path
from .views import VideoUploadView, VideoTrimView, LinkShareView, AccessSharedLinkView, VideoMergeView


urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload-api'),
    path('<int:pk>/trim/', VideoTrimView.as_view(), name='video-trim-api'),
    path('<int:pk>/share/', LinkShareView.as_view(), name='video-share-api'),
    path('<int:video_id>/share/<str:token>/', AccessSharedLinkView.as_view(), name='access-shared-link-api'),
    path('merge/', VideoMergeView.as_view(), name='video-merge-api'),
]