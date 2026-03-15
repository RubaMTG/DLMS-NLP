from rest_framework import serializers
from documents.models import Asset


class AssetUploadSerializer(serializers.ModelSerializer):
    """
    Used when uploading a new asset.
    The user field is set automatically from the logged-in user.
    """

    # Show the file URL in responses (read only)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model  = Asset
        fields = [
            'asset_id',
            'title',
            'description',
            'asset_type',
            'file',
            'file_url',
            'content',
            'privacy_level',
            'posthumous_action',
            'sensitivity_level',
            'nlp_score',
            'nlp_analyzed',
            'created_at',
            'updated_at',
        ]
        # These fields are set automatically — user can't change them
        read_only_fields = [
            'asset_id',
            'sensitivity_level',
            'nlp_score',
            'nlp_analyzed',
            'created_at',
            'updated_at',
        ]

    def get_file_url(self, obj):
        """Returns the full S3 URL of the uploaded file."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class AssetListSerializer(serializers.ModelSerializer):
    """
    Used when listing assets — lighter version without file content.
    """
    file_url = serializers.SerializerMethodField()

    class Meta:
        model  = Asset
        fields = [
            'asset_id',
            'title',
            'asset_type',
            'file_url',
            'privacy_level',
            'posthumous_action',
            'sensitivity_level',
            'nlp_score',
            'created_at',
        ]

    def get_file_url(self, obj):
        if obj.file:
            return obj.file.url
        return None