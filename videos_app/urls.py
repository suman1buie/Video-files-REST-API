from django.urls import path
from .views import VideoUploadView, VideoTrimView


urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload-api'),
     path('<int:pk>/trim/', VideoTrimView.as_view(), name='video-trim-api')  
]