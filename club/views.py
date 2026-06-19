from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.db.models import Count
from .models import Integrante, Perro, Evento, Noticia, Campeonato, Camada
from .serializers import (
    IntegranteSerializer, IntegranteListSerializer, IntegranteMapaSerializer,
    PerroSerializer, PerroListSerializer,
    EventoSerializer, NoticiaSerializer, CampeonatoSerializer, CamadaSerializer,
)

CIUDADES_COORDS = {
    'asunción': (-25.2867, -57.6470),
    'asuncion': (-25.2867, -57.6470),
    'luque': (-25.2667, -57.4833),
    'san lorenzo': (-25.3333, -57.5167),
    'lambaré': (-25.3500, -57.6167),
    'lambare': (-25.3500, -57.6167),
    'capiatá': (-25.3500, -57.4500),
    'capiata': (-25.3500, -57.4500),
    'fernando de la mora': (-25.3333, -57.5667),
    'limpio': (-25.1667, -57.4833),
    'ñemby': (-25.3833, -57.5333),
    'nemby': (-25.3833, -57.5333),
    'mariano roque alonso': (-25.2000, -57.5333),
    'ciudad del este': (-25.5167, -54.6167),
    'encarnación': (-27.3333, -55.8667),
    'encarnacion': (-27.3333, -55.8667),
    'coronel oviedo': (-25.4500, -56.4333),
    'caaguazú': (-25.4667, -56.0167),
    'caaguazu': (-25.4667, -56.0167),
    'pedro juan caballero': (-22.5333, -55.7333),
    'concepción': (-23.4167, -57.4333),
    'concepcion': (-23.4167, -57.4333),
    'villarrica': (-25.7500, -56.4333),
    'pilar': (-26.8667, -58.3000),
    'paraguay': (-25.2867, -57.6470),
}


class IntegranteViewSet(viewsets.ModelViewSet):
    queryset = Integrante.objects.annotate(total_perros=Count('perros'))
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'apodo', 'ciudad']
    ordering_fields = ['nombre', 'fecha_ingreso', 'ciudad']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return IntegranteListSerializer
        return IntegranteSerializer

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def stats(self, request):
        total_integrantes = Integrante.objects.count()
        activos = Integrante.objects.filter(activo=True).count()
        total_perros = Perro.objects.count()
        pitbulls = Perro.objects.filter(raza='pitbull').count()
        bullys = Perro.objects.filter(raza='bully').count()
        con_registro = Perro.objects.filter(tiene_registro=True).count()
        total_eventos = Evento.objects.filter(activo=True).count()
        return Response({
            'total_integrantes': total_integrantes,
            'activos': activos,
            'total_perros': total_perros,
            'pitbulls': pitbulls,
            'bullys': bullys,
            'con_registro': con_registro,
            'total_eventos': total_eventos,
        })

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def mapa(self, request):
        integrantes = Integrante.objects.filter(activo=True).annotate(
            total_perros=Count('perros', distinct=True),
            total_camadas=Count('perros__camadas_como_madre', distinct=True),
        )
        resultado = []
        for i in integrantes:
            lat = float(i.latitud) if i.latitud else None
            lng = float(i.longitud) if i.longitud else None
            if lat is None or lng is None:
                coords = CIUDADES_COORDS.get(i.ciudad.lower().strip())
                if coords:
                    lat, lng = coords
            if lat is not None and lng is not None:
                resultado.append({
                    'id': i.id,
                    'nombre': i.apodo if i.apodo else i.nombre,
                    'ciudad': i.ciudad,
                    'lat': lat,
                    'lng': lng,
                    'total_perros': i.total_perros,
                    'total_camadas': i.total_camadas,
                })
        return Response(resultado)


class PerroViewSet(viewsets.ModelViewSet):
    queryset = Perro.objects.select_related('dueno').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'color', 'procedencia', 'dueno__nombre', 'dueno__apodo', 'kennel']
    ordering_fields = ['nombre', 'fecha_nacimiento', 'raza']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return PerroListSerializer
        return PerroSerializer

    def get_queryset(self):
        qs = Perro.objects.select_related('dueno').all()
        raza = self.request.query_params.get('raza')
        sexo = self.request.query_params.get('sexo')
        estado = self.request.query_params.get('estado')
        destacado = self.request.query_params.get('destacado')
        if raza:
            qs = qs.filter(raza=raza)
        if sexo:
            qs = qs.filter(sexo=sexo)
        if estado:
            qs = qs.filter(estado=estado)
        if destacado in ('true', '1', 'True'):
            qs = qs.filter(destacado=True)
        return qs


class EventoViewSet(viewsets.ModelViewSet):
    queryset = Evento.objects.filter(activo=True)
    serializer_class = EventoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'lugar', 'ciudad', 'organizador']
    ordering_fields = ['fecha', 'tipo']
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Evento.objects.filter(activo=True)
        tipo = self.request.query_params.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs


class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.filter(publicada=True)
    serializer_class = NoticiaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CampeonatoViewSet(viewsets.ModelViewSet):
    queryset = Campeonato.objects.all()
    serializer_class = CampeonatoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CamadaViewSet(viewsets.ModelViewSet):
    queryset = Camada.objects.select_related('madre', 'padre', 'madre__dueno').all()
    serializer_class = CamadaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha_nacimiento', 'cantidad_total']

    def get_queryset(self):
        qs = Camada.objects.select_related('madre', 'padre', 'madre__dueno').all()
        madre_id = self.request.query_params.get('madre')
        if madre_id:
            qs = qs.filter(madre_id=madre_id)
        return qs
