from django.urls import path
from documents import views

urlpatterns = [
    # List all assets for logged-in user
    path('', views.list_assets, name='list_assets'),

    # Upload a new asset
    path('upload/', views.upload_asset, name='upload_asset'),

    # Get a single asset
    path('<uuid:asset_id>/', views.get_asset, name='get_asset'),

    # Delete an asset
    path('<uuid:asset_id>/delete/', views.delete_asset, name='delete_asset'),
]