"""
Serializers for the users app
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Team, APIKey


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'plan', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password2', 'first_name', 'last_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model"""
    
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'owner', 'owner_email', 'members_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def get_members_count(self, obj):
        return obj.members.count()


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for APIKey model"""
    
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'permissions', 'last_used_at', 'created_at']
        read_only_fields = ['id', 'last_used_at', 'created_at']
