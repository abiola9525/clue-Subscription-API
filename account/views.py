from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView
from account.models import User
from . serializers import MyTokenObtainPairSerializer, UserSerializer, UpdateUserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
@swagger_auto_schema(method='POST', request_body=UserSerializer)
@api_view(['POST'])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def register_user(request):
    data = request.data
    user_serializer = UserSerializer(data=data)
    
    try:
        if user_serializer.is_valid(raise_exception=False):
            UserModel = User
            email = data.get('email')
            if email and UserModel.objects.filter(email=email).exists():
                return Response({
                    'status': 'error',
                    'code': 'EMAIL_EXISTS',
                    'message': 'A user with this email already exists.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = user_serializer.save()
            user.save()
        
            return Response({
                'status': 'success',
                'message': 'Account Created successfully.',
                'user': user_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            errors = user_serializer.errors
            error_type = next(iter(errors))
            error_message = errors[error_type][0]
            
            error_codes = {
                'email': 'INVALID_EMAIL',
                'password': 'INVALID_PASSWORD',
                'phone': 'INVALID_PHONE',
                'username': 'INVALID_USERNAME',
                'non_field_errors': 'VALIDATION_ERROR'
            }
            
            return Response({
                'status': 'error',
                'code': error_codes.get(error_type, 'VALIDATION_ERROR'),
                'field': error_type,
                'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'code': 'SERVER_ERROR',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@swagger_auto_schema(method='PUT', request_body=UpdateUserSerializer)
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def user_details(request):
    if request.method == "GET":
        
        user_serializer = UserSerializer(request.user)
        data = user_serializer.data
        return Response(data, status=status.HTTP_200_OK)
    
    if request.method == "PUT":
        user_serializer = UpdateUserSerializer(request.user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_202_ACCEPTED)
        