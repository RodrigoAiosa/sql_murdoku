"""
Motor de dedução do quebra-cabeça (CSP simples), independente de UI.

REGRA DE OURO:
- Nenhum SQL é "inventado" ou completado por experiência.
- Cada campo da consulta final é resultado direto da aplicação das pistas
  sobre um domínio de possibilidades.
- Se, após todas as pistas, alguma categoria ainda tiver mais de uma
  possibilidade, o caso é declarado "INCOMPLETO" — o agente nunca escolhe
  arbitrariamente.

Por não depender do Streamlit, este módulo pode ser testado isoladamente
(veja tests/test_engine.py).
"""

# Todas as categorias abaixo existem em TODOS os níveis (para manter a
# interface consistente). Uma categoria "irrelevante" num nível simples-
# mente tem sua presença marcada como AUSENTE e não é cobrada/validada.
CATEGORY_ORDER = [
    "select_modifier", "columns", "main_table",
    "join_type", "joined_table", "join_condition",
    "where_presence", "where_condition",
    "group_by_presence", "group_by_column",
    "having_presence", "having_condition",
    "order_by_presence", "order_by_column",
    "limit_presence", "limit_value",
]


def make_clue(text, assignments):
    """Gera uma pista genérica: fixa cada categoria de `assignments`
    eliminando qualquer valor do domínio que não seja o valor correto.

    `assignments` é um dict {categoria: valor_correto}. Uma pista pode
    fixar mais de uma categoria de uma vez (ex.: "não há GROUP BY nem
    HAVING" fixa as duas).
    """
    def fn(domains):
        elims = []
        for cat, correct in assignments.items():
            before = len(domains[cat])
            domains[cat] = [v for v in domains[cat] if v == correct]
            elims.append(
                f"Categoria '{cat}' reduzida de {before} para {len(domains[cat])} "
                "possibilidade(s)."
            )
        return elims
    return (text, fn)


def run_inference(level):
    """Aplica todas as pistas do nível sequencialmente sobre o domínio
    inicial, retornando (domínios finais, log de eliminações)."""
    domains = {k: list(v) for k, v in level["options"].items()}
    log = []
    for i, (text, fn) in enumerate(level["clues"], start=1):
        eliminations = fn(domains)
        log.append({"n": i, "clue": text, "eliminations": eliminations})
    return domains, log


def is_uniquely_solved(domains):
    """Verifica unicidade apenas das categorias que de fato importam para
    a consulta final. Categorias condicionais (ex: coluna do GROUP BY) só
    precisam estar resolvidas quando a cláusula correspondente está
    PRESENTE — do contrário elas são irrelevantes e não entram no SQL."""
    core = [
        "select_modifier", "columns", "main_table", "join_type",
        "where_presence", "group_by_presence", "having_presence",
        "order_by_presence", "limit_presence",
    ]
    for key in core:
        if len(domains[key]) != 1:
            return False, key

    if domains["join_type"][0] != "SEM JOIN":
        for key in ["joined_table", "join_condition"]:
            if len(domains[key]) != 1:
                return False, key
    if domains["where_presence"][0] == "PRESENTE":
        if len(domains["where_condition"]) != 1:
            return False, "where_condition"
    if domains["group_by_presence"][0] == "PRESENTE":
        if len(domains["group_by_column"]) != 1:
            return False, "group_by_column"
    if domains["having_presence"][0] == "PRESENTE":
        if len(domains["having_condition"]) != 1:
            return False, "having_condition"
    if domains["order_by_presence"][0] == "PRESENTE":
        if len(domains["order_by_column"]) != 1:
            return False, "order_by_column"
    if domains["limit_presence"][0] == "PRESENTE":
        if len(domains["limit_value"]) != 1:
            return False, "limit_value"

    return True, None


def build_sql(domains):
    """Monta o SQL EXCLUSIVAMENTE a partir das posições deduzidas. Nunca
    otimiza, simplifica ou adiciona cláusulas inexistentes. Retorna
    (sql, None) em caso de sucesso, ou (None, categoria_faltante) se o
    quebra-cabeça ainda estiver incompleto."""
    ok, missing = is_uniquely_solved(domains)
    if not ok:
        return None, missing

    cols = sorted(domains["columns"][0])
    lines = [f"{domains['select_modifier'][0]}\n" + ",\n".join(cols)]
    lines.append(f"FROM {domains['main_table'][0]}")

    if domains["join_type"][0] != "SEM JOIN":
        lines.append(f"{domains['join_type'][0]} {domains['joined_table'][0]}")
        lines.append(f"ON {domains['join_condition'][0]}")

    if domains["where_presence"][0] == "PRESENTE":
        lines.append(f"WHERE {domains['where_condition'][0]}")

    if domains["group_by_presence"][0] == "PRESENTE":
        lines.append(f"GROUP BY {domains['group_by_column'][0]}")

    if domains["having_presence"][0] == "PRESENTE":
        lines.append(f"HAVING {domains['having_condition'][0]}")

    if domains["order_by_presence"][0] == "PRESENTE":
        lines.append(f"ORDER BY {domains['order_by_column'][0]}")

    if domains["limit_presence"][0] == "PRESENTE":
        lines.append(f"LIMIT {domains['limit_value'][0]}")

    return "\n".join(lines) + ";", None


def solve_level(level):
    """Executa a inferência completa e anota o nível com os resultados:
    domains, log, unique e target_sql. Retorna o próprio dict (mutado)."""
    domains, log = run_inference(level)
    unique, _ = is_uniquely_solved(domains)
    target_sql, _ = build_sql(domains)
    level["domains"] = domains
    level["log"] = log
    level["unique"] = unique
    level["target_sql"] = target_sql
    return level
