import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from documents.models import Asset, Beneficiary, AssetBeneficiary
from documents.serializers import AssetUploadSerializer, AssetListSerializer
from nlp_engine.hybrid import final_classification
from django.contrib.auth.models import User

logger = logging.getLogger('documents.views')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_asset(request):
    serializer = AssetUploadSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    asset = serializer.save(user=request.user)
    text_to_analyze = asset.title
    if asset.content:
        text_to_analyze += ' ' + asset.content
    try:
        nlp_result = final_classification(text_to_analyze)
        asset.sensitivity_level = nlp_result['level']
        asset.nlp_score = nlp_result['final_score']
        asset.nlp_analyzed = True
        asset.save()
    except Exception as e:
        logger.error(f'NLP failed for asset {asset.asset_id}: {e}')
    return Response(AssetUploadSerializer(asset, context={'request': request}).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_assets(request):
    assets = Asset.objects.filter(user=request.user, deleted_at__isnull=True)
    asset_type = request.query_params.get('type')
    privacy = request.query_params.get('privacy')
    sensitivity = request.query_params.get('sensitivity')
    if asset_type:
        assets = assets.filter(asset_type=asset_type)
    if privacy:
        assets = assets.filter(privacy_level=privacy)
    if sensitivity:
        assets = assets.filter(sensitivity_level=sensitivity)
    serializer = AssetListSerializer(assets, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_asset(request, asset_id):
    try:
        asset = Asset.objects.get(asset_id=asset_id, user=request.user, deleted_at__isnull=True)
    except Asset.DoesNotExist:
        return Response({"error": "Asset not found."}, status=status.HTTP_404_NOT_FOUND)
    return Response(AssetUploadSerializer(asset, context={'request': request}).data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_asset(request, asset_id):
    try:
        asset = Asset.objects.get(asset_id=asset_id, user=request.user, deleted_at__isnull=True)
    except Asset.DoesNotExist:
        return Response({"error": "Asset not found."}, status=status.HTTP_404_NOT_FOUND)
    from django.utils import timezone
    asset.deleted_at = timezone.now()
    asset.save()
    return Response({"message": "Asset deleted successfully."}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_death_certificate(request):
    return Response({
        "status": "not_activated",
        "message": "Death certificate upload via Absher is not yet activated.",
        "code": "ABSHER_NOT_ACTIVATED"
    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_beneficiary(request):
    name = request.data.get('name')
    email = request.data.get('email')
    phone = request.data.get('phone')
    relationship = request.data.get('relationship', 'other')
    if not name or not email:
        return Response({"error": "name and email are required."}, status=status.HTTP_400_BAD_REQUEST)
    beneficiary = Beneficiary.objects.create(
        user=request.user,
        name=name,
        email=email,
        phone=phone,
        relationship=relationship
    )
    return Response({
        "status": "success",
        "message": f"Beneficiary added successfully.",
        "beneficiary_id": beneficiary.id,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_asset_to_beneficiary(request):
    asset_id = request.data.get('asset_id')
    beneficiary_id = request.data.get('beneficiary_id')
    if not asset_id or not beneficiary_id:
        return Response({"error": "asset_id and beneficiary_id are required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        asset = Asset.objects.get(asset_id=asset_id, user=request.user)
    except Asset.DoesNotExist:
        return Response({"error": "Asset not found."}, status=status.HTTP_404_NOT_FOUND)
    try:
        beneficiary = Beneficiary.objects.get(id=beneficiary_id, user=request.user)
    except Beneficiary.DoesNotExist:
        return Response({"error": "Beneficiary not found."}, status=status.HTTP_404_NOT_FOUND)
    assignment, created = AssetBeneficiary.objects.get_or_create(asset=asset, beneficiary=beneficiary)
    if not created:
        return Response({"message": "Asset already assigned to this beneficiary."}, status=status.HTTP_200_OK)
    asset.posthumous_action = 'transfer'
    asset.save()
    return Response({"status": "success", "message": f"Asset assigned successfully."}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def beneficiary_verify(request):
    access_code = request.data.get('access_code')
    if not access_code:
        return Response({"error": "access_code is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        beneficiary = Beneficiary.objects.get(access_code=access_code)
    except Beneficiary.DoesNotExist:
        return Response({"error": "Invalid access code."}, status=status.HTTP_404_NOT_FOUND)
    try:
        verification = beneficiary.user.death_verification
        if verification.status != 'confirmed':
            return Response({"error": "Access not yet available."}, status=status.HTTP_403_FORBIDDEN)
    except Exception:
        return Response({"error": "No death verification found."}, status=status.HTTP_403_FORBIDDEN)
    assigned = AssetBeneficiary.objects.filter(beneficiary=beneficiary).select_related('asset')
    assets = []
    for ab in assigned:
        asset = ab.asset
        if asset.deleted_at is None:
            assets.append({
                'asset_id':   str(asset.asset_id),
                'title':      asset.title,
                'asset_type': asset.asset_type,
                'description': asset.description,
            })
    return Response({
        "status":           "verified",
        "beneficiary_name": beneficiary.name,
        "deceased_name":    beneficiary.user.get_full_name() or beneficiary.user.username,
        "assets":           assets,
        "message":          "Identity verified. You may now access your assets."
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def beneficiary_get_asset(request):
    import boto3
    from django.conf import settings
    access_code = request.data.get('access_code')
    asset_id = request.data.get('asset_id')
    if not access_code or not asset_id:
        return Response({"error": "access_code and asset_id are required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        beneficiary = Beneficiary.objects.get(access_code=access_code)
    except Beneficiary.DoesNotExist:
        return Response({"error": "Invalid access code."}, status=status.HTTP_404_NOT_FOUND)
    try:
        assignment = AssetBeneficiary.objects.get(beneficiary=beneficiary, asset__asset_id=asset_id)
    except AssetBeneficiary.DoesNotExist:
        return Response({"error": "Asset not found or not assigned to you."}, status=status.HTTP_404_NOT_FOUND)
    asset = assignment.asset
    try:
        verification = beneficiary.user.death_verification
        if verification.status != 'confirmed':
            return Response({"error": "Access not yet available."}, status=status.HTTP_403_FORBIDDEN)
    except Exception:
        return Response({"error": "No death verification found."}, status=status.HTTP_403_FORBIDDEN)
    response_data = {
        'asset_id':   str(asset.asset_id),
        'title':      asset.title,
        'asset_type': asset.asset_type,
    }
    if asset.file:
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            signed_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': asset.file.name},
                ExpiresIn=86400
            )
            response_data['download_url'] = signed_url
            response_data['url_expires'] = '24 hours'
        except Exception as e:
            logger.error(f'Failed to generate signed URL: {e}')
            response_data['download_url'] = None
    elif asset.content:
        response_data['content'] = asset.content
    beneficiary.has_accessed = True
    beneficiary.save()
    return Response(response_data)
