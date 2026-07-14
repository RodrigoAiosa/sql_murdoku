# Caso SQL: O Enigma da Consulta Perdida

Jogo de dedução lógica (estilo quadrinho noir dos anos 50) feito em **Python + Streamlit**,
onde o SQL final nunca é "inventado" — ele é sempre consequência direta da aplicação
das pistas sobre um conjunto de possibilidades (processo de inferência tipo CSP).

## Estrutura do projeto

```
sql_comic_game/
├── app.py                     # ponto de entrada (Streamlit) — só orquestra
├── requirements.txt
├── Code.gs                    # Google Apps Script (grava cadastros na planilha)
├── .gitignore
├── assets/
│   └── styles.css             # todo o CSS do tema de quadrinho
├── data/
│   └── leaderboard.json       # gerado em tempo de execução (ignorado no git)
├── src/
│   ├── config.py               # constantes: caminhos, URLs, regras de pontuação
│   ├── engine.py                 # motor de dedução (CSP) — puro, sem Streamlit
│   ├── levels.py                  # definição dos 3 casos/níveis do jogo
│   ├── session.py                  # sessão local (cadastro só uma vez por dispositivo)
│   ├── sheets.py                    # integração com Google Sheets (leitura CSV + Apps Script)
│   ├── leaderboard.py                # placar de detetives (JSON local)
│   └── ui/
│       ├── styles.py                 # injeta assets/styles.css no Streamlit
│       ├── components.py              # painéis, balões de fala, selos (HTML reutilizável)
│       ├── registration.py             # tela de cadastro/login
│       ├── sidebar.py                   # barra lateral (ficha, pontuação, navegação)
│       └── game.py                       # abas do jogo (pistas, montar, agente, placar)
└── tests/
    └── test_engine.py          # testes automatizados do motor de dedução
```

Separação de responsabilidades:
- **`engine.py`** não importa Streamlit — é lógica pura, testável isoladamente.
- **`levels.py`** só contém dados do quebra-cabeça (nenhuma regra de negócio).
- **`ui/`** só sabe desenhar telas; toda regra fica em `engine.py`, `levels.py`,
  `session.py`, `sheets.py` e `leaderboard.py`.
- **`config.py`** centraliza tudo que é configurável (URLs, pontuação, caminhos),
  então ajustar o jogo raramente exige tocar em outros arquivos.

## Como rodar

```bash
cd sql_comic_game
pip install -r requirements.txt
streamlit run app.py
```

Abra o link que aparecer no terminal (normalmente `http://localhost:8501`).

## Como rodar os testes

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Os testes cobrem o motor de dedução puro (`src/engine.py`) e garantem que os 3 níveis
convergem para solução única (nenhuma ambiguidade) e que o SQL gerado bate com o
esperado.

## Tema e contraste de texto

O jogo força um tema **claro** do Streamlit via `.streamlit/config.toml` (fundo cor de
papel, texto preto). Isso existe porque, sem essa configuração, o Streamlit Cloud pode
aplicar automaticamente um tema **escuro** ao app (dependendo da preferência do
navegador/conta de quem acessa) — e como o visual em quadrinho usa fundo claro, o texto
herdado do tema escuro (branco) ficava invisível em painéis, balões de fala, ficha do
detetive e no título do nível. Se ainda notar algum texto sem contraste em algum canto
específico, normalmente é porque aquele elemento não tem uma cor própria definida em
`assets/styles.css` — basta adicionar `color: var(--ink);` à classe correspondente.

## Como jogar

0. **Cadastro (uma única vez)** — na primeira vez que abrir o jogo, você cria sua ficha
   de detetive (nome, codinome e avatar). Nas próximas vezes, o jogo te reconhece
   automaticamente neste dispositivo. Se abrir em outro computador, basta digitar seu
   codinome na tela "Já sou cadastrado" para continuar sem preencher tudo de novo (desde
   que a planilha do Google esteja publicada — veja a seção abaixo).
1. **Aba "Pistas do Caso"** — leia as pistas do mistério (balões de fala em estilo HQ).
2. **Aba "Monte a Consulta"** — preencha cada peça do quebra-cabeça (SELECT, colunas,
   tabela, JOIN, WHERE, GROUP BY/HAVING, ORDER BY, LIMIT) com base no que você deduziu.
   Clique em **Verificar Solução** para conferir peça por peça.
3. **Aba "Sala do Agente"** — se preferir ver o raciocínio completo, chame o agente para
   resolver o caso: ele aplica as pistas uma a uma, mostra o que cada uma eliminou, e só
   revela o SQL final se **todas** as posições ficarem unicamente determinadas. Se sobrar
   ambiguidade, ele declara o caso **incompleto** em vez de chutar uma resposta.
   ⚠️ Usar o agente antes de resolver sozinho aplica uma penalidade de 400 pts.
4. **Aba "Placar de Detetives"** — ranking dos investigadores com maior pontuação
   acumulada (persistido em `leaderboard.json`).

## Cadastro único e integração com Google Sheets

O cadastro (nome, codinome, avatar) é pensado para acontecer **uma única vez** por
detetive, com dois mecanismos que trabalham juntos:

### 1. Sessão local (funciona sem nenhuma configuração)
Ao se cadastrar, o jogo salva um arquivo `~/.caso_sql_comic_session.json` no seu usuário
do sistema operacional. Da próxima vez que o Streamlit for iniciado nesse mesmo
computador, o cadastro é pulado automaticamente. Use o botão **"🚪 Trocar de Detetive"**
na barra lateral para sair dessa sessão (por exemplo, se outra pessoa for jogar no
mesmo computador).

### 2. Planilha do Google (opcional, para reconhecer o mesmo detetive em qualquer PC)
Você passou este link de planilha publicada:
```
https://docs.google.com/spreadsheets/d/e/2PACX-1vQwQTp7f0ph0nfCwOelM9XgUSi-e8-EMYDHe6Ef8WOy8GyKvzU8ZrXq00out2818c8WJ51FEHWKQTYG/pubhtml
```
**Atenção importante:** um link `/pubhtml` é **somente leitura** — o Google não permite
gravar dados através dele. Por isso a integração foi dividida em duas partes:

- **Leitura** (já funciona com o link que você mandou, sem nenhuma configuração extra):
  o jogo converte esse link para o formato de exportação CSV (`/pub?output=csv`) e lê a
  planilha para checar, na tela "Já sou cadastrado", se aquele codinome já existe.
- **Escrita** (grava um cadastro novo na planilha): exige publicar um pequeno script.
  Arquivo `Code.gs` incluso neste projeto — copie e cole no Apps Script da sua planilha.
  Passo a passo completo está comentado no topo do próprio arquivo `Code.gs`, resumindo:
  1. Abra a planilha → Extensões → Apps Script → cole o conteúdo de `Code.gs`.
  2. Na primeira aba da planilha, crie o cabeçalho: `nome | codinome | avatar | badge | timestamp`.
  3. Implantar → Nova implantação → tipo "Web app" → executar como você → acesso "Qualquer pessoa".
  4. Copie a URL gerada (termina em `/exec`).
  5. Cole essa URL na constante `GOOGLE_SCRIPT_WEBAPP_URL`, no topo do `app.py`.

Enquanto `GOOGLE_SCRIPT_WEBAPP_URL` não estiver preenchida, o jogo continua funcionando
normalmente (cadastro local + leitura da planilha), só não grava novos cadastros nela —
o jogador vê um aviso amigável explicando isso na hora do cadastro.

Se dois detetives tentarem usar o mesmo codinome, o cadastro é recusado com um aviso
para escolher outro (ou fazer login, se o codinome for realmente dele).

## Níveis

| Nível | Caso | Dificuldade | Tempo | Pontos base | Conceitos novos |
|---|---|---|---|---|---|
| 1 | O Enigma da Consulta Perdida | Fácil | 6 min | 1000 | SELECT, FROM, INNER JOIN, WHERE, ORDER BY |
| 2 | O Estoque Fantasma | Médio | 5 min | 1500 | DISTINCT, LEFT JOIN |
| 3 | O Relatório dos Grandes Clientes | Difícil | 4 min | 2000 | GROUP BY, HAVING, LIMIT, agregações |

Os níveis são desbloqueados progressivamente: resolva o nível atual para liberar o
próximo (o menu lateral mostra 🔒 para níveis bloqueados).

## Pontuação

```
pontuação do nível = base_points
                    + (segundos restantes × 2)      # bônus de tempo
                    - (tentativas erradas × 50)      # penalidade por erro
                    - (400 se usou o Agente)          # penalidade por ajuda
```
com piso mínimo de 50 pontos. A pontuação total do jogador é a soma dos níveis
resolvidos, exibida no cabeçalho e enviada ao placar (`leaderboard.json`).

## Cronômetro

Cada nível tem um tempo limite. O cronômetro é calculado a partir do horário de início
do nível e atualizado a cada interação (botões, seleções, ou o botão manual
"🔄 Atualizar cronômetro"). Se o tempo esgotar, o jogador ainda pode resolver o caso,
mas perde o bônus de tempo.

## Arquitetura do motor de dedução (`src/engine.py`)

- `CATEGORY_ORDER` — lista as posições lógicas da consulta (modificador do SELECT,
  colunas, tabela, tipo de JOIN, condição do JOIN, presença/condição do WHERE, GROUP BY,
  HAVING, ORDER BY, LIMIT).
- `make_clue(texto, assignments)` — gera uma pista associada a uma função que **remove**
  possibilidades inválidas do domínio (nunca adiciona ou "adivinha" valores).
- `run_inference(level)` — aplica todas as pistas de um nível em sequência e registra um
  log de eliminações (o "quadro do detetive"), simulando o processo de: ler pistas →
  eliminar combinações inválidas → propagar → repetir até convergência.
- `is_uniquely_solved(domains)` — verifica se todas as posições relevantes ficaram com
  exatamente uma possibilidade.
- `build_sql(domains)` — monta o SQL **apenas** se a solução for única, seguindo
  exatamente as posições deduzidas, sem otimizar, simplificar ou adicionar cláusulas
  inexistentes.
- `solve_level(level)` — açúcar sintático que roda os três passos acima e anota o
  resultado (`domains`, `log`, `unique`, `target_sql`) direto no dicionário do nível.

## Personalizando / criando novos casos

Para criar um novo mistério, edite `src/levels.py`:

1. Copie uma das funções `level_N()` como ponto de partida.
2. Ajuste `options` — as opções possíveis de cada categoria (inclua distratores
   plausíveis para o jogo ficar desafiador).
3. Reescreva `clues` — o texto do balão de fala e a categoria/valor correto que ela fixa
   (via `make_clue`).
4. Atualize os pools (`column_pool`, `main_table_pool`, `joined_table_pool`) para
   refletir as novas opções que o jogador verá na aba "Monte a Consulta".
5. Adicione o novo nível à lista em `build_levels()`.

O motor (`src/engine.py`) já é genérico e funciona com qualquer conjunto novo de
domínios e pistas — não precisa mexer nele. Rode `pytest tests/ -v` depois de criar um
nível novo para confirmar que ele converge para uma solução única.
