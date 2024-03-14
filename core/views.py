import base64
from matplotlib import pyplot
from io import BytesIO

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View
from django.views.generic import TemplateView, ListView
from xhtml2pdf import pisa
from django.db.models import Model

from core.models import Paciente, Medico, Possui, Convenio, Consulta


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
                                content_type='application/pdf')
        except Exception as e:
            print(e)
            return None


class RelatPdfPacientesConvenio(View):
    template_name = 'relatorios/pdfpacientesporconv.html'
    model = Possui
    context_object_name = 'pppc'

    def get(self, request):
        try:
            objects = self.model.objects.all()
            my_dict = {}
            for paconv in objects:
                if paconv.convenio.nome not in my_dict:
                    my_dict[paconv.convenio.nome] = {}
                my_dict[paconv.convenio.nome][paconv.paciente.nome] = paconv.paciente.idade

            print(my_dict)
            data = {self.context_object_name: my_dict}
            template = get_template(self.template_name)
            html = template.render(data)
            result = BytesIO()
            pisa.pisaDocument(BytesIO(html.encode('utf-8')), result)
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        except Exception as e:
            print(e)
            return HttpResponse("Ocorreu um erro ao gerar o PDF. Por favor, entre em contato com o administrador.")




class RelatPacientesConvenio(View):
    template_name = 'relatorios/pacientesporconv.html'
    model = Possui
    context_object_name = 'ppc'

    def get(self, request):
        objects = self.model.objects.all()
        ppc = {}
        for paconv in objects:
            if paconv.convenio.nome not in ppc:
                ppc[paconv.convenio.nome] = {'convenio': paconv.convenio.nome, 'pacientes': []}
            ppc[paconv.convenio.nome]['pacientes'].append(paconv.paciente)
        data = {self.context_object_name: ppc.values()}
        return render(request, self.template_name, data)


'''
parte dos gráficos
'''
class ConsConvView(TemplateView):
    template_name = 'graficos/consultasconvenio.html'

    def _criar_grafico(self):
        convenios = Convenio.objects.all()
        glabels = []
        gvalores = []
        for c in convenios:
            if Consulta.objects.filter(convenio=c).count() > 0:
                glabels.append(c.nome)
                quant = Consulta.objects.filter(convenio=c).count()
                gvalores.append(quant)
        pyplot.pie(gvalores, labels=glabels)
        buffer = BytesIO()
        pyplot.savefig(buffer, format='png')
        buffer.seek(0)
        imagem = buffer.getvalue()
        grafico = base64.b64encode(imagem)
        grafico = grafico.decode('utf-8')
        buffer.close()
        return grafico




    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        tabela = Consulta.objects.all().order_by('convenio')
        contexto['tabela'] = tabela
        contexto['grafico'] = self._criar_grafico()
        return contexto
