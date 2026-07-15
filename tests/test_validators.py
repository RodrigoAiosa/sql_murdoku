"""
Testes das validações de cadastro (src/validators.py).

Rodar com: pytest tests/ -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.validators import (
    validate_nome, validate_email, validate_celular, validate_codinome,
    validate_cadastro,
)


def test_nome_valido():
    assert validate_nome("Rodrigo Aiosa")
    assert validate_nome("Ana")  is False  # menos de 5 caracteres
    assert validate_nome("João")  is False  # 4 caracteres, menos de 5


def test_nome_invalido_com_numero_ou_simbolo():
    assert not validate_nome("Rodrigo123")
    assert not validate_nome("Rodrigo_Aiosa")
    assert not validate_nome("")


def test_nome_minimo_5_caracteres():
    assert validate_nome("Bruno")       # exatamente 5
    assert not validate_nome("Ana ")    # 4 letras + espaço = ainda inválido em termos de nome real, mas passa no regex de tamanho


def test_email_valido():
    assert validate_email("rodrigoaiosa@gmail.com")
    assert validate_email("nome.sobrenome@dominio.com.br")


def test_email_invalido():
    assert not validate_email("sem-arroba.com")
    assert not validate_email("com@espaco no meio.com")
    assert not validate_email("")
    assert not validate_email("a@b")  # sem TLD


def test_celular_formato_correto():
    assert validate_celular("(11) 977019335")
    assert validate_celular("(21) 123456789")


def test_celular_formato_incorreto():
    assert not validate_celular("11977019335")          # sem parênteses/espaço
    assert not validate_celular("(11)977019335")         # sem espaço
    assert not validate_celular("(011) 977019335")        # DDD com 3 dígitos
    assert not validate_celular("(11) 97701933")           # só 8 dígitos
    assert not validate_celular("")


def test_codinome_valido():
    assert validate_codinome("Aiosa123")
    assert validate_codinome("Detetive_X")


def test_codinome_invalido():
    assert not validate_codinome("Ai")          # menos de 5
    assert not validate_codinome("Nome Com Espaco")  # tem espaços
    assert not validate_codinome("")


def test_validate_cadastro_retorna_vazio_quando_tudo_certo():
    erros = validate_cadastro(
        "Rodrigo Aiosa", "rodrigoaiosa@gmail.com", "(11) 977019335", "Aiosa123"
    )
    assert erros == []


def test_validate_cadastro_acumula_todos_os_erros():
    erros = validate_cadastro("Ana", "email-invalido", "11977019335", "ab")
    assert len(erros) == 4  # os 4 campos estão errados nesse exemplo


if __name__ == "__main__":
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"OK   - {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL - {t.__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} testes passaram.")
    sys.exit(1 if failures else 0)
