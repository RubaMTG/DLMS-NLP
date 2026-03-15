content = open('documents/views.py', 'r', encoding='utf-8').read()

content = content.replace(
    "@api_view(['POST'])\ndef beneficiary_verify(request):",
    "@api_view(['POST'])\n@permission_classes([AllowAny])\ndef beneficiary_verify(request):"
)

content = content.replace(
    "@api_view(['POST'])\ndef beneficiary_get_asset(request):",
    "@api_view(['POST'])\n@permission_classes([AllowAny])\ndef beneficiary_get_asset(request):"
)

with open('documents/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done!')