from django.contrib import admin
from django.urls import path, include


v1 = "v1.0"

urlpatterns = [
    path('admin/', admin.site.urls),
    path(f'api/{v1}/videos/', include('videos_app.urls')),
]
