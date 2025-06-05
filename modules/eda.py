import streamlit as st
import pandas as pd
from utils import helpers as plot_helpers  # Importação de plot_helpers <-- chamando todos os "plots" do utils/helpers.py
from utils.eda_report_generator import generate_txt_report, generate_markdown_report

def run_eda(df: pd.DataFrame, filename: str):
    """
    Executa a Análise Exploratória de Dados no DataFrame fornecido.

    Parâmetros:
      df (pd.DataFrame): DataFrame com os dados a serem analisados.
      filename (str): Nome do arquivo original, usado para os relatórios.
    """
    st.header("Visualização e Análise Detalhada")

    # 1. Identificar tipos de colunas
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # 2. Criar as Tabs
    tab_titles = ["Visão Geral", "Histograma", "Box/Violin", "Barra", "Heatmap", "Pairplot", "Missing", "Exportar"]
    tabs = st.tabs(tab_titles)

    # Tab 0: Visão Geral (Adicionada para visualização inicial do DF)
    with tabs[0]:
        st.subheader("Visualização dos Dados")
        st.dataframe(df.head())
        st.subheader("Informações Gerais do DataFrame")
        st.text(f"Número de Linhas: {df.shape[0]}")
        st.text(f"Número de Colunas: {df.shape[1]}")
        st.subheader("Tipos de Dados por Coluna")
        st.dataframe(df.dtypes.reset_index().rename(columns={'index': 'Coluna', 0: 'Tipo de Dado'}))


    # Tab 1: Histograma
    with tabs[1]:
        st.subheader("Histogramas de Colunas Numéricas")
        if not numeric_cols:
            st.info("Nenhuma coluna numérica encontrada para plotar histogramas.")
        else:
            selected_numeric_hist = st.multiselect(
                "Selecione colunas numéricas para Histograma:",
                numeric_cols,
                default=numeric_cols[:min(3, len(numeric_cols))], # Default para as primeiras 3 ou menos
                key="hist_num_cols"
            )
            if selected_numeric_hist:
                plot_helpers.plot_histograms(df, selected_numeric_hist, st) # Usando st diretamente ou um container
            else:
                st.info("Selecione pelo menos uma coluna numérica para gerar histogramas.")

    # Tab 2: Box/Violin Plot
    with tabs[2]:
        st.subheader("Boxplots e Violin Plots de Colunas Numéricas")
        if not numeric_cols:
            st.info("Nenhuma coluna numérica encontrada para estes gráficos.")
        else:
            chart_type_bv = st.selectbox(
                "Tipo de gráfico:",
                ["Boxplot", "Violin plot"],
                key="bv_chart_type"
            )
            selected_numeric_bv = st.multiselect(
                "Selecione colunas numéricas para Box/Violin Plot:",
                numeric_cols,
                default=numeric_cols[:min(3, len(numeric_cols))],
                key="bv_num_cols"
            )
            if selected_numeric_bv:
                plot_helpers.plot_box_violin(df, selected_numeric_bv, chart_type_bv, st)
            else:
                st.info("Selecione pelo menos uma coluna numérica.")

    # Tab 3: Gráfico de Barras
    with tabs[3]:
        st.subheader("Gráficos de Barras para Colunas Categóricas")
        if not categorical_cols:
            st.info("Nenhuma coluna categórica encontrada para gráficos de barras.")
        else:
            selected_categorical_bar = st.multiselect(
                "Selecione colunas categóricas para Gráfico de Barras:",
                categorical_cols,
                default=categorical_cols[:min(3, len(categorical_cols))],
                key="bar_cat_cols"
            )
            if selected_categorical_bar:
                plot_helpers.plot_bar_charts(df, selected_categorical_bar, st)
            else:
                st.info("Selecione pelo menos uma coluna categórica.")

    # Tab 4: Heatmap de Correlação
    with tabs[4]:
        st.subheader("Heatmap de Correlação entre Colunas Numéricas")
        if len(numeric_cols) < 2:
            st.info("São necessárias pelo menos duas colunas numéricas para gerar um heatmap de correlação.")
        else:
            selected_numeric_hm = st.multiselect(
                "Selecione colunas numéricas para o Heatmap:",
                numeric_cols,
                default=numeric_cols[:min(5, len(numeric_cols))], # Default para mais colunas aqui
                key="hm_num_cols"
            )
            corr_method_hm = st.selectbox(
                "Método de correlação:",
                ["pearson", "spearman", "kendall"],
                key="hm_method"
            )
            if selected_numeric_hm and len(selected_numeric_hm) >= 2:
                plot_helpers.plot_correlation_heatmap(df, selected_numeric_hm, corr_method_hm, st)
            elif selected_numeric_hm and len(selected_numeric_hm) < 2:
                st.warning("Selecione pelo menos duas colunas numéricas para o heatmap.")
            else:
                st.info("Selecione colunas numéricas.")


    # Tab 5: Pairplot
    with tabs[5]:
        st.subheader("Pairplot entre Colunas Numéricas")
        if len(numeric_cols) < 2:
            st.info("São necessárias pelo menos duas colunas numéricas para gerar um pairplot.")
        else:
            selected_numeric_pp = st.multiselect(
                "Selecione colunas numéricas para o Pairplot (máx 5 recomendado):",
                numeric_cols,
                default=numeric_cols[:min(4, len(numeric_cols))], # Limitar default para performance
                key="pp_num_cols"
            )
            if selected_numeric_pp:
                if len(selected_numeric_pp) > 5:
                    st.warning("⚠️ Selecionar muitas colunas para o Pairplot pode levar tempo para renderizar.")
                
                # Adicionado o checkbox como no prompt original
                show_pairplot_cb = st.checkbox("Exibir Pairplot (pode ser lento com muitas colunas/dados)", key="pp_show_cb")
                if show_pairplot_cb and len(selected_numeric_pp) >=2:
                    with st.spinner("Gerando Pairplot... Isso pode levar alguns segundos."):
                        plot_helpers.plot_pairplot(df, selected_numeric_pp, st)
                elif show_pairplot_cb and len(selected_numeric_pp) < 2:
                    st.warning("Selecione pelo menos duas colunas para o Pairplot.")

            else:
                st.info("Selecione colunas numéricas para o Pairplot.")

    # Tab 6: Dados Ausentes (Missing)
    with tabs[6]:
        st.subheader("Análise de Dados Ausentes (Missing Values)")
        plot_helpers.show_missing_overview(df, st)

  # Dentro da função run_eda(df: pd.DataFrame, filename: str) no arquivo modules/eda.py

# ... (outras tabs aqui) ...

# Tab 7: Exportar Relatórios (ou o índice correto da sua tab "Exportar")
    with tabs[7]: 
        st.subheader("Exportar Relatório de Análise")
        
        st.markdown("Gere e baixe um relatório resumido da análise exploratória.")

        try:
            # Gerar o conteúdo dos relatórios
            # generate_txt_report(df, filename) retorna um objeto io.StringIO
            report_io_txt = generate_txt_report(df, filename) 
            
            # generate_markdown_report(df, filename) retorna uma string
            report_str_md = generate_markdown_report(df, filename)

            # Preparar dados para download
            data_txt = report_io_txt.getvalue().encode("utf-8")
            data_md = report_str_md.encode("utf-8")

            # Definir nomes dos arquivos para download
            base_filename = filename.split('.')[0] if '.' in filename else filename
            download_filename_txt = f"eda_report_{base_filename}.txt"
            download_filename_md = f"eda_report_{base_filename}.md"

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Baixar relatório (.txt)",
                    data=data_txt,
                    file_name=download_filename_txt,
                    mime="text/plain"
                )
            with col2:
                st.download_button(
                    label="📥 Baixar relatório (.md)",
                    data=data_md,
                    file_name=download_filename_md,
                    mime="text/markdown"
                )
            st.markdown("---")
            st.markdown("📌 Em breve: opção de download em PDF!")

        except Exception as e:
            st.error(f"Erro ao gerar ou preparar relatórios para download: {e}")