from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Cliente(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('medico', 'Médico'),
        ('clinica', 'Clínica'),
        ('centro', 'Centro de salud'),
        ('paciente', 'Paciente particular'),
    ]

    CONDICION_PAGO_CHOICES = [
        ('contado', 'Contado'),
        ('credito', 'Crédito'),
    ]

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    tipo_cliente = models.CharField(max_length=20, choices=TIPO_CLIENTE_CHOICES)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    condicion_pago = models.CharField(max_length=20, choices=CONDICION_PAGO_CHOICES)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Paciente(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    nombre = models.CharField(max_length=200)
    identidad = models.CharField(max_length=30, blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    procedencia = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Muestra(models.Model):
    TIPO_MUESTRA = [
        ('citologia', 'Citología'),
        ('biopsia', 'Biopsia'),
    ]

    ESTADO = [
        ('recibida', 'Recibida'),
        ('proceso', 'En proceso'),
        ('enviada_doctora', 'Enviada a doctora'),
        ('diagnosticada', 'Diagnosticada'),
        ('resultado_emitido', 'Resultado emitido'),
        ('entregada', 'Entregada'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, blank=True, null=True)
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, blank=True, null=True)

    tipo_muestra = models.CharField(max_length=20, choices=TIPO_MUESTRA)
    numero_muestra = models.CharField(max_length=30, blank=True, null=True, unique=True)

    medico = models.CharField(max_length=150, blank=True, null=True)
    centro = models.CharField(max_length=150, blank=True, null=True)

    fecha_recepcion = models.DateField()
    fecha_toma = models.DateField(blank=True, null=True)

    estado = models.CharField(max_length=30, choices=ESTADO, default='recibida')

    pago = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    descuento_tercera_edad = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    cantidad_muestras_recibidas = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo_muestra} - {self.numero_muestra or 'Sin número'}"

    def generar_numero_biopsia(self):
        year_short = str(timezone.now().year)[-2:]
        ultimo = (
            Muestra.objects.filter(
                tipo_muestra='biopsia',
                numero_muestra__isnull=False
            )
            .order_by('-id')
            .first()
        )

        siguiente = 1
        if ultimo and ultimo.numero_muestra:
            try:
                numero_base = ultimo.numero_muestra.split('-')[0].replace('BQ', '')
                siguiente = int(numero_base) + 1
            except (ValueError, IndexError):
                siguiente = 1

        return f"BQ{siguiente}-{year_short}"

    def clean(self):
        if not self.cliente and not self.paciente:
            raise ValidationError("Debes seleccionar al menos un cliente o un paciente.")

        if self.tipo_muestra == 'citologia':
            if not self.cantidad_muestras_recibidas or self.cantidad_muestras_recibidas < 1:
                raise ValidationError("Para citología debes indicar la cantidad de muestras recibidas.")
        else:
            self.cantidad_muestras_recibidas = None

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.tipo_muestra == 'biopsia' and not self.numero_muestra:
            self.numero_muestra = self.generar_numero_biopsia()

        super().save(*args, **kwargs)


class Resultado(models.Model):
    muestra = models.OneToOneField(Muestra, on_delete=models.CASCADE)
    diagnostico = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    recomendaciones = models.TextField(blank=True, null=True)
    fecha_resultado = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Resultado {self.muestra}"