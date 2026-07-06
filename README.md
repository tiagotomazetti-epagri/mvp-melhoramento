# 🍎 Sistema de Gestão de Melhoramento Genético Vegetal - Módulo Macieira

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

MVP do sistema modular para gestão operacional do programa de melhoramento genético da macieira (*Malus domestica*), desenvolvido para a Epagri.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Stack Tecnológica](#stack-tecnológica)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Uso](#uso)
- [Backlog](#backlog)
- [Licença](#licença)

## 🔍 Visão Geral

MVP desenvolvido para digitalizar a gestão operacional do programa de melhoramento genético da macieira na Epagri (Empresa de Pesquisa Agropecuária e Extensão Rural de Santa Catarina).

O sistema cobre o pipeline completo de melhoramento: cruzamento controlado → seedling → híbrido → seleção → cultivar, com rastreabilidade total de genealogia e mutações.

**Acesso ao sistema:**
- Área administrativa: `/admin` (login obrigatório)
- Dashboard público de passaportes: `/` (acesso livre)

## ✨ Funcionalidades

### Pipeline de Melhoramento
- [x] Cadastro de genótipos com identificador único automático (M-AAAA-NNNNN)
- [x] Planejamento e registro de cruzamentos controlados
- [x] Rastreamento de população (plântulas → matrizeiro → bloco híbridos)
- [x] Botão "Novo Híbrido" a partir do cruzamento (importa genitores automaticamente)
- [x] Promoção de material: Híbrido → Seleção → Cultivar (ações em lote)
- [x] Registro de mutações com botão "Registrar Mutante" na tela do genótipo
- [x] Herança automática de genealogia e alelos S para mutantes

### Genealogia
- [x] Árvore genealógica visual na tela do genótipo (até 4 gerações)
- [x] Links clicáveis para navegar entre parentais
- [x] Mutações de mutações em cascata

### Genética
- [x] Alelos S em dois campos dropdown independentes (S1 a S30)
- [x] Exibição combinada (ex: S3/S5)

### Avaliações
- [x] Fenotipagem: fruto (massa, firmeza, °Brix), fenologia, sanidade
- [x] Upload de fotos (planta, fruto, frutos colhidos, sintomas)
- [x] Múltiplas safras

### Dashboard Público
- [x] Página inicial com cards de seleções, cultivares e mutantes
- [x] Controle de publicação (campo `publicar_passaporte`)
- [x] Exibição de foto, nome, alelos S e genealogia resumida

### Segurança e Auditoria
- [x] Controle de acesso baseado em grupos (admin)
- [x] Histórico de alterações em todos os modelos (django-simple-history)
- [x] Registro de usuário, data/hora e tipo de operação

## 🛠️ Stack Tecnológica

| Camada | Tecnologia |
|--------|------------|
| **Linguagem** | Python 3.11+ |
| **Framework Web** | Django 5.0 |
| **Banco de Dados** | SQLite (dev) / PostgreSQL 16+ (prod) |
| **Frontend** | Django Templates + HTML/CSS |
| **Auditoria** | django-simple-history |
| **Imagens** | Pillow |

## 📁 Estrutura do Projeto

```
mvp-melhoramento/
├── config/                     # Configurações do projeto Django
│   ├── settings.py
│   └── urls.py
├── macieira/                   # App principal
│   ├── models.py              # Modelos: Genotipo, Cruzamento, Ambiente, Plantio, AvaliacaoFenotipica
│   ├── admin.py               # Configuração do Django Admin
│   └── views.py               # View do dashboard público
├── templates/                  # Templates HTML
│   ├── admin/
│   │   └── macieira/
│   │       └── genotipo/
│   │           └── change_form.html  # Botão "Registrar Mutante"
│   └── dashboard_passaportes.html    # Página inicial pública
├── media/                      # Uploads de fotos
├── docs/                       # Documentação
│   ├── arquitetura.md
│   └── backlog.md
├── manage.py
├── requirements.txt
├── LICENSE
└── README.md
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- Git

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/tiagotomazetti-epagri/mvp-melhoramento.git
cd mvp-melhoramento

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute as migrações
python manage.py migrate

# 5. Crie o superusuário
python manage.py createsuperuser

# 6. Inicie o servidor
python manage.py runserver
```

Acesse:
- **Dashboard público:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin

### Compartilhar na rede local

```bash
python manage.py runserver 0.0.0.0:8000
# Colegas acessam: http://SEU_IP:8000
```

## 📖 Uso

### Fluxo típico

1. **Cadastre parentais** no admin (tipo PARENTAL, preencher alelos S)
2. **Crie um cruzamento** informando genitores e dados de polinização
3. **Registre seedlings** como tipo SEEDLING, vinculando aos genitores
4. **Crie híbridos** pelo botão "Novo Híbrido" na listagem de cruzamentos
5. **Promova para seleção** selecionando híbridos e usando a ação "Promover para Seleção"
6. **Promova para cultivar** selecionando seleções e usando a ação "Promover para Cultivar"
7. **Publique passaportes** marcando `publicar_passaporte = Sim` nos genótipos desejados

### Perfis de usuário sugeridos

| Perfil | Permissões |
|--------|------------|
| Admin | Acesso total |
| Melhorista | CRUD completo |
| Técnico | Criar avaliações e plantios |
| Visitante | Apenas visualização |

## 📋 Backlog

As melhorias planejadas estão documentadas em [`docs/backlog.md`](docs/backlog.md).

Destaques para a próxima versão:
- Validação de compatibilidade de alelos S em cruzamentos
- Módulo de sanidade (doenças, patógenos, resistência)
- Upload múltiplo de fotos com miniaturas
- Contador automático de plantas avançadas

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

### Canais de Atendimento

- **Email:** tiagotomazetti@epagri.sc.gov.br
- **Issues:** [GitHub Issues](https://github.com/tiagotomazetti-epagri/mvp-melhoramento/issues)
- **Wiki:** [Wiki do Projeto](https://github.com/tiagotomazetti-epagri/mvp-melhoramento/wiki)
- **Plantão:** 
    - Ramal: 010 16846
    - Núm. Externo: (49)35616846

### Equipe

| Nome | Papel | Contato |
|------|-------|---------|
| Tiago Camponogara Tomazetti | Melhorista e Desenvolvedor | tiagotomazetti@epagri.sc.gov.br |
| Marcus Vinicius Kvitschal | Melhorista | marcusvinicius@epagri.sc.gov.br |
| Liane Bahr Thurow | Melhorista | lianethurow@epagri.sc.gov.br |

---

**Última atualização:** Julho 2026

---

---
*Desenvolvido com ❤️ pela equipe do Programa de Melhoramento Genético da macieira* - **Epagri**

📧 Contato: tiagotomazetti@epagri.sc.gov.br
