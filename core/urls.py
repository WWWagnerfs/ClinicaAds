from django.urls import path

from core import views

urlpatterns = [
    path('', views.HomeTemplateView.as_view(), name='home'),
    path('relatorios/pacientes', views.PacientesListView.as_view(), name='relat_pacientes'),
    path('relatorios/pdfpacientes', views.RelatPdfPacientes.as_view(), name='pdf_pacientes'),

    path('relatorios/pdfpacientesporconv', views.RelatPdfPacientesConvenio.as_view(),
         name='pdf_pacientes_por_convenio'),
    path('relatorios/pacientesporconv', views.RelatPacientesConvenio.as_view(),
         name='pacientes_por_convenio'),

    path('graficos/consultasconvenio', views.ConsConvView.as_view(), name='graf_cons_conv'),
    
    path('relatorios/consporespecialidade',views.ConsultasEspecialidadeMesListView.as_view(),
         name='rel_por_espec'),
    
    path('relatorios/consporespecialidadepdf',views.RelatConsultasEspecialidadeMes.as_view(),
         name='rel_cons_por_espec_pdf'),
    
    path('relatorios/quantpacientporespec', views.PacientesAtendidosEspecialidadeMesListView.as_view(),
         name='quant_cons_por_espec'),
    
    path('relatorios/quantpacientporespecpdf', views.RelatPacientesAtendidosEspecialidadeMes.as_view(),
         name='quant_cons_por_espec_pdf'),
    path('graficos/pacconv', views.PacientePorConvenioListView.as_view(), name='graf_pac_conv'),

    path('consjson/<int:ano>', views.RelatorioConsultasAno.as_view(), name='reljson'),
    path('consmensais/', views.EscolhaMesView.as_view(), name='consmens'),
    path('graficos/paccidade', views.GrafPacientesCidade.as_view(),
         name='graf_pac_cid'),

]