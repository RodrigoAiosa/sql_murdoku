"""
CASO SQL: O ENIGMA DA CONSULTA PERDIDA
---------------------------------------
Jogo de dedução lógica em estilo de quadrinho noir dos anos 50, feito com Streamlit.

REGRA DE OURO DO AGENTE:
- Nenhum SQL é "inventado" ou completado por experiência.
- Cada campo da consulta final é resultado direto da aplicação das pistas sobre um
  domínio de possibilidades (processo de inferência / CSP simples).
- Se, após todas as pistas, alguma categoria ainda tiver mais de uma possibilidade,
  o caso é declarado "INCOMPLETO" — o agente nunca escolhe arbitrariamente.

Este arquivo é apenas o ponto de entrada: toda a lógica mora em src/.

    src/
    ├── config.py        constantes e caminhos (URLs, pontuação, etc.)
    ├── engine.py        motor de dedução (CSP) — puro, sem Streamlit
    ├── levels.py         definição dos 3 casos/níveis do jogo
    ├── session.py         sessão local (cadastro só uma vez por dispositivo)
    ├── sheets.py           integração com Google Sheets (leitura CSV + Apps Script)
    ├── leaderboard.py       placar de detetives (JSON local)
    └── ui/
        ├── styles.py        injeta assets/styles.css
        ├── components.py     painéis, balões de fala, selos (HTML reutilizável)
        ├── registration.py    tela de cadastro/login
        ├── sidebar.py          barra lateral (ficha, pontuação, navegação)
        └── game.py              abas do jogo (pistas, montar, agente, placar)
"""

import streamlit as st

from src.config import PAGE_TITLE, PAGE_ICON, TIMER_ENABLED_BY_DEFAULT
from src.levels import LEVELS
from src.session import load_local_session
from src.ui.styles import inject_css
from src.ui.components import title_banner
from src.ui.registration import render_registration_screen
from src.ui.sidebar import render_sidebar
from src.ui.game import render_game

# ----------------------------------------------------------------------
# Configuração da página e estilo
# ----------------------------------------------------------------------
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
inject_css()

# ----------------------------------------------------------------------
# Estado do jogo
# ----------------------------------------------------------------------
if "player" not in st.session_state:
    # Se este dispositivo já tem uma sessão salva, entra direto — o
    # cadastro só é pedido na primeiríssima vez.
    st.session_state.player = load_local_session()

if "current_level" not in st.session_state:
    st.session_state.current_level = 0

if "timer_enabled" not in st.session_state:
    st.session_state.timer_enabled = TIMER_ENABLED_BY_DEFAULT

if "level_state" not in st.session_state:
    st.session_state.level_state = {
        lvl["id"]: {
            "started_at": None, "solved": False, "wrong_attempts": 0,
            "used_agent": False, "score": None,
        } for lvl in LEVELS
    }

# ----------------------------------------------------------------------
# Roteamento: cadastro ou jogo
# ----------------------------------------------------------------------
if st.session_state.player is None:
    render_registration_screen()
    st.stop()

title_banner()

# Se a sincronização com a planilha do Google falhar (ou não estiver
# configurada), avisa o jogador uma única vez. Quando dá certo, fica em
# silêncio — não precisa confirmar na tela (a barra lateral já mostra o
# status geral de sincronização).
notice = st.session_state.pop("_cloud_sync_notice", None)
if notice is not None:
    ok, msg = notice
    if not ok:
        st.info(msg)

render_sidebar(LEVELS)
render_game(LEVELS)
