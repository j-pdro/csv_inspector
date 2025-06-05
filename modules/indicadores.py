# modules/indicadores.py
import streamlit as st
import pandas as pd
from utils import stats_helpers # Importa funções auxiliares para estatísticas
# Importação para os relatórios
from utils.indicadores_report_generator import generate_txt_report, generate_markdown_report

def run_indicadores(df: pd.DataFrame, filename: str):
    """
    Executa a Calculadora de Indicadores Estatísticos no DataFrame fornecido.

    Parâmetros:
      df (pd.DataFrame): DataFrame com os dados a serem analisados.
      filename (str): Nome do arquivo original, usado para os relatórios.
    """
    st.header("Cálculo de Indicadores Estatísticos")

    # 1. Identificar tipos de colunas
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if not numeric_cols:
        st.error("Nenhuma coluna numérica encontrada no arquivo para calcular indicadores.")
        st.info("Este módulo foca em indicadores para dados numéricos. Verifique seu CSV ou use o módulo de EDA para uma análise mais geral.")
        return

    # 2. Criar as Tabs
    tab_titles = ["Descritivas", "Skew/Kurtosis", "Correlação", "Missing", "Por Categoria", "Exportar"]
    tabs = st.tabs(tab_titles)

    # Tab 0: Estatísticas Descritivas
    with tabs[0]:
        st.subheader("📌 Estatísticas Descritivas")
        if not numeric_cols:
            st.info("Nenhuma coluna numérica disponível.")
        else:
            selected_desc_cols = st.multiselect(
                "Selecione colunas numéricas para estatísticas descritivas:",
                numeric_cols,
                default=numeric_cols,
                key="desc_num_cols"
            )
            if selected_desc_cols:
                stats_helpers.show_descriptive_stats(df, selected_desc_cols, st)
            else:
                st.info("Selecione pelo menos uma coluna numérica.")

    # Tab 1: Skewness e Kurtosis
    with tabs[1]:
        st.subheader("📏 Skewness (Assimetria) e Kurtosis (Curtose)")
        if not numeric_cols:
            st.info("Nenhuma coluna numérica disponível.")
        else:
            selected_skew_kurt_cols = st.multiselect(
                "Selecione colunas numéricas para Skewness/Kurtosis:",
                numeric_cols,
                default=numeric_cols,
                key="skew_kurt_num_cols"
            )
            if selected_skew_kurt_cols:
                stats_helpers.show_skew_kurtosis(df, selected_skew_kurt_cols, st)
            else:
                st.info("Selecione pelo menos uma coluna numérica.")

    # Tab 2: Matriz de Correlação
    with tabs[2]:
        st.subheader("🔗 Matriz de Correlação")
        if len(numeric_cols) < 2:
            st.info("São necessárias pelo menos duas colunas numéricas para calcular a correlação.")
        else:
            selected_corr_cols = st.multiselect(
                "Selecione colunas numéricas para a matriz de correlação:",
                numeric_cols,
                default=numeric_cols[:min(5, len(numeric_cols))], # Default para as primeiras 5 ou menos
                key="corr_num_cols"
            )
            corr_method = st.selectbox(
                "Método de correlação:",
                ["pearson", "spearman", "kendall"],
                key="corr_method"
            )
            if selected_corr_cols and len(selected_corr_cols) >= 2:
                stats_helpers.show_correlation_matrix(df, selected_corr_cols, corr_method, st)
            elif selected_corr_cols and len(selected_corr_cols) < 2:
                 st.warning("Selecione pelo menos duas colunas numéricas para a correlação.")
            else:
                st.info("Selecione colunas numéricas.")

    # Tab 3: Dados Ausentes (Missing)
    with tabs[3]:
        st.subheader("❓ Análise de Dados Ausentes")
        # Esta função mostrará uma tabela de contagem e percentual de nulos para todas as colunas.
        stats_helpers.show_missing_table(df, st)

    # Tab 4: Métricas por Categoria
    with tabs[4]:
        st.subheader("📊 Métricas Agrupadas por Categoria")
        if not categorical_cols:
            st.info("Nenhuma coluna categórica encontrada para agrupamento.")
        elif not numeric_cols:
            st.info("Nenhuma coluna numérica encontrada para agregar.")
        else:
            selected_cat_col_group = st.selectbox(
                "Selecione a coluna categórica para agrupar:",
                categorical_cols,
                key="group_cat_col"
            )
            selected_num_cols_group = st.multiselect(
                "Selecione colunas numéricas para agregar:",
                numeric_cols,
                default=numeric_cols,
                key="group_num_cols"
            )
            agg_func_group = st.selectbox(
                "Selecione a função de agregação:",
                ["mean", "median", "sum", "count", "std", "var", "min", "max"], # Adicionando mais opções
                key="group_agg_func"
            )
            if selected_cat_col_group and selected_num_cols_group and agg_func_group:
                stats_helpers.show_grouped_metrics(df, selected_cat_col_group, selected_num_cols_group, agg_func_group, st)
            else:
                st.info("Certifique-se de selecionar uma coluna categórica, pelo menos uma numérica e uma função de agregação.")

    # Tab 5: Exportar Relatórios
    with tabs[5]:
        st.subheader("📤 Exportar Relatório de Indicadores")
        st.markdown("Gere e baixe um relatório com os principais indicadores estatísticos calculados.")

        # As colunas para o relatório podem ser as selecionadas na primeira tab, ou todas as numéricas.
        # Vamos usar todas as numéricas por padrão para o relatório, ou as selecionadas na tab "Descritivas".
        # Para simplificar, usaremos todas as numéricas do DataFrame original para o relatório.
        # Se quiser mais controle, podemos adicionar um multiselect aqui.
        
        cols_for_report = numeric_cols # Usando todas as colunas numéricas para o relatório

        if not cols_for_report:
            st.warning("Nenhuma coluna numérica para incluir no relatório.")
        else:
            st.info(f"O relatório será gerado considerando as seguintes colunas numéricas: {', '.join(cols_for_report)}")
            
            try:
                # Gerar o conteúdo dos relatórios
                # As funções vêm de utils.indicadores_report_generator
                # Elas esperam df, filename, e uma lista de colunas.
                report_io_txt = generate_txt_report(df, filename, cols_for_report)
                report_str_md = generate_markdown_report(df, filename, cols_for_report)

                # Preparar dados para download
                data_txt = report_io_txt.getvalue().encode("utf-8")
                data_md = report_str_md.encode("utf-8")

                # Definir nomes dos arquivos para download
                base_filename = filename.split('.')[0] if '.' in filename else filename
                download_filename_txt = f"indicadores_report_{base_filename}.txt"
                download_filename_md = f"indicadores_report_{base_filename}.md"

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📥 Baixar relatório (.txt)",
                        data=data_txt,
                        file_name=download_filename_txt,
                        mime="text/plain",
                        key="download_txt_indicadores"
                    )
                with col2:
                    st.download_button(
                        label="📥 Baixar relatório (.md)",
                        data=data_md,
                        file_name=download_filename_md,
                        mime="text/markdown",
                        key="download_md_indicadores"
                    )
            except Exception as e:
                st.error(f"Erro ao gerar ou preparar relatórios para download: {e}")
                st.warning("Verifique as funções em 'indicadores_report_generator.py' e as colunas selecionadas.")