from django.contrib import admin
from .models import Cliente, Paciente, Muestra, Resultado

admin.site.register(Cliente)
admin.site.register(Paciente)
admin.site.register(Muestra)
admin.site.register(Resultado)
