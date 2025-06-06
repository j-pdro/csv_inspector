# 📊 Suíte de Análise e Pré-Processamento de Dados Interativa

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-ff4b4b.svg)](https://streamlit.io)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458.svg)](https://pandas.pydata.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Uma plataforma unificada que acompanha o cientista de dados desde o primeiro contato com um CSV até a geração de um dataset limpo e pronto para modelagem. Explore, analise, limpe e transforme seus dados através de uma interface 100% visual, interativa e não-destrutiva.**

---

### ✨ Demonstração Rápida

<!-- *(Aqui é o lugar perfeito para um GIF mostrando o fluxo completo: upload -> navegação na aba de Análise Exploratória -> cálculo de alguns Indicadores Estatísticos -> aplicação de duas transformações no Pré-Processamento -> clique no "Desfazer" -> download do pipeline.)*

![GIF de Demonstração do App](https://placeholder.com/wp-content/uploads/2022/06/placeholder-image.png) 
*<-- Substitua por um GIF real da aplicação em uso!* -->

---

## 🚀 Sobre o Projeto

Este projeto nasceu da necessidade de unificar as etapas iniciais e mais repetitivas do ciclo de vida de um projeto de dados. Em vez de alternar entre notebooks para análise e scripts para limpeza, esta ferramenta oferece uma **workstation completa** em Streamlit.

Ela permite que o usuário execute todo o fluxo de trabalho de forma visual e controlada:
1.  **Análise Exploratória (EDA):** Entenda a estrutura, a qualidade e a distribuição dos seus dados.
2.  **Análise Estatística:** Calcule métricas fundamentais para validar hipóteses e guiar as próximas etapas.
3.  **Pré-processamento Avançado:** Aplique transformações complexas com a segurança de poder desfazer qualquer ação e a capacidade de exportar todo o fluxo de trabalho.

O grande diferencial é o sistema de **edição não-destrutiva com pipeline reutilizável**, que une a flexibilidade da análise manual com as melhores práticas de MLOps e automação.

> - Upload de CSV
> - Relatório exploratório
> - Gráficos automáticos

Para testar rapidamente, use o arquivo de exemplo disponível no kaggle:
 - [CSV usado para a demonstração](https://www.kaggle.com/datasets/jayaantanaath/student-habits-vs-academic-performance)

#### Basta fazer o download e fazer upload no app!
---

## 🎯 Funcionalidades por Módulo

### 1. 🧠 Analisador de CSV Inteligente (EDA)
*   Upload intuitivo de arquivos `.csv`.
*   Visualização interativa do DataFrame completo.
*   Análise de tipos de dados, contagem de nulos e uso de memória por coluna.
*   Geração de gráficos de distribuição para entender as features visivelmente.


### 2. 🔢 Calculadora de Indicadores Estatísticos
*   Cálculo de estatísticas descritivas (média, mediana, desvio padrão, quartis) para colunas numéricas.
*   Visualização de correlações através de heatmaps.
*   Geração de boxplots para análise de outliers e comparação de distribuições.

### 3. 🧹 Módulo de Pré-Processamento Avançado
*   **Tratamento de Nulos:** Estratégias de remoção ou preenchimento (média, mediana, moda, etc.).
*   **Remoção de Duplicatas:** Limpeza de registros repetidos.
*   **Conversão de Tipos:** Correção de tipos de dados de colunas.
*   **Codificação de Categóricas:** Suporte a **Label Encoding** e **One-Hot Encoding**.
*   **Escalonamento de Numéricas:** Normalização (Min-Max) e Padronização (Standard Scaler).
*   **↩️ Desfazer Ilimitado:** Desfaça qualquer transformação com um único clique.
*   **📄 Pipeline Exportável:** Salve todos os passos em um arquivo `.json` para reuso e automação.
*   **⚙️ Processamento em Lote:** Aplique um pipeline salvo a um novo dataset instantaneamente.

## 🛠️ Tecnologias Utilizadas

*   **🐍 Python:** A linguagem base para toda a lógica.
*   **🎈 Streamlit:** Para a criação da interface web interativa.
*   **🐼 Pandas:** Para a manipulação e estruturação dos dados.
*   **🤖 Scikit-Learn:** Para as operações de escalonamento e codificação.
*   **📦 NumPy:** Para cálculos numéricos eficientes.

## ⚙️ Instalação e Execução

Para executar este projeto localmente, siga os passos abaixo.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2.  **Crie e ative um ambiente virtual (Recomendado):**
    ```bash
    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação Streamlit:**
    ```bash
    streamlit run app.py
    ```
    A aplicação abrirá automaticamente no seu navegador padrão!

## 📖 Como Usar

1.  **Carregue seus Dados:** Inicie a aplicação e faça o upload de um arquivo `.csv`.
2.  **Explore e Transforme:** Navegue pelas abas (`Tratar Nulos`, `Duplicatas`, `Tipos de Dados`, etc.) para aplicar as transformações desejadas.
3.  **Controle Suas Ações:** Use os botões **"Desfazer Última Ação"** ou **"Resetar DataFrame"** a qualquer momento.
4.  **Visualize e Baixe:** Na aba **"Visualizar/Baixar Interativo"**, você pode:
    *   Ver uma prévia do seu DataFrame transformado.
    *   Analisar as informações e tipos de dados.
    *   Baixar o CSV processado.
    *   Baixar o pipeline de transformações (`.json`) que você criou.
5.  **Automatize com o Pipeline:** Na aba **"Aplicar Pipeline em Lote"**, carregue o arquivo `.json` salvo e um novo CSV para aplicar as mesmas transformações instantaneamente.

### 🔬 O Arquivo de Pipeline (`.json`)

O pipeline salvo é um arquivo JSON legível que descreve cada passo aplicado. Ele é a "receita" do seu pré-processamento.

**Exemplo de estrutura:**
```json
[
  {
    "operation_name": "Remoção de Linhas Duplicadas",
    "parameters": {
      "details": "Todas as duplicatas removidas (mantendo a primeira ocorrência)."
    }
  },
  {
    "operation_name": "Escalonamento de Colunas Numéricas",
    "parameters": {
      "columns_to_scale": [
        "idade",
        "salario"
      ],
      "method": "Min-Max Scaler (Normalização)"
    }
  }
]
```

## 🗺️ Roadmap de Futuras Melhorias

Este projeto está em desenvolvimento ativo. Aqui estão algumas das funcionalidades planejadas:

- [x] Implementar sistema de Undo para todas as operações.
- [ ] Adicionar mais estratégias de tratamento de nulos (ex: interpolação).
- [ ] Implementar funcionalidade de **Remoção de Colunas**.
- [ ] Implementar funcionalidade de **Renomear Colunas**.
- [ ] Adicionar mais opções de **Feature Engineering** (ex: criação de colunas a partir de operações matemáticas).
- [ ] Integrar visualizações (gráficos) para dar feedback instantâneo sobre o impacto de cada transformação.
- [ ] Escrever testes unitários com `pytest` para garantir a robustez das funções de backend.

## 🤝 Como Contribuir

Contribuições são o que tornam a comunidade de código aberto um lugar incrível para aprender, inspirar e criar. Qualquer contribuição que você fizer será **muito bem-vinda**.

1.  Faça um **Fork** do projeto.
2.  Crie uma **Branch** para sua feature (`git checkout -b feature/AmazingFeature`).
3.  Faça o **Commit** de suas alterações (`git commit -m 'Add some AmazingFeature'`).
4.  Faça o **Push** para a Branch (`git push origin feature/AmazingFeature`).
5.  Abra um **Pull Request**.

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](https://github.com/j-pdro/csv_inspector/blob/main/LICENSE) para mais informações.

## 📧 Contato

[LinkedIn](https://www.linkedin.com/in/devjp/)

````
