import html
from datetime import datetime
from pathlib import Path


def calcular_score(campos_por_linha):
    campos_total = 0
    campos_ok = 0
    campos_nok = 0
    linhas = len(campos_por_linha)
    linhas_completas = 0

    for l in campos_por_linha:
        todos_ok = True
        for c in l["campos"]:
            campos_total += 1
            if c["status"] == "OK":
                campos_ok += 1
            else:
                campos_nok += 1
                todos_ok = False
        if todos_ok:
            linhas_completas += 1

    score = round((campos_ok / campos_total) * 100) if campos_total else 0

    return {
        "score": score,
        "campos_total": campos_total,
        "campos_ok": campos_ok,
        "campos_nok": campos_nok,
        "linhas": linhas,
        "linhas_completas": linhas_completas,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatorio RPA - Score</title>
<style>
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f4f5f7;
    color: #1a1a1a;
    margin: 0;
    padding: 32px;
  }
  .wrap {
    max-width: 960px; margin: 0 auto; background: #fff;
    border-radius: 12px; padding: 32px;
    box-shadow: 0 2px 8px rgba(0,0,0,.08);
  }
  h1 { margin: 0 0 4px; font-size: 22px; }
  h2 { font-size: 15px; margin: 28px 0 8px; }
  .sub { color: #666; margin: 0; font-size: 13px; }
  .score-row { display: flex; align-items: baseline; gap: 16px; margin: 24px 0 4px; }
  .score-big { font-size: 72px; font-weight: 700; color: #1f6feb; line-height: 1; }
  .score-label { color: #666; font-size: 14px; }
  .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 24px 0; }
  .kpi { background: #f8f9fa; border-radius: 8px; padding: 14px 16px; }
  .kpi .l { color: #666; font-size: 11px; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 4px; }
  .kpi .v { font-size: 22px; font-weight: 600; }
  .ok { color: #1a7f37; }
  .nok { color: #cf222e; }
  table { width: 100%; border-collapse: collapse; margin-bottom: 8px; }
  th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #eee; font-size: 13px; }
  th { background: #fafafa; font-weight: 600; color: #333; }
  td.ok, td.nok { font-weight: 600; width: 80px; }
  .footer { margin-top: 32px; padding-top: 16px; border-top: 1px solid #eee; color: #999; font-size: 11px; }
</style>
</head>
<body>
  <div class="wrap">
    <h1>Relatorio de Execucao &mdash; RPA Nava</h1>
    <p class="sub">Gerado em __TIMESTAMP__</p>

    <div class="score-row">
      <div class="score-big">__SCORE__</div>
      <div class="score-label">de 100 &mdash; score geral de preenchimento</div>
    </div>
    <p class="sub">Score = campos OK / campos totais preenchidos</p>

    <div class="kpis">
      <div class="kpi"><div class="l">Campos OK</div><div class="v ok">__COK__</div></div>
      <div class="kpi"><div class="l">Campos NOK</div><div class="v nok">__CNOK__</div></div>
      <div class="kpi"><div class="l">Campos total</div><div class="v">__CTOT__</div></div>
      <div class="kpi"><div class="l">Linhas completas</div><div class="v">__LC__/__LT__</div></div>
    </div>

    __TABELAS__

    <div class="footer">RPA Nava &mdash; execucao automatica</div>
  </div>
</body>
</html>
"""


def gerar_relatorio_html(metricas, campos_por_linha, caminho_saida):
    blocos = []
    for l in campos_por_linha:
        rows = []
        for c in l["campos"]:
            cls = "ok" if c["status"] == "OK" else "nok"
            rows.append(
                "<tr>"
                "<td>" + html.escape(c["campo"]) + "</td>"
                "<td class='" + cls + "'>" + c["status"] + "</td>"
                "<td>" + html.escape(c["observacao"]) + "</td>"
                "</tr>"
            )
        blocos.append(
            "<h2>Linha " + str(l["linha"]) + " do Excel</h2>"
            "<table><thead><tr>"
            "<th>Campo</th><th>Status</th><th>Observacao</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
        )
    conteudo_tabelas = "".join(blocos)

    html_doc = HTML_TEMPLATE
    html_doc = html_doc.replace("__TIMESTAMP__", metricas["timestamp"])
    html_doc = html_doc.replace("__SCORE__", str(metricas["score"]))
    html_doc = html_doc.replace("__COK__", str(metricas["campos_ok"]))
    html_doc = html_doc.replace("__CNOK__", str(metricas["campos_nok"]))
    html_doc = html_doc.replace("__CTOT__", str(metricas["campos_total"]))
    html_doc = html_doc.replace("__LC__", str(metricas["linhas_completas"]))
    html_doc = html_doc.replace("__LT__", str(metricas["linhas"]))
    html_doc = html_doc.replace("__TABELAS__", conteudo_tabelas)

    Path(caminho_saida).write_text(html_doc, encoding="utf-8")
    return html_doc
