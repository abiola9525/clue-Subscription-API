from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.db.models import Q
from django.contrib.auth import authenticate
from account.backends import CustomAuthenticationBackend
from account.models import User

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get(self.username_field)
        password = attrs.get('password')
        
        if not email:
            raise serializers.ValidationError(
                {
                    'status': 'error',
                    'code': 'EMAIL_REQUIRED',
                    'message': 'Email is required.'
                }
            )
            
        if not password:
            raise serializers.ValidationError(
                {
                    'status': 'error',
                    'code': 'PASSWORD_REQUIRED',
                    'message': 'Password is required.'
                }
            )
        
        UserModel = User
        try:
            user_exists = UserModel.objects.filter(Q(email=email) | Q(phone=email)).exists()
            if not user_exists:
                raise serializers.ValidationError(
                    {
                        'status': 'error',
                        'code': 'USER_NOT_FOUND',
                        'message': 'No account found with this email/phone.'
                    }
                )
            
            user = self.user = authenticate(
                request=self.context.get('request'),
                username=email,  
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    {
                        'status': 'error',
                        'code': 'INVALID_CREDENTIALS',
                        'message': 'Incorrect password.'
                    }
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    {
                        'status': 'error',
                        'code': 'ACCOUNT_INACTIVE',
                        'message': 'This account is inactive or unverified.'
                    }
                )
            
            data = super().validate(attrs)
            
            user_info = {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'phone': user.phone,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
            }
            
            return {
                'status': 'success',
                'message': 'Login successful',
                'user': user_info,
                'access': data['access'],
                'refresh': data['refresh']
            }
            
        except UserModel.DoesNotExist:
            raise serializers.ValidationError(
                {
                    'status': 'error',
                    'code': 'USER_NOT_FOUND',
                    'message': 'No account found with this email/phone.'
                }
            )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "phone", "is_user", "is_active", "password"]
        read_only_fields = ["is_user", "is_active"]
        extra_kwargs = {
                    'password': {'write_only': True}
                }
        
    def create(self, validated_data):
        user = User.objects.create(
                    email=validated_data['email'],
                    full_name=validated_data['full_name'],
                    phone = validated_data['phone'],
                    is_user=True,
                    is_active=True,
                )
        
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    def get_fields(self):
        fields = super().get_fields()
        if self.instance:
            fields['email'].read_only = True
        return fields
    
    
class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields = ["id", "email", "full_name", "phone", 'is_user', "is_active", 'is_admin']
        read_only_fields = ['email', 'is_user', 'is_active', 'is_admin']
