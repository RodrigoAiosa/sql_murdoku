"""
Tela inicial de cadastro/login do detetive.

Fluxo:
1. Se já existe sessão local neste dispositivo, esta tela nem aparece
   (ver app.py / src/session.py).
2. Caso contrário, o jogador pode:
   a) fazer "login" digitando o codinome — o app procura na planilha do
      Google (leitura via CSV publicado, sempre disponível); ou
   b) se cadastrar pela primeira vez (nome, email, celular, codinome,
      avatar). O cadastro é salvo localmente e, se configurado,
      sincronizado com a planilha via Google Apps Script.

Campos gerados automaticamente (não pedidos ao jogador):
- ID_REGISTRO: identificador único do cadastro (gerado no momento do envio).
- DATA_HORA: carimbo de data/hora, gravado pelo próprio Apps Script (Code.gs).
- IP: capturado via st.context.ip_address, quando disponível (ver
  src/client_info.py).
"""

import random
import re
import uuid

import streamlit as st

from src.client_info import get_client_ip
from src.config import AVATARS
from src.session import save_local_session
from src.sheets import find_cloud_player, register_cloud_player
from src.ui.components import title_banner, panel

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _new_id_registro():
    return uuid.uuid4().hex[:10].upper()


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
                        "email": cloud.get("email", ""),
                        "celular": cloud.get("celular", ""),
                        "codinome": cloud.get("codinome", login_codinome.strip()),
                        "avatar": cloud.get("avatar") or AVATARS[0],
                        "badge": cloud.get("badge") or random.randint(1000, 9999),
                        "id_registro": cloud.get("id_registro") or _new_id_registro(),
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
            email = st.text_input("Email")
            celular = st.text_input("Celular (com DDD)")
            codinome = st.text_input("Codinome (usado no placar público)")
            avatar = st.radio("Escolha seu avatar", AVATARS, horizontal=True)
            enviado = st.form_submit_button("🔍 Começar Investigação")

        if enviado:
            erros = []
            if not nome.strip():
                erros.append("nome")
            if not email.strip() or not EMAIL_REGEX.match(email.strip()):
                erros.append("email válido")
            if not celular.strip():
                erros.append("celular")
            if not codinome.strip():
                erros.append("codinome")

            if erros:
                st.error(f"Preencha corretamente: {', '.join(erros)}.")
            elif find_cloud_player(codinome):
                st.error(
                    "Esse codinome já está em uso por outro detetive. Escolha outro, ou "
                    "use 'Já sou cadastrado' acima se ele for seu."
                )
            else:
                player = {
                    "nome": nome.strip(),
                    "email": email.strip(),
                    "celular": celular.strip(),
                    "codinome": codinome.strip(),
                    "avatar": avatar,
                    "badge": random.randint(1000, 9999),
                    "id_registro": _new_id_registro(),
                    "ip": get_client_ip(),
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
