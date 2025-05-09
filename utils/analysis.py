# analysis.py

import streamlit as st
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def mostrar_informacoes_gerais(df: pd.DataFrame) -> None:
    try:
        st.markdown("### ℹ️ Informações Gerais")
        st.write("**Dimensões do dataset:**")
        st.write(f"{df.shape[0]} linhas × {df.shape[1]} colunas")

        st.write("**Tipos de dados:**")
        st.write(df.dtypes)

        st.write("**Estatísticas descritivas:**")
        st.write(df.describe(include='all'))

        st.write("**Valores ausentes por coluna:**")
        st.write(df.isnull().sum())

        logger.info("Informações gerais exibidas com sucesso.")

    except Exception as e:
        logger.exception("Erro ao gerar informações gerais.")
        st.error(f"Ocorreu um erro ao gerar as informações: {e}")
