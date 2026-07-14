/**
 * CASO SQL — Web App de cadastro de detetives
 * --------------------------------------------
 * Recebe cadastros via POST vindos do jogo Streamlit e grava (ou
 * atualiza, se o codinome já existir) uma linha na primeira aba da
 * planilha, sempre nesta ordem de colunas:
 *
 *   DATA_HORA | ID_REGISTRO | NOME | EMAIL | CELULAR | IP | CODINOME | AVATAR | BADGE
 *
 * - DATA_HORA é preenchida automaticamente por este script (new Date()),
 *   nunca pelo cliente — garante consistência de fuso/formatação.
 * - ID_REGISTRO, IP, CODINOME, AVATAR e BADGE vêm prontos do jogo.
 * - CODINOME, AVATAR e BADGE são usados pelas telas de login/placar do
 *   jogo; se você não precisa deles, pode simplesmente ignorar essas
 *   colunas na sua planilha (o script continua funcionando).
 *
 * COMO INSTALAR:
 * 1. Abra a planilha (a mesma do link /pubhtml) no navegador.
 * 2. Menu Extensões > Apps Script.
 * 3. Apague o conteúdo padrão e cole todo o conteúdo deste arquivo.
 * 4. Na primeira aba da planilha, crie a linha de cabeçalho (linha 1):
 *      DATA_HORA | ID_REGISTRO | NOME | EMAIL | CELULAR | IP | CODINOME | AVATAR | BADGE
 * 5. Clique em "Implantar" (Deploy) > "Nova implantação" (New deployment).
 *    - Tipo: "Web app" (Aplicativo da Web)
 *    - Executar como: Eu (você)
 *    - Quem tem acesso: Qualquer pessoa (Anyone)
 * 6. Autorize as permissões pedidas (é o seu próprio script acessando a
 *    sua própria planilha).
 * 7. Copie a URL gerada, terminada em "/exec".
 * 8. Cole essa URL na constante GOOGLE_SCRIPT_WEBAPP_URL em src/config.py.
 * 9. Garanta que a planilha também esteja publicada na web (Arquivo >
 *    Compartilhar > Publicar na Web) — é isso que permite a leitura via
 *    CSV usada pelo botão "Já sou cadastrado" do jogo.
 *
 * Se você já tinha uma versão anterior deste script/planilha (com as
 * colunas antigas nome|codinome|avatar|badge|timestamp), refaça o
 * cabeçalho da linha 1 para a ordem nova acima antes de reimplantar.
 */

// Índices de coluna (0-based) na ordem definida acima.
var COL_DATA_HORA = 0;
var COL_ID_REGISTRO = 1;
var COL_NOME = 2;
var COL_EMAIL = 3;
var COL_CELULAR = 4;
var COL_IP = 5;
var COL_CODINOME = 6;
var COL_AVATAR = 7;
var COL_BADGE = 8;
var TOTAL_COLS = 9;

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheets()[0];

    var data = JSON.parse(e.postData.contents);
    var idRegistro = data.id_registro || "";
    var nome = data.nome || "";
    var email = data.email || "";
    var celular = data.celular || "";
    var ip = data.ip || "";
    var codinome = data.codinome || "";
    var avatar = data.avatar || "";
    var badge = data.badge || "";
    var dataHora = new Date(); // sempre automático, nunca vindo do cliente

    var values = sheet.getDataRange().getValues();
    var rowIndex = -1; // índice 1-based da linha a atualizar, se existir

    for (var i = 1; i < values.length; i++) {
      var existingCodinome = String(values[i][COL_CODINOME] || "").trim().toLowerCase();
      if (existingCodinome === String(codinome).trim().toLowerCase()) {
        rowIndex = i + 1; // +1 porque getRange é 1-indexed e values[0] é o cabeçalho
        break;
      }
    }

    var row = [];
    row[COL_DATA_HORA] = dataHora;
    row[COL_ID_REGISTRO] = idRegistro;
    row[COL_NOME] = nome;
    row[COL_EMAIL] = email;
    row[COL_CELULAR] = celular;
    row[COL_IP] = ip;
    row[COL_CODINOME] = codinome;
    row[COL_AVATAR] = avatar;
    row[COL_BADGE] = badge;

    if (rowIndex > -1) {
      // Codinome já existia: atualiza os dados em vez de duplicar a linha.
      // DATA_HORA também é atualizada para refletir o momento da atualização.
      sheet.getRange(rowIndex, 1, 1, TOTAL_COLS).setValues([row]);
    } else {
      // Novo detetive: adiciona uma linha nova.
      sheet.appendRow(row);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ status: "ok", id_registro: idRegistro }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: "error", message: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ status: "Use POST para cadastrar um detetive." }))
    .setMimeType(ContentService.MimeType.JSON);
}
