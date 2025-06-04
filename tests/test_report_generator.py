import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from report_generator import generate_txt_report

def test_generate_txt_report_stats():
    df = pd.DataFrame({
        "Idade": [20, 30, 40, 50, 60],
        "Salario": [2000.0, 3000.0, 4000.0, 5000.0, 6000.0],
        "Nota": [8.5, 9.0, 7.5, 8.0, 9.5]
    })

    buffer = generate_txt_report(df, "relatorio_teste.csv")
    report_content = buffer.getvalue().lower()

    # Verifica se os nomes das colunas aparecem
    assert "idade" in report_content
    assert "salario" in report_content
    assert "nota" in report_content

    # Verifica se as estatísticas estão presentes
    assert "média" in report_content
    assert "mediana" in report_content
    assert "desvio padrão" in report_content
    assert "valor mínimo" in report_content
    assert "valor máximo" in report_content
    assert "valores ausentes" in report_content

def test_generate_txt_report_categorical():
    df = pd.DataFrame({
        "Sexo": ["M", "F", "M", "F", "M"],
        "Cidade": ["SP", "RJ", "SP", "SP", "RJ"]
    })
    buffer = generate_txt_report(df, "cat_teste.csv")
    txt = buffer.getvalue().lower()
    assert "análise de colunas categóricas" in txt
    assert "sexo" in txt
    assert "cidade" in txt
    assert "mais frequente" in txt
    assert "únicos" in txt

def test_generate_txt_report_no_numeric():
    df = pd.DataFrame({
        "Nome": ["Ana", "Bia", "Caio"],
        "Cidade": ["SP", "RJ", "MG"]
    })
    buffer = generate_txt_report(df, "no_numeric.csv")
    txt = buffer.getvalue().lower()
    assert "nenhuma coluna numérica" in txt or "estatísticas descritivas" in txt
    
def test_generate_txt_report_empty():
    df = pd.DataFrame()
    buffer = generate_txt_report(df, "vazio.csv")
    txt = buffer.getvalue().lower()
    assert "número de linhas  : 0" in txt
    assert "número de colunas : 0" in txt
    
def test_generate_txt_report_categorical_missing():
    df = pd.DataFrame({
        "Cor": ["Azul", None, "Verde", "Azul", None]
    })
    buffer = generate_txt_report(df, "cat_missing.csv")
    txt = buffer.getvalue().lower()
    assert "cor" in txt
    assert "ausentes" in txt
    assert "2" in txt  # 2 valores ausentes