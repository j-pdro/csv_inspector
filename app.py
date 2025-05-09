# main.py
import streamlit as st
import pandas as pd
from datetime import datetime
from report_generator import generate_txt_report, generate_markdown_report

# Configurações da página
st.set_page_config(page_title="CSV Analyzer", layout="wide")
st.title("🔎 CSV Analyzer Inteligente")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Selecione um arquivo CSV", type="csv")

if uploaded_file is not None:
    try:
        # Leitura do arquivo
        df = pd.read_csv(uploaded_file)
        st.success("✅ CSV carregado com sucesso!")

        # Exibição dos dados
        with st.expander("📂 Visualização dos Dados"):
            st.dataframe(df)

        # Geração dos relatórios (.txt para download e .md para exibição)
        report_txt = generate_txt_report(df, uploaded_file.name)
        report_md = generate_markdown_report(df, uploaded_file.name)

        # Exibição do relatório no app
        with st.expander("📄 Relatório de Análise - Visualização Completa"):
            st.markdown(report_md)

        # Área de download do relatório
        col1, col2 = st.columns([1, 2])
        with col1:
            st.download_button(
                label="📥 Baixar relatório (.txt)",
                data=report_txt.getvalue().encode("utf-8"),
                file_name="relatorio_analise.txt",
                mime="text/plain"
            )
        with col2:
            st.markdown("###### _📌 Em breve: opção de download em PDF!_")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        st.warning("⚠️ O arquivo pode não ser um CSV válido ou estar corrompido.")
        st.warning("⚠️ Tente novamente com um arquivo diferente.")
