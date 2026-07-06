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
        ('HIBRIDO', 'Híbrido'),
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
        verbose_name="Genótipo Original (para mutações)"
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
        if not self.identificador_unico:
            ano = timezone.now().year
            ultimo = Genotipo.objects.filter(
                identificador_unico__startswith=f"M-{ano}-"
            ).order_by('-identificador_unico').first()

            if ultimo:
                numero = int(ultimo.identificador_unico.split('-')[-1]) + 1
            else:
                numero = 1
            
            self.identificador_unico = f"M-{ano}-{numero:05d}"
        
        if self.tipo == "MUTANTE" and self.genotipo_original:
            self.genitor_feminino = self.genotipo_original.genitor_feminino
            self.genitor_masculino = self.genotipo_original.genitor_masculino
            self.origem = "MUTACAO"
            self.alelo_s1 = self.genotipo_original.alelo_s1
            self.alelo_s2 = self.genotipo_original.alelo_s2

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
        return f"{self.identificador_unico} - {self.nome_designacao}"


class Ambiente(models.Model):
    TIPO_CHOICES = [
        ('MATRIZEIRO', 'Matrizeiro'),
        ('BLOCO_HIBRIDOS', 'Bloco de Híbridos'),
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
        verbose_name="Identificador"
    )
    genitor_feminino = models.ForeignKey(
        Genotipo,
        on_delete=models.PROTECT,
        related_name='cruzamentos_como_mae',
        verbose_name="Genitor Feminino"
    )
    genitor_masculino = models.ForeignKey(
        Genotipo,
        on_delete=models.PROTECT,
        related_name='cruzamentos_como_pai',
        verbose_name="Genitor Masculino"
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
        verbose_name="N° Plantulas Formadas"
    )
    num_matrizeiro = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="N° Plantas Levadas ao Matrizeiro"
    )
    num_bloco_hibridos = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="N°. Plantas Levadas ao Bloco de Hibridos"
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
        return f"{self.identificador}: {self.genitor_feminino} × {self.genitor_masculino}"


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
        return f"{self.genotipo.identificador_unico} - {self.ambiente.nome} B{self.bloco}L{self.linha}P{self.planta}"


class AvaliacaoFenotipica(models.Model):

    # Localização
    ambiente = models.ForeignKey(Ambiente, on_delete=models.PROTECT, null=True, verbose_name="Local da avaliação")

    # Identificação
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
    massa_media_fruto = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Massa Média Fruto (g)"
    )
    firmeza_polpa = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Firmeza Polpa (lbs)"
    )
    solidos_soluveis = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Sólidos Solúveis (°Brix)"
    )
    nota_calibre = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Calibre (0-5)",
        choices=NOTAS_CHOICES
    )
    cor_epiderme = models.CharField(
        max_length=8,
        verbose_name="Cor da Epiderme",
        null=True,
        blank=True,
        choices=[
            ("VERMELHO", "Vermelho"),
            ("AMARELO", "Amarelo"),
            ("VERDE", "Verde")
        ]
    )
    nota_aparencia = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Aparência (0 - 5)",
        choices=NOTAS_CHOICES
    )
    nota_firmeza = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Firmeza (0-5)",
        choices=NOTAS_CHOICES
    )
    nota_fineza = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Fineza (0-5)",
        choices=NOTAS_CHOICES
    )
    nota_suculencia = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Suculência (0-5)",
        choices=NOTAS_CHOICES
    )
    nota_crocancia = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Crocância (0-5)",
        choices=NOTAS_CHOICES
    )
    nota_balanco_acucar_acidez = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Balanço Açucar / Acides (0-5)",
        choices=NOTAS_CHOICES
    )
    nota_adistringencia = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Adistringência (0-5)",
        choices=NOTAS_CHOICES
    )
    nota_sabor = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Sabor (0-5)",
        choices=NOTAS_CHOICES
    )
    nota_aroma = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Aroma (0-5)",
        choices=NOTAS_CHOICES
    )
    nota_global = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Global (0-5)",
        choices=NOTAS_CHOICES
    )
    abertura_tubo = models.CharField(
        max_length=8,
        verbose_name="Abertura Tubo Polinico",
        null=True,
        blank=True,
        choices=P_A_CHOICES
    )
    queimadura_sol = models.CharField(
        max_length=8,
        verbose_name="Queimadura de Sol",
        null=True,
        blank=True,
        choices=P_A_CHOICES
    )
    russting = models.CharField(
        max_length=8,
        verbose_name="Presença de Russting",
        null=True,
        blank=True,
        choices=P_A_CHOICES
    )
    cork_spot = models.CharField(
        max_length=8,
        verbose_name="Presença de Cork Spot",
        null=True,
        blank=True,
        choices=P_A_CHOICES
    )
    def_peduncular = models.CharField(
        max_length=8,
        verbose_name="Deformação Peduncular",
        null=True,
        blank=True,
        choices=P_A_CHOICES
    )
    rachadura = models.CharField(
        max_length=8,
        verbose_name="Rachadura",
        null=True,
        blank=True,
        choices=P_A_CHOICES
    )
    pingo_mel = models.CharField(
        max_length=8,
        verbose_name="Presença de Pingo de Mel",
        null=True,
        blank=True,
        choices=P_A_CHOICES
    )
    queda_pre_colheita = models.CharField(
        max_length=8,
        verbose_name="Queda Pré-Colheita",
        null=True,
        blank=True,
        choices=P_A_CHOICES
    )
    
    # Planta
    nota_vigor = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Vigor",
        choices=NOTAS_CHOICES
    )
    produtividade = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Produtividade (kg/planta)"
    )
    nota_brotacao = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Brotação (0-5)",
        choices=NOTAS_CHOICES
    )
    nota_esporonamento = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Esporonamento (0-5)",
        choices=NOTAS_CHOICES
    )
    nota_burrknots = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Burrknots (0-5)",
        choices=NOTAS_CHOICES
    )
    nota_fruit_set = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Fruit Set (0-5)",
        choices=NOTAS_CHOICES
    )
    fruto_cacho = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Quantidade de Frutos por Cacho (1-9)",
        choices=[(n_f, str(n_f)) for n_f in range(1, 10)]
    )
    nota_producao = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota Produção (0-5)",
        choices=NOTAS_CHOICES
    )

    # Sanidade
    incidencia_sarna = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Incidência de Sarna (0-5)",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("5.0")),
        ],
        choices=NOTAS_CHOICES
    )
    incidencia_mfg = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Incidência de Mancha Foliar da Glomerella (0-5)",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("5.0")),
        ],
        choices=NOTAS_CHOICES
    )
    incidencia_oidio = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Incidência de Oídio (0-5)",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("5.0")),
        ],
        choices=NOTAS_CHOICES
    )
    incidencia_marsonina = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Incidência de Marsonina (0-5)",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("5.0")),
        ],
        choices=NOTAS_CHOICES
    )
    incidencia_outras_manchas = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Incidência de Outras Manchas (0-5)",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("5.0")),
        ],
        choices=NOTAS_CHOICES
    )
    incidencia_podridoes_diversas = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Incidência de Podridões Diversas (0-5)",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("5.0")),
        ],
        choices=NOTAS_CHOICES
    )
    incidencia_podridao_carpelar = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Incidência de Podridão Carpelar (0-5)",
        validators=[
            MinValueValidator(Decimal("0.0")),
            MaxValueValidator(Decimal("5.0")),
        ],
        choices=NOTAS_CHOICES
    )
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    avaliador = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Avaliador")

    # Pós Colheita
    dias_armazenamento = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Dias de Armazenamento",
        validators=[MinValueValidator(Decimal("0"))]
    )
    firmeza_pos_col = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Firmeza Polpa na Pós Colheita (lbs)"
    )
    SST_pos_col = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Sólidos Soluveis Totais na Pós Colheita"
    )
    nota_potencial_armazenagem = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Nota para o Potêncial de armazenagem (0-5)",
        choices=NOTAS_CHOICES
    )

    # Fotos
    foto_frutos_colhidos = models.ImageField(
        upload_to="avaliacoes/frutos/",
        null=True,
        blank=True,
        verbose_name="Foto dos Frutos Colhidos"
    )
    foto_sintomas = models.ImageField(
        upload_to="avaliacoes/sintomas/",
        null=True,
        blank=True,
        verbose_name="Foto de Sintomas"
    )
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = "Avaliação Fenotípica"
        verbose_name_plural = "Avaliações Fenotípicas"
    
    def __str__(self):
        return f"{self.genotipo.identificador_unico} - Safra {self.safra}"
