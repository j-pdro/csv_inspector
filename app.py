import streamlit as st
import pandas as pd
from modules import eda, indicadores, preprocessamento # Adicionado preprocessamento

# --- Configuração da Página ---
# Deve ser a primeira comando Streamlit e chamada apenas uma vez.
st.set_page_config(page_title="🧭 CSV Inspector", layout="wide", initial_sidebar_state="expanded")

# --- Inicialização do Estado da Sessão ---
if "active_section" not in st.session_state:
    st.session_state.active_section = "home" # Iniciar na home
if "uploaded_file_data" not in st.session_state: # Armazenar o objeto do arquivo
    st.session_state.uploaded_file_data = None
if "df" not in st.session_state: # Armazenar o DataFrame original carregado
    st.session_state.df = None
if "filename" not in st.session_state: # Armazenar o nome do arquivo
    st.session_state.filename = None

# --- Funções Auxiliares ---
def switch_section(section_name):
    st.session_state.active_section = section_name
    # Não é necessário st.rerun() aqui, pois o Streamlit re-executa ao mudar o estado da sessão
    # que afeta a renderização condicional do conteúdo principal.

def reset_preprocess_state():
    """Reseta os estados específicos do módulo de pré-processamento."""
    keys_to_delete = [
        'df_processed', 
        'preprocess_df_original_ref_columns', 
        'preprocess_df_original_ref_shape', 
        'preprocess_feedback'
    ]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]
    # st.toast("Estado do pré-processamento resetado.", icon="🧹") # Opcional

# === SIDEBAR ===
with st.sidebar:
    st.markdown("## 🧭 CSV Inspector")
    st.markdown("### Navegação")
    st.button("🏠 Home", on_click=switch_section, args=("home",), use_container_width=True, key="nav_home")
    
    # Habilitar botões de análise apenas se um DF estiver carregado
    df_loaded = st.session_state.df is not None

    st.button("🔎 Análise Exploratória", on_click=switch_section, args=("eda",), use_container_width=True, key="nav_eda", disabled=not df_loaded)
    st.button("📊 Indicadores Estatísticos", on_click=switch_section, args=("stats",), use_container_width=True, key="nav_stats", disabled=not df_loaded)
    st.button("🧹 Pré-processamento", on_click=switch_section, args=("prep",), use_container_width=True, key="nav_prep", disabled=not df_loaded) # Habilitado e condicional
    
    st.markdown("---")
    st.markdown("### 📂 Faça Upload do CSV:")
    
    uploaded_file_obj = st.file_uploader(
        "Selecione um arquivo CSV",
        type="csv",
        key="main_csv_uploader"
    )

    if uploaded_file_obj is not None:
        # Se um novo arquivo for carregado (nome diferente ou era None), atualize o estado
        is_new_file = (st.session_state.uploaded_file_data is None or 
                       uploaded_file_obj.name != st.session_state.filename)

        if is_new_file:
            st.session_state.uploaded_file_data = uploaded_file_obj
            st.session_state.filename = uploaded_file_obj.name
            try:
                # Ler o DataFrame aqui para que esteja disponível para todas as seções
                # Importante: usar uma cópia do uploaded_file_obj para leitura,
                # pois o objeto pode ser fechado ou modificado pelo Streamlit.
                # Para CSVs, pd.read_csv(uploaded_file_obj) geralmente funciona bem.
                df_temp = pd.read_csv(uploaded_file_obj)
                st.session_state.df = df_temp # Armazena o DataFrame original
                
                st.success(f"Arquivo '{st.session_state.filename}' carregado!")
                
                # Resetar estados de módulos específicos ao carregar NOVO arquivo
                reset_preprocess_state() # Reseta o estado do pré-processamento
                
                # Opcional: Mudar para uma seção padrão após o upload, se desejado
                if st.session_state.active_section == "home": # Se estava na home, talvez ir para EDA
                     switch_section("eda")
                
                st.rerun() # Força a re-execução para atualizar a UI com o novo DF e seção

            except Exception as e:
                st.error(f"Erro ao ler o CSV: {e}")
                st.session_state.df = None
                st.session_state.uploaded_file_data = None
                st.session_state.filename = None
                reset_preprocess_state() # Também reseta em caso de erro no upload
                st.rerun()

    elif st.session_state.uploaded_file_data is not None and uploaded_file_obj is None:
        # Lógica para quando o usuário remove o arquivo do uploader (clica no 'x')
        # st.info("Arquivo removido. Faça upload de um novo CSV.") # Opcional
        st.session_state.df = None
        st.session_state.uploaded_file_data = None
        st.session_state.filename = None
        reset_preprocess_state() # Reseta o estado do pré-processamento
        switch_section("home") # Volta para home
        st.rerun()

# === Conteúdo Principal ===
current_section = st.session_state.active_section
current_df = st.session_state.df # Este é o DataFrame ORIGINAL
current_filename = st.session_state.filename

if current_section == "home":
    st.header("Bem-vindo ao CSV Inspector! 👋")
    st.markdown("""
    Esta ferramenta ajuda você a realizar Análise Exploratória de Dados (EDA),
    calcular Indicadores Estatísticos e realizar Limpeza e Pré-Processamento
    de forma rápida e interativa a partir de arquivos CSV.

    **Como usar:**
    1.  Clique em **"Procurar arquivos"** (ou arraste e solte) na barra lateral para fazer o upload do seu arquivo CSV.
    2.  Após o upload, os botões de análise serão habilitados. Selecione uma das opções:
        *   **🔎 Análise Exploratória:** Para visualizar distribuições, correlações, dados ausentes e mais.
        *   **📊 Indicadores Estatísticos:** Para obter métricas descritivas detalhadas.
        *   **🧹 Pré-processamento:** Para limpar, transformar e preparar seus dados.
    """)
    if current_df is None:
        st.info("⬅️ Por favor, faça o upload de um arquivo CSV na barra lateral para começar.")
    else:
        st.success(f"Arquivo '{current_filename}' está carregado e pronto. Escolha uma seção de análise na barra lateral.")

elif current_df is None: # Se não for home e não tiver DF, mostrar aviso
    st.warning("⚠️ Por favor, faça o upload de um arquivo CSV na barra lateral primeiro.")
    st.button("Ir para Home", on_click=switch_section, args=("home",))

elif current_section == "eda":
    st.header("🔎 Análise Exploratória de Dados")
    st.caption(f"Analisando o arquivo: **{current_filename}**")
    eda.run_eda(current_df, current_filename)

elif current_section == "stats":
    st.header("📊 Indicadores Estatísticos")
    st.caption(f"Calculando indicadores para o arquivo: **{current_filename}**")
    indicadores.run_indicadores(current_df, current_filename)

elif current_section == "prep":
    st.header("🧹 Limpeza e Pré-Processamento de Dados")
    st.caption(f"Modificando o arquivo: **{current_filename}** (as alterações são aplicadas a uma cópia)")
    # A função run_preprocessamento usará st.session_state.df como o df_original
    # e gerenciará st.session_state.df_processed internamente.
    preprocessamento.run_preprocessamento(current_df, current_filename)

else:
    # Caso padrão ou se active_section for None (não deve acontecer com a inicialização)
    st.error("Seção desconhecida. Retornando para a Home.")
    switch_section("home")
    st.rerun()