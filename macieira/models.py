from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from simple_history.models import HistoricalRecords
from django.utils import timezone

ALELOS_S_CHOICES = [(f"S{i}", f"S{i}") for i in range(1, 31)]
NOTAS_CHOICES = [
    (Decimal(f"{note * 0.5:.1f}"), f"{note * 0.5:.1f}") for note in range(11)
]
P_A_CHOICES = [("AUSENTE", "Ausente"), ("PRESENTE", "Presente (em baixa intensidade)"), ("INTENSO", "Muito Presente")]

class Genotipo(models.Model):
    TIPO_CHOICES = [
        ('PARENTAL', 'Parental'),
        ('SEEDLING', 'Seedling'),
        ('PRE_SELECAO', 'Pré-Seleção'),
        ('SELECAO', 'Seleção'),
        ('CULTIVAR', 'Cultivar'),
        ('MUTANTE', 'Mutante'),
        ('ACESSO_BAG', 'Acesso BAG'),
    ]
    
    ORIGEM_CHOICES = [
        ('CRUZAMENTO', 'Cruzamento'),
        ('MUTACAO', 'Mutação'),
        ('INTRODUCAO', 'Introdução'),
        ('COLETA', 'Coleta'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
        ('DESCARTADO', 'Descartado'),
        ('MORTO', 'Morto'),
    ]
    
    identificador_unico = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="Identificador Único"
    )
    nome_designacao = models.CharField(max_length=200, verbose_name="Nome/Designação")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    origem = models.CharField(max_length=20, choices=ORIGEM_CHOICES, verbose_name="Origem")
    
    # Rastreabilidade Técnica
    codigo_pre_selecao = models.CharField(max_length=50, blank=True, null=True, verbose_name="Cód. Pré-Seleção", editable=False)
    codigo_selecao = models.CharField(max_length=50, blank=True, null=True, verbose_name="Cód. Seleção", editable=False)
    ano_selecao = models.IntegerField(blank=True, null=True, verbose_name="Ano de Seleção", editable=False)
    
    # Genealogia
    genitor_feminino = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filhos_como_mae',
        verbose_name="Genitor Feminino"
    )
    genitor_masculino = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filhos_como_pai',
        verbose_name="Genitor Masculino"
    )
    genotipo_original = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mutacoes',
        verbose_name="Genótipo Original (para mutações/promoções)"
    )
    
    # Características genéticas
    alelo_s1 = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        choices=ALELOS_S_CHOICES,
        verbose_name="Alelo S - primeiro"
    )
    alelo_s2 = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        choices=ALELOS_S_CHOICES,
        verbose_name="Alelo S - segundo"
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVO', verbose_name="Status")
    data_criacao = models.DateField(verbose_name="Data de Criação/Registro")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    cruzamento_origem = models.ForeignKey(
        "Cruzamento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Cruzamento de Origem"
    )
    foto_planta = models.ImageField(
        upload_to='genotipos/plantas/',
        null=True,
        blank=True,
        verbose_name="Foto da Planta"
    )
    foto_fruto = models.ImageField(
        upload_to='genotipos/frutos/',
        null=True,
        blank=True,
        verbose_name="Foto do Fruto"
    )
    publicar_passaporte = models.BooleanField(
        default=False,
        verbose_name="Publicar Passaporte"
    )

    def alelos_s_display(self):
        if self.alelo_s1 and self.alelo_s2:
            return f"{self.alelo_s1} / {self.alelo_s2}"
        elif self.alelo_s1:
            return f"{self.alelo_s1} / S?"
        return "-"

    def save(self, *args, **kwargs):
        # 1. Gerar Identificador Único Padrão (M-AAAA-NNNNN) se não existir
        if not self.identificador_unico:
            ano = timezone.now().year
            ultimo = Genotipo.objects.filter(
                identificador_unico__startswith=f"M-{ano}-"
            ).order_by('-identificador_unico').first()

            if ultimo:
                try:
                    numero = int(ultimo.identificador_unico.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    numero = 1
            else:
                numero = 1
            
            self.identificador_unico = f"M-{ano}-{numero:05d}"
        
        # 2. Lógica para Mutantes
        if self.tipo == "MUTANTE" and self.genotipo_original:
            self.genitor_feminino = self.genotipo_original.genitor_feminino
            self.genitor_masculino = self.genotipo_original.genitor_masculino
            self.origem = "MUTACAO"
            self.alelo_s1 = self.genotipo_original.alelo_s1
            self.alelo_s2 = self.genotipo_original.alelo_s2

        # 3. Lógica de Nomeação de Pré-Seleção (ex: 263/1)
        if self.tipo == "PRE_SELECAO" and self.cruzamento_origem:
            if not self.codigo_pre_selecao:
                prefixo = self.cruzamento_origem.identificador
                # Contar quantas pré-seleções já existem para este cruzamento
                count = Genotipo.objects.filter(
                    tipo="PRE_SELECAO", 
                    cruzamento_origem=self.cruzamento_origem
                ).count() + 1
                self.codigo_pre_selecao = f"{prefixo}/{count}"
            
            # O nome de designação passa a ser o código de pré-seleção por padrão
            if not self.nome_designacao or self.nome_designacao == "Nova Pré-Seleção":
                self.nome_designacao = self.codigo_pre_selecao

        # 4. Lógica de Nomeação de Seleção (ex: M.15/2026)
        if self.tipo == "SELECAO":
            if not self.ano_selecao:
                self.ano_selecao = timezone.now().year
            
            if not self.codigo_selecao:
                ano = self.ano_selecao
                # Contar seleções do ano
                count = Genotipo.objects.filter(tipo="SELECAO", ano_selecao=ano).count() + 1
                self.codigo_selecao = f"M.{count}/{ano}"
            
            # O nome de designação passa a ser o código de seleção
            self.nome_designacao = self.codigo_selecao

        super().save(*args, **kwargs)
    
    criado_por = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Criado por")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    # Auditoria
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Genótipo"
        verbose_name_plural = "Genótipos"
        ordering = ['-criado_em']
    
    def __str__(self):
        return f"{self.identificador_unico} ({self.nome_designacao})"


class Ambiente(models.Model):
    TIPO_CHOICES = [
        ('MATRIZEIRO', 'Matrizeiro'),
        ('BLOCO_PRE_SELECAO', 'Bloco de Pré-Seleção'),
        ('BLOCO_SELECOES', 'Bloco de Seleções'),
        ('POMAR_PARENTAIS', 'Pomar de Parentais'),
        ('BAG', 'BAG'),
        ('CASA_VEGETACAO', 'Casa de Vegetação'),
    ]
    
    nome = models.CharField(max_length=200, verbose_name="Nome")
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, verbose_name="Tipo")
    municipio = models.CharField(max_length=100, verbose_name="Município")
    altitude = models.IntegerField(null=True, blank=True, verbose_name="Altitude (m)")
    area_hectares = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                                        verbose_name="Área (ha)")
    responsavel = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Responsável")
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Ambiente"
        verbose_name_plural = "Ambientes"
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class Cruzamento(models.Model):
    identificador = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nº Cruzamento",
        help_text="Número sequencial do cruzamento (ex: 263)"
    )
    genitor_feminino = models.ForeignKey(
        Genotipo,
        on_delete=models.PROTECT,
        related_name='cruzamentos_como_mae',
        verbose_name="Genitor Feminino (Mãe)"
    )
    genitor_masculino = models.ForeignKey(
        Genotipo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='cruzamentos_como_pai',
        verbose_name="Genitor Masculino (Pai)",
        help_text="Deixe em branco para Polinização Livre"
    )
    data_polinizacao = models.DateField(verbose_name="Data da Polinização")
    ambiente = models.ForeignKey(
        Ambiente,
        on_delete=models.PROTECT,
        verbose_name="Local"
    )
    num_flores_polinizadas = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Nº Flores Polinizadas"
    )
    num_frutos_colhidos = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Nº Frutos Colhidos"
    )
    num_sementes_obtidas = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Nº Sementes Obtidas"
    )
    num_plantulas_formadas = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="N° Plântulas Formadas"
    )
    num_matrizeiro = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="N° Plantas no Matrizeiro"
    )
    num_bloco_pre_selecao = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="N°. Plantas no Bloco de Pré-Seleção"
    )
    tecnico_responsavel = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Técnico Responsável"
    )
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Cruzamento"
        verbose_name_plural = "Cruzamentos"
    
    def __str__(self):
        pai = self.genitor_masculino if self.genitor_masculino else "Polinização Livre"
        return f"{self.identificador}: {self.genitor_feminino} × {pai}"


class Plantio(models.Model):
    STATUS_PLANTA_CHOICES = [
        ('VIVA', 'Viva'),
        ('MORTA', 'Morto'),
        ('DOENTE', 'Doente'),
        ('REMOVIDA', 'Removida'),
    ]
    
    genotipo = models.ForeignKey(Genotipo, on_delete=models.PROTECT, verbose_name="Genótipo")
    ambiente = models.ForeignKey(Ambiente, on_delete=models.PROTECT, verbose_name="Ambiente")
    bloco = models.CharField(max_length=10, verbose_name="Bloco")
    linha = models.IntegerField(verbose_name="Linha")
    planta = models.IntegerField(verbose_name="Planta")
    repeticao = models.IntegerField(default=1, verbose_name="Repetição")
    porta_enxerto = models.ForeignKey(Genotipo, on_delete=models.PROTECT, null=True, blank=True, 
                                      related_name='plantios_como_porta_enxerto', verbose_name="Porta-enxerto")
    data_plantio = models.DateField(verbose_name="Data do Plantio")
    data_remocao = models.DateField(null=True, blank=True, verbose_name="Data da Remoção")
    status = models.CharField(max_length=20, choices=STATUS_PLANTA_CHOICES, default='VIVA', verbose_name="Status")
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Plantio"
        verbose_name_plural = "Plantios"
        unique_together = ('ambiente', 'bloco', 'linha', 'planta')
    
    def __str__(self):
        return f"{self.genotipo.nome_designacao} - {self.ambiente.nome} B{self.bloco}L{self.linha}P{self.planta}"


class AvaliacaoFenotipica(models.Model):
    ambiente = models.ForeignKey(Ambiente, on_delete=models.PROTECT, null=True, verbose_name="Local da avaliação")
    genotipo = models.ForeignKey(Genotipo, on_delete=models.PROTECT, verbose_name="Genótipo")
    safra = models.CharField(max_length=9, verbose_name="Safra", help_text="Ex: 2025/2026")
    data_avaliacao = models.DateField(verbose_name="Data da Avaliação")
    
    # Fenologia
    data_inicio_brotacao = models.DateField(null=True, blank=True, verbose_name="Data Inicio Brotação")
    data_inicio_floracao = models.DateField(null=True, blank=True, verbose_name="Data Inicio Floração")
    data_plena_floracao = models.DateField(null=True, blank=True, verbose_name="Data Plena Floração")
    data_final_floracao = models.DateField(null=True, blank=True, verbose_name="Data Final Floração")
    data_inicio_frutificacao = models.DateField(null=True, blank=True, verbose_name="Data Inicio Frutificação")
    data_colheita = models.DateField(null=True, blank=True, verbose_name="Data Colheita")
    
    # Fruto
    massa_media_fruto = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, verbose_name="Massa Média Fruto (g)")
    firmeza_polpa = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Firmeza Polpa (lbs)")
    solidos_soluveis = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Sólidos Solúveis (°Brix)")
    nota_calibre = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Calibre (0-5)", choices=NOTAS_CHOICES)
    cor_epiderme = models.CharField(max_length=8, verbose_name="Cor da Epiderme", null=True, blank=True, choices=[("VERMELHO", "Vermelho"), ("AMARELO", "Amarelo"), ("VERDE", "Verde")])
    nota_aparencia = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Aparência (0 - 5)", choices=NOTAS_CHOICES)
    nota_firmeza = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Firmeza (0-5)", choices=NOTAS_CHOICES)
    nota_fineza = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Fineza (0-5)", choices=NOTAS_CHOICES)
    nota_suculencia = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Suculência (0-5)", choices=NOTAS_CHOICES)
    nota_crocancia = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Crocância (0-5)", choices=NOTAS_CHOICES)
    nota_balanco_acucar_acidez = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Balanço Açucar / Acides (0-5)", choices=NOTAS_CHOICES)
    nota_adistringencia = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Adistringência (0-5)", choices=NOTAS_CHOICES)
    nota_sabor = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Sabor (0-5)", choices=NOTAS_CHOICES)
    nota_aroma = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Aroma (0-5)", choices=NOTAS_CHOICES)
    nota_global = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Global (0-5)", choices=NOTAS_CHOICES)
    abertura_tubo = models.CharField(max_length=8, verbose_name="Abertura Tubo Polinico", null=True, blank=True, choices=P_A_CHOICES)
    queimadura_sol = models.CharField(max_length=8, verbose_name="Queimadura de Sol", null=True, blank=True, choices=P_A_CHOICES)
    russting = models.CharField(max_length=8, verbose_name="Russting", null=True, blank=True, choices=P_A_CHOICES)
    cork_spot = models.CharField(max_length=8, verbose_name="Cork Spot", null=True, blank=True, choices=P_A_CHOICES)
    def_peduncular = models.CharField(max_length=8, verbose_name="Deformação Peduncular", null=True, blank=True, choices=P_A_CHOICES)
    rachadura = models.CharField(max_length=8, verbose_name="Rachadura", null=True, blank=True, choices=P_A_CHOICES)
    pingo_mel = models.CharField(max_length=8, verbose_name="Pingo de Mel", null=True, blank=True, choices=P_A_CHOICES)
    queda_pre_colheita = models.CharField(max_length=8, verbose_name="Queda Pré-Colheita", null=True, blank=True, choices=P_A_CHOICES)
    
    # Planta
    nota_brotacao = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Brotação (0-5)", choices=NOTAS_CHOICES)
    nota_vigor = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Vigor (0-5)", choices=NOTAS_CHOICES)
    nota_esporonamento = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Esporonamento (0-5)", choices=NOTAS_CHOICES)
    nota_burrknots = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Burrknots (0-5)", choices=NOTAS_CHOICES)
    nota_fruit_set = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Fruit Set (0-5)", choices=NOTAS_CHOICES)
    fruto_cacho = models.IntegerField(null=True, blank=True, verbose_name="N° Frutos/Cacho")
    nota_producao = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Produção (0-5)", choices=NOTAS_CHOICES)
    produtividade = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Produtividade (kg/planta)")
    
    # Sanidade
    incidencia_sarna = models.CharField(max_length=8, verbose_name="Incidência Sarna", null=True, blank=True, choices=P_A_CHOICES)
    incidencia_mfg = models.CharField(max_length=8, verbose_name="Incidência MFG", null=True, blank=True, choices=P_A_CHOICES)
    incidencia_oidio = models.CharField(max_length=8, verbose_name="Incidência Oídio", null=True, blank=True, choices=P_A_CHOICES)
    incidencia_marsonina = models.CharField(max_length=8, verbose_name="Incidência Marsonina", null=True, blank=True, choices=P_A_CHOICES)
    incidencia_outras_manchas = models.CharField(max_length=8, verbose_name="Incidência Outras Manchas", null=True, blank=True, choices=P_A_CHOICES)
    incidencia_podridoes_diversas = models.CharField(max_length=8, verbose_name="Incidência Podridões Diversas", null=True, blank=True, choices=P_A_CHOICES)
    incidencia_podridao_carpelar = models.CharField(max_length=8, verbose_name="Incidência Podridão Carpelar", null=True, blank=True, choices=P_A_CHOICES)
    
    # Pós Colheita
    dias_armazenamento = models.IntegerField(null=True, blank=True, verbose_name="Dias Armazenamento")
    firmeza_pos_col = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Firmeza Pós Colheita (lbs)")
    SST_pos_col = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="SST Pós Colheita (°Brix)")
    nota_potencial_armazenagem = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Nota Potencial Armazenagem (0-5)", choices=NOTAS_CHOICES)
    
    # Fotos
    foto_frutos_colhidos = models.ImageField(upload_to='avaliacoes/frutos/', null=True, blank=True, verbose_name="Foto Frutos Colhidos")
    foto_sintomas = models.ImageField(upload_to='avaliacoes/sintomas/', null=True, blank=True, verbose_name="Foto Sintomas/Outros")
    
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    avaliador = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Avaliador")
    criado_em = models.DateTimeField(auto_now_add=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True, null=True)
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Avaliação Fenotípica"
        verbose_name_plural = "Avaliações Fenotípicas"
        ordering = ['-data_avaliacao']
    
    def __str__(self):
        return f"{self.genotipo.nome_designacao} - {self.safra}"
