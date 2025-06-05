# indicadores_report_generator.py
import pandas as pd
from io import StringIO
from datetime import datetime

def generate_txt_report(df: pd.DataFrame, filename: str, selected_cols: list) -> StringIO:
    buffer = StringIO()

    buffer.write("=" * 60 + "\n")
    buffer.write("📊 RELATÓRIO DE INDICADORES ESTATÍSTICOS\n")
    buffer.write("=" * 60 + "\n")
    buffer.write(f"Arquivo analisado : {filename}\n")
    buffer.write(f"Data da geração   : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    buffer.write("\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 INDICADORES POR COLUNA\n")
    buffer.write("-" * 60 + "\n")
    for col in selected_cols:
        buffer.write(f"Coluna: {col}\n")
        buffer.write(f"  - Média     : {df[col].mean():.4f}\n")
        buffer.write(f"  - Mediana   : {df[col].median():.4f}\n")
        try:
            modo = df[col].mode().iloc[0]
        except:
            modo = "N/A"
        buffer.write(f"  - Moda      : {modo}\n")
        buffer.write(f"  - Desvio Padrão: {df[col].std():.4f}\n")
        buffer.write(f"  - Variância : {df[col].var():.4f}\n")
        buffer.write(f"  - Mínimo    : {df[col].min():.4f}\n")
        buffer.write(f"  - Máximo    : {df[col].max():.4f}\n")
        buffer.write("\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 MATRIZ DE CORRELAÇÃO (NUMÉRICA)\n")
    buffer.write("-" * 60 + "\n")
    corr = df[selected_cols].corr()
    buffer.write(corr.to_string())
    buffer.write("\n\n")

    buffer.write("---\n")
    buffer.write("Relatório gerado automaticamente pelo CSV Inspector.\n")
    return buffer


def generate_markdown_report(df: pd.DataFrame, filename: str, selected_cols: list) -> str:
    md = f"# 📊 Relatório de Indicadores Estatísticos\n"
    md += f"**Arquivo analisado:** `{filename}`  \n"
    md += f"**Data da geração:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"

    md += "## 🔹 Indicadores por Coluna\n"
    for col in selected_cols:
        md += f"### {col}\n"
        md += f"- **Média**     : {df[col].mean():.4f}  \n"
        md += f"- **Mediana**   : {df[col].median():.4f}  \n"
        try:
            modo = df[col].mode().iloc[0]
        except:
            modo = "N/A"
        md += f"- **Moda**      : {modo}  \n"
        md += f"- **Desvio Padrão**: {df[col].std():.4f}  \n"
        md += f"- **Variância** : {df[col].var():.4f}  \n"
        md += f"- **Mínimo**    : {df[col].min():.4f}  \n"
        md += f"- **Máximo**    : {df[col].max():.4f}  \n\n"

    md += "## 🔹 Matriz de Correlação\n"
    corr = df[selected_cols].corr()
    md += corr.to_markdown() + "\n\n"
    md += "---\n"
    md += "Relatório gerado automaticamente pelo CSV Inspector.\n"
    return md