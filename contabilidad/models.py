from django.db import models
from django.core.exceptions import ValidationError
from core.models import Cliente, Muestra


class ConceptoFrecuente(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class TipoEspecimen(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class TarifaCliente(models.Model):
    TIPO_SERVICIO_CHOICES = [
        ('citologia', 'Citología'),
        ('biopsia', 'Biopsia'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='tarifas')
    tipo_servicio = models.CharField(max_length=20, choices=TIPO_SERVICIO_CHOICES)
    tipo_especimen = models.ForeignKey(
        TipoEspecimen,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text='Solo aplica para biopsias.'
    )
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ('cliente', 'tipo_servicio', 'tipo_especimen')

    def __str__(self):
        if self.tipo_servicio == 'citologia':
            return f"{self.cliente} - Citología - L {self.precio}"
        return f"{self.cliente} - {self.tipo_especimen} - L {self.precio}"


class Movimiento(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('egreso', 'Egreso'),
        ('pendiente', 'Pendiente'),
        ('cambio', 'Cambio'),
        ('entrega', 'Entrega'),
    ]

    TIPO_SERVICIO_CHOICES = [
        ('citologia', 'Citología'),
        ('biopsia', 'Biopsia'),
    ]

    fecha = models.DateField()
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO_CHOICES, default='ingreso')

    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, blank=True, null=True)

    concepto = models.CharField(max_length=200)
    concepto_frecuente = models.ForeignKey(
        ConceptoFrecuente,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    tipo_servicio = models.CharField(max_length=20, choices=TIPO_SERVICIO_CHOICES, blank=True, null=True)

    cantidad_citologias = models.PositiveIntegerField(blank=True, null=True)

    numero_biopsia = models.CharField(max_length=30, blank=True, null=True)
    tipo_especimen = models.ForeignKey(
        TipoEspecimen,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    descripcion = models.TextField(blank=True, null=True)
    registrado_por = models.CharField(max_length=150, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fecha} - {self.tipo_movimiento} - {self.concepto}"

    def clean(self):
        if self.tipo_servicio == 'citologia':
            if not self.cantidad_citologias or self.cantidad_citologias < 1:
                raise ValidationError("Debes indicar la cantidad de citologías.")
            self.numero_biopsia = None
            self.tipo_especimen = None

        if self.tipo_servicio == 'biopsia':
            if not self.tipo_especimen:
                raise ValidationError("Debes seleccionar el tipo de espécimen para biopsia.")
            if not self.numero_biopsia:
                raise ValidationError("Debes indicar el número de biopsia.")
            self.cantidad_citologias = None

    def calcular_monto(self):
        if not self.cliente or not self.tipo_servicio:
            return self.monto

        if self.tipo_servicio == 'citologia':
            tarifa = TarifaCliente.objects.filter(
                cliente=self.cliente,
                tipo_servicio='citologia',
                activo=True
            ).first()
            if tarifa and self.cantidad_citologias:
                return tarifa.precio * self.cantidad_citologias

        if self.tipo_servicio == 'biopsia':
            tarifa = TarifaCliente.objects.filter(
                cliente=self.cliente,
                tipo_servicio='biopsia',
                tipo_especimen=self.tipo_especimen,
                activo=True
            ).first()
            if tarifa:
                return tarifa.precio

        return self.monto

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.concepto_frecuente and not self.concepto:
            self.concepto = self.concepto_frecuente.nombre

        monto_calculado = self.calcular_monto()
        if monto_calculado is not None:
            self.monto = monto_calculado

        super().save(*args, **kwargs)


class GastoPorPagar(models.Model):
    fecha = models.DateField()
    concepto = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    pagado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.concepto} - L {self.valor}"


class CajaDiaria(models.Model):
    fecha = models.DateField(unique=True)
    total_ingresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_egresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_pendientes = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_cambios = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_entregas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_dia = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Caja diaria {self.fecha}"
