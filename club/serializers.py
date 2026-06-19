from rest_framework import serializers
from .models import Integrante, Perro, FotoPerro, Titulo, Evento, Noticia, Campeonato, PuntoCampeonato, Camada


class FotoPerroSerializer(serializers.ModelSerializer):
    imagen = serializers.SerializerMethodField()

    class Meta:
        model = FotoPerro
        fields = ['id', 'imagen', 'es_principal', 'orden']

    def get_imagen(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class TituloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Titulo
        fields = ['id', 'nombre', 'organizacion', 'fecha', 'descripcion']


class PerroListSerializer(serializers.ModelSerializer):
    dueno_nombre = serializers.CharField(source='dueno.nombre', read_only=True)
    raza_display = serializers.CharField(source='get_raza_display', read_only=True)
    variante_display = serializers.CharField(source='get_variante_display', read_only=True)
    sexo_display = serializers.CharField(source='get_sexo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Perro
        fields = [
            'id', 'nombre', 'raza', 'raza_display', 'variante', 'variante_display',
            'sexo', 'sexo_display', 'color', 'fecha_nacimiento', 'tiene_registro',
            'numero_registro', 'kennel', 'estado', 'estado_display', 'destacado',
            'dueno_nombre', 'foto_url',
        ]

    def get_foto_url(self, obj):
        request = self.context.get('request')
        if obj.foto_principal and request:
            return request.build_absolute_uri(obj.foto_principal.url)
        return None


class PerroSerializer(serializers.ModelSerializer):
    dueno_nombre = serializers.CharField(source='dueno.nombre', read_only=True)
    dueno_ciudad = serializers.CharField(source='dueno.ciudad', read_only=True)
    raza_display = serializers.CharField(source='get_raza_display', read_only=True)
    variante_display = serializers.CharField(source='get_variante_display', read_only=True)
    sexo_display = serializers.CharField(source='get_sexo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    fotos = FotoPerroSerializer(many=True, read_only=True)
    titulos = TituloSerializer(many=True, read_only=True)

    class Meta:
        model = Perro
        fields = '__all__'


class IntegranteListSerializer(serializers.ModelSerializer):
    total_perros = serializers.IntegerField(read_only=True)
    tiene_usuario = serializers.SerializerMethodField()

    class Meta:
        model = Integrante
        fields = ['id', 'nombre', 'apodo', 'ciudad', 'pais', 'whatsapp', 'activo', 'foto', 'total_perros', 'cedula', 'tiene_usuario']

    def get_tiene_usuario(self, obj):
        return obj.usuario_id is not None


class IntegranteSerializer(serializers.ModelSerializer):
    perros = PerroListSerializer(many=True, read_only=True)
    total_perros = serializers.IntegerField(read_only=True)

    class Meta:
        model = Integrante
        fields = '__all__'


class EventoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = '__all__'

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class NoticiaSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Noticia
        fields = '__all__'

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class PuntoCampeonatoSerializer(serializers.ModelSerializer):
    perro_nombre = serializers.CharField(source='perro.nombre', read_only=True)
    perro_raza = serializers.CharField(source='perro.raza', read_only=True)
    perro_raza_display = serializers.CharField(source='perro.get_raza_display', read_only=True)
    dueno_nombre = serializers.CharField(source='perro.dueno.nombre', read_only=True)
    perro_foto = serializers.SerializerMethodField()

    class Meta:
        model = PuntoCampeonato
        fields = '__all__'

    def get_perro_foto(self, obj):
        request = self.context.get('request')
        if obj.perro.foto_principal and request:
            return request.build_absolute_uri(obj.perro.foto_principal.url)
        return None


class CampeonatoSerializer(serializers.ModelSerializer):
    puntos = PuntoCampeonatoSerializer(many=True, read_only=True)

    class Meta:
        model = Campeonato
        fields = '__all__'


class CamadaSerializer(serializers.ModelSerializer):
    madre_nombre = serializers.CharField(source='madre.nombre', read_only=True)
    madre_raza = serializers.CharField(source='madre.raza', read_only=True)
    padre_nombre = serializers.CharField(source='padre.nombre', read_only=True, allow_null=True)
    dueno_nombre = serializers.CharField(source='madre.dueno.nombre', read_only=True)

    class Meta:
        model = Camada
        fields = '__all__'


class IntegranteMapaSerializer(serializers.ModelSerializer):
    total_perros = serializers.IntegerField(read_only=True)
    total_camadas = serializers.IntegerField(read_only=True)

    class Meta:
        model = Integrante
        fields = ['id', 'nombre', 'apodo', 'ciudad', 'pais', 'latitud', 'longitud', 'activo', 'total_perros', 'total_camadas']
