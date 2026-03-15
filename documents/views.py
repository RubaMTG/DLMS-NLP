import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from documents.models import Asset
from documents.serializers import AssetUploadSerializer, AssetListSerializer
from nlp_engine.hybrid import final_classification

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_asset(request):
    """
    Upload a new digital asset.

    POST /api/documents/upload/

    Form data:
        title            : string (required)
        description      : string (optional)
        asset_type       : document | image | video | note |
                           financial | social | other
        file             : the actual file (optional)
        content          : text content (optional, for notes)
        privacy_level    : LOW | MEDIUM | HIGH
        posthumous_action: delete | transfer

    Returns the created asset with its S3 URL and NLP results.
    """

    serializer = AssetUploadSerializer(
        data=request.data,
        context={'request': request}
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # Save the asset — assign to logged-in user
    asset = serializer.save(user=request.user)

    # ── Run NLP Analysis ──────────────────────────────────────────
    # Analyze the title + content for sensitivity
    text_to_analyze = asset.title
    if asset.content:
        text_to_analyze += " " + asset.content

    try:
        nlp_result = final_classification(text_to_analyze)

        # Update asset with NLP results
        asset.sensitivity_level = nlp_result['level']
        asset.nlp_score         = nlp_result['final_score']
        asset.nlp_analyzed      = True
        asset.save()

        logger.info(
            f"[upload] NLP analysis complete for asset "
            f"{asset.asset_id} | "
            f"level: {nlp_result['level']} | "
            f"score: {nlp_result['final_score']:.2f}"
        )

    except Exception as e:
        logger.error(
            f"[upload] NLP analysis failed for asset "
            f"{asset.asset_id}: {e}"
        )

    # ── Return Response ───────────────────────────────────────────
    return Response(
        AssetUploadSerializer(
            asset,
            context={'request': request}
        ).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_assets(request):
    """
    List all assets belonging to the logged-in user.

    GET /api/documents/

    Optional query params:
        ?type=document    filter by asset_type
        ?privacy=HIGH     filter by privacy_level
        ?sensitivity=HIGH filter by sensitivity_level
    """

    assets = Asset.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    )

    # Apply filters if provided
    asset_type  = request.query_params.get('type')
    privacy     = request.query_params.get('privacy')
    sensitivity = request.query_params.get('sensitivity')

    if asset_type:
        assets = assets.filter(asset_type=asset_type)
    if privacy:
        assets = assets.filter(privacy_level=privacy)
    if sensitivity:
        assets = assets.filter(sensitivity_level=sensitivity)

    serializer = AssetListSerializer(
        assets,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_asset(request, asset_id):
    """
    Get a single asset by ID.

    GET /api/documents/<asset_id>/
    """

    try:
        asset = Asset.objects.get(
            asset_id=asset_id,
            user=request.user,
            deleted_at__isnull=True
        )
    except Asset.DoesNotExist:
        return Response(
            {"error": "Asset not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = AssetUploadSerializer(
        asset,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_asset(request, asset_id):
    """
    Soft delete an asset (marks deleted_at, doesn't remove from S3).

    DELETE /api/documents/<asset_id>/delete/
    """

    try:
        asset = Asset.objects.get(
            asset_id=asset_id,
            user=request.user,
            deleted_at__isnull=True
        )
    except Asset.DoesNotExist:
        return Response(
            {"error": "Asset not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    from django.utils import timezone
    asset.deleted_at = timezone.now()
    asset.save()

    logger.info(
        f"[delete] Asset {asset_id} soft deleted "
        f"by user {request.user.username}"
    )

    return Response(
        {"message": "Asset deleted successfully."},
        status=status.HTTP_200_OK
    )