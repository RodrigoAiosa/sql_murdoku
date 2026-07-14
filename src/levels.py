"""
Definição dos casos (níveis) do jogo.

Cada função `level_N()` devolve um dicionário com:
- metadados (id, título, dificuldade, narrativa, tempo, pontuação base)
- `options`: domínio inicial de cada categoria (todas as possibilidades)
- `clues`: lista de pistas geradas com `engine.make_clue`
- pools de opções usados para montar os widgets da UI

Depois de definidos, `solve_level()` (de src/engine.py) é aplicado a cada
nível para pré-computar a solução única e o SQL alvo.
"""

from src.engine import make_clue, solve_level


def level_1():
    options = {
        "select_modifier": ["SELECT", "SELECT DISTINCT"],
        "columns": [
            {"cliente.nome", "pedido.valor"},
            {"cliente.nome", "cliente.email"},
            {"pedido.valor", "pedido.data"},
            {"cliente.nome", "pedido.valor", "pedido.data"},
        ],
        "main_table": ["clientes", "produtos", "funcionarios"],
        "join_type": ["SEM JOIN", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN"],
        "joined_table": ["pedidos", "pagamentos", "enderecos"],
        "join_condition": [
            "clientes.id = pedidos.cliente_id",
            "clientes.id = pedidos.id",
            "clientes.cpf = pedidos.cliente_id",
        ],
        "where_presence": ["AUSENTE", "PRESENTE"],
        "where_condition": ["pedido.valor > 100", "pedido.valor < 100", "pedido.status = 'pago'"],
        "group_by_presence": ["AUSENTE", "PRESENTE"],
        "group_by_column": ["cliente.id", "pedido.status", "cliente.nome"],
        "having_presence": ["AUSENTE", "PRESENTE"],
        "having_condition": ["COUNT(*) > 1", "SUM(pedido.valor) > 500", "COUNT(*) > 5"],
        "order_by_presence": ["AUSENTE", "PRESENTE"],
        "order_by_column": ["pedido.valor DESC", "pedido.valor ASC", "pedido.data DESC"],
        "limit_presence": ["AUSENTE", "PRESENTE"],
        "limit_value": ["5", "10", "20"],
    }

    clues = [
        make_clue("O relatório do detetive não usa registros duplicados propositalmente "
                  "marcados — não há DISTINCT neste caso.", {"select_modifier": "SELECT"}),
        make_clue("O informe final mostra apenas o nome do cliente e o valor do pedido — "
                  "nada além disso.", {"columns": {"cliente.nome", "pedido.valor"}}),
        make_clue("A tabela principal do arquivo é onde moram os dados dos COMPRADORES.",
                  {"main_table": "clientes"}),
        make_clue("A tabela unida ao caso é onde ficam registradas as COMPRAS feitas.",
                  {"joined_table": "pedidos"}),
        make_clue("Só entram na história clientes que possuem ao menos um pedido "
                  "correspondente, e nenhum pedido órfão pode sobrar: a junção é interna "
                  "(INNER JOIN).", {"join_type": "INNER JOIN"}),
        make_clue("A ligação entre as tabelas se dá pelo identificador do cliente e pela "
                  "referência de cliente dentro do pedido.",
                  {"join_condition": "clientes.id = pedidos.cliente_id"}),
        make_clue("O detetive não aceita revisar TODOS os pedidos — existe um filtro "
                  "(cláusula WHERE) nesta investigação.", {"where_presence": "PRESENTE"}),
        make_clue("O filtro só interessa a pedidos de valor ACIMA de 100.",
                  {"where_condition": "pedido.valor > 100"}),
        make_clue("Este caso é simples demais para agrupamentos: não há GROUP BY nem HAVING.",
                  {"group_by_presence": "AUSENTE", "having_presence": "AUSENTE"}),
        make_clue("O relatório final precisa estar ORDENADO — o caso exige uma cláusula "
                  "ORDER BY.", {"order_by_presence": "PRESENTE"}),
        make_clue("A ordenação é pelo valor do pedido, do MAIOR para o MENOR.",
                  {"order_by_column": "pedido.valor DESC"}),
        make_clue("O chefe quer o dossiê completo — nada de cortar a lista: sem LIMIT, "
                  "sem OFFSET.", {"limit_presence": "AUSENTE"}),
    ]

    return {
        "id": "nivel_1",
        "titulo": "O Enigma da Consulta Perdida",
        "dificuldade": "Fácil",
        "css_class": "level-facil",
        "narrativa": "O chefe da delegacia precisa de um relatório extraído do banco de "
                      "dados da loja. Só restaram anotações rabiscadas às pressas.",
        "time_limit": 360,
        "base_points": 1000,
        "options": options,
        "clues": clues,
        "column_pool": ["cliente.nome", "cliente.email", "pedido.valor", "pedido.data"],
        "main_table_pool": ["clientes", "produtos", "funcionarios"],
        "joined_table_pool": ["pedidos", "pagamentos", "enderecos"],
    }


def level_2():
    options = {
        "select_modifier": ["SELECT", "SELECT DISTINCT"],
        "columns": [
            {"produtos.nome", "fornecedores.nome"},
            {"produtos.nome", "produtos.preco"},
            {"fornecedores.nome", "fornecedores.cidade"},
            {"produtos.nome", "fornecedores.cidade"},
        ],
        "main_table": ["produtos", "clientes", "funcionarios"],
        "join_type": ["SEM JOIN", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN"],
        "joined_table": ["fornecedores", "pagamentos", "enderecos"],
        "join_condition": [
            "produtos.fornecedor_id = fornecedores.id",
            "produtos.id = fornecedores.produto_id",
            "produtos.fornecedor_id = fornecedores.codigo",
        ],
        "where_presence": ["AUSENTE", "PRESENTE"],
        "where_condition": ["produtos.preco > 50", "produtos.preco < 50", "produtos.ativo = true"],
        "group_by_presence": ["AUSENTE", "PRESENTE"],
        "group_by_column": ["produtos.categoria", "fornecedores.cidade", "produtos.nome"],
        "having_presence": ["AUSENTE", "PRESENTE"],
        "having_condition": ["COUNT(*) > 1", "SUM(produtos.preco) > 1000", "COUNT(*) > 3"],
        "order_by_presence": ["AUSENTE", "PRESENTE"],
        "order_by_column": ["produtos.nome ASC", "produtos.preco DESC", "fornecedores.nome ASC"],
        "limit_presence": ["AUSENTE", "PRESENTE"],
        "limit_value": ["5", "10", "25"],
    }

    clues = [
        make_clue("O estoquista suspeita de produtos repetidos no relatório: quer apenas "
                  "combinações ÚNICAS (SELECT DISTINCT).", {"select_modifier": "SELECT DISTINCT"}),
        make_clue("O relatório mostra o nome do produto lado a lado com o nome do "
                  "fornecedor — só isso.", {"columns": {"produtos.nome", "fornecedores.nome"}}),
        make_clue("A tabela principal guarda os itens à venda, não pessoas nem funcionários.",
                  {"main_table": "produtos"}),
        make_clue("A tabela unida guarda quem FORNECE os produtos.",
                  {"joined_table": "fornecedores"}),
        make_clue("O gerente quer ver TODOS os produtos no relatório, mesmo os que ainda "
                  "não têm fornecedor cadastrado — nenhum produto pode ficar de fora "
                  "(LEFT JOIN).", {"join_type": "LEFT JOIN"}),
        make_clue("A ligação usa o código do fornecedor salvo dentro do cadastro do "
                  "produto, comparado ao identificador do fornecedor.",
                  {"join_condition": "produtos.fornecedor_id = fornecedores.id"}),
        make_clue("Não há filtro de preço nem de qualquer outra coisa — o estoquista quer "
                  "a lista completa, sem cortes: nada de WHERE.",
                  {"where_presence": "AUSENTE"}),
        make_clue("Nenhum agrupamento é necessário neste inventário: sem GROUP BY, sem "
                  "HAVING.", {"group_by_presence": "AUSENTE", "having_presence": "AUSENTE"}),
        make_clue("A lista final deve vir em ORDEM ALFABÉTICA pelo nome do produto.",
                  {"order_by_presence": "PRESENTE", "order_by_column": "produtos.nome ASC"}),
        make_clue("Nenhum corte na lista é permitido: sem LIMIT, sem OFFSET.",
                  {"limit_presence": "AUSENTE"}),
    ]

    return {
        "id": "nivel_2",
        "titulo": "O Estoque Fantasma",
        "dificuldade": "Médio",
        "css_class": "level-medio",
        "narrativa": "Produtos sumindo do sistema, fornecedores sem cadastro... o "
                      "estoquista precisa de um relatório completo, sem exceções.",
        "time_limit": 300,
        "base_points": 1500,
        "options": options,
        "clues": clues,
        "column_pool": ["produtos.nome", "produtos.preco", "fornecedores.nome", "fornecedores.cidade"],
        "main_table_pool": ["produtos", "clientes", "funcionarios"],
        "joined_table_pool": ["fornecedores", "pagamentos", "enderecos"],
    }


def level_3():
    options = {
        "select_modifier": ["SELECT", "SELECT DISTINCT"],
        "columns": [
            {"pedidos.cliente_id", "SUM(pedidos.valor) AS total_gasto"},
            {"pedidos.cliente_id", "COUNT(*) AS total_pedidos"},
            {"pedidos.cliente_id", "pedidos.valor"},
            {"pedidos.status", "SUM(pedidos.valor) AS total_gasto"},
        ],
        "main_table": ["pedidos", "clientes", "produtos"],
        "join_type": ["SEM JOIN", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN"],
        "joined_table": ["clientes", "pagamentos", "enderecos"],
        "join_condition": [
            "pedidos.cliente_id = clientes.id",
            "pedidos.id = clientes.pedido_id",
            "pedidos.cliente_id = clientes.codigo",
        ],
        "where_presence": ["AUSENTE", "PRESENTE"],
        "where_condition": [
            "pedidos.status = 'concluido'",
            "pedidos.status = 'cancelado'",
            "pedidos.valor > 500",
        ],
        "group_by_presence": ["AUSENTE", "PRESENTE"],
        "group_by_column": ["pedidos.cliente_id", "pedidos.data", "pedidos.status"],
        "having_presence": ["AUSENTE", "PRESENTE"],
        "having_condition": [
            "SUM(pedidos.valor) > 1000",
            "COUNT(*) > 5",
            "SUM(pedidos.valor) < 1000",
        ],
        "order_by_presence": ["AUSENTE", "PRESENTE"],
        "order_by_column": ["total_gasto DESC", "pedidos.cliente_id ASC", "COUNT(*) DESC"],
        "limit_presence": ["AUSENTE", "PRESENTE"],
        "limit_value": ["5", "10", "20"],
    }

    clues = [
        make_clue("Não interessa remover duplicatas aqui — cada linha já representa um "
                  "cliente agrupado (sem DISTINCT).", {"select_modifier": "SELECT"}),
        make_clue("O relatório mostra o identificador do cliente e o TOTAL GASTO por ele "
                  "(soma dos valores dos pedidos).",
                  {"columns": {"pedidos.cliente_id", "SUM(pedidos.valor) AS total_gasto"}}),
        make_clue("A tabela principal é onde ficam registrados os PEDIDOS, não os "
                  "cadastros de clientes ou produtos.", {"main_table": "pedidos"}),
        make_clue("Este relatório não precisa cruzar com nenhuma outra tabela — o "
                  "identificador do cliente já está dentro da própria tabela de pedidos "
                  "(sem JOIN).", {"join_type": "SEM JOIN"}),
        make_clue("Só entram na conta os pedidos já CONCLUÍDOS — existe um filtro.",
                  {"where_presence": "PRESENTE", "where_condition": "pedidos.status = 'concluido'"}),
        make_clue("Os valores são agrupados por cliente — GROUP BY pelo identificador do "
                  "cliente.", {"group_by_presence": "PRESENTE", "group_by_column": "pedidos.cliente_id"}),
        make_clue("Só interessam clientes cujo total gasto ultrapasse 1000 — um filtro "
                  "APÓS o agrupamento (HAVING).",
                  {"having_presence": "PRESENTE", "having_condition": "SUM(pedidos.valor) > 1000"}),
        make_clue("A lista final é ordenada pelo total gasto, do maior para o menor.",
                  {"order_by_presence": "PRESENTE", "order_by_column": "total_gasto DESC"}),
        make_clue("A diretoria só quer ver o TOP 10 — a lista é cortada em 10 registros.",
                  {"limit_presence": "PRESENTE", "limit_value": "10"}),
    ]

    return {
        "id": "nivel_3",
        "titulo": "O Relatório dos Grandes Clientes",
        "dificuldade": "Difícil",
        "css_class": "level-dificil",
        "narrativa": "A diretoria quer saber quem são os clientes mais valiosos da "
                      "empresa — e quer a lista enxuta, só com os melhores.",
        "time_limit": 240,
        "base_points": 2000,
        "options": options,
        "clues": clues,
        "column_pool": [
            "pedidos.cliente_id", "pedidos.status", "pedidos.valor",
            "SUM(pedidos.valor) AS total_gasto", "COUNT(*) AS total_pedidos",
        ],
        "main_table_pool": ["pedidos", "clientes", "produtos"],
        "joined_table_pool": ["clientes", "pagamentos", "enderecos"],
    }


def build_levels():
    """Constrói e resolve (pré-computa) todos os níveis do jogo."""
    levels = [level_1(), level_2(), level_3()]
    return [solve_level(lvl) for lvl in levels]


LEVELS = build_levels()
