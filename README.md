README.md

# 📊 CSV Analyzer Inteligente

Aplicação web construída com Streamlit para realizar análise exploratória de dados em arquivos CSV. Permite visualizar dados, gerar relatórios detalhados e baixar resultados.

## 🚀 Funcionalidades Implementadas

### Upload de CSV
- Suporte a arquivos `.csv` via `st.file_uploader`.

### Visualização de Dados
- Exibição dentro de `st.expander` para ocultar/mostrar a tabela.

### Geração de Relatório
- **TXT (download):** via `generate_txt_report()`.
- **Markdown (exibição):** via `generate_markdown_report()`.

#### Seções do relatório:
1. Informações Gerais
2. Tipos de Dados por Coluna
3. Valores Ausentes
4. Estatísticas Descritivas
5. Diversidade de Valores
6. Observações Finais

### Exibição Organizada
- Uso de `st.expander` para declutter da interface.
- Relatório formatado com Markdown para melhor legibilidade.

### Download de Relatório
- Botão para baixar `.txt`.
- Mensagem indicativa de futura opção de PDF.

## 📁 Estrutura de Pastas

```
csv_inspector/
├── app.py                  # App principal Streamlit
├── report_generator.py     # Funções de geração de relatório (TXT e Markdown)
├── utils/                  # Módulos auxiliares (futuro)
│   └── logger_config.py    # Configuração de logging
├── sample_data/            # CSVs de exemplo
│   └── exemplo.csv
├── logs/                   # Diretório de logs da aplicação
│   └── app.log
├── requirements.txt        # Dependências
└── README.md               # Documentação
```

## 🛠️ Próximos Passos (Tasks)

### Testes Unitários Simples
- Criar testes para `generate_txt_report()`:
  - Verificar que o buffer não é vazio.
  - Conferir presença de seções-chave (título, informações gerais).
- Criar testes para `generate_markdown_report()`:
  - Validar que o output começa com `## 📊 Relatório`.
  - Garantir que todas as colunas do DataFrame aparecem.

### Configuração de Logging
- Implementar `utils/logger_config.py` e integrar ao `app.py`:
  - Registrar eventos de upload bem-sucedido.
  - Registrar erros em `try-except`.
- Testar geração de `logs/app.log` com entradas de `INFO` e `ERROR`.

### Validações e Segurança
- Adicionar checagens antes da análise:
  - Garantir que o CSV tenha pelo menos uma coluna numérica.
  - Tratar arquivos mal formatados com mensagem amigável.

### Melhoria de Relatório
- Incluir contagem de duplicatas.
- Adicionar correlação entre variáveis numéricas.

### Download em PDF
- Pesquisar e integrar biblioteca (ex: `pdfkit` ou `reportlab`).
- Gerar PDF com gráficos estáticos exportados como imagens.

### Deploy no Streamlit Cloud
- Conectar repositório GitHub.
- Configurar branch principal e `requirements.txt`.
- Publicar e validar funcionamento online.

## 📥 Como Rodar Localmente

```bash
git clone git@github.com:j-pdro/csv_inspector.git
cd csv_inspector
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
streamlit run app.py
```

---

Desenvolvido como parte do seu portfólio de Ciência de Dados, com foco em código limpo, boas práticas e interatividade.
