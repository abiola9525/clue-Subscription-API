from django.urls import path
from . import views


urlpatterns = [
    path('account/register/', views.register_user, name="sign_up"),
    path('account/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('account/', views.user_details, name="my_account"),
]