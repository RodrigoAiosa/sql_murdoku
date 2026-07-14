"""
Sessão local do jogador — permite que o cadastro seja pedido apenas uma
vez por dispositivo. Os dados ficam salvos em um arquivo JSON no diretório
do usuário do sistema operacional (independente de onde o projeto está
instalado).
"""

import json

from src.config import LOCAL_SESSION_PATH


def load_local_session():
    """Retorna o dict do jogador salvo neste dispositivo, ou None se não
    houver sessão salva (ou se o arquivo estiver corrompido)."""
    if not LOCAL_SESSION_PATH.exists():
        return None
    try:
        with open(LOCAL_SESSION_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_local_session(player):
    """Salva os dados do jogador atual neste dispositivo."""
    try:
        with open(LOCAL_SESSION_PATH, "w", encoding="utf-8") as f:
            json.dump(player, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def clear_local_session():
    """Remove a sessão local (usado pelo botão 'Trocar de Detetive')."""
    try:
        if LOCAL_SESSION_PATH.exists():
            LOCAL_SESSION_PATH.unlink()
    except Exception:
        pass
