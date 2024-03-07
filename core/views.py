from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View
from django.views.generic import TemplateView, ListView
from xhtml2pdf import pisa

from core.models import Paciente


# Create your views here.
class HomeTemplateView(TemplateView):
    template_name = "index.html"


class PacientesListView(ListView):
    template_name = "relatorios/pacientes.html"
    model = Paciente
    context_object_name = 'pacientes'


class RelatPdfPacientes(View):
    def get(self, request):
        pacientes = Paciente.objects.all()
        data = {
            'pacientes': pacientes,
        }
        template = get_template("relatorios/pdfpacientes.html")
        html = template.render(data)
        result = BytesIO()
        try:
            pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
            return HttpResponse(result.getvalue(),
                                content_type='aplication/pfd')

        except Exception as e:
            print(e)
            return HttpResponse("Erro ao gerar PDF.", status=500)
