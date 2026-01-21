from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.sheets import carregar_planilha


def normalizar_valor(col):
    return (
        col.astype(str)
        .str.replace("R$", "", regex=False)
        #    .str.replace(".", "", regex=False)   # remove milhar
        .str.replace(",", ".", regex=False)  # corrige decimal
        .str.strip()
        .replace("", "0")
        .astype(float)
    )


def render_financeiro():
    # Estilização para um aspeto mais profissional
    st.markdown(
        """
        <style>
        [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: bold; }
        .stProgress > div > div > div > div { background-color: #2ecc71; }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("💲 Gestão Financeira - 100Cueca")

    try:
        df_mensalidades = carregar_planilha("Mensalidades")
        df_ent_sai = carregar_planilha("Entrada/Saida")

        # --- SEÇÃO DE FILTROS (No topo da página) ---
        st.write("### 📅 Período de Análise")
        c_ano, c_mes = st.columns(2)

        with c_ano:
            anos = []

            if "Data_dt" in df_mensalidades.columns:
                anos += df_mensalidades["Data_dt"].dt.year.dropna().unique().tolist()

            if "Data_dt" in df_ent_sai.columns:
                anos += df_ent_sai["Data_dt"].dt.year.dropna().unique().tolist()

            if not anos:
                anos = [datetime.now().year]

            anos = sorted(set(anos), reverse=True)

            ano_sel = st.selectbox("Ano", anos)

        with c_mes:
            meses_nomes = {
                1: "Janeiro",
                2: "Fevereiro",
                3: "Março",
                4: "Abril",
                5: "Maio",
                6: "Junho",
                7: "Julho",
                8: "Agosto",
                9: "Setembro",
                10: "Outubro",
                11: "Novembro",
                12: "Dezembro",
            }
            mes_sel_nome = st.selectbox("Mês", ["Todos"] + list(meses_nomes.values()))

        # --- LÓGICA DE FILTRAGEM ---
        def filtrar(df, ano, mes_nome):
            if "Data_dt" not in df.columns:
                return df
            mask = df["Data_dt"].dt.year == ano
            if mes_nome != "Todos":
                mes_num = [k for k, v in meses_nomes.items() if v == mes_nome][0]
                mask &= df["Data_dt"].dt.month == mes_num
            return df[mask]

        df_mensal = filtrar(df_mensalidades, ano_sel, mes_sel_nome).copy()
        df_ent_sai_filtered = filtrar(df_ent_sai, ano_sel, mes_sel_nome).copy()

        df_ent = df_ent_sai_filtered[df_ent_sai_filtered["Tipo"] == "Entrada"].copy()
        df_sai = df_ent_sai_filtered[df_ent_sai_filtered["Tipo"] == "Saida"].copy()

        df_mensal["Descrição"] = df_mensal["Jogador"]
        df_mensal["Origem"] = "Mensalidade"
        df_mensal["Tipo"] = "Entrada"
        df_ent["Origem"] = "Avulsa"

        # Tratamento de Valores
        for df in [df_mensal, df_ent, df_sai]:
            df["Valor"] = normalizar_valor(df["Valor"])

        df_entradas = pd.concat([df_ent, df_mensal], ignore_index=True)

        # --- CÁLCULOS TOTAIS ---
        total_mensal = df_mensal[df_mensal["Status"] == "Pago"]["Valor"].sum()
        total_ent = df_entradas[df_entradas["Tipo"] == "Entrada"]["Valor"].sum()
        total_sai = df_sai["Valor"].sum()

        saldo_periodo = total_ent - total_sai

        # --- TERMÓMETRO DA FESTA (Baseado no saldo acumulado do ano ou período) ---
        st.divider()
        META_FESTA = 3000.00
        progresso = min(1.0, max(0.0, saldo_periodo / META_FESTA))

        col_t1, col_t2 = st.columns([3, 1])
        with col_t1:
            st.write(
                f"**🥳 Termómetro da Festa de Final de Ano ({ano_sel}) | Meta: R$ {META_FESTA}**"
            )
            st.progress(progresso)
        with col_t2:
            st.write(f"**R$ {saldo_periodo:,.2f}**")

        # --- DASHBOARD DE MÉTRICAS ---
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Receitas", f"R$ {total_ent:,.2f}")
        m2.metric(
            "Despesas",
            f"R$ {total_sai:,.2f}",
            delta=f"-{total_sai:,.2f}",
            delta_color="inverse",
        )
        m3.metric("Saldo", f"R$ {saldo_periodo:,.2f}")

        adimplencia = (
            (len(df_ent[df_ent["Status"] == "Pago"]) / len(df_ent) * 100)
            if len(df_ent) > 0
            else 0
        )
        m4.metric("Adimplência", f"{adimplencia:.0f}%")

        # --- GRÁFICOS PROFISSIONAIS ---
        st.divider()
        c_dir, c_esq = st.columns([2, 1])

        with c_dir:
            st.subheader("📈 Fluxo de Caixa")
            fig = px.bar(
                df_entradas[df_entradas["Status"] == "Pago"],
                x="Data",
                y="Valor",
                title="Entradas por Dia",
                color_discrete_sequence=["#2ecc71"],
            )
            fig.update_layout(height=300, margin=dict(l=0, r=0, b=0, t=30))
            st.plotly_chart(fig, width="stretch")

        with c_esq:
            st.subheader("💸 Gastos")
            if "Categoria" in df_sai.columns and not df_sai.empty:
                fig_pie = px.pie(df_sai, values="Valor", names="Categoria", hole=0.4)
                fig_pie.update_layout(
                    height=300, showlegend=False, margin=dict(l=0, r=0, b=0, t=30)
                )
                st.plotly_chart(fig_pie, width="stretch")

        # --- TABELAS ---
        st.divider()
        t1, t2 = st.tabs(["💰 Detalhe Entradas", "💸 Detalhe Saídas"])
        with t1:
            colunas_exibir = [
                "Data",
                "Descrição",
                "Categoria",
                "Origem",
                "Valor",
                "Status",
            ]
            st.dataframe(
                df_entradas[colunas_exibir].sort_values("Data", ascending=False),
                column_config={
                    "Valor": st.column_config.NumberColumn(
                        "Valor (R$)", format="R$ %.2f"
                    )
                },
                width="stretch",
                hide_index=True,
            )
            # st.dataframe(df_entradas.drop(columns=['Data_dt'], errors='ignore'), width='stretch', hide_index=True)
        with t2:
            colunas_exibir = ["Data", "Descrição", "Categoria", "Valor", "Status"]
            st.dataframe(
                df_sai[colunas_exibir],
                column_config={
                    "Valor": st.column_config.NumberColumn(
                        "Valor (R$)", format="R$ %.2f"
                    )
                },
                width="stretch",
                hide_index=True,
            )
            # st.dataframe(df_sai.drop(columns=['Data_dt'], errors='ignore'), width='stretch', hide_index=True)

    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
