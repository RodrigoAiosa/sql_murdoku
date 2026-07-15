"""
Validação dos campos do cadastro, via expressões regulares.

Módulo puro (sem Streamlit) — testável isoladamente em
tests/test_validators.py.

Regras:
- NOME: só letras (com acentos) e espaços, mínimo 5 caracteres no total.
- EMAIL: formato clássico usuário@dominio.tld.
- CELULAR: exatamente o formato "(xx) xxxxxxxxx" — DDD entre parênteses,
  espaço, 9 dígitos do número (padrão brasileiro com o 9º dígito).
- CODINOME: letras, números e underscore, sem espaços, mínimo 5 caracteres.
"""

import re

NOME_REGEX = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]{5,}$")
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
CELULAR_REGEX = re.compile(r"^\(\d{2}\) \d{9}$")
CODINOME_REGEX = re.compile(r"^[A-Za-z0-9À-ÖØ-öø-ÿ_]{5,}$")

CELULAR_EXEMPLO = "(11) 977019335"


def validate_nome(value):
    return bool(NOME_REGEX.match((value or "").strip()))


def validate_email(value):
    return bool(EMAIL_REGEX.match((value or "").strip()))


def validate_celular(value):
    return bool(CELULAR_REGEX.match((value or "").strip()))


def validate_codinome(value):
    return bool(CODINOME_REGEX.match((value or "").strip()))


def validate_cadastro(nome, email, celular, codinome):
    """Valida os 4 campos de uma vez. Retorna uma lista de mensagens de
    erro (vazia se tudo estiver certo)."""
    erros = []
    if not validate_nome(nome):
        erros.append(
            "Nome: use só letras e espaços, com no mínimo 5 caracteres."
        )
    if not validate_email(email):
        erros.append("Email: informe um email válido (ex: nome@exemplo.com).")
    if not validate_celular(celular):
        erros.append(
            f"Celular: use exatamente o formato {CELULAR_EXEMPLO} "
            "(DDD entre parênteses, espaço, 9 dígitos)."
        )
    if not validate_codinome(codinome):
        erros.append(
            "Codinome: letras, números ou underscore, sem espaços, mínimo "
            "5 caracteres."
        )
    return erros
