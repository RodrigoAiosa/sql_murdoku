"""
Tela inicial de cadastro/login do detetive.

Fluxo:
1. Se já existe sessão local neste dispositivo, esta tela nem aparece
   (ver app.py / src/session.py).
2. Caso contrário, o jogador pode:
   a) fazer "login" digitando o codinome — o app procura na planilha do
      Google (leitura via CSV publicado, sempre disponível); ou
   b) se cadastrar pela primeira vez (nome, codinome, avatar). O cadastro
      é salvo localmente e, se configurado, sincronizado com a planilha
      via Google Apps Script.
"""

import random

import streamlit as st

from src.config import AVATARS
from src.session import save_local_session
from src.sheets import find_cloud_player, register_cloud_player
from src.ui.components import title_banner, panel


def render_registration_screen():
    title_banner()
    st.write("")

    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        panel(
            "🔑 JÁ SOU CADASTRADO",
            "Se você já tem distintivo (cadastrado neste ou em outro dispositivo), "
            "digite seu codinome para continuar sem preencher tudo de novo.",
        )
        with st.form("login_form"):
            login_codinome = st.text_input("Seu codinome")
            login_btn = st.form_submit_button("🔎 Continuar investigação")

        if login_btn:
            if not login_codinome.strip():
                st.error("Digite seu codinome para localizar seu cadastro.")
            else:
                with st.spinner("Consultando os arquivos da agência..."):
                    cloud = find_cloud_player(login_codinome)
                if cloud:
                    player = {
                        "nome": cloud.get("nome", login_codinome.strip()),
                        "codinome": cloud.get("codinome", login_codinome.strip()),
                        "avatar": cloud.get("avatar") or AVATARS[0],
                        "badge": cloud.get("badge") or random.randint(1000, 9999),
                    }
                    st.session_state.player = player
                    save_local_session(player)
                    st.rerun()
                else:
                    st.warning(
                        "Codinome não encontrado nos arquivos da agência. Se é sua "
                        "primeira vez, cadastre-se abaixo."
                    )

        st.markdown("<hr class='comic-hr'>", unsafe_allow_html=True)

        panel(
            "📋 NOVO CADASTRO (uma única vez)",
            "Todo bom detetive precisa de um distintivo. Preencha seus dados uma única "
            "vez — nas próximas vezes o jogo vai te reconhecer automaticamente.",
        )
        with st.form("cadastro_form"):
            nome = st.text_input("Nome completo do detetive")
            codinome = st.text_input("Codinome (usado no placar público)")
            avatar = st.radio("Escolha seu avatar", AVATARS, horizontal=True)
            enviado = st.form_submit_button("🔍 Começar Investigação")

        if enviado:
            if not nome.strip() or not codinome.strip():
                st.error("Preencha nome e codinome para receber seu distintivo, detetive.")
            elif find_cloud_player(codinome):
                st.error(
                    "Esse codinome já está em uso por outro detetive. Escolha outro, ou "
                    "use 'Já sou cadastrado' acima se ele for seu."
                )
            else:
                player = {
                    "nome": nome.strip(),
                    "codinome": codinome.strip(),
                    "avatar": avatar,
                    "badge": random.randint(1000, 9999),
                }
                st.session_state.player = player
                save_local_session(player)
                ok, msg = register_cloud_player(player)
                # Guarda o resultado da sincronização para exibir na tela
                # seguinte — se disparássemos st.success/st.info aqui e já
                # chamássemos st.rerun() na sequência, a mensagem seria
                # apagada antes do jogador conseguir lê-la.
                st.session_state["_cloud_sync_notice"] = (ok, msg)
                st.rerun()
