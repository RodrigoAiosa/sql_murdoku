"""
Configurações e constantes centralizadas do jogo.

Nenhuma lógica de jogo mora aqui — apenas caminhos, URLs e parâmetros
que outros módulos importam. Isso facilita ajustar o projeto (por
exemplo, plugar a URL do Apps Script) sem mexer em código de lógica.
"""

from pathlib import Path

# ----------------------------------------------------------------------
# Caminhos do projeto
# ----------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)

STYLES_PATH = ASSETS_DIR / "styles.css"
LEADERBOARD_PATH = DATA_DIR / "leaderboard.json"

# Sessão local: uma vez cadastrado neste computador, o cadastro não é
# pedido de novo nas próximas execuções do app.
LOCAL_SESSION_PATH = Path.home() / ".caso_sql_comic_session.json"

# ----------------------------------------------------------------------
# Integração com Google Sheets
#
#   IMPORTANTE: um link "/pubhtml" é SOMENTE LEITURA — o Google não
#   permite escrever numa planilha publicada assim. Por isso:
#
#   - LEITURA (checar se um codinome já está cadastrado) é feita direto
#     a partir do link pubhtml abaixo, convertido para exportação CSV.
#     Não requer nenhuma configuração extra além de a planilha estar
#     publicada na web (Arquivo > Compartilhar > Publicar na web).
#
#   - ESCRITA (gravar um novo cadastro) exige um Google Apps Script Web
#     App publicado a partir da PRÓPRIA planilha (veja Code.gs e o
#     README). Cole a URL /exec gerada em GOOGLE_SCRIPT_WEBAPP_URL.
#     Enquanto essa URL não for configurada, o cadastro continua
#     funcionando normalmente, só que sem sincronizar com a planilha.
# ----------------------------------------------------------------------
GOOGLE_SHEET_PUBHTML_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vQwQTp7f0ph0nfCwOelM9XgUSi-e8-EMYDHe6"
    "Ef8WOy8GyKvzU8ZrXq00out2818c8WJ51FEHWKQTYG/pubhtml"
)
GOOGLE_SCRIPT_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbw1Xhktq6GnYV5exfQPCNpcw0XKVDItk9VeF7JWEHZ62KpIl8PJhs8IC7j1ZdI2T2VGMQ/exec"  # <-- cole aqui a URL /exec do seu Apps Script (ver README)

# ----------------------------------------------------------------------
# Aparência / geral
# ----------------------------------------------------------------------
PAGE_TITLE = "Caso SQL: O Enigma da Consulta Perdida"
PAGE_ICON = "🕵️"

AVATARS = ["🕵️‍♂️", "🕵️‍♀️", "🐺", "🦉", "🐈‍⬛", "🎩", "🔦", "🧢"]

# ----------------------------------------------------------------------
# Regras de pontuação
# ----------------------------------------------------------------------
POINTS_PER_SECOND_REMAINING = 2
PENALTY_PER_WRONG_ATTEMPT = 50
PENALTY_FOR_USING_AGENT = 400
MIN_SCORE_FLOOR = 50

# ----------------------------------------------------------------------
# Cronômetro
# ----------------------------------------------------------------------
# O jogador pode ligar/desligar o cronômetro a qualquer momento (barra
# superior do jogo). Este é apenas o valor padrão ao abrir o jogo.
TIMER_ENABLED_BY_DEFAULT = True
TIMER_REFRESH_INTERVAL_MS = 1000
