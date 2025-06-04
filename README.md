
# 🔎 CSV Inspector

![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)

Um aplicativo interativo em **Streamlit** para análise exploratória automática de arquivos CSV.  
Ideal para quem quer entender rapidamente a estrutura, qualidade e padrões dos dados — sem precisar programar!

---

## 🚀 Demonstração Online

> [Acesse o app no Streamlit](https://csv-inspector.streamlit.app/)

---

## ✨ Funcionalidades

- **Upload de CSV**: Carregue qualquer arquivo CSV para análise.
- **Visualização dos Dados**: Veja a tabela completa no navegador.
- **Relatório Exploratória Automático**:
  - Informações gerais (linhas, colunas, tipos de dados)
  - Valores ausentes
  - Estatísticas descritivas (média, mediana, desvio padrão, mínimo, máximo)
  - Análise de colunas categóricas (moda, frequência, diversidade)
  - Diversidade de valores por coluna
- **Download do Relatório**: Baixe o relatório em `.txt`.
- **Gráficos Automáticos**:
  - **Boxplots** para colunas numéricas
  - **Gráficos de barras** para colunas categóricas
  - Visualização lado a lado para facilitar a análise
- **Interface amigável**: Tudo organizado em expansores, sem poluição visual.
- **Em breve**: Exportação em PDF e HTML.

---

## 🖼️ Exemplos Visuais

> **Adicione aqui printscreens do app rodando!**
>
> - Upload de CSV
> - Relatório exploratório
> - Gráficos automáticos

---

## ⚙️ Como usar

### 1. Clone o repositório

```bash
git clone https://github.com/j-pdro/csv_inspector.git
cd csv_inspector
```

### 2. Crie o ambiente virtual e instale as dependências

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Rode o app

```bash
streamlit run app.py
```

---

## 🧪 Testes

Execute os testes unitários com:

```bash
pytest tests/
```

---

## 📦 Estrutura do Projeto

```
csv_inspector/
│
├── app.py
├── report_generator.py
├── requirements.txt
├── tests/
│   └── test_report_generator.py
└── ...
```

---

## 🛣️ Roadmap

- [x] Relatório TXT e Markdown
- [x] Gráficos automáticos (boxplot, barras)
- [x] Testes unitários
- [ ] Exportação em PDF/HTML
- [ ] Filtros e seleção de colunas para gráficos
- [ ] Melhorias visuais e responsividade

---

## 📢 Licença

MIT

---

```