"""Barra lateral: ficha do jogador, pontuação total e navegação entre níveis."""

import streamlit as st

from src.config import GOOGLE_SCRIPT_WEBAPP_URL
from src.session import clear_local_session
from src.ui.components import player_card, score_box


def _fresh_level_state(levels):
    return {
        lvl["id"]: {
            "started_at": None, "solved": False, "wrong_attempts": 0,
            "used_agent": False, "agent_revealed": False, "score": None, "score_breakdown": None,
        } for lvl in levels
    }


def total_score():
    return sum(v["score"] or 0 for v in st.session_state.level_state.values())


def is_level_unlocked(levels, idx):
    if idx == 0:
        return True
    prev_id = levels[idx - 1]["id"]
    return st.session_state.level_state[prev_id]["solved"]


def render_sidebar(levels):
    player = st.session_state.player

    with st.sidebar:
        player_card(player["avatar"], player["codinome"], player["nome"], player["badge"])
        score_box(f"🏆 {total_score()} pts")

        if GOOGLE_SCRIPT_WEBAPP_URL:
            st.caption("☁️ Sincronização com a planilha: **configurada**")
        else:
            st.caption(
                "☁️ Sincronização com a planilha: **não configurada** — os cadastros "
                "estão sendo salvos só localmente. Veja o README (seção 'Cadastro único "
                "e integração com Google Sheets') para ativar."
            )
        st.write("")

        st.markdown("**Níveis do caso:**")
        for i, lvl in enumerate(levels):
            unlocked = is_level_unlocked(levels, i)
            solved = st.session_state.level_state[lvl["id"]]["solved"]
            icon = "🔒 " if not unlocked else ("✅ " if solved else "▶️ ")
            label = f"{icon}{lvl['titulo']} ({lvl['dificuldade']})"
            if unlocked:
                if st.button(label, key=f"btn_lvl_{i}"):
                    st.session_state.current_level = i
                    st.rerun()
            else:
                st.markdown(
                    f"<span class='level-badge level-locked'>{label}</span>",
                    unsafe_allow_html=True,
                )

        st.markdown("<hr class='comic-hr'>", unsafe_allow_html=True)

        if st.button("🔄 Reiniciar Progresso do Jogo"):
            st.session_state.current_level = 0
            st.session_state.level_state = _fresh_level_state(levels)
            st.rerun()

        if st.button("🚪 Trocar de Detetive"):
            clear_local_session()
            st.session_state.player = None
            st.session_state.current_level = 0
            st.session_state.level_state = _fresh_level_state(levels)
            st.rerun()
