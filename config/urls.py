from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),

    # NLP engine endpoints (already existed)
    path('api/nlp/', include('nlp_engine.urls')),

    # Notification endpoints (newly added)
    # Gives us:
    #   /notifications/alive/<token>/
    #   /notifications/beneficiary/<id>/access/
    path('notifications/', include('notifications.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/nlp/', include('nlp_engine.urls')),
    path('notifications/', include('notifications.urls')),
    path('api/documents/', include('documents.urls')),  # ← ADD THIS
]
