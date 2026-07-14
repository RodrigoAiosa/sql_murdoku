/**
 * CASO SQL — Web App de cadastro de detetives
 * --------------------------------------------
 * Este script recebe cadastros (nome, codinome, avatar, badge) via POST
 * vindos do jogo Streamlit e grava (ou atualiza, se o codinome já existir)
 * uma linha na primeira aba da planilha.
 *
 * COMO INSTALAR:
 * 1. Abra a planilha (a mesma do link /pubhtml) no navegador.
 * 2. Menu Extensões > Apps Script.
 * 3. Apague o conteúdo padrão e cole todo o conteúdo deste arquivo.
 * 4. Na primeira aba da planilha, crie a linha de cabeçalho (linha 1):
 *      nome | codinome | avatar | badge | timestamp
 * 5. Clique em "Implantar" (Deploy) > "Nova implantação" (New deployment).
 *    - Tipo: "Web app" (Aplicativo da Web)
 *    - Executar como: Eu (você)
 *    - Quem tem acesso: Qualquer pessoa (Anyone)
 * 6. Autorize as permissões pedidas (é o seu próprio script acessando a
 *    sua própria planilha).
 * 7. Copie a URL gerada, terminada em "/exec".
 * 8. Cole essa URL na constante GOOGLE_SCRIPT_WEBAPP_URL no topo do
 *    arquivo app.py do jogo.
 * 9. Garanta que a planilha também esteja publicada na web (Arquivo >
 *    Compartilhar > Publicar na Web) — é isso que permite a leitura via
 *    CSV usada pelo botão "Já sou cadastrado" do jogo.
 */

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheets()[0];

    var data = JSON.parse(e.postData.contents);
    var nome = data.nome || "";
    var codinome = data.codinome || "";
    var avatar = data.avatar || "";
    var badge = data.badge || "";
    var timestamp = new Date();

    var values = sheet.getDataRange().getValues();
    var rowIndex = -1; // índice 1-based da linha a atualizar, se existir

    for (var i = 1; i < values.length; i++) {
      var existingCodinome = String(values[i][1] || "").trim().toLowerCase();
      if (existingCodinome === String(codinome).trim().toLowerCase()) {
        rowIndex = i + 1; // +1 porque getRange é 1-indexed e values[0] é o cabeçalho
        break;
      }
    }

    var row = [nome, codinome, avatar, badge, timestamp];

    if (rowIndex > -1) {
      // Codinome já existia: atualiza os dados em vez de duplicar a linha.
      sheet.getRange(rowIndex, 1, 1, row.length).setValues([row]);
    } else {
      // Novo detetive: adiciona uma linha nova.
      sheet.appendRow(row);
    }

    return ContentService
      .createTextOutput(JSON.stringify({ status: "ok" }))
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
