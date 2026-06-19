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
    list_display = ['nombre', 'apodo', 'cedula', 'ciudad', 'whatsapp', 'activo', 'total_perros', 'tiene_usuario', 'tiene_coords']
    list_filter = ['activo', 'pais', 'ciudad', 'debe_cambiar_password']
    search_fields = ['nombre', 'apodo', 'ciudad', 'cedula']
    inlines = [PerroInline]
    fieldsets = [
        (None, {'fields': ['nombre', 'apodo', 'ciudad', 'pais', 'whatsapp', 'email', 'activo', 'foto', 'notas']}),
        ('Acceso al sistema', {'fields': ['cedula', 'usuario', 'debe_cambiar_password'],
            'description': 'Ingresá la cédula y luego usá la acción "Crear usuario" para generar el acceso.'}),
        ('Ubicación en mapa', {'fields': ['latitud', 'longitud'], 'classes': ['collapse'],
            'description': 'Opcional. Si no se completa, se usa la ciudad para ubicar en el mapa.'}),
    ]
    actions = ['crear_usuarios_accion']

    def total_perros(self, obj):
        return obj.perros.count()
    total_perros.short_description = 'Perros'

    def tiene_usuario(self, obj):
        return obj.usuario is not None
    tiene_usuario.boolean = True
    tiene_usuario.short_description = 'Usuario'

    def tiene_coords(self, obj):
        return obj.latitud is not None and obj.longitud is not None
    tiene_coords.boolean = True
    tiene_coords.short_description = 'GPS'

    def crear_usuarios_accion(self, request, queryset):
        from django.contrib.auth.models import User
        creados = 0
        errores = []
        for integrante in queryset:
            if integrante.usuario:
                errores.append(f'{integrante.nombre}: ya tiene usuario')
                continue
            if not integrante.cedula:
                errores.append(f'{integrante.nombre}: sin cédula')
                continue
            if User.objects.filter(username=integrante.cedula).exists():
                errores.append(f'{integrante.nombre}: cédula {integrante.cedula} ya en uso')
                continue
            user = User.objects.create_user(username=integrante.cedula, password='pitbull123')
            integrante.usuario = user
            integrante.debe_cambiar_password = True
            integrante.save()
            creados += 1
        msg = f'{creados} usuario(s) creado(s) con contraseña "pitbull123".'
        if errores:
            msg += ' Errores: ' + ' | '.join(errores)
        self.message_user(request, msg)
    crear_usuarios_accion.short_description = 'Crear usuario (cédula + pitbull123)'


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
