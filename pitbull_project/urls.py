from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from club.views import MeView, CambiarPasswordView, VerificarCIView, ActivarCuentaView, MiPerfilView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/me/', MeView.as_view(), name='me'),
    path('api/cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),
    path('api/mi-perfil/', MiPerfilView.as_view(), name='mi_perfil'),
    path('api/verificar-ci/', VerificarCIView.as_view(), name='verificar_ci'),
    path('api/activar-cuenta/', ActivarCuentaView.as_view(), name='activar_cuenta'),
    path('api/', include('club.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
