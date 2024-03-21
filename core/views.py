import base64

from matplotlib import pyplot
import matplotlib
matplotlib.use('Agg')

from io import BytesIO
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View
from django.views.generic import TemplateView, ListView
from xhtml2pdf import pisa
from django.db.models import Model
from django.db.models import Count
from django.db.models.functions import ExtractYear

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

    def get(self, request):
        objects = Possui.objects.all()
        ppc = {}
        for paconv in objects:
            if paconv.convenio.nome not in ppc:
                ppc[paconv.convenio.nome] = {'convenio': paconv.convenio.nome, 'pacientes': []}
            ppc[paconv.convenio.nome]['pacientes'].append(paconv.paciente)

        context = {'ppc': ppc.values()}
        template = get_template('relatorios/pdfpacientesporconv.html')
        html = template.render(context)

        result = BytesIO()
        try:
            pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
            if not pdf.err:
                return HttpResponse(result.getvalue(), content_type='application/pdf')
        except Exception as e:
            print(e)

        return HttpResponse('Erro ao gerar PDF', content_type='text/plain')


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


'''
'''


class ConsultasEspecialidadeMesListView(ListView):
    template_name = 'relatorios/consporespecialidade.html'
    context_object_name = 'consultas'

    def get_queryset(self):
        return Consulta.objects.values('medico__especialidade', 'data', 'data__month') \
            .annotate(num_consultas=Count('id'))


class PacientesAtendidosEspecialidadeMesListView(ListView):
    template_name = 'relatorios/quantpacientporespec.html'
    context_object_name = 'pacientes_atendidos'

    def get_queryset(self):
        return Consulta.objects.values('medico__especialidade', 'data', ano=ExtractYear('data')) \
            .annotate(num_pacientes=Count('paciente', distinct=True))


class RelatConsultasEspecialidadeMes(View):

    def get(self, request):
        consultas = Consulta.objects.values('medico__especialidade', 'data__month') \
            .annotate(num_consultas=Count('id'))

        context = {'consultas': consultas}
        template = get_template('relatorios/consporespecialidadepdf.html')
        html = template.render(context)

        result = BytesIO()
        try:
            pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
            if not pdf.err:
                return HttpResponse(result.getvalue(), content_type='application/pdf')
        except Exception as e:
            print(e)

        return HttpResponse('Erro ao gerar PDF', content_type='text/plain')


class RelatPacientesAtendidosEspecialidadeMes(View):

    def get(self, request):
        pacientes_atendidos = Consulta.objects.values('medico__especialidade', ano=ExtractYear('data')) \
            .annotate(num_pacientes=Count('paciente', distinct=True))

        context = {'pacientes_atendidos': pacientes_atendidos}
        template = get_template('relatorios/quantpacientporespecpdf.html')
        html = template.render(context)

        result = BytesIO()
        try:
            pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
            if not pdf.err:
                return HttpResponse(result.getvalue(), content_type='application/pdf')
        except Exception as e:
            print(e)

        return HttpResponse('Erro ao gerar PDF', content_type='text/plain')


'''Gerando gráficos com google chart'''


class PacientePorConvenioListView(ListView):
    template_name = 'graficos/pacconvgooglechart.html'
    model = Paciente

    def get_context_data(self, *args, **kwargs):
        contexto = super().get_context_data(*args, **kwargs)
        convenios = Convenio.objects.all()
        dados = []
        for c in convenios:
            dados.append(
                {
                    'convenio': c.nome,
                    'pacientes': Possui.objects.filter(convenio=c.codconv).count()
                }
            )
        contexto['dados'] = dados
        return contexto


class RelatorioConsultasAno(View):

    def get(self, request, ano):
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        data = []
        labels = []
        # consultas = Consulta.objects.all().values('data__year').annotate(total=Count(id))
        consultasano = Consulta.objects.all().filter(data__year=ano)
        consultas = consultasano.values('data__month').annotate(total=Count(id))
        for i in range(1, 12):
            labels.append(meses[i - 1])
            for c in consultas:
                if i == c['data__month']:
                    data.append(c['total'])
            data.append(0)

        return JsonResponse({'labels': labels, 'data': data})


class EscolhaMesView(TemplateView):
    template_name = "graficos/pacconvchartjs.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        anos = Consulta.objects.all().values('data__year').distinct()
        ctx['anos'] = anos
        return ctx


class GrafPacientesCidade(TemplateView):
    template_name = "graficos/pacporcidade.html"

    def _criar_grafico(self):
        cidades = Paciente.objects.distinct().values_list('cidade', flat=True)
        pacientes = Paciente.objects.all()
        glabels = []
        gvalores = []
        for c in cidades:
            glabels.append(c)
            quant = pacientes.filter(cidade=c).count()
            gvalores.append(quant)
        pyplot.bar(glabels, gvalores)
        buffer = BytesIO()
        pyplot.savefig(buffer, format='png')
        buffer.seek(0)
        img = buffer.getvalue()
        graf = base64.b64encode(img)
        graf = graf.decode('utf-8')
        pyplot.close()
        buffer.close()
        return graf

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['grafico'] = self._criar_grafico()
        return contexto
