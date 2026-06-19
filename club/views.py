from rest_framework import viewsets, filters, serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated, IsAdminUser
from django.db.models import Count
from django.contrib.auth.models import User
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


# ─── ENDPOINTS DE SESIÓN ────────────────────────────────────────────────────

def normalizar_tel(numero):
    import re
    return re.sub(r'[\s\-\.\(\)]', '', numero or '')


class VerificarCIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        telefono = normalizar_tel(request.data.get('cedula', ''))
        if not telefono:
            return Response({'error': 'Ingresá tu número de WhatsApp'}, status=400)

        # Buscar por whatsapp normalizado o por cedula
        integrante = None
        for i in Integrante.objects.filter(activo=True):
            if normalizar_tel(i.whatsapp) == telefono:
                integrante = i
                break
            if i.cedula and normalizar_tel(i.cedula) == telefono:
                integrante = i
                break

        if integrante:
            return Response({
                'existe': True,
                'tipo': 'miembro',
                'primer_ingreso': integrante.usuario is None,
                'nombre': integrante.apodo or integrante.nombre.split()[0],
            })

        # Permite login de admin por username (sosaro)
        if User.objects.filter(username=telefono, is_staff=True).exists():
            return Response({'existe': True, 'tipo': 'admin', 'primer_ingreso': False, 'nombre': telefono})

        return Response({'existe': False, 'error': 'Número no encontrado en el registro del club'}, status=404)


class ActivarCuentaView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken

        telefono = normalizar_tel(request.data.get('cedula', ''))
        password = request.data.get('password', '')

        if not telefono or not password:
            return Response({'error': 'Datos incompletos'}, status=400)

        if len(password) < 6:
            return Response({'error': 'La contraseña debe tener al menos 6 caracteres'}, status=400)

        integrante = None
        for i in Integrante.objects.filter(activo=True):
            if normalizar_tel(i.whatsapp) == telefono:
                integrante = i
                break
            if i.cedula and normalizar_tel(i.cedula) == telefono:
                integrante = i
                break

        if not integrante:
            return Response({'error': 'Número no encontrado'}, status=404)

        if integrante.usuario:
            return Response({'error': 'Esta cuenta ya está activada. Usá tu contraseña.'}, status=400)

        username = f'tel_{telefono}'
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Este número ya tiene usuario. Usá tu contraseña.'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        integrante.usuario = user
        integrante.debe_cambiar_password = False
        integrante.save()

        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh)})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'integrante_id': None,
            'nombre': user.username,
            'debe_cambiar_password': False,
        }
        try:
            i = user.integrante
            data['integrante_id'] = i.id
            data['nombre'] = i.apodo or i.nombre
            data['debe_cambiar_password'] = i.debe_cambiar_password
        except Exception:
            pass
        return Response(data)


class CambiarPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')

        if not old_password or not new_password:
            return Response({'error': 'Ambos campos son requeridos'}, status=400)

        if not request.user.check_password(old_password):
            return Response({'error': 'Contraseña actual incorrecta'}, status=400)

        if len(new_password) < 6:
            return Response({'error': 'La nueva contraseña debe tener al menos 6 caracteres'}, status=400)

        request.user.set_password(new_password)
        request.user.save()

        try:
            request.user.integrante.debe_cambiar_password = False
            request.user.integrante.save()
        except Exception:
            pass

        return Response({'ok': True})


# ─── INTEGRANTES ────────────────────────────────────────────────────────────

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

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def crear_usuario(self, request, pk=None):
        integrante = self.get_object()

        if not integrante.cedula:
            return Response({'error': 'El integrante no tiene cédula registrada'}, status=400)

        if integrante.usuario:
            return Response({'error': 'El integrante ya tiene usuario creado'}, status=400)

        if User.objects.filter(username=integrante.cedula).exists():
            return Response({'error': f'Ya existe un usuario con cédula {integrante.cedula}'}, status=400)

        user = User.objects.create_user(username=integrante.cedula, password='pitbull123')
        integrante.usuario = user
        integrante.debe_cambiar_password = True
        integrante.save()

        return Response({'ok': True, 'username': integrante.cedula, 'password_inicial': 'pitbull123'})


# ─── PERROS ─────────────────────────────────────────────────────────────────

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

    @action(detail=False, methods=['get'], permission_classes=[AllowAny], url_path='mapa-razas')
    def mapa_razas(self, request):
        from django.db.models import Count
        from collections import defaultdict

        filas = (
            Perro.objects
            .filter(dueno__activo=True, estado='activo')
            .values('dueno__ciudad', 'raza')
            .annotate(total=Count('id'))
        )

        ciudades = defaultdict(lambda: {'pitbulls': 0, 'bullys': 0})
        for fila in filas:
            ciudad = (fila['dueno__ciudad'] or '').strip()
            if fila['raza'] == 'pitbull':
                ciudades[ciudad]['pitbulls'] += fila['total']
            elif fila['raza'] == 'bully':
                ciudades[ciudad]['bullys'] += fila['total']

        resultado = []
        for ciudad, counts in ciudades.items():
            coords = CIUDADES_COORDS.get(ciudad.lower())
            if coords:
                resultado.append({
                    'ciudad': ciudad,
                    'lat': coords[0],
                    'lng': coords[1],
                    'pitbulls': counts['pitbulls'],
                    'bullys': counts['bullys'],
                    'total': counts['pitbulls'] + counts['bullys'],
                })

        return Response(sorted(resultado, key=lambda x: -x['total']))

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


# ─── PANEL DE MIEMBRO ────────────────────────────────────────────────────────

class MisPerrosViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return PerroListSerializer
        return PerroSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Perro.objects.select_related('dueno').all()
        try:
            return Perro.objects.select_related('dueno').filter(dueno=user.integrante)
        except Exception:
            return Perro.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            try:
                serializer.save(dueno=user.integrante)
            except Exception:
                raise drf_serializers.ValidationError('No tenés perfil de integrante asociado')
        else:
            serializer.save()

    def perform_update(self, serializer):
        obj = self.get_object()
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            try:
                if obj.dueno != user.integrante:
                    raise drf_serializers.ValidationError('No podés editar perros de otro integrante')
            except Exception:
                raise drf_serializers.ValidationError('Sin permisos')
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            try:
                if instance.dueno != user.integrante:
                    raise drf_serializers.ValidationError('No podés eliminar perros de otro integrante')
            except Exception:
                raise drf_serializers.ValidationError('Sin permisos')
        instance.delete()


class MisCamadasViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CamadaSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Camada.objects.select_related('madre', 'padre', 'madre__dueno').all()
        try:
            return Camada.objects.select_related('madre', 'padre').filter(madre__dueno=user.integrante)
        except Exception:
            return Camada.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.is_superuser):
            madre_id = self.request.data.get('madre')
            try:
                madre = Perro.objects.get(id=madre_id, dueno=user.integrante, sexo='H')
                serializer.save(madre=madre)
            except Perro.DoesNotExist:
                raise drf_serializers.ValidationError('La madre seleccionada no es tuya o no es hembra')
        else:
            serializer.save()


# ─── OTROS ──────────────────────────────────────────────────────────────────

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
