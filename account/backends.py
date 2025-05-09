from django.contrib.auth import get_user_model
from django.db.models import Q

class CustomAuthenticationBackend(object):
    def authenticate(self, request, email=None, password=None):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(Q(email=email) | Q(phone=email))
        except UserModel.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None
    
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None