from rest_framework.routers import DefaultRouter
from .views import IntegranteViewSet, PerroViewSet, EventoViewSet, NoticiaViewSet, CampeonatoViewSet

router = DefaultRouter()
router.register('integrantes', IntegranteViewSet)
router.register('perros', PerroViewSet)
router.register('eventos', EventoViewSet)
router.register('noticias', NoticiaViewSet)
router.register('campeonatos', CampeonatoViewSet)

urlpatterns = router.urls
