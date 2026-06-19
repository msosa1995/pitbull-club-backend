from django.db import models


class Integrante(models.Model):
    nombre = models.CharField(max_length=100)
    apodo = models.CharField(max_length=50, blank=True)
    ciudad = models.CharField(max_length=100)
    pais = models.CharField(max_length=100, default='Paraguay')
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='integrantes/', blank=True, null=True)
    notas = models.TextField(blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Integrante'
        verbose_name_plural = 'Integrantes'

    def __str__(self):
        return self.apodo if self.apodo else self.nombre


class Perro(models.Model):
    RAZA_CHOICES = [
        ('pitbull', 'American Pit Bull Terrier'),
        ('bully', 'American Bully'),
    ]
    VARIANTE_CHOICES = [
        ('na', 'N/A'),
        ('pocket', 'Pocket'),
        ('standard', 'Standard'),
        ('classic', 'Classic'),
        ('xl', 'XL'),
        ('extreme', 'Extreme'),
    ]
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('H', 'Hembra'),
    ]
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('retirado', 'Retirado'),
        ('fallecido', 'Fallecido'),
    ]

    dueno = models.ForeignKey(Integrante, on_delete=models.CASCADE, related_name='perros', verbose_name='Dueño')
    criador = models.ForeignKey(
        Integrante, on_delete=models.SET_NULL,
        related_name='criados', null=True, blank=True, verbose_name='Criador'
    )
    nombre = models.CharField(max_length=100)
    raza = models.CharField(max_length=20, choices=RAZA_CHOICES)
    variante = models.CharField(max_length=20, choices=VARIANTE_CHOICES, default='na')
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    color = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    procedencia = models.CharField(max_length=200, blank=True, help_text='De quién adquirió el perro')
    tiene_registro = models.BooleanField(default=False)
    numero_registro = models.CharField(max_length=100, blank=True)
    kennel = models.CharField(max_length=100, blank=True, help_text='Nombre del kennel o asociación')
    padre = models.CharField(max_length=100, blank=True)
    madre = models.CharField(max_length=100, blank=True)
    foto_principal = models.ImageField(upload_to='perros/', blank=True, null=True)
    notas = models.TextField(blank=True)
    fecha_registro = models.DateField(auto_now_add=True)
    # Campos extendidos
    microchip = models.CharField(max_length=50, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Peso en kg')
    altura = models.IntegerField(null=True, blank=True, help_text='Altura en cm al hombro')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    destacado = models.BooleanField(default=False, help_text='Mostrar en la página principal')

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Perro'
        verbose_name_plural = 'Perros'

    def __str__(self):
        return f'{self.nombre} ({self.dueno})'


class FotoPerro(models.Model):
    perro = models.ForeignKey(Perro, on_delete=models.CASCADE, related_name='fotos')
    imagen = models.ImageField(upload_to='perros/galeria/')
    es_principal = models.BooleanField(default=False)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ['orden', 'id']
        verbose_name = 'Foto'
        verbose_name_plural = 'Fotos'

    def __str__(self):
        return f'Foto de {self.perro.nombre}'


class Titulo(models.Model):
    perro = models.ForeignKey(Perro, on_delete=models.CASCADE, related_name='titulos')
    nombre = models.CharField(max_length=200)
    organizacion = models.CharField(max_length=100, blank=True)
    fecha = models.DateField(blank=True, null=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Título'
        verbose_name_plural = 'Títulos'

    def __str__(self):
        return f'{self.nombre} — {self.perro.nombre}'


class Evento(models.Model):
    TIPO_CHOICES = [
        ('exposicion', 'Exposición'),
        ('competencia', 'Competencia'),
        ('seminario', 'Seminario'),
        ('reunion', 'Reunión'),
        ('capacitacion', 'Capacitación'),
        ('otro', 'Otro'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='exposicion')
    fecha = models.DateField()
    hora = models.TimeField(blank=True, null=True)
    lugar = models.CharField(max_length=200)
    ciudad = models.CharField(max_length=100, blank=True)
    organizador = models.CharField(max_length=200, blank=True)
    imagen = models.ImageField(upload_to='eventos/', blank=True, null=True)
    inscripcion_abierta = models.BooleanField(default=True)
    cupo = models.IntegerField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha']
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'

    def __str__(self):
        return f'{self.titulo} ({self.fecha})'


class Noticia(models.Model):
    titulo = models.CharField(max_length=300)
    resumen = models.TextField(blank=True)
    contenido = models.TextField()
    imagen = models.ImageField(upload_to='noticias/', blank=True, null=True)
    fecha_publicacion = models.DateField(auto_now_add=True)
    publicada = models.BooleanField(default=True)
    destacada = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_publicacion']
        verbose_name = 'Noticia'
        verbose_name_plural = 'Noticias'

    def __str__(self):
        return self.titulo


class Campeonato(models.Model):
    año = models.IntegerField()
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-año']
        verbose_name = 'Campeonato'
        verbose_name_plural = 'Campeonatos'

    def __str__(self):
        return f'{self.nombre} {self.año}'


class PuntoCampeonato(models.Model):
    campeonato = models.ForeignKey(Campeonato, on_delete=models.CASCADE, related_name='puntos')
    perro = models.ForeignKey(Perro, on_delete=models.CASCADE, related_name='puntos_campeonato')
    puntos = models.IntegerField(default=0)
    posicion = models.IntegerField(blank=True, null=True)
    categoria = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['posicion', '-puntos']
        verbose_name = 'Punto de Campeonato'
        verbose_name_plural = 'Puntos de Campeonato'

    def __str__(self):
        return f'{self.perro.nombre} — {self.campeonato} — {self.puntos}pts'


class Camada(models.Model):
    madre = models.ForeignKey(
        Perro, on_delete=models.CASCADE,
        related_name='camadas_como_madre',
        limit_choices_to={'sexo': 'H'},
        verbose_name='Madre'
    )
    padre = models.ForeignKey(
        Perro, on_delete=models.SET_NULL,
        related_name='camadas_como_padre',
        null=True, blank=True,
        limit_choices_to={'sexo': 'M'},
        verbose_name='Padre (del club)'
    )
    padre_externo = models.CharField(
        max_length=100, blank=True,
        help_text='Nombre del padre si no es integrante del club'
    )
    fecha_nacimiento = models.DateField(verbose_name='Fecha de nacimiento')
    cantidad_total = models.IntegerField(default=0, verbose_name='Total cachorros')
    cantidad_machos = models.IntegerField(default=0, verbose_name='Machos')
    cantidad_hembras = models.IntegerField(default=0, verbose_name='Hembras')
    notas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_nacimiento']
        verbose_name = 'Camada'
        verbose_name_plural = 'Camadas'

    def __str__(self):
        padre_str = self.padre.nombre if self.padre else self.padre_externo or 'Padre desconocido'
        return f'{self.madre.nombre} × {padre_str} ({self.fecha_nacimiento})'
