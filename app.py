# main.py
import streamlit as st
import pandas as pd
from report_generator import generate_txt_report, generate_markdown_report
from datetime import datetime

st.set_page_config(page_title="CSV Analyzer", layout="wide")

st.title("🔎 CSV Analyzer Inteligente")

uploaded_file = st.file_uploader("Selecione um arquivo CSV", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("✅ CSV carregado com sucesso!")

        with st.expander("### 📂 Visualização dos dados"):
            st.dataframe(df)

        # Gera relatório: versão .txt (para download) e versão .md (para exibir no app)
        report_text = generate_txt_report(df, uploaded_file.name)
        report_markdown = generate_markdown_report(df, uploaded_file.name)


        # Exibição bonita no app
        with st.expander("📄 Relatório de Análise - Visualizar relatório completo"):
            st.markdown(report_markdown)

        # Botão de download + mensagem lateral
        col1, col2 = st.columns([1, 2])
        with col1:
            st.download_button(
                label="📥 Baixar relatório (.txt)",
                data=report_text.getvalue().encode("utf-8"),
                file_name="relatorio_analise.txt",
                mime="text/plain"
            )
        with col2:
            st.markdown("###### _📌 Em breve: opção de download em PDF!_")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        st.warning("⚠️ O arquivo não é um CSV válido ou está corrompido.")
        st.warning("⚠️ Tente novamente com um arquivo diferente.")