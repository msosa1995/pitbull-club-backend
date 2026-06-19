from django.contrib import admin
from .models import Integrante, Perro, FotoPerro, Titulo, Evento, Noticia, Campeonato, PuntoCampeonato, Camada


class PerroInline(admin.TabularInline):
    model = Perro
    fk_name = 'dueno'
    extra = 0
    fields = ['nombre', 'raza', 'variante', 'sexo', 'color', 'tiene_registro', 'estado', 'destacado']


class FotoPerroInline(admin.TabularInline):
    model = FotoPerro
    extra = 1
    fields = ['imagen', 'es_principal', 'orden']


class TituloInline(admin.TabularInline):
    model = Titulo
    extra = 1
    fields = ['nombre', 'organizacion', 'fecha']


class PuntoCampeonatoInline(admin.TabularInline):
    model = PuntoCampeonato
    extra = 1
    fields = ['perro', 'puntos', 'posicion', 'categoria']


class CamadaInline(admin.TabularInline):
    model = Camada
    fk_name = 'madre'
    extra = 0
    fields = ['padre', 'padre_externo', 'fecha_nacimiento', 'cantidad_total', 'cantidad_machos', 'cantidad_hembras']


@admin.register(Integrante)
class IntegranteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apodo', 'ciudad', 'pais', 'whatsapp', 'activo', 'total_perros', 'tiene_coords']
    list_filter = ['activo', 'pais', 'ciudad']
    search_fields = ['nombre', 'apodo', 'ciudad']
    inlines = [PerroInline]
    fieldsets = [
        (None, {'fields': ['nombre', 'apodo', 'ciudad', 'pais', 'whatsapp', 'email', 'activo', 'foto', 'notas']}),
        ('Ubicación en mapa', {'fields': ['latitud', 'longitud'], 'classes': ['collapse'],
            'description': 'Opcional. Si no se completa, se usa la ciudad para ubicar en el mapa.'}),
    ]

    def total_perros(self, obj):
        return obj.perros.count()
    total_perros.short_description = 'Perros'

    def tiene_coords(self, obj):
        return obj.latitud is not None and obj.longitud is not None
    tiene_coords.boolean = True
    tiene_coords.short_description = 'GPS'


@admin.register(Perro)
class PerroAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'dueno', 'raza', 'variante', 'sexo', 'color', 'estado', 'destacado', 'tiene_registro']
    list_filter = ['raza', 'variante', 'sexo', 'tiene_registro', 'estado', 'destacado']
    search_fields = ['nombre', 'dueno__nombre', 'dueno__apodo', 'color', 'procedencia', 'kennel']
    raw_id_fields = ['dueno', 'criador']
    inlines = [FotoPerroInline, TituloInline, CamadaInline]


@admin.register(Camada)
class CamadaAdmin(admin.ModelAdmin):
    list_display = ['madre', 'padre', 'padre_externo', 'fecha_nacimiento', 'cantidad_total', 'cantidad_machos', 'cantidad_hembras']
    list_filter = ['fecha_nacimiento']
    search_fields = ['madre__nombre', 'padre__nombre', 'padre_externo']
    raw_id_fields = ['madre', 'padre']


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'fecha', 'lugar', 'ciudad', 'inscripcion_abierta', 'activo']
    list_filter = ['tipo', 'activo', 'inscripcion_abierta']
    search_fields = ['titulo', 'lugar', 'ciudad', 'organizador']
    list_editable = ['activo', 'inscripcion_abierta']


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'fecha_publicacion', 'publicada', 'destacada']
    list_filter = ['publicada', 'destacada']
    search_fields = ['titulo', 'resumen']
    list_editable = ['publicada', 'destacada']


@admin.register(Campeonato)
class CampeonatoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'año', 'activo', 'fecha_inicio', 'fecha_fin']
    list_filter = ['activo', 'año']
    inlines = [PuntoCampeonatoInline]
