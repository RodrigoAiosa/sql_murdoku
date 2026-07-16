"""
Tela principal do jogo: cabeçalho do nível (cronômetro/pontuação) e as
quatro abas — Pistas, Monte a Consulta, Sala do Agente e Placar.
"""

import time

import streamlit as st

from src.config import (
    POINTS_PER_SECOND_REMAINING,
    PENALTY_PER_WRONG_ATTEMPT,
    PENALTY_FOR_USING_AGENT,
    MIN_SCORE_FLOOR,
    TIMER_REFRESH_INTERVAL_MS,
)
from src.leaderboard import update_leaderboard, top_entries
from src.ui.components import panel, speech_bubble, badge_pow, case_closed, timer_box, score_box
from src.ui.sidebar import total_score


def _render_pistas_tab(level):
    panel(
        "DOSSIÊ DO CASO",
        f'{level["narrativa"]} Junte as pistas, uma a uma, e descubra exatamente qual '
        "comando SQL resolve o mistério — <b>sem chutar, sem completar por conta "
        "própria.</b>",
    )
    for i, (text, _) in enumerate(level["clues"], start=1):
        speech_bubble(i, text)


def _score_breakdown_text(level, breakdown):
    return (
        f"Pontuação: base {level['base_points']}"
        + (f" + bônus de tempo {breakdown['time_bonus']}" if breakdown["used_timer"] else "")
        + f" - penalidade de erros {breakdown['penalty']}"
        + (f" - penalidade por ajuda {breakdown['agent_penalty']}" if breakdown["agent_penalty"] else "")
        + f" = **{breakdown['score']} pts**"
    )


def _render_solved_result(level, ls, current_level_idx, total_levels):
    case_closed("CASO ENCERRADO!")
    badge_pow("100% DEDUZIDO")
    st.code(level["target_sql"], language="sql")
    if ls.get("score_breakdown"):
        st.success(_score_breakdown_text(level, ls["score_breakdown"]))
    else:
        st.info(f"Pontuação obtida neste nível: **{ls['score']} pts**.")
    if current_level_idx < total_levels - 1:
        st.info("Um novo nível foi desbloqueado no menu lateral! 👈")
    else:
        case_closed(f"INVESTIGAÇÃO CONCLUÍDA!<br>Pontuação total: {total_score()} pts")


def _render_montar_tab(level, ls, player, remaining, current_level_idx, total_levels):
    if ls["solved"]:
        _render_solved_result(level, ls, current_level_idx, total_levels)
        return

    if remaining is not None and remaining <= 0:
        st.error(
            "⏱ O TEMPO ESGOTOU! Você ainda pode resolver o caso, mas sem bônus de "
            "tempo. Clique em 'Verificar Solução' quando estiver pronto, ou peça ajuda "
            "ao Agente na próxima aba."
        )

    panel(
        "MONTE A CONSULTA",
        "Use as pistas da primeira aba para preencher cada peça do quebra-cabeça.",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**1) Modificador do SELECT**")
        p_select_mod = st.radio("select_modifier", ["SELECT", "SELECT DISTINCT"],
                                 label_visibility="collapsed", horizontal=True,
                                 key=f"sm_{level['id']}")

        st.markdown("**2) Colunas retornadas**")
        p_columns = st.multiselect("columns", level["column_pool"],
                                    label_visibility="collapsed", key=f"cols_{level['id']}")

        st.markdown("**3) Tabela principal (FROM)**")
        p_main_table = st.selectbox("main_table", level["main_table_pool"],
                                     label_visibility="collapsed", key=f"mt_{level['id']}")

        st.markdown("**4) Tipo de JOIN**")
        p_join_type = st.selectbox(
            "join_type", ["SEM JOIN", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN"],
            label_visibility="collapsed", key=f"jt_{level['id']}",
        )

        p_joined_table, p_join_cond = None, None
        if p_join_type != "SEM JOIN":
            st.markdown("**5) Tabela unida / condição do JOIN**")
            p_joined_table = st.selectbox("joined_table", level["joined_table_pool"],
                                           label_visibility="collapsed", key=f"jtab_{level['id']}")
            p_join_cond = st.selectbox("join_condition", level["options"]["join_condition"],
                                        label_visibility="collapsed", key=f"jc_{level['id']}")

    with col2:
        st.markdown("**6) Existe WHERE?**")
        p_where_presence = st.radio("where_presence", ["AUSENTE", "PRESENTE"],
                                     label_visibility="collapsed", horizontal=True,
                                     key=f"wp_{level['id']}")
        p_where_cond = None
        if p_where_presence == "PRESENTE":
            p_where_cond = st.selectbox("where_condition", level["options"]["where_condition"],
                                         label_visibility="collapsed", key=f"wc_{level['id']}")

        st.markdown("**7) GROUP BY?**")
        p_group_by = st.radio("group_by_presence", ["AUSENTE", "PRESENTE"],
                               label_visibility="collapsed", horizontal=True, key=f"gb_{level['id']}")
        p_group_col = None
        if p_group_by == "PRESENTE":
            p_group_col = st.selectbox("group_by_column", level["options"]["group_by_column"],
                                        label_visibility="collapsed", key=f"gbc_{level['id']}")

        st.markdown("**8) HAVING?**")
        p_having = st.radio("having_presence", ["AUSENTE", "PRESENTE"],
                             label_visibility="collapsed", horizontal=True, key=f"hv_{level['id']}")
        p_having_cond = None
        if p_having == "PRESENTE":
            p_having_cond = st.selectbox("having_condition", level["options"]["having_condition"],
                                          label_visibility="collapsed", key=f"hvc_{level['id']}")

        st.markdown("**9) ORDER BY?**")
        p_order_presence = st.radio("order_by_presence", ["AUSENTE", "PRESENTE"],
                                     label_visibility="collapsed", horizontal=True, key=f"ob_{level['id']}")
        p_order_col = None
        if p_order_presence == "PRESENTE":
            p_order_col = st.selectbox("order_by_column", level["options"]["order_by_column"],
                                        label_visibility="collapsed", key=f"obc_{level['id']}")

        st.markdown("**10) LIMIT?**")
        p_limit = st.radio("limit_presence", ["AUSENTE", "PRESENTE"],
                            label_visibility="collapsed", horizontal=True, key=f"lim_{level['id']}")
        p_limit_val = None
        if p_limit == "PRESENTE":
            p_limit_val = st.selectbox("limit_value", level["options"]["limit_value"],
                                        label_visibility="collapsed", key=f"limv_{level['id']}")

    st.markdown("<hr class='comic-hr'>", unsafe_allow_html=True)
    if ls["wrong_attempts"] > 0:
        st.caption(
            f"❌ Tentativas erradas até agora: **{ls['wrong_attempts']}** "
            f"(-{ls['wrong_attempts'] * PENALTY_PER_WRONG_ATTEMPT} pts na pontuação final)"
        )
    verify = st.button("🔍 Verificar Solução", type="primary")

    if verify:
        sol = level["domains"]
        checks = {
            "Modificador SELECT": p_select_mod == sol["select_modifier"][0],
            "Colunas": set(p_columns) == sol["columns"][0],
            "Tabela principal": p_main_table == sol["main_table"][0],
            "Tipo de JOIN": p_join_type == sol["join_type"][0],
            "Presença de WHERE": p_where_presence == sol["where_presence"][0],
            "GROUP BY": p_group_by == sol["group_by_presence"][0],
            "HAVING": p_having == sol["having_presence"][0],
            "Presença de ORDER BY": p_order_presence == sol["order_by_presence"][0],
            "LIMIT": p_limit == sol["limit_presence"][0],
        }
        if sol["join_type"][0] != "SEM JOIN":
            checks["Tabela unida"] = p_joined_table == sol["joined_table"][0]
            checks["Condição do JOIN"] = p_join_cond == sol["join_condition"][0]
        if sol["where_presence"][0] == "PRESENTE":
            checks["Condição do WHERE"] = p_where_cond == sol["where_condition"][0]
        if sol["group_by_presence"][0] == "PRESENTE":
            checks["Coluna do GROUP BY"] = p_group_col == sol["group_by_column"][0]
        if sol["having_presence"][0] == "PRESENTE":
            checks["Condição do HAVING"] = p_having_cond == sol["having_condition"][0]
        if sol["order_by_presence"][0] == "PRESENTE":
            checks["Coluna do ORDER BY"] = p_order_col == sol["order_by_column"][0]
        if sol["limit_presence"][0] == "PRESENTE":
            checks["Valor do LIMIT"] = p_limit_val == sol["limit_value"][0]

        all_correct = all(checks.values())

        # Guarda o resultado da última verificação no estado do nível (em vez
        # de só numa variável local): assim ele continua na tela mesmo depois
        # de reruns causados por outras interações (cronômetro, sidebar etc.).
        ls["last_check"] = {"checks": checks, "all_correct": all_correct}

        if not all_correct:
            ls["wrong_attempts"] += 1
        else:
            penalty = ls["wrong_attempts"] * PENALTY_PER_WRONG_ATTEMPT
            agent_penalty = PENALTY_FOR_USING_AGENT if ls["used_agent"] else 0
            time_bonus = int(remaining) * POINTS_PER_SECOND_REMAINING if remaining is not None else 0
            score = max(MIN_SCORE_FLOOR, level["base_points"] + time_bonus - penalty - agent_penalty)
            ls["solved"] = True
            ls["score"] = score
            ls["score_breakdown"] = {
                "time_bonus": time_bonus,
                "penalty": penalty,
                "agent_penalty": agent_penalty,
                "used_timer": remaining is not None,
                "score": score,
            }
            update_leaderboard(player["codinome"], player["nome"], player["avatar"], total_score())

            if current_level_idx == total_levels - 1:
                st.balloons()

            _render_solved_result(level, ls, current_level_idx, total_levels)
            return

    # Sempre renderiza o último relatório de perícia guardado no estado do
    # nível — não só na execução em que o botão foi clicado. É isso que
    # impede o relatório de "sumir" a cada rerun automático da página.
    last_check = ls.get("last_check")
    if last_check:
        panel_lines = "".join(
            f"{'✅' if ok else '❌'} {label}<br>" for label, ok in last_check["checks"].items()
        )
        panel("RELATÓRIO DA PERÍCIA", panel_lines)
        if not last_check["all_correct"]:
            st.warning(
                "Ainda há contradições no seu dossiê, detetive. Releia as pistas e tente "
                f"de novo. (Cada erro reduz sua pontuação final em {PENALTY_PER_WRONG_ATTEMPT} pts.)"
            )


def _render_agente_tab(level, ls):
    panel(
        "O AGENTE DETETIVE",
        "Se preferir, chame o agente para aplicar cada pista, uma de cada vez: ler "
        "pistas → construir possibilidades → eliminar combinações inválidas → propagar "
        "→ repetir até convergência. <b>Atenção:</b> usar o agente neste nível aplica "
        f"uma penalidade de {PENALTY_FOR_USING_AGENT} pts na pontuação final, se o nível "
        "ainda não tiver sido resolvido.",
    )

    already_revealed = ls.get("agent_revealed", False)
    button_label = (
        "🔁 Ver de novo a resolução do Agente" if already_revealed
        else "🤖 Chamar o Agente para Resolver o Caso"
    )
    if st.button(button_label):
        if not ls["solved"]:
            ls["used_agent"] = True
        ls["agent_revealed"] = True

    if not ls.get("agent_revealed"):
        return

    if already_revealed:
        st.caption("ℹ️ O agente já foi chamado neste nível — a resolução abaixo continua disponível a qualquer momento.")

    for entry in level["log"]:
        speech_bubble(entry["n"], entry["clue"])
        for elim in entry["eliminations"]:
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;⤷ *{elim}*")

    st.markdown("<hr class='comic-hr'>", unsafe_allow_html=True)

    if not level["unique"]:
        st.error(
            "⚠️ O QUEBRA-CABEÇA ESTÁ INCOMPLETO. Alguma categoria ainda tem mais de uma "
            "possibilidade após todas as pistas. O agente NUNCA escolhe arbitrariamente "
            "— pistas adicionais seriam necessárias."
        )
    else:
        case_closed("O AGENTE RESOLVEU O CASO!")
        st.write(
            "Todas as posições foram deduzidas de forma única. O comando SQL é "
            "consequência direta das pistas:"
        )
        st.code(level["target_sql"], language="sql")


def _render_placar_tab():
    panel(
        "🏆 PLACAR DE DETETIVES",
        "Os investigadores com a maior pontuação acumulada em toda a agência.",
    )
    entries = top_entries(10)
    if not entries:
        st.write("Nenhum caso resolvido ainda. Seja o primeiro a entrar para o placar!")
        return
    for pos, e in enumerate(entries, start=1):
        medalha = {1: "🥇", 2: "🥈", 3: "🥉"}.get(pos, f"{pos}.")
        speech_bubble_html = (
            f'{medalha} {e["avatar"]} <b>{e["codinome"]}</b> — {e["total_score"]} pts'
        )
        st.markdown(f'<div class="speech-bubble">{speech_bubble_html}</div>', unsafe_allow_html=True)


@st.fragment(run_every=TIMER_REFRESH_INTERVAL_MS / 1000)
def _render_timer_fragment(level_id, time_limit):
    """Atualiza só a caixinha do cronômetro a cada segundo.

    Antes, o autorrefresh re-executava a página INTEIRA a cada segundo.
    Isso tinha dois efeitos colaterais visíveis para o jogador:
    - na aba "Monte a Consulta", o relatório de perícia (que só existia
      enquanto durava aquele clique do botão) sumia da tela em ~1s;
    - na aba "Sala do Agente", a re-execução completa fazia a interface
      voltar para a primeira aba, dando a impressão de que a resposta do
      agente tinha desaparecido.
    Isolando o tique do relógio num fragmento, só esta função reroda a
    cada intervalo — o resto da página (abas, relatórios, resultado do
    agente) fica intacto.
    """
    ls = st.session_state.level_state[level_id]
    if ls["solved"]:
        timer_box("✅ RESOLVIDO")
        return
    if ls["started_at"] is None:
        ls["started_at"] = time.time()
    elapsed = time.time() - ls["started_at"]
    remaining = max(0, time_limit - elapsed)
    mins, secs = divmod(int(remaining), 60)
    timer_box(f"⏱ {mins:02d}:{secs:02d}", danger=remaining < 30)


def render_game(levels):
    player = st.session_state.player
    level = levels[st.session_state.current_level]
    ls = st.session_state.level_state[level["id"]]
    timer_enabled = st.session_state.timer_enabled

    # `remaining` aqui é só o valor usado nesta execução do script (pontuação
    # e avisos da aba "Monte a Consulta"); é recalculado a cada clique real
    # do jogador, então fica sempre correto no momento de "Verificar Solução".
    # O tique visual do relógio, à parte, é responsabilidade do fragmento
    # acima e não depende deste valor.
    remaining = None
    if timer_enabled:
        if ls["started_at"] is None:
            ls["started_at"] = time.time()
        elapsed = time.time() - ls["started_at"]
        remaining = max(0, level["time_limit"] - elapsed)

    top1, top2, top3 = st.columns([2, 1, 1])
    with top1:
        st.markdown(
            f'<span class="level-badge {level["css_class"]}">{level["dificuldade"]}</span>'
            f'<b style="font-family:Bangers; font-size:1.4rem; color:var(--ink);">{level["titulo"]}</b>',
            unsafe_allow_html=True,
        )
    with top2:
        if not timer_enabled:
            timer_box("⏱ Desativado", off=True)
        else:
            _render_timer_fragment(level["id"], level["time_limit"])
        toggle = st.checkbox("Ativar cronômetro", value=timer_enabled, key="timer_toggle")
        if toggle != timer_enabled:
            st.session_state.timer_enabled = toggle
            st.rerun()
    with top3:
        score_box(f"⭐ {ls['score'] if ls['score'] is not None else '—'}")

    st.write("")

    tab_pistas, tab_montar, tab_agente, tab_placar = st.tabs(
        ["🔎 Pistas do Caso", "🧩 Monte a Consulta", "🤖 Sala do Agente", "🏆 Placar de Detetives"]
    )

    with tab_pistas:
        _render_pistas_tab(level)
    with tab_montar:
        _render_montar_tab(level, ls, player, remaining, st.session_state.current_level, len(levels))
    with tab_agente:
        _render_agente_tab(level, ls)
    with tab_placar:
        _render_placar_tab()
