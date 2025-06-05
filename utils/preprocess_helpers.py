import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, LabelEncoder

def handle_missing_values(df: pd.DataFrame, columns: list, strategy: str, 
                          threshold: int = None, 
                          fill_numeric_method: str = None, 
                          fill_categorical_method: str = None, 
                          specific_value: str = None) -> tuple[pd.DataFrame, str]:
    """
    Trata valores ausentes em um DataFrame com base na estratégia especificada.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        columns (list): Lista de colunas para processar. Se vazia, processa todas as colunas.
        strategy (str): Estratégia para tratar nulos ("Remover Linhas com Nulos", 
                        "Remover Colunas com Nulos", "Preencher Nulos").
        threshold (int, optional): Threshold percentual para remover colunas.
        fill_numeric_method (str, optional): Método para preencher nulos numéricos 
                                             ("Média", "Mediana", "Moda", "Valor Específico").
        fill_categorical_method (str, optional): Método para preencher nulos categóricos 
                                                 ("Moda", "Valor Específico").
        specific_value (str, optional): Valor específico para preenchimento.

    Returns:
        tuple[pd.DataFrame, str]: DataFrame modificado e mensagem de status.
    """
    df_processed = df.copy()
    cols_to_process = columns if columns else df_processed.columns.tolist()
    
    if not cols_to_process and strategy != "Remover Colunas com Nulos": # For column removal, it might process all if none selected based on threshold
        if strategy == "Preencher Nulos" or strategy == "Remover Linhas com Nulos":
             return df_processed, "Nenhuma coluna selecionada e a estratégia requer seleção de colunas."


    original_shape = df_processed.shape
    # Calculate NaNs only on relevant columns or all if none selected for certain strategies
    relevant_cols_for_nan_count = cols_to_process if cols_to_process else df_processed.columns.tolist()
    nans_before = df_processed[relevant_cols_for_nan_count].isnull().sum().sum()


    if strategy == "Remover Linhas com Nulos":
        if not cols_to_process:
            return df, "Por favor, selecione colunas para aplicar a remoção de linhas com nulos."
        df_processed.dropna(subset=cols_to_process, inplace=True)
        msg = f"Linhas com valores nulos nas colunas selecionadas ({', '.join(cols_to_process)}) foram removidas. {original_shape[0] - df_processed.shape[0]} linhas removidas."
    
    elif strategy == "Remover Colunas com Nulos":
        if threshold is None:
            return df, "Threshold para remoção de colunas não especificado."
        
        # If no columns are selected, apply to all columns
        cols_to_evaluate = cols_to_process if cols_to_process else df_processed.columns.tolist()
        if not cols_to_evaluate:
            return df, "Nenhuma coluna para avaliar a remoção."

        thresh_val = (threshold / 100.0)
        cols_dropped = []
        for col in cols_to_evaluate:
            if col in df_processed.columns: 
                if df_processed[col].isnull().mean() > thresh_val:
                    df_processed.drop(columns=[col], inplace=True)
                    cols_dropped.append(col)
        if cols_dropped:
            msg = f"Colunas com mais de {threshold}% de valores nulos removidas: {', '.join(cols_dropped)}."
        else:
            msg = f"Nenhuma coluna (dentre as avaliadas: {', '.join(cols_to_evaluate)}) excedeu o threshold de {threshold}% de valores nulos para remoção."

    elif strategy == "Preencher Nulos":
        if not cols_to_process:
            return df, "Por favor, selecione colunas para preencher os valores nulos."
        
        filled_cols_details = []
        for col in cols_to_process:
            if col not in df_processed.columns: continue 

            if df_processed[col].isnull().sum() == 0:
                continue 

            original_nan_count = df_processed[col].isnull().sum()
            
            if pd.api.types.is_numeric_dtype(df_processed[col]):
                if fill_numeric_method == "Média":
                    fill_val = df_processed[col].mean()
                    df_processed[col].fillna(fill_val, inplace=True)
                elif fill_numeric_method == "Mediana":
                    fill_val = df_processed[col].median()
                    df_processed[col].fillna(fill_val, inplace=True)
                elif fill_numeric_method == "Moda":
                    mode_val = df_processed[col].mode()
                    fill_val = mode_val[0] if not mode_val.empty else np.nan
                    df_processed[col].fillna(fill_val, inplace=True)
                elif fill_numeric_method == "Valor Específico":
                    try:
                        val = float(specific_value) if specific_value is not None and specific_value.strip() != "" else np.nan
                        df_processed[col].fillna(val, inplace=True)
                        fill_val = val
                    except ValueError:
                        return df, f"Valor específico '{specific_value}' não é numérico válido para a coluna numérica '{col}'."
                filled_cols_details.append(f"'{col}' (numérica) com {fill_numeric_method} (valor: {fill_val:.2f if isinstance(fill_val, (int,float)) else fill_val})")
            else: # Categorical/Object column
                if fill_categorical_method == "Moda":
                    mode_val = df_processed[col].mode()
                    fill_val = mode_val[0] if not mode_val.empty else "Desconhecido"
                    df_processed[col].fillna(fill_val, inplace=True)
                elif fill_categorical_method == "Valor Específico":
                    fill_val = specific_value if specific_value is not None else "Desconhecido"
                    df_processed[col].fillna(fill_val, inplace=True)
                filled_cols_details.append(f"'{col}' (categórica) com {fill_categorical_method} (valor: {fill_val})")
        
        if filled_cols_details:
            msg = f"Valores nulos preenchidos em: {'; '.join(filled_cols_details)}."
        else:
            msg = "Nenhuma coluna selecionada precisou de preenchimento ou as colunas não tinham nulos."
    else:
        return df, "Estratégia de tratamento de nulos inválida."

    nans_after = df_processed.isnull().sum().sum()
    msg += f" Total de NaNs antes (nas colunas avaliadas): {nans_before}, NaNs totais depois no DF: {nans_after}."
    return df_processed, msg

def remove_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """
    Remove linhas duplicadas do DataFrame.

    Args:
        df (pd.DataFrame): DataFrame de entrada.

    Returns:
        tuple[pd.DataFrame, str]: DataFrame sem duplicatas e mensagem de status.
    """
    duplicates_before = df.duplicated().sum()
    if duplicates_before == 0:
        return df, "Nenhuma linha duplicada encontrada."
    
    df_processed = df.drop_duplicates(keep='first', inplace=False)
    # duplicates_after = df_processed.duplicated().sum() # Should be 0
    msg = f"{duplicates_before} linhas duplicadas foram removidas."
    return df_processed, msg

def convert_data_type(df: pd.DataFrame, column_to_convert: str, new_type_str: str) -> tuple[pd.DataFrame, str]:
    """
    Converte o tipo de dados de uma coluna especificada.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        column_to_convert (str): Nome da coluna para converter.
        new_type_str (str): String do tipo de dados de destino ("Numérico (float)", 
                            "Numérico (int)", "Texto (string)", "Data/Hora (datetime)").

    Returns:
        tuple[pd.DataFrame, str]: DataFrame com a coluna convertida e mensagem de status.
    """
    df_processed = df.copy()
    if column_to_convert not in df_processed.columns:
        return df, f"Coluna '{column_to_convert}' não encontrada no DataFrame."

    original_type = df_processed[column_to_convert].dtype
    nan_before_conversion = df_processed[column_to_convert].isnull().sum()

    try:
        if new_type_str == "Numérico (float)":
            converted_series = pd.to_numeric(df_processed[column_to_convert], errors='coerce')
            if converted_series.isnull().all() and not df[column_to_convert].isnull().all() and df[column_to_convert].notnull().any():
                 return df, f"Falha ao converter '{column_to_convert}' para float. Todos os valores não nulos resultaram em NaN. Verifique o conteúdo da coluna."
            df_processed[column_to_convert] = converted_series.astype(float)
        elif new_type_str == "Numérico (int)":
            temp_series = pd.to_numeric(df_processed[column_to_convert], errors='coerce')
            if temp_series.isnull().all() and not df[column_to_convert].isnull().all() and df[column_to_convert].notnull().any():
                 return df, f"Falha ao converter '{column_to_convert}' para int. Todos os valores não nulos resultaram em NaN. Verifique o conteúdo da coluna."
            
            if temp_series.isnull().any():
                try: # Tenta usar o tipo Int64 que suporta NaN
                    df_processed[column_to_convert] = temp_series.astype(pd.Int64Dtype())
                except Exception:
                    return df, (f"Não é possível converter '{column_to_convert}' para int diretamente pois contém NaNs "
                                f"após tentativa de coerção numérica (total de NaNs: {temp_series.isnull().sum()}). "
                                "Considere tratar os NaNs ou converter para float.")
            else: # Sem NaNs, pode converter para int padrão
                df_processed[column_to_convert] = temp_series.astype(int)
        elif new_type_str == "Texto (string)":
            df_processed[column_to_convert] = df_processed[column_to_convert].astype(str)
        elif new_type_str == "Data/Hora (datetime)":
            converted_series = pd.to_datetime(df_processed[column_to_convert], errors='coerce')
            if converted_series.isnull().all() and not df[column_to_convert].isnull().all() and df[column_to_convert].notnull().any():
                 return df, f"Falha ao converter '{column_to_convert}' para datetime. Todos os valores não nulos resultaram em NaT. Verifique o formato das datas."
            df_processed[column_to_convert] = converted_series
        else:
            return df, f"Tipo de destino '{new_type_str}' não suportado."
        
        nan_after_conversion = df_processed[column_to_convert].isnull().sum()
        msg = (f"Coluna '{column_to_convert}' convertida de {original_type} para {df_processed[column_to_convert].dtype}. "
               f"NaNs antes: {nan_before_conversion}, NaNs/NaTs depois: {nan_after_conversion}.")
        return df_processed, msg
    except Exception as e:
        return df, f"Erro ao converter coluna '{column_to_convert}' para '{new_type_str}': {e}"

def encode_categorical_features(df: pd.DataFrame, columns_to_encode: list, method: str) -> tuple[pd.DataFrame, str]:
    """
    Codifica colunas categóricas especificadas usando One-Hot ou Label Encoding.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        columns_to_encode (list): Lista de nomes de colunas categóricas para codificar.
        method (str): Método de encoding ("One-Hot Encoding (Dummy Variables)", "Label Encoding").

    Returns:
        tuple[pd.DataFrame, str]: DataFrame com features codificadas e mensagem de status.
    """
    df_processed = df.copy()
    if not columns_to_encode:
        return df, "Nenhuma coluna selecionada para encoding."

    processed_cols_names = []
    if method == "One-Hot Encoding (Dummy Variables)":
        try:
            # Check for high cardinality - simple warning for now
            for col in columns_to_encode:
                if col in df_processed.columns and df_processed[col].nunique() > 50: # Arbitrary threshold
                     st.warning(f"Atenção: A coluna '{col}' possui alta cardinalidade ({df_processed[col].nunique()} valores únicos). One-Hot Encoding pode gerar muitas colunas.")
            
            df_processed = pd.get_dummies(df_processed, columns=columns_to_encode, prefix=columns_to_encode, dummy_na=False)
            processed_cols_names = columns_to_encode
        except Exception as e:
            return df, f"Erro durante One-Hot Encoding: {e}"
    
    elif method == "Label Encoding":
        le = LabelEncoder()
        for col in columns_to_encode:
            if col in df_processed.columns:
                # Converter para string para evitar erros com tipos mistos ou numéricos interpretados como categoria
                df_processed[col] = df_processed[col].astype(str) 
                df_processed[col] = le.fit_transform(df_processed[col])
                processed_cols_names.append(col)
            else: # Should not happen if list is from df.columns
                return df, f"Coluna '{col}' não encontrada para Label Encoding." 
    else:
        return df, "Método de encoding inválido."

    if not processed_cols_names:
         return df, "Nenhuma coluna foi efetivamente codificada."
        
    msg = f"{method} aplicado às colunas: {', '.join(processed_cols_names)}."
    return df_processed, msg

def scale_numerical_features(df: pd.DataFrame, columns_to_scale: list, method: str) -> tuple[pd.DataFrame, str]:
    """
    Escalona colunas numéricas especificadas usando Min-Max ou Standard Scaling.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        columns_to_scale (list): Lista de nomes de colunas numéricas para escalonar.
        method (str): Método de escalonamento ("Min-Max Scaler (Normalização)", 
                      "Standard Scaler (Padronização)").

    Returns:
        tuple[pd.DataFrame, str]: DataFrame com features escalonadas e mensagem de status.
    """
    df_processed = df.copy()
    if not columns_to_scale:
        return df, "Nenhuma coluna selecionada para escalonamento."

    scaled_cols_names = []
    for col in columns_to_scale:
        if col not in df_processed.columns:
            # This case should ideally be prevented by UI logic
            return df, f"Coluna '{col}' não encontrada para escalonamento."
        if not pd.api.types.is_numeric_dtype(df_processed[col]):
            return df, f"Coluna '{col}' (tipo: {df_processed[col].dtype}) não é numérica e não pode ser escalonada. Por favor, converta para tipo numérico primeiro."
        if df_processed[col].isnull().any():
            return df, f"Coluna '{col}' contém valores nulos. Por favor, trate os nulos antes de escalonar."

        try:
            data_to_scale = df_processed[col].values.reshape(-1, 1)
            if method == "Min-Max Scaler (Normalização)":
                scaler = MinMaxScaler()
                df_processed[col] = scaler.fit_transform(data_to_scale)
            elif method == "Standard Scaler (Padronização)":
                scaler = StandardScaler()
                df_processed[col] = scaler.fit_transform(data_to_scale)
            else:
                return df, "Método de escalonamento inválido."
            scaled_cols_names.append(col)
        except Exception as e:
            return df, f"Erro ao escalonar coluna '{col}': {e}"
    
    if not scaled_cols_names:
        return df, "Nenhuma coluna foi efetivamente escalonada (verifique tipos e nulos)."

    msg = f"{method} aplicado às colunas: {', '.join(scaled_cols_names)}."
    return df_processed, msg