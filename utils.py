import streamlit as st
import pandas as pd
import plotly.express as px

def mostrar_info_basica(df):
    st.markdown("### ℹ️ Informações Básicas")
    st.write(f"**Dimensão do dataset:** {df.shape[0]} linhas × {df.shape[1]} colunas")
    st.write("**Tipos de dados:**")
    st.write(df.dtypes)
    
    st.markdown("### 📊 Estatísticas Descritivas")
    st.write(df.describe())

    st.markdown("### 🧱 Valores Nulos")
    st.write(df.isnull().sum())

def gerar_graficos(df):
    st.markdown("### 📈 Gráficos Automáticos")
    colunas_numericas = df.select_dtypes(include='number').columns
    colunas_categoricas = df.select_dtypes(include='object').columns

    if len(colunas_numericas) > 0:
        col_num = st.selectbox("Escolha uma coluna numérica para visualizar", colunas_numericas)
        fig = px.histogram(df, x=col_num)
        st.plotly_chart(fig)

    if len(colunas_categoricas) > 0:
        col_cat = st.selectbox("Escolha uma coluna categórica para visualizar", colunas_categoricas)
        fig2 = px.bar(df[col_cat].value_counts().reset_index(), x='index', y=col_cat)
        st.plotly_chart(fig2)
