from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.shortcuts import redirect
from simple_history.admin import SimpleHistoryAdmin
from .models import Genotipo, Ambiente, Cruzamento, Plantio, AvaliacaoFenotipica

@admin.register(Genotipo)
class GenotipoAdmin(SimpleHistoryAdmin):
    list_display = [
        'identificador_unico',
        'nome_designacao',
        'tipo',
        'origem',
        'status',
        'alelos_s_display'
    ]
    list_filter = ['tipo', 'origem', 'status']
    search_fields = ['identificador_unico', 'nome_designacao']
    readonly_fields = ["identificador_unico", "genealogia_display"]
    fieldsets = (
        ('Identificação', {
            'fields': (
                'identificador_unico',
                'nome_designacao',
                'tipo',
                'origem',
                'status',
                'publicar_passaporte'
            )
        }),
        ('Genealogia', {
            'fields': (
                'genitor_feminino',
                'genitor_masculino',
                'genotipo_original',
                'cruzamento_origem',
                'genealogia_display',
            )
        }),
        ('Características Genéticas', {
            'fields': ('alelo_s1', 'alelo_s2')
        }),
        ('Datas e Observações', {
            'fields': ('data_criacao', 'observacoes', 'criado_por')
        }),
        ('Fotos', {
            'fields': ('foto_planta', 'foto_fruto')
        }),
    )
    change_form_template = "admin/macieira/genotipo/change_form.html"

    actions = ["promover_para_selecao", "promover_para_cultivar"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/registrar-mutante/',
                self.admin_site.admin_view(self.registrar_mutante_view),
                name='macieira_genotipo_registrar_mutante'
            ),
        ]
        return custom_urls + urls
    
    def registrar_mutante_view(self, request, object_id):
        genotipo = self.get_object(request, object_id)
        url_end = f"?tipo=MUTANTE&genotipo_original={genotipo.id}&origem=MUTACAO"
        url = reverse('admin:macieira_genotipo_add') + url_end
        return redirect(url)
    
    def response_change(self, request, obj):
        return super().response_change(request, obj)
    
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        tipo = request.GET.get('tipo')
        genotipo_original = request.GET.get('genotipo_original')
        origem = request.GET.get('origem')
        genitor_feminino = request.GET.get('genitor_feminino')
        genitor_masculino = request.GET.get('genitor_masculino')
        cruzamento_origem = request.GET.get('cruzamento_origem')

        if tipo:
            initial['tipo'] = tipo
        if genotipo_original:
            initial['genotipo_original'] = genotipo_original
        if origem:
            initial['origem'] = origem
        if genitor_feminino:
            initial["genitor_feminino"] = genitor_feminino
        if genitor_masculino:
            initial["genitor_masculino"] = genitor_masculino
        if cruzamento_origem:
            initial["cruzamento_origem"] = cruzamento_origem
        return initial

    def genealogia_display(self, obj):
        """Exibe a árvore genealógica do genótipo"""
        html = '<div style="font-family: monospace; line-height: 1.8;">'
        html += self._build_tree(obj, 0)
        html += '</div>'
        return mark_safe(html)

    def _build_tree(self, genotipo, nivel):
        """Constrói a árvore recursivamente"""
        if genotipo is None or nivel > 4:
            return ''
        
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * nivel
        result = ''
        
        if nivel == 0:
            result += f'<strong>{genotipo.identificador_unico} - {genotipo.nome_designacao}</strong><br>'
        
        if genotipo.genitor_feminino or genotipo.genitor_masculino:
            if genotipo.genitor_feminino:
                result += f'{indent}├─ ♀ <a href="/admin/macieira/genotipo/{genotipo.genitor_feminino.id}/change/">{genotipo.genitor_feminino.identificador_unico} - {genotipo.genitor_feminino.nome_designacao}</a><br>'
            else:
                result += f'{indent}├─ ♀ ?<br>'
            
            if genotipo.genitor_masculino:
                result += f'{indent}└─ ♂ <a href="/admin/macieira/genotipo/{genotipo.genitor_masculino.id}/change/">{genotipo.genitor_masculino.identificador_unico} - {genotipo.genitor_masculino.nome_designacao}</a><br>'
            else:
                result += f'{indent}└─ ♂ ?<br>'
            
            if genotipo.genitor_feminino:
                result += f'{indent}&nbsp;&nbsp;&nbsp;&nbsp;♀ mãe:<br>'
                result += self._build_tree(genotipo.genitor_feminino, nivel + 2)
            if genotipo.genitor_masculino:
                result += f'{indent}&nbsp;&nbsp;&nbsp;&nbsp;♂ pai:<br>'
                result += self._build_tree(genotipo.genitor_masculino, nivel + 2)
        
        return result
    
    def promover_para_selecao(self, request, queryset):
        """Promove híbridos para seleção, criando novo registro com histórico herdade"""
        promovidos = 0
        for genotipo in queryset:
            if genotipo.tipo not in ["HIBRIDO", "MUTANTE"]:
                self.message_user(
                    request,
                    f'{genotipo.identificador_unico} não é um híbrido/mutante',
                    level='warning'
                )
                continue

            novo = Genotipo.objects.create(
                nome_designacao=f"{genotipo.nome_designacao} (Seleção)",
                tipo='SELECAO',
                origem=genotipo.origem,
                genitor_feminino=genotipo.genitor_feminino,
                genitor_masculino=genotipo.genitor_masculino,
                genotipo_original=genotipo,
                alelo_s1=genotipo.alelo_s1 if genotipo.alelo_s1 else "",
                alelo_s2=genotipo.alelo_s2 if genotipo.alelo_s2 else "",
                data_criacao=timezone.now().date(),
                criado_por=request.user,
                observacoes=f"Promovido de {genotipo.identificador_unico} - {genotipo.nome_designacao}"
            )
            promovidos += 1

        self.message_user(request, f"{promovidos} genótipo(s) promovido(s) para Seleção")
    
    def promover_para_cultivar(self, request, queryset):
        """Promove seleções para cultivar"""
        promovidos = 0
        for genotipo in queryset:
            if genotipo.tipo != 'SELECAO':
                self.message_user(
                    request,
                    f'{genotipo.identificador_unico} não é uma seleção.',
                    level='warning'
                )
                continue
            
            novo = Genotipo.objects.create(
                nome_designacao=genotipo.nome_designacao.replace(' (Seleção)', ''),
                tipo='CULTIVAR',
                origem=genotipo.origem,
                genitor_feminino=genotipo.genitor_feminino,
                genitor_masculino=genotipo.genitor_masculino,
                genotipo_original=genotipo,
                alelo_s1=genotipo.alelo_s1 if genotipo.alelo_s1 else "",
                alelo_s2=genotipo.alelo_s2 if genotipo.alelo_s2 else "",
                data_criacao=timezone.now().date(),
                criado_por=request.user,
                observacoes=f"Promovido de {genotipo.identificador_unico} - {genotipo.nome_designacao}. Cultivar registrada."
            )
            promovidos += 1
        
        self.message_user(request, f'{promovidos} genótipo(s) promovido(s) para Cultivar.')

    promover_para_cultivar.short_description = '⭐ Promover para Cultivar'
    promover_para_selecao.short_description = '⬆️ Promover para Seleção'
    genealogia_display.short_description = "Genealogia"
    genealogia_display.allow_tags = True

@admin.register(Ambiente)
class AmbienteAdmin(SimpleHistoryAdmin):
    list_display = [
        'nome',
        'tipo',
        'municipio',
        'responsavel'
    ]
    list_filter = ['tipo', 'municipio']

@admin.register(Cruzamento)
class CruzamentoAdmin(SimpleHistoryAdmin):
    list_display = [
        'identificador',
        'genitor_feminino',
        'genitor_masculino',
        'data_polinizacao',
        'num_plantulas_formadas',
        'num_matrizeiro',
        'num_bloco_hibridos',
        'acoes_hibridos'
    ]
    list_filter = ['data_polinizacao', 'ambiente']
    search_fields = [
        'identificador',
        'genitor_feminino__nome_designacao',
        'genitor_masculino__nome_designacao'
    ]

    fieldsets = (
        ("Identificação", {
            'fields': ('identificador', 'data_polinizacao', 'ambiente')
        }),
        ("Genitores", {
            "fields": ('genitor_feminino', 'genitor_masculino')
        }),
        ("Dados de Polinização", {
            "fields": ('num_flores_polinizadas', 'num_frutos_colhidos', 'num_sementes_obtidas')
        }),
        ("Avanço de População", {
            'fields': ('num_plantulas_formadas', 'num_matrizeiro', 'num_bloco_hibridos'),
            'description': 'Registre quantas plantas avançaram em cada etapa'
        }),
        ("Responsável e Observações", {
            'fields': ('tecnico_responsavel', 'observacoes')
        })
    )

    def acoes_hibridos(self, obj):
        genit_fem = f"genitor_feminino={obj.genitor_feminino.id}"
        genit_masc = f"genitor_masculino={obj.genitor_masculino.id}"
        url = reverse(
            'admin:macieira_genotipo_add'
        ) + f'?tipo=HIBRIDO&{genit_fem}&{genit_masc}&origem=CRUZAMENTO&cruzamento_origem={obj.id}'
        return format_html(
            '<a class="button" href="{}" style="background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">🌱 Novo Híbrido</a>',
            url
        )
    
    acoes_hibridos.short_description = 'Ações'
    acoes_hibridos.allow_tags = True

@admin.register(Plantio)
class PlantioAdmin(SimpleHistoryAdmin):
    list_display = ['genotipo', 'ambiente', 'bloco', 'linha', 'planta', 'status']
    list_filter = ['ambiente', 'status']

@admin.register(AvaliacaoFenotipica)
class AvaliacaoFenotipicaAdmin(SimpleHistoryAdmin):
    list_display = ['genotipo', 'safra', 'data_avaliacao', 'massa_media_fruto', 'solidos_soluveis']
    list_filter = ['safra']

    fieldsets = (
        ('Identificação', {
            'fields': (
                'genotipo',
                'safra',
                'data_avaliacao',
                'avaliador'
            )
        }),
        ('Localização', {
            'fields': (
                'ambiente',
            )
        }),
        ('Fenologia', {
            'fields': (
                'data_inicio_brotacao',
                'data_inicio_floracao',
                'data_plena_floracao',
                'data_final_floracao',
                'data_inicio_frutificacao',
                'data_colheita'
            )
        }),
        ('Fruto', {
            'fields': (
                'massa_media_fruto',
                'solidos_soluveis',
                'nota_calibre',
                'cor_epiderme',
                'nota_aparencia',
                'firmeza_polpa',
                'nota_firmeza',
                'nota_fineza',
                'nota_suculencia',
                'nota_crocancia',
                'nota_balanco_acucar_acidez',
                'nota_adistringencia',
                'nota_sabor',
                'nota_aroma',
                'nota_global',
                'abertura_tubo',
                'queimadura_sol',
                'russting',
                'cork_spot',
                'def_peduncular',
                'rachadura',
                'pingo_mel',
                'queda_pre_colheita',
            )
        }),
        ('Planta', {
            'fields': (
                'nota_brotacao',
                'nota_vigor',
                'nota_esporonamento',
                'nota_burrknots',
                'nota_fruit_set',
                'fruto_cacho',
                'nota_producao',
                'produtividade',
            )
        }),
        ('Sanidade', {
            'fields': (
                'incidencia_sarna',
                'incidencia_mfg',
                'incidencia_oidio',
                'incidencia_marsonina',
                'incidencia_outras_manchas',
                'incidencia_podridoes_diversas',
                'incidencia_podridao_carpelar'
            )
        }),
        ('Pós Colheita', {
            'fields': (
                'dias_armazenamento',
                'firmeza_pos_col',
                'SST_pos_col',
                'nota_potencial_armazenagem',
            )
        }),
        ('Fotos', {
            'fields': (
                'foto_frutos_colhidos',
                'foto_sintomas'
            )
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
    )
