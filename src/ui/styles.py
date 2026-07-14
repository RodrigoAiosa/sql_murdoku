"""Injeção do CSS externo (assets/styles.css) na página Streamlit."""

import streamlit as st

from src.config import STYLES_PATH


def inject_css():
    css = STYLES_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
