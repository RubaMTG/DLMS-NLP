from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from users.models import UserProfile


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'message': 'User registered successfully.',
        'token': token.key,
        'username': user.username,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'message': 'Login successful.',
        'token': token.key,
        'username': user.username,
        'status': user.profile.account_status,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
        'account_status': user.profile.account_status,
        'phone': user.profile.phone,
        'national_id': user.profile.national_id,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    })
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_nlp_preference(request):
    enabled = request.data.get('enabled', False)
    request.user.profile.nlp_classification_enabled = enabled
    request.user.profile.save()
    return Response({
        'message': 'NLP preference saved.',
        'nlp_classification_enabled': enabled
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_nlp_preference(request):
    enabled = request.user.profile.nlp_classification_enabled
    return Response({
        'nlp_classification_enabled': enabled
    })