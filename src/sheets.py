"""
Integração com a planilha do Google.

LEITURA: converte o link /pubhtml em exportação CSV pública e lê direto,
sem precisar de credenciais. Funciona assim que a planilha estiver
publicada na web (Arquivo > Compartilhar > Publicar na web) — usado para
checar se um codinome já está cadastrado, mesmo em outro dispositivo.

ESCRITA: feita via POST ao Web App do Google Apps Script (ver Code.gs e
o README para o passo a passo de publicação). O payload enviado inclui
id_registro, nome, email, celular, ip, codinome, avatar e badge — a
DATA_HORA é sempre gerada pelo próprio Code.gs, nunca pelo cliente. Se
config.GOOGLE_SCRIPT_WEBAPP_URL não estiver preenchida, o cadastro
continua funcionando, só que sem sincronizar com a planilha.
"""

import csv
import io
import json
import urllib.request

from src.config import GOOGLE_SHEET_PUBHTML_URL, GOOGLE_SCRIPT_WEBAPP_URL


def _pubhtml_to_csv_url(pubhtml_url):
    """Converte um link .../pubhtml em .../pub?output=csv."""
    base = pubhtml_url.split("/pubhtml")[0]
    return base + "/pub?output=csv"


def fetch_cloud_players(timeout=5):
    """Lê a planilha publicada e devolve uma lista de dicts (uma por linha).
    Em qualquer erro de rede/formatação, devolve lista vazia silenciosamente
    (o cadastro local continua funcionando normalmente)."""
    if not GOOGLE_SHEET_PUBHTML_URL:
        return []
    url = _pubhtml_to_csv_url(GOOGLE_SHEET_PUBHTML_URL)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        rows = list(csv.reader(io.StringIO(raw)))
        if not rows:
            return []
        header = [h.strip().lower() for h in rows[0]]
        players = []
        for row in rows[1:]:
            if not row or not any(cell.strip() for cell in row):
                continue
            players.append(dict(zip(header, row)))
        return players
    except Exception:
        return []


def find_cloud_player(codinome):
    """Procura um jogador pelo codinome (case-insensitive) na planilha."""
    codinome_l = codinome.strip().lower()
    for p in fetch_cloud_players():
        if p.get("codinome", "").strip().lower() == codinome_l:
            return p
    return None


def register_cloud_player(payload, timeout=6):
    """Envia o cadastro para o Google Apps Script Web App (se configurado).
    Retorna (sucesso: bool, mensagem: str) para exibir ao jogador."""
    if not GOOGLE_SCRIPT_WEBAPP_URL:
        return False, (
            "Sincronização com a planilha ainda não configurada — o cadastro foi "
            "salvo apenas neste dispositivo. Veja o README para ativar a planilha "
            "do Google."
        )
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            GOOGLE_SCRIPT_WEBAPP_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read()
        return True, "Cadastro sincronizado com a planilha do Google. ✅"
    except Exception as e:
        return False, (
            f"Não foi possível sincronizar com a planilha agora ({e}). Seu cadastro "
            "foi salvo neste dispositivo mesmo assim."
        )
