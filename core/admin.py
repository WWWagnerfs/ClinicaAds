from django.contrib import admin
from . import models

@admin.register(models.Ambulatorio)
class AmbulatorioAdmin(admin.ModelAdmin):
    list_display = ['nome', 'numleitos', 'andar']

@admin.register(models.Atende)
class AtendeAdmin(admin.ModelAdmin):
    pass


class MedicoConvenioInline(admin.StackedInline):
    model = models.Atende
    extra = 1


@admin.register(models.Medico)
class MedicoAdmin(admin.ModelAdmin):
    list_display = ['crm', 'nome', 'telefone', 'salario', 'ambulatorio']
    inlines = [MedicoConvenioInline,]

class PacienteConvenioInline(admin.TabularInline):
    model = models.Possui
    extra = 1
    
@admin.register(models.Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'telefone', 'cidade', 'ambulatorio')
    inlines = [PacienteConvenioInline]