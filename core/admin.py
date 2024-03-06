from django.contrib import admin

# Register your models here.
from . import models

@admin.register(models.Ambulatorio)
class AmbulatorioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'numleitos', 'andar']


class MedicoConvenioInline(admin.StackedInline):
    model = models.Atende
    extra = 1
    raw_id_fields = ['convenio']

@admin.register(models.Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['crm', 'nome', 'telefone', 'salario', 'ambulatorio']
    inlines = [MedicoConvenioInline]



@admin.register(models.Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'telefone', 'idade', 'ambulatorio']


@admin.register(models.Convenio)
class ConvenioAdmin(admin.ModelAdmin):
    list_display = ['nome']


@admin.register(models.Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = []
