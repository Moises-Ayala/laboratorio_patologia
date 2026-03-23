from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import (
    Movimiento,
    GastoPorPagar,
    CajaDiaria,
    ConceptoFrecuente,
    TipoEspecimen,
    TarifaCliente,
)


class MovimientoAdminForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['fecha'].initial = timezone.localdate()
        self.fields['tipo_movimiento'].initial = 'ingreso'

        self.order_fields([
            'fecha',
            'tipo_movimiento',
            'cliente',
            'concepto_frecuente',
            'concepto',
            'tipo_servicio',
            'cantidad_citologias',
            'numero_biopsia',
            'tipo_especimen',
            'monto',
            'descripcion',
            'registrado_por',
        ])


@admin.register(ConceptoFrecuente)
class ConceptoFrecuenteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)


@admin.register(TipoEspecimen)
class TipoEspecimenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    search_fields = ('nombre',)
    list_filter = ('activo',)


@admin.register(TarifaCliente)
class TarifaClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo_servicio', 'tipo_especimen', 'precio', 'activo')
    search_fields = ('cliente__nombre', 'tipo_especimen__nombre')
    list_filter = ('tipo_servicio', 'activo')


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    form = MovimientoAdminForm

    list_display = (
        'fecha',
        'tipo_movimiento',
        'cliente',
        'concepto',
        'tipo_servicio',
        'cantidad_citologias',
        'numero_biopsia',
        'tipo_especimen',
        'monto',
        'registrado_por',
    )
    search_fields = ('concepto', 'cliente__nombre', 'registrado_por', 'numero_biopsia')
    list_filter = ('tipo_movimiento', 'tipo_servicio', 'fecha', 'cliente')


@admin.register(GastoPorPagar)
class GastoPorPagarAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'concepto', 'valor', 'pagado')
    search_fields = ('concepto',)
    list_filter = ('pagado', 'fecha')


@admin.register(CajaDiaria)
class CajaDiariaAdmin(admin.ModelAdmin):
    list_display = (
        'fecha',
        'total_ingresos',
        'total_egresos',
        'total_pendientes',
        'total_cambios',
        'total_entregas',
        'saldo_dia',
    )
    list_filter = ('fecha',)
