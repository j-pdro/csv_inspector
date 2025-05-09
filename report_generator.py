# report_generator.py

from io import StringIO
from datetime import datetime
import pandas as pd

def generate_txt_report(df, filename):
    buffer = StringIO()
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    buffer.write("=" * 60 + "\n")
    buffer.write("📊 RELATÓRIO DE ANÁLISE DE DADOS\n")
    buffer.write("=" * 60 + "\n")
    buffer.write(f"Arquivo analisado : {filename}\n")
    buffer.write(f"Data da geração   : {now}\n\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 INFORMAÇÕES GERAIS\n")
    buffer.write("-" * 60 + "\n")
    buffer.write(f"Número de linhas  : {df.shape[0]}\n")
    buffer.write(f"Número de colunas : {df.shape[1]}\n\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 TIPOS DE DADOS POR COLUNA\n")
    buffer.write("-" * 60 + "\n")
    for col, dtype in df.dtypes.items():
        buffer.write(f"{col:<30} -> {dtype}\n")
    buffer.write("\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 VALORES AUSENTES\n")
    buffer.write("-" * 60 + "\n")
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if not nulls.empty:
        for col, total in nulls.items():
            buffer.write(f"{col:<30} {total} valores ausentes\n")
    else:
        buffer.write("✅ Nenhuma coluna com valores ausentes.\n")
    buffer.write("\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 ESTATÍSTICAS DESCRITIVAS (NUMÉRICAS)\n")
    buffer.write("-" * 60 + "\n")
    describe = df.describe().T
    for col in describe.index:
        buffer.write(
            f"{col:<20} | média: {describe.loc[col, 'mean']:.2f} | min: {describe.loc[col, 'min']:.2f} | max: {describe.loc[col, 'max']:.2f} | desvio: {describe.loc[col, 'std']:.2f}\n"
        )
    buffer.write("\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("🔹 DIVERSIDADE DE VALORES\n")
    buffer.write("-" * 60 + "\n")
    for col in df.columns:
        unique_count = df[col].nunique()
        buffer.write(f"{col:<30} {unique_count} valores únicos\n")
    buffer.write("\n")

    buffer.write("-" * 60 + "\n")
    buffer.write("📌 OBSERVAÇÕES FINAIS\n")
    buffer.write("-" * 60 + "\n")
    buffer.write("- Relatório gerado automaticamente pelo CSV Analyzer.\n")
    if nulls.shape[0] > 0:
        buffer.write(f"- {nulls.shape[0]} colunas possuem valores ausentes.\n")
    else:
        buffer.write("- Todas as colunas estão completas.\n")

    buffer.seek(0)
    return buffer


def generate_markdown_report(df, filename):
    now = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    lines = []

    lines.append("## 📊 Relatório de Análise de Dados")
    lines.append(f"**Arquivo analisado:** `{filename}`  ")
    lines.append(f"**Data da geração:** {now}\n")

    lines.append("### 🔹 Informações Gerais")
    lines.append(f"- **Número de linhas:** {df.shape[0]}")
    lines.append(f"- **Número de colunas:** {df.shape[1]}\n")

    lines.append("### 🔹 Tipos de Dados por Coluna")
    types_df = pd.DataFrame({
        "Coluna": df.columns,
        "Tipo de Dado": df.dtypes.astype(str).values
    })
    lines.append(types_df.to_markdown(index=False))
    lines.append("")

    lines.append("### 🔹 Valores Ausentes")
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    if not nulls.empty:
        for col, total in nulls.items():
            lines.append(f"- `{col}`: {total} valores ausentes")
    else:
        lines.append("✅ Nenhuma coluna com valores ausentes.")
    lines.append("")

    lines.append("### 🔹 Estatísticas Descritivas")
    describe = df.describe().T
    for col in describe.index:
        lines.append(
            f"- `{col}` → média: **{describe.loc[col, 'mean']:.2f}**, min: **{describe.loc[col, 'min']:.2f}**, max: **{describe.loc[col, 'max']:.2f}**, desvio: **{describe.loc[col, 'std']:.2f}**"
        )
    lines.append("")

    lines.append("### 🔹 Diversidade de Valores")
    for col in df.columns:
        unique_count = df[col].nunique()
        lines.append(f"- `{col}`: {unique_count} valores únicos")
    lines.append("")

    lines.append("### 📌 Observações Finais")
    lines.append("- Relatório gerado automaticamente pelo **CSV Analyzer**.")
    if nulls.shape[0] > 0:
        lines.append(f"- {nulls.shape[0]} colunas possuem valores ausentes.")
    else:
        lines.append("- Todas as colunas estão completas.")

    return "\n".join(lines)
