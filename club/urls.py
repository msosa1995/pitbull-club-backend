from rest_framework.routers import DefaultRouter
from .views import (
    IntegranteViewSet, PerroViewSet, EventoViewSet,
    NoticiaViewSet, CampeonatoViewSet, CamadaViewSet,
    MisPerrosViewSet, MisCamadasViewSet,
)

router = DefaultRouter()
router.register('integrantes', IntegranteViewSet)
router.register('perros', PerroViewSet)
router.register('mis-perros', MisPerrosViewSet, basename='mis-perros')
router.register('mis-camadas', MisCamadasViewSet, basename='mis-camadas')
router.register('eventos', EventoViewSet)
router.register('noticias', NoticiaViewSet)
router.register('campeonatos', CampeonatoViewSet)
router.register('camadas', CamadaViewSet)

urlpatterns = router.urls
