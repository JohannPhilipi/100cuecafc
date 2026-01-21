import streamlit as st

from views.financeiro import render_financeiro
from views.elenco import render_elenco
from views.home import render_principal
from views.estatisticas import render_estatisticas

# --- 1. CONFIGURAÇÕES E ESTILO ---
def setup_layout():
    st.set_page_config(page_title="100Cueca FC", layout="wide", page_icon="images/logo_16x16.png")
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; }
        [data-testid="stMetricValue"] { font-size: 1.8rem; color: #3b82f6; }
        </style>
    """, unsafe_allow_html=True)


# --- 2. CONTROLLER PRINCIPAL ---
def main():
    setup_layout()
    
    # Sidebar Customizada
    st.sidebar.image("images/logo_256x256.png")
    with st.sidebar:
        escolha = st.radio("------", ["Início", "Elenco", "Financeiro", "Estatísticas"])
    
    st.sidebar.divider()
    st.sidebar.write("**Versão 0.1.0 (Beta)**")

    # Roteamento de Abas
    if escolha == "Início":
        render_principal()
    elif escolha == "Elenco":
        render_elenco()
    elif escolha == "Financeiro":
        render_financeiro()
    elif escolha == "Estatísticas":
        render_estatisticas()

# Execução do App
if __name__ == "__main__":
    main()