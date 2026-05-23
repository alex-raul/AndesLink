from django.db import models
from django.conf import settings


class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    icono = models.CharField(max_length=10, default='🌿')   # emoji simple
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    class Unidad(models.TextChoices):
        KG = 'kg', 'Kilogramo'
        TN = 'tn', 'Tonelada'
        SACO = 'saco', 'Saco'
        UNIDAD = 'unidad', 'Unidad'

    class Estado(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        RESERVADO = 'RESERVADO', 'Reservado'
        VENDIDO = 'VENDIDO', 'Vendido'

    productor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='productos',
        limit_choices_to={'rol': 'PRODUCTOR'}
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        related_name='productos'
    )
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad = models.CharField(max_length=10, choices=Unidad.choices, default=Unidad.KG)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_cosecha = models.DateField()
    departamento = models.CharField(max_length=80)
    provincia = models.CharField(max_length=80, blank=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.DISPONIBLE
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.nombre} — {self.productor.get_full_name()}"