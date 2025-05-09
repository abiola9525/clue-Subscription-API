from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="CLUE Subscription API",
        default_version="v1.0.0",
        description="An API for CLUE Subscription",
        contact= openapi.Contact(email="omotosoabiola0911@gmail.com"),
        license= openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny,],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('account.urls')),
    path('api/', include('subscription.urls')),
    path('api/account/login/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/account/login/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('', schema_view.with_ui('swagger'), name='schema-swagger-ui'),
    path('docs/', schema_view.with_ui('redoc'), name='schema-redoc'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)