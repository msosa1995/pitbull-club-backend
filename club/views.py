from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.db.models import Count
from .models import Integrante, Perro, Evento, Noticia, Campeonato
from .serializers import (
    IntegranteSerializer, IntegranteListSerializer,
    PerroSerializer, PerroListSerializer,
    EventoSerializer, NoticiaSerializer, CampeonatoSerializer,
)


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
