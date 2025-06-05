# utils/helpers.py

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# --- Funções de Plotagem para o Módulo EDA ---

def plot_histograms(df: pd.DataFrame, cols: list[str], container: st.delta_generator.DeltaGenerator):
    """
    Plota histogramas para cada coluna numérica selecionada dentro do container fornecido.

    Parâmetros:
      df (pd.DataFrame): DataFrame com os dados.
      cols (list[str]): Lista de colunas numéricas para plotar.
      container (streamlit.delta_generator.DeltaGenerator): Contêiner do Streamlit para exibir os gráficos.
    """
    if not cols:
        container.info("Nenhuma coluna selecionada para histogramas.")
        return

    container.subheader("Histogramas")
    for col in cols:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            try:
                fig = px.histogram(df, x=col, nbins=30, title=f"Histograma de {col}")
                fig.update_layout(bargap=0.1)
                container.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                container.error(f"Não foi possível gerar o histograma para {col}: {e}")
        else:
            container.warning(f"Coluna '{col}' não é numérica ou não existe no DataFrame. Pulando histograma.")

def plot_box_violin(df: pd.DataFrame, cols: list[str], chart_type: str, container: st.delta_generator.DeltaGenerator):
    """
    Plota boxplots ou violin plots para cada coluna numérica selecionada.

    Parâmetros:
      df (pd.DataFrame): DataFrame com os dados.
      cols (list[str]): Lista de colunas numéricas para plotar.
      chart_type (str): "Boxplot" ou "Violin plot".
      container (streamlit.delta_generator.DeltaGenerator): Contêiner do Streamlit para exibir os gráficos.
    """
    if not cols:
        container.info(f"Nenhuma coluna selecionada para {chart_type}.")
        return

    container.subheader(f"{chart_type}s")
    # Determina o número de colunas para o layout dos gráficos
    num_plot_cols = min(len(cols), 2) # No máximo 2 gráficos por linha
    
    for i in range(0, len(cols), num_plot_cols):
        plot_cols_streamlit = container.columns(num_plot_cols)
        for j, col_name in enumerate(cols[i : i + num_plot_cols]):
            if col_name in df.columns and pd.api.types.is_numeric_dtype(df[col_name]):
                with plot_cols_streamlit[j]:
                    fig, ax = plt.subplots(figsize=(6, 4)) # Ajuste o tamanho conforme necessário
                    if chart_type == "Boxplot":
                        sns.boxplot(y=df[col_name], ax=ax, color="skyblue")
                        ax.set_title(f"Boxplot de {col_name}", fontsize=10)
                    elif chart_type == "Violin plot":
                        sns.violinplot(y=df[col_name], ax=ax, color="lightgreen")
                        ax.set_title(f"Violin Plot de {col_name}", fontsize=10)
                    
                    ax.set_ylabel(col_name)
                    ax.tick_params(axis='x', labelsize=8)
                    ax.tick_params(axis='y', labelsize=8)
                    plt.tight_layout()
                    st.pyplot(fig) # Usar st.pyplot() diretamente no container da coluna
            else:
                with plot_cols_streamlit[j]:
                    container.warning(f"Coluna '{col_name}' não é numérica ou não existe. Pulando {chart_type}.")


def plot_bar_charts(df: pd.DataFrame, cols: list[str], container: st.delta_generator.DeltaGenerator):
    """
    Plota gráficos de barras para as contagens de valores de colunas categóricas.

    Parâmetros:
      df (pd.DataFrame): DataFrame com os dados.
      cols (list[str]): Lista de colunas categóricas para plotar.
      container (streamlit.delta_generator.DeltaGenerator): Contêiner do Streamlit para exibir os gráficos.
    """
    if not cols:
        container.info("Nenhuma coluna selecionada para gráficos de barras.")
        return

    container.subheader("Gráficos de Barras (Frequência)")
    num_plot_cols = min(len(cols), 2)

    for i in range(0, len(cols), num_plot_cols):
        plot_cols_streamlit = container.columns(num_plot_cols)
        for j, col_name in enumerate(cols[i : i + num_plot_cols]):
            if col_name in df.columns and df[col_name].dtype in ['object', 'category']:
                with plot_cols_streamlit[j]:
                    try:
                        counts = df[col_name].value_counts().nlargest(15) # Limitar às 15 categorias mais frequentes
                        if counts.empty:
                            st.write(f"Coluna '{col_name}' não tem dados para exibir ou todas as categorias são raras.")
                            continue

                        fig, ax = plt.subplots(figsize=(7, 5))
                        sns.barplot(x=counts.index, y=counts.values, ax=ax, palette="viridis")
                        ax.set_title(f"Frequência em {col_name}", fontsize=10)
                        ax.set_xlabel(col_name, fontsize=8)
                        ax.set_ylabel("Contagem", fontsize=8)
                        # Ajuste para rotação e alinhamento dos labels do eixo X
                        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=7)
                        ax.tick_params(axis='y', labelsize=7) # Mantém para o eixo Y
        
                        plt.tight_layout()
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Erro ao plotar gráfico de barras para {col_name}: {e}")
            else:
                 with plot_cols_streamlit[j]:
                    container.warning(f"Coluna '{col_name}' não é categórica ou não existe. Pulando gráfico de barras.")


def plot_correlation_heatmap(df: pd.DataFrame, cols: list[str], method: str, container: st.delta_generator.DeltaGenerator):
    """
    Calcula e plota um heatmap da matriz de correlação.

    Parâmetros:
      df (pd.DataFrame): DataFrame com os dados.
      cols (list[str]): Lista de colunas numéricas para calcular a correlação.
      method (str): Método de correlação ('pearson', 'spearman', 'kendall').
      container (streamlit.delta_generator.DeltaGenerator): Contêiner do Streamlit para exibir o gráfico.
    """
    if len(cols) < 2:
        container.info("Selecione pelo menos duas colunas numéricas para o heatmap de correlação.")
        return

    container.subheader(f"Heatmap de Correlação ({method.capitalize()})")
    numeric_df_selected = df[cols].select_dtypes(include=['number'])
    
    if numeric_df_selected.shape[1] < 2:
        container.warning("Não há colunas numéricas suficientes selecionadas para calcular a correlação.")
        return

    try:
        corr_matrix = numeric_df_selected.corr(method=method)
        fig, ax = plt.subplots(figsize=(max(8, len(cols)), max(6, len(cols)-2))) # Ajustar tamanho dinamicamente
        sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax, linewidths=.5, annot_kws={"size": 8})
        ax.set_title(f"Matriz de Correlação ({method.capitalize()})", fontsize=12)
        plt.xticks(rotation=45, ha="right", fontsize=9)
        plt.yticks(rotation=0, fontsize=9)
        plt.tight_layout()
        container.pyplot(fig)
    except Exception as e:
        container.error(f"Erro ao gerar heatmap de correlação: {e}")

def plot_pairplot(df: pd.DataFrame, cols: list[str], container: st.delta_generator.DeltaGenerator):
    """
    Gera e exibe um pairplot para as colunas numéricas selecionadas.

    Parâmetros:
      df (pd.DataFrame): DataFrame com os dados.
      cols (list[str]): Lista de colunas numéricas para o pairplot.
      container (streamlit.delta_generator.DeltaGenerator): Contêiner do Streamlit para exibir o gráfico.
    """
    if len(cols) < 2:
        container.info("Selecione pelo menos duas colunas numéricas para o pairplot.")
        return
    
    numeric_df_selected = df[cols].select_dtypes(include=['number'])
    if numeric_df_selected.shape[1] < 2:
        container.warning("Não há colunas numéricas suficientes selecionadas para o pairplot.")
        return

    container.subheader("Pairplot")
    try:
        # Adicionar uma verificação para o número de colunas para evitar sobrecarga
        if len(cols) > 5: # Limite arbitrário, pode ser ajustado
            container.warning(f"Pairplot com {len(cols)} colunas pode ser lento e visualmente complexo. Considerar menos colunas.")
        
        # Usar st.spinner diretamente aqui se a operação for demorada
        with st.spinner(f"Gerando pairplot para {len(cols)} colunas..."):
            pair_fig = sns.pairplot(numeric_df_selected, diag_kind='kde', corner=True) # Adicionado corner=True para melhor visualização
            # Ajustar títulos e labels para melhor legibilidade
            pair_fig.fig.suptitle("Pairplot das Colunas Selecionadas", y=1.02, fontsize=14)
            for ax in pair_fig.axes.flatten():
                if ax is not None:
                    ax.tick_params(axis='both', which='major', labelsize=7)
                    ax.xaxis.label.set_size(8)
                    ax.yaxis.label.set_size(8)
            plt.tight_layout()
            container.pyplot(pair_fig)

    except Exception as e:
        container.error(f"Erro ao gerar pairplot: {e}")


def show_missing_overview(df: pd.DataFrame, container: st.delta_generator.DeltaGenerator):
    """
    Exibe uma visão geral dos dados ausentes, incluindo uma tabela e um heatmap.

    Parâmetros:
      df (pd.DataFrame): DataFrame com os dados.
      container (streamlit.delta_generator.DeltaGenerator): Contêiner do Streamlit para exibir as informações.
    """
    container.subheader("Visão Geral de Dados Ausentes")
    
    missing_counts = df.isnull().sum()
    missing_percentage = (missing_counts / len(df)) * 100
    missing_df = pd.DataFrame({
        'Coluna': df.columns,
        'Nº de Ausentes': missing_counts,
        '% de Ausentes': missing_percentage
    }).sort_values(by='% de Ausentes', ascending=False)

    missing_df_display = missing_df[missing_df['Nº de Ausentes'] > 0]

    if missing_df_display.empty:
        container.success("🎉 Ótima notícia! Não há dados ausentes neste dataset.")
    else:
        container.write("Tabela de Dados Ausentes por Coluna:")
        container.dataframe(missing_df_display.style.format({'% de Ausentes': '{:.2f}%'}), use_container_width=True)

        container.write("Heatmap de Dados Ausentes:")
        if not df.isnull().any().any(): # Verifica se há algum valor nulo no DataFrame
             container.info("Nenhum dado ausente para exibir no heatmap.")
        else:
            fig, ax = plt.subplots(figsize=(10, max(4, df.shape[1] * 0.3))) # Ajustar altura dinamicamente
            sns.heatmap(df.isnull(), cbar=False, cmap='viridis', ax=ax, yticklabels=False)
            ax.set_title("Localização de Dados Ausentes", fontsize=12)
            plt.tight_layout()
            container.pyplot(fig)

# --- Outras funções helpers podem ser adicionadas aqui no futuro ---