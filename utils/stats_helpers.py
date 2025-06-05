# utils/stats_helpers.py

import streamlit as st
import pandas as pd
import numpy as np # Para cálculos estatísticos se necessário
import seaborn as sns
import matplotlib.pyplot as plt

def show_descriptive_stats(df: pd.DataFrame, cols: list[str], container: st.delta_generator.DeltaGenerator):
    """
    Calcula e exibe estatísticas descritivas de colunas numéricas selecionadas.

    Parâmetros:
      df (pd.DataFrame): DataFrame com dados.
      cols (list[str]): Lista de colunas numéricas para calcular estatísticas.
      container (streamlit.delta_generator.DeltaGenerator): Container para exibição.
    """
    if not cols:
        container.info("Nenhuma coluna selecionada para exibir estatísticas descritivas.")
        return

    try:
        desc_stats = df[cols].agg(['count', 'mean', 'median', 'std', 'var', 'min', 'max', 
                                   lambda x: x.quantile(0.25), 
                                   lambda x: x.quantile(0.75)]).T
        desc_stats = desc_stats.rename(columns={
            'count': 'Contagem',
            'mean': 'Média',
            'median': 'Mediana',
            'std': 'Desvio Padrão',
            'var': 'Variância',
            'min': 'Mínimo',
            'max': 'Máximo',
            '<lambda_0>': '25º Percentil (Q1)', # Nomes podem variar com a versão do pandas
            '<lambda_1>': '75º Percentil (Q3)'
        })
        # Renomear colunas lambda de forma mais robusta
        desc_stats.columns = ['Contagem', 'Média', 'Mediana', 'Desvio Padrão', 'Variância', 
                              'Mínimo', 'Máximo', '25º Percentil (Q1)', '75º Percentil (Q3)']

        container.dataframe(desc_stats.style.format("{:.2f}")) # Formatar para 2 casas decimais
    except Exception as e:
        container.error(f"Erro ao calcular estatísticas descritivas: {e}")

def show_skew_kurtosis(df: pd.DataFrame, cols: list[str], container: st.delta_generator.DeltaGenerator):
    """
    Calcula e exibe Skewness (Assimetria) e Kurtosis (Curtose) para colunas numéricas.

    Parâmetros:
      df (pd.DataFrame): DataFrame com dados.
      cols (list[str]): Lista de colunas numéricas.
      container (streamlit.delta_generator.DeltaGenerator): Container para exibição.
    """
    if not cols:
        container.info("Nenhuma coluna selecionada para Skewness/Kurtosis.")
        return

    try:
        skew_kurt_data = []
        for col in cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                skewness = df[col].skew()
                kurtosis_val = df[col].kurtosis() # Fisher's definition (normal is 0.0)
                skew_kurt_data.append({
                    "Coluna": col,
                    "Skewness (Assimetria)": skewness,
                    "Kurtosis (Curtose)": kurtosis_val
                })
            else:
                container.warning(f"Coluna '{col}' não é numérica. Pulando Skewness/Kurtosis.")
        
        if skew_kurt_data:
            skew_kurt_df = pd.DataFrame(skew_kurt_data)
            container.dataframe(skew_kurt_df.set_index("Coluna").style.format("{:.3f}"))
        else:
            container.info("Nenhuma coluna numérica válida selecionada para Skewness/Kurtosis.")
            
    except Exception as e:
        container.error(f"Erro ao calcular Skewness/Kurtosis: {e}")

def show_correlation_matrix(df: pd.DataFrame, cols: list[str], method: str, container: st.delta_generator.DeltaGenerator):
    """
    Calcula e exibe a matriz de correlação e, opcionalmente, um heatmap.

    Parâmetros:
      df (pd.DataFrame): DataFrame com dados.
      cols (list[str]): Lista de colunas numéricas para correlação.
      method (str): Método de correlação ('pearson', 'spearman', 'kendall').
      container (streamlit.delta_generator.DeltaGenerator): Container para exibição.
    """
    if len(cols) < 2:
        container.info("Selecione pelo menos duas colunas numéricas para a matriz de correlação.")
        return

    numeric_df_selected = df[cols].select_dtypes(include=['number'])
    if numeric_df_selected.shape[1] < 2:
        container.warning("Não há colunas numéricas suficientes selecionadas para calcular a correlação.")
        return

    try:
        corr_matrix = numeric_df_selected.corr(method=method)
        container.write(f"Matriz de Correlação ({method.capitalize()}):")
        container.dataframe(corr_matrix.style.format("{:.2f}").background_gradient(cmap='coolwarm', axis=None))

        # Opção para exibir heatmap
        if container.checkbox("Exibir Heatmap da Correlação", key=f"heatmap_corr_{method}"):
            fig, ax = plt.subplots(figsize=(max(8, len(cols)), max(6, len(cols)-2)))
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, linewidths=.5, annot_kws={"size": 8})
            ax.set_title(f"Heatmap de Correlação ({method.capitalize()})", fontsize=12)
            plt.xticks(rotation=45, ha="right", fontsize=9)
            plt.yticks(rotation=0, fontsize=9)
            plt.tight_layout()
            container.pyplot(fig)
            
    except Exception as e:
        container.error(f"Erro ao calcular ou exibir a matriz de correlação: {e}")

def show_missing_table(df: pd.DataFrame, container: st.delta_generator.DeltaGenerator):
    """
    Calcula e exibe uma tabela com a contagem e o percentual de dados ausentes por coluna.

    Parâmetros:
      df (pd.DataFrame): DataFrame com dados.
      container (streamlit.delta_generator.DeltaGenerator): Container para exibição.
    """
    try:
        missing_counts = df.isnull().sum()
        missing_percentage = (missing_counts / len(df)) * 100
        missing_df = pd.DataFrame({
            'Coluna': df.columns,
            'Nº de Ausentes': missing_counts,
            '% de Ausentes': missing_percentage
        }).sort_values(by='% de Ausentes', ascending=False)

        # Exibir apenas colunas que têm dados ausentes, ou uma mensagem se não houver.
        missing_df_display = missing_df[missing_df['Nº de Ausentes'] > 0]

        if missing_df_display.empty:
            container.success("🎉 Ótima notícia! Não há dados ausentes neste dataset.")
        else:
            container.write("Tabela de Dados Ausentes por Coluna:")
            container.dataframe(missing_df_display.style.format({'% de Ausentes': '{:.2f}%'}), use_container_width=True)
            
    except Exception as e:
        container.error(f"Erro ao calcular dados ausentes: {e}")

def show_grouped_metrics(df: pd.DataFrame, cat_col: str, numeric_cols: list[str], agg_func: str, container: st.delta_generator.DeltaGenerator):
    """
    Calcula e exibe métricas numéricas agrupadas por uma coluna categórica.

    Parâmetros:
      df (pd.DataFrame): DataFrame com dados.
      cat_col (str): Nome da coluna categórica para agrupar.
      numeric_cols (list[str]): Lista de colunas numéricas para agregar.
      agg_func (str): Função de agregação a ser aplicada (ex: 'mean', 'sum', 'count').
      container (streamlit.delta_generator.DeltaGenerator): Container para exibição.
    """
    if not cat_col:
        container.warning("Nenhuma coluna categórica selecionada para agrupamento.")
        return
    if not numeric_cols:
        container.warning("Nenhuma coluna numérica selecionada para agregação.")
        return
    if not agg_func:
        container.warning("Nenhuma função de agregação selecionada.")
        return

    try:
        # Garante que apenas colunas numéricas existentes sejam usadas
        valid_numeric_cols = [col for col in numeric_cols if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
        if not valid_numeric_cols:
            container.error("As colunas numéricas selecionadas não são válidas ou não existem no DataFrame.")
            return

        grouped_data = df.groupby(cat_col)[valid_numeric_cols].agg(agg_func)
        container.write(f"Métricas ({agg_func}) de '{', '.join(valid_numeric_cols)}' agrupadas por '{cat_col}':")
        container.dataframe(grouped_data.style.format("{:.2f}"))
    except Exception as e:
        container.error(f"Erro ao calcular métricas agrupadas: {e}")