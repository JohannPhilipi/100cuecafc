import streamlit as st

from utils.sheet import carregar_planilha

def render_estatisticas():
    st.title("📊 Estatísticas - 100Cueca")

    # ======================
    # CARGA
    # ======================
    df_series = carregar_planilha("Series")
    df_jogos = carregar_planilha("Jogos")
    df_gols = carregar_planilha("Gols")

    if df_series.empty:
        st.warning("Nenhuma série encontrada.")
        return

    # ======================
    # SELEÇÃO DA SÉRIE
    # ======================
    st.subheader("🎯 Seleção da Série")

    series_ids = df_series["Serie_id"].astype(str).tolist()
    serie_sel = st.selectbox("Série", series_ids)

    serie = df_series[df_series["Serie_id"] == serie_sel].iloc[0]

    # ======================
    # MELHOR DE 3
    # ======================
    st.divider()
    st.subheader("🔥 Desafio Melhor de 3")

    jogos_serie = df_jogos[df_jogos["Serie_id"] == serie_sel]

    vitorias_roxo = (jogos_serie["Vencedor"] == "Roxo").sum()
    vitorias_amarelo = (jogos_serie["Vencedor"] == "Amarelo").sum()

    c1, c2, c3 = st.columns([2, 1, 2])

    with c1:
        st.markdown(
            "<h2 style='text-align:center;color:#8a2be2;'>🟪 TIME ROXO</h2>",
            unsafe_allow_html=True
        )
        st.markdown(f"<h1 style='text-align:center;'>{vitorias_roxo}</h1>", unsafe_allow_html=True)

    with c2:
        st.markdown("<h1 style='text-align:center;padding-top:20px;'>VS</h1>", unsafe_allow_html=True)
        if vitorias_roxo > vitorias_amarelo:
            st.success("Roxo na frente!")
        elif vitorias_roxo < vitorias_amarelo:
            st.warning("Amarelo na frente!")
        else:
            st.info("Série empatada!")

    with c3:
        st.markdown(
            "<h2 style='text-align:center;color:#ffd700;'>🟨 TIME AMARELO</h2>",
            unsafe_allow_html=True
        )
        st.markdown(f"<h1 style='text-align:center;'>{vitorias_amarelo}</h1>", unsafe_allow_html=True)

    # ======================
    # JOGOS DA SÉRIE
    # ======================
    st.divider()
    st.subheader("📋 Jogos da Série")

    df_view = jogos_serie.copy()

    if "Data_dt" in df_view.columns:
        df_view["Data"] = df_view["Data_dt"].dt.strftime("%d/%m/%Y")
        df_view = df_view.drop(columns=["Data_dt"])

    colunas = ["Jogo", "Data", "Placar_roxo", "Placar_amarelo", "Vencedor"]
    colunas = [c for c in colunas if c in df_view.columns]

    st.dataframe(df_view[colunas], width="stretch", hide_index=True)

    # ======================
    # ARTILHARIA DA SÉRIE
    # ======================
    st.divider()
    st.subheader("⚽ Artilharia da Série")

    gols_serie = df_gols[df_gols["Serie_id"] == serie_sel]

    if gols_serie.empty:
        st.info("Nenhum gol registrado nesta série.")
    else:
        artilharia = (
            gols_serie
            .groupby(["Jogador", "Time"], as_index=False)["Gols"]
            .sum()
            .sort_values("Gols", ascending=False)
        )

        st.dataframe(artilharia, width="stretch", hide_index=True)
