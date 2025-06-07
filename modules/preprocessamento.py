import streamlit as st
import pandas as pd
import numpy as np
import io
import json
from utils import preprocess_helpers

def run_preprocessamento(df_original: pd.DataFrame, filename_original: str):
    """
    Executa o módulo de limpeza e pré-processamento de dados no Streamlit.

    Args:
    df_original (pd.DataFrame): O DataFrame original carregado pelo usuário.
    filename_original (str): O nome do arquivo original do CSV carregado.
    """

    # 1. Gerenciamento de Estado do DataFrame Processado (para edição interativa)
    if 'df_processed' not in st.session_state or \
       st.session_state.get('preprocess_df_original_ref_columns') != df_original.columns.tolist() or \
       st.session_state.get('preprocess_df_original_ref_shape') != df_original.shape:

        st.session_state.df_processed = df_original.copy()
        st.session_state.preprocess_df_original_ref_columns = df_original.columns.tolist()
        st.session_state.preprocess_df_original_ref_shape = df_original.shape
        st.session_state.preprocess_feedback = None
        st.session_state.pipeline_steps = []
        st.session_state.undo_stack = []

    if 'undo_stack' not in st.session_state:
        st.session_state.undo_stack = []

    # Gerenciamento de Estado para DataFrame processado em lote
    if 'df_batch_processed' not in st.session_state:
        st.session_state.df_batch_processed = None
    if 'batch_feedback' not in st.session_state:
        st.session_state.batch_feedback = None
    if 'new_csv_filename_for_batch' not in st.session_state:
        st.session_state.new_csv_filename_for_batch = None

    # Exibir feedback para processamento interativo
    if st.session_state.get('preprocess_feedback'):
        feedback = st.session_state.preprocess_feedback
        if feedback["type"] == "success":
            st.success(feedback["message"])
        elif feedback["type"] == "error":
            st.error(feedback["message"])
        elif feedback["type"] == "warning":
            st.warning(feedback["message"])
        else:
            st.info(feedback["message"])
        st.session_state.preprocess_feedback = None

    st.info("As transformações nas primeiras abas são aplicadas sequencialmente ao DataFrame. Você pode resetar para o estado original ou desfazer a última ação a qualquer momento.")

    col1_controls, col2_info_rows, col3_info_cols = st.columns([2,1,1])
    with col1_controls:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            # Lógica do botão Desfazer atualizada
            if st.button("Desfazer Última Ação", key="undo_action_btn", use_container_width=True):
                if st.session_state.undo_stack:
                    last_undo_action = st.session_state.undo_stack.pop()
                    
                    operation_to_undo = last_undo_action["operation_name"]
                    data_to_restore = last_undo_action["data_for_undo"]
                    description = last_undo_action["description_for_history"]

                    # --- LÓGICA DE REVERSÃO ESPECÍFICA ---
                    if operation_to_undo == "Tratamento de Nulos":
                        strategy = data_to_restore.get("strategy")
                        if strategy == "Remover Linhas com Nulos" and "removed_rows_df" in data_to_restore:
                            df_to_reinsert = data_to_restore["removed_rows_df"]
                            st.session_state.df_processed = pd.concat([st.session_state.df_processed, df_to_reinsert]).sort_index()
                            # TODO: Adicionar lógica de reversão para outras estratégias de nulos aqui
                    
                    elif operation_to_undo == "Remoção de Linhas Duplicadas":
                        if "removed_rows_df" in data_to_restore:
                            df_to_reinsert = data_to_restore["removed_rows_df"]
                            st.session_state.df_processed = pd.concat([st.session_state.df_processed, df_to_reinsert]).sort_index()
                    
                    elif operation_to_undo == "Conversão de Tipos de Dados":
                        col = data_to_restore["column_name"]
                        st.session_state.df_processed[col] = data_to_restore["original_series"]

                    elif operation_to_undo == "Escalonamento de Colunas Numéricas":
                        for col in data_to_restore["original_columns_df"].columns:
                            st.session_state.df_processed[col] = data_to_restore["original_columns_df"][col]

                    elif operation_to_undo == "Codificação de Colunas Categóricas":
                        if data_to_restore.get("encoding_type") == "label":
                            for col, series in data_to_restore["original_series_dict"].items():
                                st.session_state.df_processed[col] = series
                        elif data_to_restore.get("encoding_type") == "onehot":
                            st.session_state.df_processed.drop(columns=data_to_restore["dummy_columns"], inplace=True, errors="ignore")
                            for col in data_to_restore["original_columns_df"].columns:
                                st.session_state.df_processed[col] = data_to_restore["original_columns_df"][col]

                    if st.session_state.pipeline_steps:
                        st.session_state.pipeline_steps.pop()
                    
                    st.session_state.preprocess_feedback = {"type": "success", "message": f"Ação '{description}' desfeita com sucesso!"}
                    st.rerun()
                else:
                    st.session_state.preprocess_feedback = {"type": "warning", "message": "Nenhuma ação para desfazer."}
                    st.rerun()

        with btn_col2:
            if st.button("Resetar DataFrame", key="reset_df_preprocess_btn", use_container_width=True):
                st.session_state.df_processed = df_original.copy()
                st.session_state.preprocess_df_original_ref_columns = df_original.columns.tolist()
                st.session_state.preprocess_df_original_ref_shape = df_original.shape
                st.session_state.pipeline_steps = []
                st.session_state.undo_stack = []
                st.session_state.preprocess_feedback = {"type": "info", "message": "DataFrame resetado para o estado original e pipeline limpo."}
                st.rerun()

    with col2_info_rows:
        st.metric(label="Linhas Atuais", value=st.session_state.df_processed.shape[0])
    with col3_info_cols:
        st.metric(label="Colunas Atuais", value=st.session_state.df_processed.shape[1])

    st.markdown("---")

    tabs_list = ["Tratar Nulos", "Duplicatas", "Tipos de Dados", "Codificação de Categorias", "Escalonamento", "Visualizar/Baixar Interativo", "Aplicar Pipeline em Lote"]
    tab_nulos, tab_duplicatas, tab_tipos, tab_encoding, tab_escalonamento, tab_visualizar, tab_aplicar_pipeline = st.tabs(tabs_list)

    # --- Tab: Tratar Nulos ---
    with tab_nulos:
        st.subheader("Tratamento de Valores Nulos")
        with st.form("nulos_form", clear_on_submit=False):
            na_cols_all = st.session_state.df_processed.columns.tolist()
            na_cols = st.multiselect(
                "Selecione colunas para tratar nulos", na_cols_all, default=None, key="na_cols_select_key"
            )
            na_strategy = st.radio(
                "Estratégia:", ["Remover Linhas com Nulos", "Remover Colunas com Nulos", "Preencher Nulos"],
                key="na_strategy_radio_key", horizontal=True
            )
            na_col_thresh_percent, na_fill_num_method, na_fill_cat_method, na_fill_value = 50, "Média", "Moda", ""

            if na_strategy == "Remover Colunas com Nulos":
                na_col_thresh_percent = st.slider(
                    "Threshold de remoção (% de nulos)", 0, 100, 50, key="na_col_thresh_slider_key"
                )
            elif na_strategy == "Preencher Nulos":
                st.markdown("#### Opções de Preenchimento")
                col_fill_1, col_fill_2 = st.columns(2)
                with col_fill_1:
                    na_fill_num_method = st.selectbox(
                        "Método para numéricas:", ["Média", "Mediana", "Moda", "Valor Específico"],
                        key="na_fill_num_method_select_key"
                    )
                with col_fill_2:
                    na_fill_cat_method = st.selectbox(
                        "Método para categóricas:", ["Moda", "Valor Específico"],
                        key="na_fill_cat_method_select_key"
                    )
                if "Valor Específico" in [na_fill_num_method, na_fill_cat_method]:
                    na_fill_value = st.text_input(
                        "Valor específico:", key="na_fill_value_input_key"
                    )
            submitted_nulos = st.form_submit_button("Aplicar Tratamento de Nulos")

        if submitted_nulos:
            cols_to_process_nulos = na_cols
            if not na_cols and na_strategy == "Remover Colunas com Nulos":
                cols_to_process_nulos = st.session_state.df_processed.columns.tolist()
            elif not na_cols and na_strategy != "Remover Colunas com Nulos":
                st.session_state.preprocess_feedback = {"type": "warning", "message": "Selecione colunas para esta estratégia."}
                st.rerun()

            if cols_to_process_nulos or (na_strategy == "Remover Colunas com Nulos"):
                
                if na_strategy == "Remover Linhas com Nulos":
                    df = st.session_state.df_processed
                    condition = df[cols_to_process_nulos].isnull().any(axis=1)
                    removed_rows_df = df[condition].copy()

                    if not removed_rows_df.empty:
                        description = f"Removeu {len(removed_rows_df)} linha(s) com nulos em {', '.join(cols_to_process_nulos)}"
                        undo_action = {
                            "operation_name": "Tratamento de Nulos",
                            "description_for_history": description,
                            "data_for_undo": {
                                "strategy": "Remover Linhas com Nulos",
                                "removed_rows_df": removed_rows_df
                            }
                        }
                        st.session_state.undo_stack.append(undo_action)
                        # TODO: Implementar coleta de undo para outras estratégias de nulos

                df_temp, msg = preprocess_helpers.handle_missing_values(
                    st.session_state.df_processed, columns=cols_to_process_nulos, strategy=na_strategy,
                    threshold=na_col_thresh_percent, fill_numeric_method=na_fill_num_method,
                    fill_categorical_method=na_fill_cat_method, specific_value=na_fill_value
                )
                if "Erro" in msg or "inválida" in msg or "Por favor, selecione colunas" in msg:
                    st.session_state.preprocess_feedback = {"type": "error", "message": msg}
                    if na_strategy == "Remover Linhas com Nulos" and st.session_state.undo_stack:
                        if st.session_state.undo_stack[-1]["description_for_history"].startswith("Removeu"):
                            st.session_state.undo_stack.pop()
                else:
                    st.session_state.df_processed = df_temp
                    st.session_state.preprocess_feedback = {"type": "success", "message": msg}
                    step_params = {"strategy": na_strategy, "columns": cols_to_process_nulos}
                    if na_strategy == "Remover Colunas com Nulos":
                        step_params["threshold_percentage"] = na_col_thresh_percent
                    elif na_strategy == "Preencher Nulos":
                        fill_details = {"numeric_method": na_fill_num_method, "categorical_method": na_fill_cat_method}
                        if "Valor Específico" in [na_fill_num_method, na_fill_cat_method] and na_fill_value:
                            fill_details["specific_value"] = na_fill_value
                        step_params["fill_details"] = fill_details
                    st.session_state.pipeline_steps.append({"operation_name": "Tratamento de Nulos", "parameters": step_params})
                st.rerun()

    # --- Tab: Duplicatas ---
    with tab_duplicatas:
        st.subheader("Remoção de Linhas Duplicadas")
        
        # CORREÇÃO APLICADA AQUI
        num_duplicates = st.session_state.df_processed.duplicated().sum() if not st.session_state.df_processed.empty else 0
        is_button_disabled = (int(num_duplicates) == 0)
        
        st.write(f"Linhas duplicadas encontradas: **{num_duplicates}**")
        
        if st.button("Remover Linhas Duplicadas", key="remove_duplicates_btn_key", disabled=is_button_disabled):
            df = st.session_state.df_processed
            duplicates_df = df[df.duplicated(keep='first')].copy()

            if not duplicates_df.empty:
                description = f"Removeu {len(duplicates_df)} linha(s) duplicada(s)"
                undo_action = {
                    "operation_name": "Remoção de Linhas Duplicadas",
                    "description_for_history": description,
                    "data_for_undo": {
                        "removed_rows_df": duplicates_df
                    }
                }
                st.session_state.undo_stack.append(undo_action)

            df_temp, msg = preprocess_helpers.remove_duplicates(st.session_state.df_processed)
            
            if "Erro" in msg:
                st.session_state.preprocess_feedback = {"type": "error", "message": msg}
                if not duplicates_df.empty and st.session_state.undo_stack:
                    if st.session_state.undo_stack[-1]["operation_name"] == "Remoção de Linhas Duplicadas":
                        st.session_state.undo_stack.pop()
            else:
                st.session_state.df_processed = df_temp
                st.session_state.preprocess_feedback = {"type": "success" if "removidas" in msg else "info", "message": msg}
                st.session_state.pipeline_steps.append({
                    "operation_name": "Remoção de Linhas Duplicadas",
                    "parameters": {"details": "Todas as duplicatas removidas (mantendo a primeira ocorrência)."}
                })
            st.rerun()

    # --- Tab: Tipos de Dados ---
    with tab_tipos:
        st.subheader("Conversão de Tipos de Dados")
        if st.session_state.df_processed.empty: st.warning("DataFrame vazio.")
        else:
            with st.form("types_form", clear_on_submit=True):
                type_col_select = st.selectbox("Coluna para alterar tipo:", st.session_state.df_processed.columns.tolist(), key="type_col_select_box_key", index=None)
                type_new_type = st.selectbox("Converter para:", ["Numérico (float)", "Numérico (int)", "Texto (string)", "Data/Hora (datetime)"], key="type_new_type_select_key")
                submitted_types = st.form_submit_button("Aplicar Conversão")
            if submitted_types and type_col_select:
                # --- COLETA PARA UNDO ---
                original_series = st.session_state.df_processed[type_col_select].copy()
                undo_action = {
                    "operation_name": "Conversão de Tipos de Dados",
                    "description_for_history": f"Conversão de tipo da coluna '{type_col_select}'",
                    "data_for_undo": {
                        "original_series": original_series,
                        "column_name": type_col_select
                    }
                }
                st.session_state.undo_stack.append(undo_action)
                # --- FIM COLETA ---

                df_temp, msg = preprocess_helpers.convert_data_type(st.session_state.df_processed, type_col_select, type_new_type)
                if "Erro" not in msg and "Falha" not in msg:
                    st.session_state.df_processed = df_temp
                    st.session_state.preprocess_feedback = {"type": "success", "message": msg}
                    st.session_state.pipeline_steps.append({
                        "operation_name": "Conversão de Tipos de Dados",
                        "parameters": {"column_to_convert": type_col_select, "new_type": type_new_type}
                    })
                    buffer_info_col = io.StringIO()
                    st.session_state.df_processed[[type_col_select]].info(buf=buffer_info_col)
                    st.text_area(f"Info da coluna '{type_col_select}' após conversão:", buffer_info_col.getvalue(), height=100, key=f"info_conv_{type_col_select}")

                else:
                    st.session_state.preprocess_feedback = {"type": "error", "message": msg}
                    if st.session_state.undo_stack and st.session_state.undo_stack[-1]["operation_name"] == "Conversão de Tipos de Dados":
                        st.session_state.undo_stack.pop()
                st.rerun()
            elif submitted_types and not type_col_select:
                st.session_state.preprocess_feedback = {"type": "warning", "message": "Nenhuma coluna selecionada."}
                st.rerun()

    # --- Tab: Codificação de Categorias ---
    with tab_encoding:
        st.subheader("Codificação de Colunas Categóricas")
        cat_cols_options = st.session_state.df_processed.select_dtypes(include=['object', 'category']).columns.tolist() if not st.session_state.df_processed.empty else []
        if not cat_cols_options: st.info("Nenhuma coluna categórica detectada.")
        else:
            with st.form("encoding_form"):
                enc_cols = st.multiselect("Colunas para codificar:", cat_cols_options, key="enc_cols_select_key")
                enc_method_options = {"One-Hot Encoding (Colunas Binárias)": "One-Hot Encoding (Dummy Variables)", "Label Encoding (Rótulos Numéricos)": "Label Encoding"}
                enc_method_display = st.radio("Método:", list(enc_method_options.keys()), key="enc_method_radio_key", horizontal=True)
                submitted_encoding = st.form_submit_button("Aplicar Codificação")
            if submitted_encoding:
                if not enc_cols:
                    st.session_state.preprocess_feedback = {"type": "warning", "message": "Nenhuma coluna selecionada."}
                else:
                    actual_enc_method = enc_method_options[enc_method_display]
                    # --- COLETA PARA UNDO ---
                    if actual_enc_method == "Label Encoding":
                        # Salva todas as colunas originais
                        original_series_dict = {col: st.session_state.df_processed[col].copy() for col in enc_cols}
                        undo_action = {
                            "operation_name": "Codificação de Colunas Categóricas",
                            "description_for_history": f"Label Encoding em {', '.join(enc_cols)}",
                            "data_for_undo": {
                                "encoding_type": "label",
                                "original_series_dict": original_series_dict
                            }
                        }
                        st.session_state.undo_stack.append(undo_action)
                    elif actual_enc_method == "One-Hot Encoding (Dummy Variables)":
                        original_columns_df = st.session_state.df_processed[enc_cols].copy()
                        df_temp, _ = preprocess_helpers.encode_categorical_features(st.session_state.df_processed, enc_cols, actual_enc_method)
                        new_dummy_columns = list(set(df_temp.columns) - set(st.session_state.df_processed.columns))
                        undo_action = {
                            "operation_name": "Codificação de Colunas Categóricas",
                            "description_for_history": f"One-Hot Encoding em {', '.join(enc_cols)}",
                            "data_for_undo": {
                                "encoding_type": "onehot",
                                "original_columns_df": original_columns_df,
                                "dummy_columns": new_dummy_columns
                            }
                        }
                        st.session_state.undo_stack.append(undo_action)
                    # --- FIM COLETA ---

                    df_temp, msg = preprocess_helpers.encode_categorical_features(st.session_state.df_processed, enc_cols, actual_enc_method)
                    if "Erro" not in msg:
                        st.session_state.df_processed = df_temp
                        st.session_state.preprocess_feedback = {"type": "success", "message": msg}
                        st.session_state.pipeline_steps.append({
                            "operation_name": "Codificação de Colunas Categóricas",
                            "parameters": {"columns_to_encode": enc_cols, "method": actual_enc_method}
                        })
                        st.dataframe(st.session_state.df_processed.head())
                    else:
                        st.session_state.preprocess_feedback = {"type": "error", "message": msg}
                        if st.session_state.undo_stack and st.session_state.undo_stack[-1]["operation_name"] == "Codificação de Colunas Categóricas":
                            st.session_state.undo_stack.pop()
                st.rerun()

    # --- Tab: Escalonamento ---
    with tab_escalonamento:
        st.subheader("Escalonamento de Colunas Numéricas")
        num_cols_options = st.session_state.df_processed.select_dtypes(include=[np.number]).columns.tolist() if not st.session_state.df_processed.empty else []
        if not num_cols_options: st.info("Nenhuma coluna numérica detectada.")
        else:
            with st.form("scaling_form"):
                scale_cols = st.multiselect("Colunas para escalonar:", num_cols_options, key="scale_cols_select_key")
                scale_method = st.radio("Método:", ["Min-Max Scaler (Normalização)", "Standard Scaler (Padronização)"], key="scale_method_radio_key", horizontal=True)
                submitted_scaling = st.form_submit_button("Aplicar Escalonamento")
            if submitted_scaling:
                if not scale_cols:
                    st.session_state.preprocess_feedback = {"type": "warning", "message": "Nenhuma coluna selecionada."}
                else:
                    # --- COLETA PARA UNDO ---
                    original_columns_df = st.session_state.df_processed[scale_cols].copy()
                    undo_action = {
                        "operation_name": "Escalonamento de Colunas Numéricas",
                        "description_for_history": f"Escalonamento de {', '.join(scale_cols)}",
                        "data_for_undo": {
                            "original_columns_df": original_columns_df
                        }
                    }
                    st.session_state.undo_stack.append(undo_action)
                    # --- FIM COLETA ---

                    df_temp, msg = preprocess_helpers.scale_numerical_features(st.session_state.df_processed, scale_cols, scale_method)
                    if "Erro" not in msg and "não pode ser escalonada" not in msg:
                        st.session_state.df_processed = df_temp
                        st.session_state.preprocess_feedback = {"type": "success", "message": msg}
                        st.session_state.pipeline_steps.append({
                            "operation_name": "Escalonamento de Colunas Numéricas",
                            "parameters": {"columns_to_scale": scale_cols, "method": scale_method}
                        })
                        st.dataframe(st.session_state.df_processed[scale_cols].describe())
                    else:
                        st.session_state.preprocess_feedback = {"type": "error", "message": msg}
                        if st.session_state.undo_stack and st.session_state.undo_stack[-1]["operation_name"] == "Escalonamento de Colunas Numéricas":
                            st.session_state.undo_stack.pop()
                st.rerun()

    # --- Tab: Visualizar/Baixar Interativo ---
    with tab_visualizar:
        st.subheader("Visualizar DataFrame (Edição Interativa) e Baixar")
        st.markdown("#### Pré-visualização (Primeiras 5 linhas)")
        if not st.session_state.df_processed.empty: st.dataframe(st.session_state.df_processed.head())
        else: st.warning("DataFrame de edição interativa está vazio.")

        st.markdown("#### Informações do DataFrame")
        if not st.session_state.df_processed.empty:
            buffer_info_df = io.StringIO()
            st.session_state.df_processed.info(buf=buffer_info_df)
            st.text_area("Informações:", buffer_info_df.getvalue(), height=200, key="df_info_processed_text_area", disabled=True)
        else: st.warning("DataFrame vazio, sem informações.")

        if not st.session_state.df_processed.empty:
            csv_processed = st.session_state.df_processed.to_csv(index=False).encode('utf-8')
            st.download_button(label="Baixar CSV (Edição Interativa)", data=csv_processed, file_name=f"processed_interactive_{filename_original}", mime="text/csv", key="download_interactive_csv")

        st.markdown("---")
        st.subheader("Pipeline de Pré-Processamento Aplicado (Edição Interativa)")
        if 'pipeline_steps' in st.session_state and st.session_state.pipeline_steps:
            st.write("Passos aplicados:")
            st.json(st.session_state.pipeline_steps, expanded=False)
            pipeline_json_str = json.dumps(st.session_state.pipeline_steps, indent=2, ensure_ascii=False)
            base_fn = filename_original.rsplit('.', 1)[0] if '.' in filename_original else filename_original
            st.download_button(label="Baixar Pipeline (JSON)", data=pipeline_json_str, file_name=f"pipeline_{base_fn}.json", mime="application/json", key="download_pipeline_json")
        else: st.info("Nenhum passo registrado na edição interativa.")

    # --- Tab: Aplicar Pipeline em Lote ---
    with tab_aplicar_pipeline:
        st.subheader("Aplicar Pipeline Salvo a um Novo CSV")
        if st.session_state.get('batch_feedback'):
            feedback_batch = st.session_state.batch_feedback
            if feedback_batch["type"] == "success":
                st.success(feedback_batch["message"])
            elif feedback_batch["type"] == "error":
                st.error(feedback_batch["message"])
            elif feedback_batch["type"] == "warning":
                st.warning(feedback_batch["message"])
            else:
                st.info(feedback_batch["message"])
            st.session_state.batch_feedback = None

        uploaded_pipeline_file = st.file_uploader("1. Carregar arquivo de Pipeline (.json)", type=["json"], key="pipeline_uploader")
        uploaded_new_csv_file = st.file_uploader("2. Carregar NOVO arquivo CSV para aplicar o pipeline", type=["csv"], key="new_csv_uploader")

        if st.button("Aplicar Pipeline ao Novo CSV", key="apply_batch_pipeline_btn"):
            if uploaded_pipeline_file is not None and uploaded_new_csv_file is not None:
                try:
                    pipeline_data = json.load(uploaded_pipeline_file)
                    new_df_to_process = pd.read_csv(uploaded_new_csv_file)
                    st.session_state.new_csv_filename_for_batch = uploaded_new_csv_file.name

                    if not isinstance(pipeline_data, list):
                        st.session_state.batch_feedback = {"type": "error", "message": "Arquivo de pipeline inválido. Deve ser uma lista de passos."}
                        st.rerun()

                    current_df_state = new_df_to_process.copy()
                    applied_steps_summary = []

                    for i, step in enumerate(pipeline_data):
                        op_name = step.get("operation_name")
                        params = step.get("parameters", {})

                        if not op_name:
                            st.session_state.batch_feedback = {"type": "error", "message": f"Passo {i+1} do pipeline não tem 'operation_name'."}
                            current_df_state = None
                            break

                        required_cols_keys = ['columns', 'column_to_convert', 'columns_to_encode', 'columns_to_scale']
                        for key in required_cols_keys:
                            if key in params:
                                cols_in_step = params[key]
                                if isinstance(cols_in_step, str):
                                    cols_in_step = [cols_in_step]
                                if not all(col in current_df_state.columns for col in cols_in_step):
                                    st.session_state.batch_feedback = {"type": "error", "message": f"Erro no passo '{op_name}': Uma ou mais colunas ({', '.join(cols_in_step)}) não encontradas no CSV atual."}
                                    current_df_state = None
                                    break
                        if current_df_state is None: break

                        temp_df_state = current_df_state.copy()
                        msg = "Operação não reconhecida ou erro interno."

                        if op_name == "Tratamento de Nulos":
                            temp_df_state, msg = preprocess_helpers.handle_missing_values(
                                temp_df_state,
                                columns=params.get("columns"),
                                strategy=params.get("strategy"),
                                threshold=params.get("threshold_percentage"),
                                fill_numeric_method=params.get("fill_details", {}).get("numeric_method"),
                                fill_categorical_method=params.get("fill_details", {}).get("categorical_method"),
                                specific_value=params.get("fill_details", {}).get("specific_value")
                            )
                        elif op_name == "Remoção de Linhas Duplicadas":
                            temp_df_state, msg = preprocess_helpers.remove_duplicates(temp_df_state)
                        elif op_name == "Conversão de Tipos de Dados":
                            temp_df_state, msg = preprocess_helpers.convert_data_type(
                                temp_df_state,
                                column_to_convert=params.get("column_to_convert"),
                                new_type_str=params.get("new_type")
                            )
                        elif op_name == "Codificação de Colunas Categóricas":
                            temp_df_state, msg = preprocess_helpers.encode_categorical_features(
                                temp_df_state,
                                columns_to_encode=params.get("columns_to_encode"),
                                method=params.get("method")
                            )
                        elif op_name == "Escalonamento de Colunas Numéricas":
                            temp_df_state, msg = preprocess_helpers.scale_numerical_features(
                                temp_df_state,
                                columns_to_scale=params.get("columns_to_scale"),
                                method=params.get("method")
                            )
                        else:
                            msg = f"Operação '{op_name}' não suportada na aplicação em lote."
                            st.session_state.batch_feedback = {"type": "warning", "message": msg}
                            applied_steps_summary.append(f"Passo {i+1}: {op_name} - AVISO: {msg}")
                            continue

                        if "Erro" in msg or "inválida" in msg or "Falha" in msg or "não suportado" in msg or "Não é possível converter" in msg:
                            st.session_state.batch_feedback = {"type": "error", "message": f"Erro ao aplicar passo '{op_name}': {msg}"}
                            current_df_state = None
                            break
                        else:
                            current_df_state = temp_df_state
                            applied_steps_summary.append(f"Passo {i+1}: {op_name} - OK. {msg.split('.')[0] if '.' in msg else msg}")

                    if current_df_state is not None:
                        st.session_state.df_batch_processed = current_df_state
                        st.session_state.batch_feedback = {"type": "success", "message": "Pipeline aplicado com sucesso ao novo CSV!"}
                        st.write("Resumo da aplicação dos passos:")
                        for item in applied_steps_summary:
                            st.text(item)

                except Exception as e:
                    st.session_state.batch_feedback = {"type": "error", "message": f"Erro geral ao aplicar pipeline: {str(e)}"}

                st.rerun()

            else:
                st.session_state.batch_feedback = {"type": "warning", "message": "Por favor, carregue o arquivo de pipeline (.json) e o novo arquivo CSV."}
                st.rerun()

        if st.session_state.df_batch_processed is not None:
            st.markdown("---")
            st.subheader("Resultado do Processamento em Lote")
            st.markdown("#### Pré-visualização do DataFrame Processado em Lote (Primeiras 5 linhas)")
            st.dataframe(st.session_state.df_batch_processed.head())

            st.markdown("#### Informações do DataFrame Processado em Lote")
            buffer_info_batch_df = io.StringIO()
            st.session_state.df_batch_processed.info(buf=buffer_info_batch_df)
            info_batch_str = buffer_info_batch_df.getvalue()
            st.text_area("Informações:", info_batch_str, height=200, key="df_info_batch_processed_text_area", disabled=True)

            try:
                csv_batch_processed = st.session_state.df_batch_processed.to_csv(index=False).encode('utf-8')
                batch_processed_filename = f"batched_processed_{st.session_state.new_csv_filename_for_batch}" if st.session_state.new_csv_filename_for_batch else "batched_processed_data.csv"
                st.download_button(
                    label="Baixar CSV Processado em Lote",
                    data=csv_batch_processed,
                    file_name=batch_processed_filename,
                    mime="text/csv",
                    key="download_batch_processed_csv"
                )
            except Exception as e:
                st.error(f"Erro ao gerar CSV (processado em lote) para download: {e}")