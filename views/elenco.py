import streamlit as st

import plotly.express as px
from utils.sheets import carregar_planilha


def render_elenco():
    # --- ESTILO ---
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏃‍♀️ Elenco - 100Cueca")

    try:
        df_mensalistas = carregar_planilha("Mensalistas")
        df_espera = carregar_planilha("ListaDeEspera")

        # ======================
        # MÉTRICAS GERAIS
        # ======================
        st.divider()
        m1, m2, m3 = st.columns(3)

        total_mensalistas = len(df_mensalistas)
        ativos = (
            len(df_mensalistas[df_mensalistas["Status"] == "Ativo"])
            if "Status" in df_mensalistas.columns
            else total_mensalistas
        )
        espera = len(df_espera)

        m1.metric("Mensalistas", total_mensalistas)
        m2.metric("Ativos", ativos)
        m3.metric("Lista de Espera", espera)

        # ======================
        # GRÁFICOS
        # ======================
        st.divider()
        g1, g2 = st.columns(2)

        with g1:
            st.subheader("📊 Mensalistas por Posição")
            if "Posição" in df_mensalistas.columns and not df_mensalistas.empty:
                fig_pos = px.bar(
                    df_mensalistas,
                    x="Posição",
                    color_discrete_sequence=["#3498db"]
                )
                fig_pos.update_layout(
                    height=300, margin=dict(l=0, r=0, b=0, t=30)
                )
                st.plotly_chart(fig_pos, width="stretch")

        with g2:
            st.subheader("📌 Status dos Mensalistas")
            if "Status" in df_mensalistas.columns and not df_mensalistas.empty:
                fig_status = px.pie(
                    df_mensalistas,
                    names="Status",
                    hole=0.4
                )
                fig_status.update_layout(
                    height=300, margin=dict(l=0, r=0, b=0, t=30)
                )
                st.plotly_chart(fig_status, width="stretch")
        
        # ======================
        # ELENCO (MENSALISTAS)
        # ======================
        st.divider()
        st.subheader("📋 Mensalistas")

        if not df_mensalistas.empty:
            c1, c2 = st.columns(2)

            with c1:
                posicoes = ["Todas"] + sorted(
                    df_mensalistas["Posição"].dropna().unique()
                )
                pos_sel = st.selectbox("Posição", posicoes)

            with c2:
                if "Status" in df_mensalistas.columns:
                    status = ["Todos"] + sorted(
                        df_mensalistas["Status"].dropna().unique()
                    )
                    status_sel = st.selectbox("Status", status)
                else:
                    status_sel = "Todos"

            df_filtrado = df_mensalistas.copy()

            if pos_sel != "Todas":
                df_filtrado = df_filtrado[df_filtrado["Posição"] == pos_sel]

            if status_sel != "Todos" and "Status" in df_filtrado.columns:
                df_filtrado = df_filtrado[df_filtrado["Status"] == status_sel]

            st.dataframe(df_filtrado, width="stretch", hide_index=True)
        else:
            st.info("Nenhum mensalista cadastrado.")
            

        # ======================
        # LISTA DE ESPERA
        # ======================
        st.divider()
        st.subheader("⏳ Lista de Espera")

        if not df_espera.empty and "Nome" in df_espera.columns:
            st.dataframe(
                df_espera[["Nome"]],
                width="stretch",
                hide_index=True
            )
        else:
            st.info("Lista de espera vazia.")

    except Exception as e:
        st.error(f"Erro ao carregar jogadores: {e}")
