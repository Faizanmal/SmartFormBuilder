"""
API Views for users app
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Team, APIKey
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    TeamSerializer, APIKeySerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User operations"""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for Team operations"""
    
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Team.objects.filter(owner=self.request.user) | Team.objects.filter(members=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the team"""
        team = self.get_object()
        if team.owner != request.user:
            return Response(
                {'error': 'Only team owner can add members'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            team.members.add(user)
            return Response({'status': 'member added'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class APIKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for APIKey operations"""
    
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        import secrets
        import hashlib
        
        # Generate random API key
        key = f"ff_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        api_key = serializer.save(user=self.request.user, key_hash=key_hash)
        
        # Return the plain key only once
        return Response({
            'id': api_key.id,
            'name': api_key.name,
            'key': key,  # Only shown once!
            'permissions': api_key.permissions,
            'created_at': api_key.created_at
        }, status=status.HTTP_201_CREATED)
