"""
Testes do motor de dedução (src/engine.py) e dos níveis (src/levels.py).

Rodar com: pytest tests/ -v
(ou, sem pytest instalado: python -m tests.test_engine)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.engine import make_clue, run_inference, is_uniquely_solved, build_sql, solve_level
from src.levels import level_1, level_2, level_3, LEVELS


def test_make_clue_reduces_domain():
    domains = {"cor": ["azul", "verde", "vermelho"]}
    _, fn = make_clue("A cor é azul.", {"cor": "azul"})
    fn(domains)
    assert domains["cor"] == ["azul"]


def test_level_1_is_unique_and_matches_expected_sql():
    lvl = solve_level(level_1())
    ok, missing = is_uniquely_solved(lvl["domains"])
    assert ok, f"Nível 1 deveria ser único, mas '{missing}' ficou ambíguo"
    expected = (
        "SELECT\n"
        "cliente.nome,\n"
        "pedido.valor\n"
        "FROM clientes\n"
        "INNER JOIN pedidos\n"
        "ON clientes.id = pedidos.cliente_id\n"
        "WHERE pedido.valor > 100\n"
        "ORDER BY pedido.valor DESC;"
    )
    assert lvl["target_sql"] == expected


def test_level_2_is_unique():
    lvl = solve_level(level_2())
    ok, missing = is_uniquely_solved(lvl["domains"])
    assert ok, f"Nível 2 deveria ser único, mas '{missing}' ficou ambíguo"
    assert "LEFT JOIN" in lvl["target_sql"]
    assert "SELECT DISTINCT" in lvl["target_sql"]


def test_level_3_is_unique():
    lvl = solve_level(level_3())
    ok, missing = is_uniquely_solved(lvl["domains"])
    assert ok, f"Nível 3 deveria ser único, mas '{missing}' ficou ambíguo"
    assert "GROUP BY" in lvl["target_sql"]
    assert "HAVING" in lvl["target_sql"]
    assert "LIMIT 10" in lvl["target_sql"]


def test_all_precomputed_levels_are_unique():
    for lvl in LEVELS:
        assert lvl["unique"], f"{lvl['titulo']} não convergiu para solução única"
        assert lvl["target_sql"] is not None


def test_incomplete_puzzle_is_detected():
    # Um nível sem nenhuma pista aplicada nunca deve ser considerado único
    # (múltiplas categorias continuam com mais de uma opção).
    lvl = level_1()
    domains = {k: list(v) for k, v in lvl["options"].items()}
    ok, missing = is_uniquely_solved(domains)
    assert not ok
    sql, missing2 = build_sql(domains)
    assert sql is None
    assert missing2 is not None


if __name__ == "__main__":
    # Permite rodar sem pytest: python -m tests.test_engine
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
