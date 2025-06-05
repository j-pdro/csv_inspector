import pandas as pd
from io import StringIO
from datetime import datetime

def generate_txt_report(df: pd.DataFrame, filename: str) -> StringIO:
    buffer = StringIO()

    buffer.write("=" * 60 + "\n")
    buffer.write("📊 RELATÓRIO DE ANÁLISE DE DADOS\n")
    buffer.write("=" * 60 + "\n")
    buffer.write(f"Arquivo analisado : {filename}\n")
    buffer.write(f"Data da geração   : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    buffer.write("\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 INFORMAÇÕES GERAIS\n")
    buffer.write("-" * 60 + "\n")
    buffer.write(f"Número de linhas  : {df.shape[0]}\n")
    buffer.write(f"Número de colunas : {df.shape[1]}\n")
    buffer.write("\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 TIPOS DE DADOS POR COLUNA\n")
    buffer.write("-" * 60 + "\n")
    for col in df.columns:
        buffer.write(f"{col:<30} -> {df[col].dtype}\n")
    buffer.write("\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 VALORES AUSENTES\n")
    buffer.write("-" * 60 + "\n")
    missing = df.isnull().sum()
    if missing.sum() == 0:
        buffer.write("✅ Nenhuma coluna com valores ausentes.\n")
    else:
        for col in df.columns:
            if missing[col] > 0:
                buffer.write(f"{col:<30} -> {missing[col]} valores ausentes\n")
    buffer.write("\n")


    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 ANÁLISE DE COLUNAS CATEGÓRICAS\n")
    buffer.write("-" * 60 + "\n")
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    if len(categorical_cols) == 0:
        buffer.write("Nenhuma coluna categórica encontrada.\n")
    else:
        for col in categorical_cols:
            unicos = df[col].nunique(dropna=True)
            modo = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
            freq = df[col].value_counts(dropna=True).iloc[0] if not df[col].value_counts(dropna=True).empty else 0
            ausentes = df[col].isnull().sum()
            buffer.write(f"{col:<30} | únicos: {unicos} | mais frequente: '{modo}' ({freq}x) | ausentes: {ausentes}\n")
    buffer.write("\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 DIVERSIDADE DE VALORES\n")
    buffer.write("-" * 60 + "\n")
    for col in df.columns:
        unicos = df[col].nunique(dropna=True)
        buffer.write(f"{col:<30} {unicos} valores únicos\n")
    buffer.write("\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("📌 OBSERVAÇÕES FINAIS\n")
    buffer.write("-" * 60 + "\n")
    buffer.write("- Relatório gerado automaticamente.\n")
    if missing.sum() == 0:
        buffer.write("- Todas as colunas estão completas.\n")
    else:
        buffer.write("- Algumas colunas possuem valores ausentes.\n")

    return buffer

def generate_markdown_report(df: pd.DataFrame, filename: str) -> str:
    from datetime import datetime

    md = f"# 📊 Relatório de Análise de Dados\n"
    md += f"**Arquivo analisado:** `{filename}`  \n"
    md += f"**Data da geração:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"

    md += "## 🔹 Informações Gerais\n"
    md += f"- **Linhas:** {df.shape[0]}\n"
    md += f"- **Colunas:** {df.shape[1]}\n\n"

    md += "## 🔹 Tipos de Dados por Coluna\n"
    md += df.dtypes.to_frame("Tipo").to_markdown() + "\n\n"

    md += "## 🔹 Valores Ausentes\n"
    missing = df.isnull().sum()
    if missing.sum() == 0:
        md += "✅ Nenhuma coluna com valores ausentes.\n\n"
    else:
        md += missing.to_frame("Valores Ausentes").to_markdown() + "\n\n"


    md += "## 🔹 Análise de Colunas Categóricas\n"
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns
    if len(categorical_cols) == 0:
        md += "Nenhuma coluna categórica encontrada.\n\n"
    else:
        for col in categorical_cols:
            unicos = df[col].nunique(dropna=True)
            modo = df[col].mode().iloc[0] if not df[col].mode().empty else "N/A"
            freq = df[col].value_counts(dropna=True).iloc[0] if not df[col].value_counts(dropna=True).empty else 0
            ausentes = df[col].isnull().sum()
            md += f"- **{col}**: únicos: {unicos} | mais frequente: `{modo}` ({freq}x) | ausentes: {ausentes}\n"
        md += "\n"

    md += "## 🔹 Diversidade de Valores\n"
    for col in df.columns:
        unicos = df[col].nunique(dropna=True)
        md += f"- **{col}**: {unicos} valores únicos\n"
    md += "\n"

    md += "---\n"
    md += "Relatório gerado automaticamente.\n"

    return md