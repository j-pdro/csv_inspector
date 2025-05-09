# plots.py

import streamlit as st
import plotly.express as px
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def gerar_graficos(df: pd.DataFrame) -> None:
    try:
        st.markdown("### 📈 Visualização de Dados")

        colunas_numericas = df.select_dtypes(include='number').columns
        colunas_categoricas = df.select_dtypes(include='object').columns

        if len(colunas_numericas) > 0:
            col_num = st.selectbox("Selecione uma coluna numérica:", colunas_numericas)
            fig = px.histogram(df, x=col_num)
            st.plotly_chart(fig, use_container_width=True)

        if len(colunas_categoricas) > 0:
            col_cat = st.selectbox("Selecione uma coluna categórica:", colunas_categoricas)
            contagem = df[col_cat].value_counts().reset_index()
            contagem.columns = [col_cat, 'count']
            fig2 = px.bar(contagem, x=col_cat, y='count')
            st.plotly_chart(fig2, use_container_width=True)

        logger.info("Gráficos gerados com sucesso.")

    except Exception as e:
        logger.exception("Erro ao gerar os gráficos.")
        st.error(f"Ocorreu um erro ao gerar os gráficos: {e}")
