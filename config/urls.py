from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/nlp/', include('nlp_engine.urls')),
    path('notifications/', include('notifications.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/users/', include('users.urls')),
]