# Arquitetura do Sistema de Gestão de Melhoramento Genético Vegetal - Módulo Macieira

## Documento de Arquitetura de Software v1.0

**Empresa:** [Nome da Empresa de Pesquisa Agropecuária]
**Data:** Julho/2026
**Responsável Técnico:** [Nome do Melhorista Responsável]

---

## Sumário

1. [Visão Geral do Sistema](#1-visão-geral-do-sistema)
2. [Decisões Arquiteturais](#2-decisões-arquiteturais)
3. [Stack Tecnológica](#3-stack-tecnológica)
4. [Modelagem de Domínio](#4-modelagem-de-domínio)
5. [Fluxos Operacionais](#5-fluxos-operacionais)
6. [Modelo de Dados Detalhado](#6-modelo-de-dados-detalhado)
7. [Controle de Acesso e Segurança](#7-controle-de-acesso-e-segurança)
8. [Integrações e APIs](#8-integrações-e-apis)
9. [Plano de Implementação](#9-plano-de-implementação)
10. [Glossário de Termos do Domínio](#10-glossário-de-termos-do-domínio)

---

## 1. Visão Geral do Sistema

### 1.1 Propósito
Sistema de gestão operacional para o programa de melhoramento genético vegetal, com arquitetura modular por espécie, iniciando pelo módulo da macieira (Malus domestica).

### 1.2 Escopo Atual (Módulo Macieira)
- Gestão completa do pipeline de melhoramento: Cruzamento → Seedling → Híbridos → Seleções → Cultivar
- Controle de ambientes físicos: Matrizeiro, Blocos, Pomar de Parentais, BAG
- Registro e rastreamento de mutações
- Genotipagem de alelos S e protocolos laboratoriais
- Construção automática de árvores genealógicas
- Geração de passaportes de germoplasma
- Controle de acesso baseado em papéis com auditoria completa

### 1.3 Fora do Escopo (Momento Atual)
- Gestão financeira ou contábil
- Integração com sistemas de RH
- E-commerce ou vendas de cultivares

---

## 2. Decisões Arquiteturais

### 2.1 Abordagem Modular
**Decisão:** Sistema monolítico modular com kernel comum + módulos por espécie.

**Justificativa:**
- Simplicidade operacional (único deploy, único banco)
- Consistência transacional para dados compartilhados
- Equipe não especializada em DevOps
- Facilidade de evolução futura para arquitetura de plugins

### 2.2 Padrão Arquitetural
**Domain-Driven Design (DDD)** com separação clara entre:
- **Kernel:** Funcionalidades comuns a todas as espécies
- **Módulo Macieira:** Regras de negócio específicas da cultura

### 2.3 Princípios de Design
- **Baixo acoplamento, alta coesão** entre módulos
- **Interface segregation** para comunicação kernel-módulo
- **Single source of truth** para dados de genótipos
- **Audit trail** em todas as alterações críticas

---

## 3. Stack Tecnológica

### 3.1 Backend
- **Linguagem:** Python 3.11+
- **Framework Web:** Django 5.0
- **API REST:** Django REST Framework
- **ORM:** Django ORM + django-simple-history (auditoria)

### 3.2 Banco de Dados
- **Principal:** PostgreSQL 16+
- **Extensões necessárias:** PostGIS (futuro), ltree (árvore genealógica)
- **Cache:** Redis (para sessões e cache de consultas frequentes)

### 3.3 Frontend
- **Administrativo:** Django Admin (customizado)
- **Interface Melhorista:** Django Templates + HTMX + Alpine.js
- **Dashboards e Gráficos:** Plotly/Dash (reuso de conhecimento em data science)

### 3.4 Infraestrutura
- **Containerização:** Docker + Docker Compose
- **Armazenamento de Arquivos:** Sistema de arquivos local (com migração futura para S3)
- **Backup:** Scripts automatizados para PostgreSQL dump

---

## 4. Modelagem de Domínio

### 4.1 Contextos Delimitados (Bounded Contexts)

#### Contexto Comum (Kernel)
- Gestão de Usuários e Permissões
- Cadastro de Instituições e Programas
- Localizações Geográficas

#### Contexto de Germoplasma
- Registro de Genótipos
- Árvore Genealógica
- Passaporte de Acessos

#### Contexto de Melhoramento
- Planejamento e Execução de Cruzamentos
- Pipeline de Seleção (Seedling → Híbrido → Seleção)
- Avaliações Fenotípicas

#### Contexto Laboratorial
- Primers e Marcadores Moleculares
- Protocolos de PCR
- Resultados de Genotipagem

#### Contexto de Campo
- Ambientes Físicos
- Plantios e Repetições
- Manejo de Mutações

### 4.2 Linguagem Ubíqua

| Termo | Definição | Domínio |
|-------|-----------|---------|
| **Genótipo** | Constituição genética única de um indivíduo | Germoplasma |
| **Seedling** | Plântula resultante de cruzamento, fase juvenil | Melhoramento |
| **Híbrido** | Planta individual selecionada a partir de seedlings | Melhoramento |
| **Seleção** | Genótipo em fase avançada de avaliação, com repetições | Melhoramento |
| **Cultivar** | Variedade comercial lançada | Melhoramento |
| **Mutação/Sport** | Variação somática espontânea em planta existente | Campo |
| **Alelos S** | Alelos de autoincompatibilidade em macieira | Laboratorial |
| **BAG** | Banco Ativo de Germoplasma | Germoplasma |

---

## 5. Fluxos Operacionais

### 5.1 Pipeline Principal de Melhoramento

```
                    ┌─────────────────────────────────────────────┐
                    │         POMAR DE PARENTAIS                  │
                    │  (Genitores Femininos e Masculinos)         │
                    └─────────────┬───────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────────────────┐
                    │         CRUZAMENTO CONTROLADO               │
                    │  (Polinização manual controlada)            │
                    └─────────────┬───────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────────────────────┐
                    │              SEEDLINGS                      │
                    │  População em linha no Matrizeiro           │
                    │  Avaliação: Vigor, Sanidade, SAM            │
                    │  (Descarte de plantas com defeitos)         │
                    └─────────────┬───────────────────────────────┘
                                  │ Seleção positiva
                                  ▼
                    ┌─────────────────────────────────────────────┐
                    │          BLOCO DE HÍBRIDOS                  │
                    │  Cada planta = 1 genótipo único             │
                    │  Avaliação: Fruto, Arquitetura, Produção    │
                    └─────────────┬───────────────────────────────┘
                                  │ Seleção dos melhores
                                  ▼
                    ┌─────────────────────────────────────────────┐
                    │         BLOCO DE SELEÇÕES                   │
                    │  10 plantas por genótipo                    │
                    │  5 plantas em Ambiente 1                    │
                    │  5 plantas em Ambiente 2                    │
                    │  Avaliação multi-ambientes e multi-safras   │
                    └─────────────┬───────────────────────────────┘
                                  │ Aprovação final
                                  ▼
                    ┌─────────────────────────────────────────────┐
                    │        LANÇAMENTO DE CULTIVAR               │
                    │  Registro, Proteção, Comercialização        │
                    └─────────────────────────────────────────────┘

```
### 5.2 Fluxo de Mutações

```
Cultivar/Híbrido/Seleção 
    │
    ├─ Mutação 1 (ex: coloração mais intensa)
    │   ├─ Avaliação → Pode virar Seleção
    │   └─ Mutação 1.1 (mutação da mutação)
    │
    └─ Mutação 2 (ex: maturação precoce)
        └─ Avaliação → Pode virar Cultivar
```

### 5.3 Fluxo de Avaliação no BAG

```
Acessos do BAG
    │
    ├─ Caracterização fenológica
    ├─ Avaliação de características específicas
    └─ Identificação de potenciais parentais
        │
        └─ Transferência para Pomar de Parentais
```

---

## 6. Modelo de Dados Detalhado

### 6.1 Diagrama Entidade-Relacionamento (Conceitual)

#### Entidades Principais

**genotipo**
- id (PK)
- identificador_unico (unique) - ex: "M-2024-001"
- nome_designacao - Nome de trabalho
- tipo - [PARENTAL, SEEDLING, HIBRIDO, SELECAO, CULTIVAR, MUTANTE, ACESSO_BAG]
- origem - [CRUZAMENTO, MUTACAO, INTRODUCAO, COLETA]
- genitor_feminino_id (FK self)
- genitor_masculino_id (FK self)
- genotipo_original_id (FK self) - Para mutações
- alelos_s (JSONField) - ex: {"S1": "S3", "S2": "S5"}
- status - [ATIVO, INATIVO, DESCARTADO, MORTO]
- data_criacao
- observacoes
- criado_por_id (FK user)
- criado_em
- atualizado_em

**programa_melhoramento**
- id (PK)
- nome
- especie
- data_inicio
- responsavel_id (FK user)
- status

**ambiente**
- id (PK)
- nome - ex: "Matrizeiro Estação Experimental X"
- tipo - [MATRIZEIRO, BLOCO_HIBRIDOS, BLOCO_SELECOES, POMAR_PARENTAIS, BAG, CASA_VEGETACAO]
- localizacao - Texto descritivo
- municipio
- altitude
- area_hectares
- irmao_id (FK self) - Para ambientes pareados nos blocos de seleção
- responsavel_id (FK user)

**cruzamento**
- id (PK)
- identificador - ex: "CRUZ-2024-089"
- programa_id (FK programa_melhoramento)
- genitor_feminino_id (FK genotipo)
- genitor_masculino_id (FK genotipo)
- data_polinizacao
- ambiente_id (FK ambiente) - Onde foi realizado
- num_flores_polinizadas
- num_frutos_colhidos
- num_sementes_obtidas
- tecnico_id (FK user)
- observacoes

**plantio**
- id (PK)
- genotipo_id (FK genotipo)
- ambiente_id (FK ambiente)
- bloco
- linha
- planta
- repeticao - Para blocos de seleção (1-10)
- porta_enxerto_id (FK genotipo) - Específico da macieira
- data_plantio
- data_remocao
- status - [VIVA, MORTA, DOENTE, REMOVIDA]

**avaliacao_fenotipica**
- id (PK)
- plantio_id (FK plantio)
- genotipo_id (FK genotipo)
- safra - ex: "2025/2026"
- data_avaliacao
- fenologia (JSONField)
- fruto (JSONField)
- planta (JSONField)
- sanidade (JSONField)
- dados_adicionais (JSONField)
- avaliador_id (FK user)

**mutacao**
- id (PK)
- genotipo_original_id (FK genotipo)
- genotipo_mutante_id (FK genotipo)
- tipo - [GEMA, RAMO, SPORT, INDUZIDA]
- descricao_fenotipica
- data_observacao
- observador_id (FK user)

**primer**
- id (PK)
- nome - ex: "S3_F"
- sequencia
- alelo_alvo
- temperatura_anelamento
- comprimento_amplicon
- referencia

**protocolo_pcr**
- id (PK)
- nome
- ciclos_termicos (JSONField)
- mix_reacao (JSONField)
- observacoes
- primers (ManyToManyField)

**resultado_genotipagem**
- id (PK)
- genotipo_id (FK genotipo)
- primer_id (FK primer)
- protocolo_id (FK protocolo_pcr)
- resultado
- data_analise
- tecnico_id (FK user)
- arquivo_eletroforese (FileField)

**passaporte**
- id (PK)
- genotipo_id (FK genotipo, unique)
- numero_acesso
- dados_coleta (JSONField)
- genealogia_textual
- documento_pdf (FileField)
- data_geracao

### 6.2 Índices Recomendados

```sql
-- Performance para consultas genealógicas
CREATE INDEX idx_genotipo_genitores ON genotipo(genitor_feminino_id, genitor_masculino_id);

-- Busca por identificador único
CREATE UNIQUE INDEX idx_genotipo_identificador ON genotipo(identificador_unico);

-- Consultas de plantios ativos por ambiente
CREATE INDEX idx_plantio_ativo ON plantio(ambiente_id, status) WHERE status = 'VIVA';

-- Avaliações por safra
CREATE INDEX idx_avaliacao_safra ON avaliacao_fenotipica(genotipo_id, safra);

-- Busca por tipo de genótipo
CREATE INDEX idx_genotipo_tipo_status ON genotipo(tipo, status);
```

---

## 7. Controle de Acesso e Segurança

### 7.1 Estrutura de Papéis (RBAC)

```
Super Admin (TI)
    └── Admin Programa (Melhorista Chefe)
        ├── Melhoristas
        │   └── Pode: CRUD todos os dados do programa
        │
        ├── Fitotecnistas
        │   └── Pode: CRUD avaliações, visualizar tudo, não pode deletar
        │
        ├── Assistente de pesquisa
        │   └── Pode: Cadastrar plantios, avaliações; Visualizar dados
        │
        ├── Técnico de Campo e Laboratório
        │   └── Pode: Cadastrar primers, protocolos, resultados; Visualizar dados
        │
        └── Visitante/Estagiário
            └── Pode: Visualizar dados limitados, sem exportação
```

### 7.2 Matriz de Permissões Detalhada

| Funcionalidade | Admin | Melhoristas | Fitotecnistas | Assistente pesquisa | Técnicos | Visitante |
|----------------|-------|--------------|--------------|------------|----------|-----------|
| Criar/Editar Genótipos | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Planejar Cruzamentos | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Registrar Avaliações | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| Registrar Genotipagens | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Visualizar Dados | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* |
| Exportar Relatórios | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| Gerenciar Usuários | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |

*Dados limitados, sem informações sensíveis de futuros lançamentos

### 7.3 Auditoria (django-simple-history)

**Tabelas auditadas:**
- genotipo (todas as alterações)
- cruzamento
- avaliacao_fenotipica
- plantio

**Dados registrados automaticamente:**
- Usuário que fez a alteração
- Data/hora da alteração
- Tipo de alteração (criação, edição, deleção)
- Valores anteriores e novos
- Razão da alteração (campo opcional)

**Query de exemplo para auditoria:**
```python
# Quem alterou o status do genótipo X nos últimos 30 dias?
from simple_history.utils import get_history_manager

history = Genotipo.history.filter(
    id=genotipo_x,
    history_date__gte=timezone.now() - timedelta(days=30)
).values('history_user__username', 'history_date', 'history_type', 'status')
```

---

## 8. Integrações e APIs

### 8.1 Estrutura de APIs REST (Django REST Framework)

```python
# api/v1/genotipos/
GET    /api/v1/genotipos/              # Lista genótipos (com filtros)
POST   /api/v1/genotipos/              # Cria novo genótipo
GET    /api/v1/genotipos/{id}/         # Detalhes do genótipo
PUT    /api/v1/genotipos/{id}/         # Atualiza genótipo
GET    /api/v1/genotipos/{id}/tree/    # Árvore genealógica
GET    /api/v1/genotipos/{id}/passport/ # Gera/obtém passaporte

# api/v1/cruzamentos/
GET    /api/v1/cruzamentos/            # Lista cruzamentos
POST   /api/v1/cruzamentos/            # Planeja novo cruzamento

# api/v1/avaliacoes/
GET    /api/v1/avaliacoes/             # Lista avaliações com filtros
POST   /api/v1/avaliacoes/             # Registra nova avaliação
GET    /api/v1/avaliacoes/stats/       # Estatísticas agregadas

# api/v1/laboratorio/
GET    /api/v1/laboratorio/primers/     # Lista primers
POST   /api/v1/laboratorio/genotipagem/ # Registra resultado
```

### 8.2 Integrações Futuras (Planejadas)

- **Sistema de Informação Geográfica (SIG):** Mapeamento de campos
- **Equipamentos de Fenotipagem:** Drones, sensores automáticos
- **Sistema de Gestão Financeira:** Apenas leitura de custos operacionais
- **Plataformas de Bioinformática:** BLAST, bancos de dados de sequências

---

## 9. Plano de Implementação

### Fase 1 - Fundação (MVP) - 4-6 semanas
**Objetivo:** Sistema funcional mínimo para cadastro e rastreamento básico

- [x] Setup do projeto Django + PostgreSQL
- [x] Modelos: Genotipo, Ambiente, Cruzamento, Plantio
- [x] Django Admin customizado para CRUD básico
- [x] Autenticação e perfis de usuário
- [x] Auditoria básica com django-simple-history
- [x] Interface simples para cadastro de cruzamentos e seedlings

### Fase 2 - Funcionalidades Core - 6-8 semanas
**Objetivo:** Fluxo completo do pipeline de melhoramento

- [ ] Pipeline completo: Seedling → Híbrido → Seleção → Cultivar
- [ ] Avaliações Fenotípicas com campos configuráveis
- [ ] Árvore genealógica automática
- [ ] Controle de ambientes e blocos de seleção com repetições
- [ ] Gerenciamento de mutações
- [ ] Dashboard básico para melhoristas

### Fase 3 - Laboratório e Especializações - 4-6 semanas
**Objetivo:** Integração com dados laboratoriais

- [ ] Cadastro de primers e protocolos PCR
- [ ] Registro de resultados de genotipagem (alelos S)
- [ ] Seleção Assistida por Marcadores (SAM) básica
- [ ] Geração de passaporte de genótipos

### Fase 4 - Análises e Relatórios - 4-6 semanas
**Objetivo:** Ferramentas de apoio à decisão

- [ ] Cálculo de índices de seleção configuráveis
- [ ] Relatórios avançados (progresso do programa, genealogias)
- [ ] Exportação de dados para análise estatística (R/Python)
- [ ] Visualização gráfica de árvores genealógicas

### Fase 5 - Outras Espécies (Futuro)
**Objetivo:** Expandir arquitetura modular

- [ ] Módulo Milho
- [ ] Módulo Arroz
- [ ] Módulo Cebola

---

## 10. Glossário de Termos do Domínio

### Termos de Melhoramento da Macieira

| Termo | Definição |
|-------|-----------|
| **Autoincompatibilidade** | Mecanismo genético que impede a autofecundação, controlado pelos alelos S |
| **BAG** | Banco Ativo de Germoplasma - coleção de acessos para conservação |
| **Bloco de Híbridos** | Área onde cada planta é um genótipo único, primeira seleção individual |
| **Bloco de Seleções** | Área com repetições (10 plantas/genótipo) para avaliação avançada |
| **Cultivar** | Variedade comercial oficialmente lançada e registrada |
| **Híbrido** | Neste contexto, planta individual selecionada entre seedlings (não híbrido F1 comercial) |
| **Matrizeiro** | Área onde seedlings são plantados em população para seleção inicial |
| **Mutação/Sport** | Variação somática espontânea em um ramo ou gema |
| **Pomar de Parentais** | Coleção de genótipos utilizados como genitores nos cruzamentos |
| **Porta-enxerto** | Genótipo que forma o sistema radicular da planta composta |
| **SAM** | Seleção Assistida por Marcadores moleculares |
| **Seedling** | Plântula resultante de semente, fase juvenil da macieira |
| **Seleção** | Genótipo em fase avançada de avaliação, com múltiplas repetições |

### Termos Técnicos de Software

| Termo | Definição |
|-------|-----------|
| **DDD** | Domain-Driven Design - abordagem de design focada no domínio do negócio |
| **ORM** | Object-Relational Mapping - mapeamento entre objetos e banco de dados relacional |
| **RBAC** | Role-Based Access Control - controle de acesso baseado em papéis |
| **MVP** | Minimum Viable Product - produto mínimo viável |
| **Audit Trail** | Registro cronológico de todas as alterações em dados críticos |

---

## Apêndice A: Comandos Úteis para Início Rápido

### Setup do Ambiente de Desenvolvimento

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install django==5.0 psycopg2-binary djangorestframework django-simple-history

# Criar projeto
django-admin startproject melhoramento_genetico
cd melhoramento_genetico
python manage.py startapp core
python manage.py startapp macieira

# Configurar banco de dados (settings.py)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'melhoramento_db',
        'USER': 'melhoramento_user',
        'PASSWORD': 'sua_senha_segura',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Criar migrações
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

---

## Apêndice B: Exemplos de Consultas Genealógicas

### Árvore Genealógica Recursiva (Python/Django)

```python
from django.db.models import Q

def construir_arvore_genealogica(genotipo, profundidade_max=5, profundidade_atual=0):
    """
    Constrói árvore genealógica recursivamente
    
    Args:
        genotipo: Instância do modelo Genotipo
        profundidade_max: Profundidade máxima da árvore
        profundidade_atual: Controle da recursão
    
    Returns:
        dict: Árvore genealógica estruturada
    """
    if profundidade_atual >= profundidade_max or genotipo is None:
        return None
    
    return {
        'id': genotipo.id,
        'identificador': genotipo.identificador_unico,
        'nome': genotipo.nome_designacao,
        'tipo': genotipo.tipo,
        'mae': construir_arvore_genealogica(
            genotipo.genitor_feminino, 
            profundidade_max, 
            profundidade_atual + 1
        ),
        'pai': construir_arvore_genealogica(
            genotipo.genitor_masculino, 
            profundidade_max, 
            profundidade_atual + 1
        ),
    }

def buscar_descendentes(genotipo):
    """
    Encontra todos os descendentes de um genótipo
    
    Args:
        genotipo: Instância do modelo Genotipo
    
    Returns:
        QuerySet: Todos os genótipos descendentes
    """
    descendentes = Genotipo.objects.filter(
        Q(genitor_feminino=genotipo) | 
        Q(genitor_masculino=genotipo)
    )
    
    # Busca recursiva
    for filho in descendentes:
        descendentes = descendentes | buscar_descendentes(filho)
    
    return descendentes.distinct()

def validar_compatibilidade_cruzamento(genotipo_mae, genotipo_pai):
    """
    Verifica compatibilidade de alelos S para cruzamento
    
    Args:
        genotipo_mae: Genótipo feminino
        genotipo_pai: Genótipo masculino
    
    Returns:
        tuple: (compativel, mensagem)
    """
    alelos_mae = set(genotipo_mae.alelos_s.values())
    alelos_pai = set(genotipo_pai.alelos_s.values())
    
    if not alelos_mae or not alelos_pai:
        return (False, "Alelos S não cadastrados para um dos genitores")
    
    if alelos_mae & alelos_pai:
        return (False, "Incompatível: compartilham alelos S")
    
    return (True, "Cruzamento compatível")
```

---

## Controle de Versão do Documento

| Versão | Data | Autor | Alterações |
|--------|------|-------|------------|
| 1.0 | Jul/2026 | [Nome] | Versão inicial completa |

```