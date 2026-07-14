"""
Informações do cliente/visitante (IP).

Streamlit (a partir da versão 1.37) expõe `st.context.ip_address` com o IP
de quem está acessando o app, quando rodando em um servidor real (ex:
Streamlit Cloud). Em execução local, ou em versões mais antigas do
Streamlit, essa informação pode não existir — nesse caso, registramos
"desconhecido" em vez de adivinhar um valor errado (nunca usamos um
serviço externo de "qual é meu IP" aqui, porque isso retornaria o IP do
SERVIDOR do Streamlit, não o do visitante, o que seria uma informação
incorreta).
"""

import streamlit as st


def get_client_ip():
    try:
        ctx = getattr(st, "context", None)
        ip = getattr(ctx, "ip_address", None) if ctx else None
        if ip:
            return ip
    except Exception:
        pass
    return "desconhecido"
