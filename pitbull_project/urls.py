from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from club.views import MeView, CambiarPasswordView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/me/', MeView.as_view(), name='me'),
    path('api/cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),
    path('api/', include('club.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
