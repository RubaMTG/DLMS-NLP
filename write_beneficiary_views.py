content = open('documents/views.py', 'r', encoding='utf-8').read()

addition = '''


# ================================================================
# BENEFICIARY ACCESS PORTAL
# ================================================================

@api_view(['POST'])
def beneficiary_verify(request):
    """
    Step 1 of beneficiary access.
    Beneficiary enters their access code to verify identity.

    POST /api/documents/beneficiary/verify/

    Body:
        access_code : the code sent to beneficiary via email/SMS
    """
    from documents.models import Beneficiary

    access_code = request.data.get('access_code')

    if not access_code:
        return Response(
            {"error": "access_code is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Find beneficiary with this access code
    try:
        beneficiary = Beneficiary.objects.get(
            access_code=access_code
        )
    except Beneficiary.DoesNotExist:
        return Response(
            {"error": "Invalid access code."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check that death has been confirmed for this user
    try:
        verification = beneficiary.user.death_verification
        if verification.status != "confirmed":
            return Response(
                {
                    "error": "Access not yet available.",
                    "detail": "Death has not been confirmed yet."
                },
                status=status.HTTP_403_FORBIDDEN
            )
    except Exception:
        return Response(
            {"error": "No death verification found."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Return beneficiary info and their assigned assets
    from documents.models import AssetBeneficiary
    assigned = AssetBeneficiary.objects.filter(
        beneficiary=beneficiary
    ).select_related('asset')

    assets = []
    for ab in assigned:
        asset = ab.asset
        if asset.deleted_at is None:
            assets.append({
                'asset_id':    str(asset.asset_id),
                'title':       asset.title,
                'asset_type':  asset.asset_type,
                'description': asset.description,
            })

    return Response({
        "status":           "verified",
        "beneficiary_name": beneficiary.name,
        "deceased_name":    beneficiary.user.get_full_name()
                            or beneficiary.user.username,
        "assets":           assets,
        "message":          "Identity verified. You may now access your assets."
    })


@api_view(['POST'])
def beneficiary_get_asset(request):
    """
    Step 2 of beneficiary access.
    Beneficiary requests a download URL for a specific asset.

    POST /api/documents/beneficiary/asset/

    Body:
        access_code : the beneficiary access code
        asset_id    : UUID of the asset to download
    """
    from documents.models import Beneficiary, AssetBeneficiary
    import boto3
    from django.conf import settings

    access_code = request.data.get('access_code')
    asset_id    = request.data.get('asset_id')

    if not access_code or not asset_id:
        return Response(
            {"error": "access_code and asset_id are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify beneficiary
    try:
        beneficiary = Beneficiary.objects.get(access_code=access_code)
    except Beneficiary.DoesNotExist:
        return Response(
            {"error": "Invalid access code."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verify asset is assigned to this beneficiary
    try:
        assignment = AssetBeneficiary.objects.get(
            beneficiary=beneficiary,
            asset__asset_id=asset_id
        )
    except AssetBeneficiary.DoesNotExist:
        return Response(
            {"error": "Asset not found or not assigned to you."},
            status=status.HTTP_404_NOT_FOUND
        )

    asset = assignment.asset

    # Check death is confirmed
    try:
        verification = beneficiary.user.death_verification
        if verification.status != "confirmed":
            return Response(
                {"error": "Access not yet available."},
                status=status.HTTP_403_FORBIDDEN
            )
    except Exception:
        return Response(
            {"error": "No death verification found."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Generate signed S3 URL valid for 24 hours
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
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key':    asset.file.name,
                },
                ExpiresIn=86400   # 24 hours
            )
            response_data['download_url'] = signed_url
            response_data['url_expires']  = '24 hours'
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            response_data['download_url'] = None

    elif asset.content:
        response_data['content'] = asset.content

    # Mark beneficiary as having accessed
    beneficiary.has_accessed = True
    beneficiary.save()

    return Response(response_data)
'''

with open('documents/views.py', 'w', encoding='utf-8') as f:
    f.write(content + addition)

print('Done!')