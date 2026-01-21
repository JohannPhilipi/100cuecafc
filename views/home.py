import streamlit as st
import pandas as pd

from datetime import datetime, timedelta
from utils.sheets import carregar_planilha
def render_principal():
    # Cabeçalho com Estilo
    st.title("⚽ Central 100Cueca FC")
    st.markdown("---")

    # 1. ACESSO RÁPIDO (Estatuto e Links)
    col_est, col_redes, col_pix = st.columns(3)
    
    with col_est:
        with st.container(border=True):
            st.markdown("📜 **Estatuto do Time**")
            # Aqui você pode linkar um PDF no Google Drive
            st.link_button("Ler Regulamento", "https://tinyurl.com/Regras100cuecafc", width='stretch')
    
    with col_redes:
        with st.container(border=True):
            st.markdown("📸 **Siga o 100Cueca**")
            st.link_button("Instagram", "https://instagram.com/100cuecafc", width='stretch')

    with col_pix:
        with st.container(border=True):
            st.markdown("💸 **Chave PIX - PicPay**")
            st.code("100cuecafc@gmail.com ", language="text")


    st.divider()

    # ==========================
    # 2. O GRANDE CONFRONTO
    # ==========================

    df_series = carregar_planilha("Series")
    df_jogos = carregar_planilha("Jogos")

    # --- Identificar série atual ---
    serie = df_series[df_series["Status"] == "Em andamento"]
    serie_atual = serie.iloc[0]

    data_inicio = serie_atual.get("Data_inicio")

    try:
        data_fmt = pd.to_datetime(data_inicio, errors="coerce").strftime("%d/%m/%Y")
    except Exception:
        data_fmt = "Data não informada"

    if serie_atual.empty:
        serie_atual = df_series.sort_values("Data_inicio", ascending=False).head(1)

    serie_id = serie_atual["Serie_id"]

    st.subheader(f"🔥 Desafio Melhor de 3 | Série atual: **{serie_id}** | Início: {data_fmt}")

    # --- Jogos da série ---
    jogos_serie = df_jogos[df_jogos["Serie_id"] == serie_id]

    vitorias_roxo = (jogos_serie["Vencedor"] == "Roxo").sum()
    vitorias_amarelo = (jogos_serie["Vencedor"] == "Amarelo").sum()

    c1, c2, c3 = st.columns([2, 1, 2])

    with c1:
        st.markdown(
            "<h2 style='text-align: center; color: #8a2be2;'>🟪 TIME ROXO</h2>",
            unsafe_allow_html=True
        )
        st.markdown(f"<h1 style='text-align: center;'>{vitorias_roxo}</h1>", unsafe_allow_html=True)

    with c2:
        st.markdown(
            "<h1 style='text-align: center; padding-top: 20px;'>VS</h1>",
            unsafe_allow_html=True
        )
        if vitorias_roxo > vitorias_amarelo:
            st.success("Roxo vencendo!")
        elif vitorias_roxo < vitorias_amarelo:
            st.warning("Amarelo vencendo!")
        else:
            st.info("Série empatada!")

    with c3:
        st.markdown(
            "<h2 style='text-align: center; color: #ffd700;'>🟨 TIME AMARELO</h2>",
            unsafe_allow_html=True
        )
        st.markdown(f"<h1 style='text-align: center;'>{vitorias_amarelo}</h1>", unsafe_allow_html=True)


    # 3. CALENDÁRIO E HISTÓRICO DE "SÉRIES"
    st.divider()
    col_prox, col_hist = st.columns(2)

    with col_prox:
        st.subheader("📅 Próxima Pelada")
        with st.container(border=True):

            hoje = datetime.today()
            # Quinta-feira = 3 (segunda=0)
            dias_ate_quinta = (3 - hoje.weekday()) % 7
            dias_ate_quinta = 7 if dias_ate_quinta == 0 else dias_ate_quinta
            proxima_quinta = hoje + timedelta(days=dias_ate_quinta)

            st.write(f"**Data:** {proxima_quinta.strftime('%d/%m/%Y')} - 20:30hs")
            st.write("**Local:** Sport Center Biguaçu - Rua São Francisco de Paula, 444 Biguaçu")


    with col_hist:
        st.subheader("⏪ Histórico de Séries")

        series_encerradas = df_series[df_series["Status"] == "Encerrada"]

        if series_encerradas.empty:
            st.info("Nenhuma série encerrada ainda.")
        else:
            historico = []

            for _, serie in series_encerradas.iterrows():
                sid = serie["Serie_id"]
                jogos = df_jogos[df_jogos["Serie_id"] == sid]

                vr = (jogos["Vencedor"] == "Roxo").sum()
                va = (jogos["Vencedor"] == "Amarelo").sum()

                if vr > va:
                    campeao = "🟪 Roxo"
                elif va > vr:
                    campeao = "🟨 Amarelo"
                else:
                    campeao = "Empate"

                historico.append({
                    "Data": serie["Data_inicio"].strftime("%d/%m/%Y"),
                    "Campeão": campeao,
                    "Placar Série": f"🟪 {vr} x {va} 🟨"
                })

            df_hist = pd.DataFrame(historico).sort_values("Data", ascending=False)

            st.table(df_hist)

    # 4. MURAL DE AVISOS (Agregando valor)
    st.info("📢 **Aviso:** Mensalidade vence todo dia 15.")
