"""
Componentes visuais reutilizáveis do tema de quadrinho.

Cada função apenas emite HTML/Markdown via st.markdown — mantém a lógica
de layout fora das telas (registration.py, sidebar.py, game.py).
"""

import streamlit as st


def panel(title, body_html):
    st.markdown(
        f'<div class="panel"><div class="panel-title">{title}</div>{body_html}</div>',
        unsafe_allow_html=True,
    )


def speech_bubble(number, text):
    st.markdown(
        f'<div class="speech-bubble"><span class="clue-number">{number}</span>{text}</div>',
        unsafe_allow_html=True,
    )


def badge_pow(text):
    st.markdown(f'<div class="badge-pow">{text}</div>', unsafe_allow_html=True)


def case_closed(html):
    st.markdown(f'<div class="case-closed">{html}</div>', unsafe_allow_html=True)


def level_badge(text, css_class):
    st.markdown(f'<span class="level-badge {css_class}">{text}</span>', unsafe_allow_html=True)


def timer_box(text, danger=False, off=False):
    if off:
        cls = "timer-off"
    else:
        cls = "timer-box timer-danger" if danger else "timer-box"
    st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)


def score_box(text):
    st.markdown(f'<div class="score-box">{text}</div>', unsafe_allow_html=True)


def player_card(avatar, codinome, nome, badge):
    st.markdown(
        f'<div class="player-card">{avatar} <b>{codinome}</b><br>'
        f'{nome}<br>Distintivo nº {badge}</div>',
        unsafe_allow_html=True,
    )


def title_banner():
    st.markdown('<div class="comic-title">CASO SQL</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="center-wrap"><span class="comic-subtitle">'
        'O ENIGMA DA CONSULTA PERDIDA — Uma Aventura de Dedução Lógica</span></div>',
        unsafe_allow_html=True,
    )
