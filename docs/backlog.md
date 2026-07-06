# Backlog de Melhorias - Sistema de Melhoramento Genético Vegetal

**Versão atual:** MVP 1.0  
**Data:** Julho 2026  

---

## Versão 2.0 - Melhorias Core e Sanidade

### Melhorias de Usabilidade

| ID | Funcionalidade | Descrição | Prioridade |
|----|---------------|-----------|------------|
| US01 | Validação de alelos S | Impedir cruzamentos entre genótipos com alelos S incompatíveis | Alta |
| US02 | Botão "Promover" na tela | Botão "Promover para Seleção/Cultivar" dentro da página do genótipo (igual ao "Registrar Mutante") | Alta |
| US03 | Contador automático de avanço | `num_bloco_hibridos` incrementa automaticamente quando um híbrido é criado a partir do cruzamento | Média |
| US04 | Upload múltiplo de fotos | Galeria de imagens por genótipo (múltiplos uploads) | Média |
| US05 | Miniaturas no admin | Exibir thumbnail das fotos na listagem do admin | Média |
| US06 | Legendas para fotos | Permitir nomes/descrições customizadas para cada foto | Baixa |

### Módulo de Sanidade (Fitossanidade)

| ID | Funcionalidade | Descrição | Prioridade |
|----|---------------|-----------|------------|
| SA01 | Cadastro de doenças | CRUD para doenças (nome comum, nome científico) | Alta |
| SA02 | Cadastro de patógenos | CRUD para agentes causais (fungo, bactéria, vírus) vinculado à doença | Alta |
| SA03 | Tipo de resistência | Campo no genótipo: resistência vertical (imunidade) ou horizontal (parcial) | Alta |
| SA04 | Nível de resistência | Para resistência parcial: escala ou percentual de resistência | Média |
| SA05 | Mapeamento genético | Campo para loco gênico associado à resistência (ex: Rvi6, Vf) | Média |
| SA06 | Observações de resistência | Campo texto livre para notas do melhorista | Baixa |
| SA07 | Cadastro de insetos-praga | CRUD para insetos que atacam a cultura | Média |
| SA08 | Resistência a insetos | Registro de não-preferência, antibiose ou tolerância | Média |
| SA09 | Filtro por resistência | "Quais genótipos possuem resistência à doença X?" | Alta |

---

## Versão 3.0 - Interface e Experiência

| ID | Funcionalidade | Descrição | Prioridade |
|----|---------------|-----------|------------|
| UI01 | Árvore genealógica visual | Gráfico interativo (D3.js) em vez de texto indentado | Média |
| UI02 | Dashboard público aprimorado | Layout profissional, QR code, versão para impressão | Média |
| UI03 | Busca no dashboard público | Campo de pesquisa por nome ou identificador | Baixa |
| UI04 | Telas customizadas | Interface própria para técnicos de campo (além do admin) | Baixa |
| UI05 | Exportação de dados | Botão para exportar tabelas em CSV/Excel | Média |
| UI06 | Relatórios em PDF | Geração de relatórios de passaporte, cruzamentos, etc. | Média |

---

## Versão 4.0 - Expansão para Outras Culturas

| ID | Funcionalidade | Descrição | Prioridade |
|----|---------------|-----------|------------|
| EX01 | Módulo Milho | Adaptação do sistema para Zea mays | Planejado |
| EX02 | Módulo Arroz | Adaptação do sistema para Oryza sativa | Planejado |
| EX03 | Módulo Cebola | Adaptação do sistema para Allium cepa | Planejado |

---

## Bugs Conhecidos

| ID | Descrição | Status |
|----|-----------|--------|
| - | Nenhum bug reportado até o momento | - |

---

## Convenções

- **Alta:** Implementar na próxima versão
- **Média:** Implementar em até 2 versões
- **Baixa:** Quando houver oportunidade
- **Planejado:** Sem data definida

---

**Atualizado em:** Julho 2026  
**Responsável:** Equipe de Melhoramento Genético da Macieira - Epagri
