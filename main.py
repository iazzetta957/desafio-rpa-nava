import sys
from datetime import datetime
from pathlib import Path
import yaml
from openpyxl import load_workbook
from playwright.sync_api import sync_playwright
from form_filler import clicar_botao, preencher_formulario
from logger import configurar_logger, registrar_resultado_campo
from score import calcular_score, gerar_relatorio_html

BASE_DIR = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def carregar_config():
    with open(BASE_DIR / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _norm(v, col=None):
    if v is None:
        return v
    if isinstance(v, str):
        v = v.strip()
        if col == "Data de Nascimento" and "/" in v:
            p = v.split("/")
            if len(p) == 3 and len(p[0]) == 2:
                try:
                    return "%d/%d/%s" % (int(p[1]), int(p[0]), p[2])
                except ValueError:
                    return v
        return v
    if hasattr(v, "strftime"):
        return "%d/%d/%d" % (v.month, v.day, v.year)
    return v


def ler_planilha(caminho):
    wb = load_workbook(caminho, read_only=True, data_only=True)
    ws = wb.active
    h = [
        str(c.value).strip() if c.value is not None else ""
        for c in next(ws.iter_rows(min_row=1, max_row=1))
    ]
    linhas = []
    for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not any(row):
            continue
        d = {k: _norm(v, k) for k, v in zip(h, row)}
        d["__linha__"] = idx
        linhas.append(d)
    wb.close()
    return linhas


def main():
    logger = configurar_logger()
    cfg = carregar_config()
    excel = BASE_DIR / cfg["arquivo_excel"]
    url = cfg["url"]
    csv_path = BASE_DIR / "resultados" / "resultados.csv"

    if cfg.get("limpar_resultados_no_inicio", True) and csv_path.exists():
        csv_path.unlink()

    submeter = bool(cfg.get("submeter_formulario", False))

    logger.info("Iniciando execucao")
    logger.info("Planilha: %s", excel)
    logger.info("URL: %s", url)
    logger.info("Submit: %s", "SIM" if submeter else "NAO (modo validacao)")

    if not excel.exists():
        logger.error("Planilha nao encontrada: %s", excel)
        sys.exit(1)

    regs = ler_planilha(excel)
    logger.info("%s registro(s)", len(regs))

    evidencias = BASE_DIR / "evidencias"
    evidencias.mkdir(exist_ok=True)
    campos_por_linha = []

    with sync_playwright() as p:
        nav = p.chromium.launch(headless=False, executable_path=CHROME)
        page = nav.new_context().new_page()
        page.set_default_timeout(20000)

        for i, dados in enumerate(regs):
            linha = dados["__linha__"]
            logger.info("Processando linha %s", linha)
            try:
                page.goto(url, wait_until="domcontentloaded")
                todos_ok, resultados = preencher_formulario(page, dados, cfg)

                for r in resultados:
                    registrar_resultado_campo(
                        linha, r["campo"], r["status"], r["observacao"], csv_path
                    )
                    logger.info(
                        "  [%s] %s - %s",
                        r["status"], r["campo"], r["observacao"],
                    )

                campos_por_linha.append({"linha": linha, "campos": resultados})
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")

                if not todos_ok and cfg.get("submeter_apenas_se_todos_ok", True):
                    logger.error("Campos NOK. Nao submetendo.")
                    page.screenshot(
                        path=str(
                            evidencias / ("linha%s_incompleta_%s.png" % (linha, ts))
                        ),
                        full_page=True,
                    )
                    continue

                if submeter:
                    ok, msg = clicar_botao(
                        page, cfg["seletor_submit"], "Enviar",
                        timeout=cfg.get("timeout_submit_ms", 15000),
                    )
                    if not ok:
                        logger.error("Falha no submit: %s", msg)
                        registrar_resultado_campo(
                            linha, "<submit>", "NOK", msg, csv_path
                        )
                        continue
                    try:
                        page.locator(cfg["seletor_submit"]).first.wait_for(
                            state="hidden", timeout=30000
                        )
                    except Exception:
                        logger.warning("Submit ainda visivel apos envio.")
                    page.wait_for_timeout(1500)
                    page.screenshot(
                        path=str(
                            evidencias / ("linha%s_confirmacao_%s.png" % (linha, ts))
                        ),
                        full_page=True,
                    )
                    registrar_resultado_campo(
                        linha, "<submit>", "OK", "Submetido", csv_path
                    )
                    logger.info("Submetido. Print: linha%s_confirmacao_%s.png", linha, ts)
                else:
                    page.screenshot(
                        path=str(
                            evidencias / ("linha%s_preenchida_%s.png" % (linha, ts))
                        ),
                        full_page=True,
                    )
                    registrar_resultado_campo(
                        linha, "<submit>", "SKIP", "Submit desativado", csv_path
                    )
                    logger.info(
                        "Modo validacao. Print: linha%s_preenchida_%s.png", linha, ts
                    )

            except Exception as e:
                logger.exception("Erro na linha %s: %s", linha, e)
                registrar_resultado_campo(
                    linha, "<erro>", "NOK", str(e), csv_path
                )

            if i < len(regs) - 1:
                page.wait_for_timeout(3000)

        if cfg.get("gerar_relatorio_score", True) and campos_por_linha:
            m = calcular_score(campos_por_linha)
            rel = evidencias / "relatorio.html"
            gerar_relatorio_html(m, campos_por_linha, rel)
            page.goto("file://" + str(rel.resolve()))
            page.wait_for_timeout(800)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            score_shot = evidencias / ("score_final_%s.png" % ts)
            page.screenshot(path=str(score_shot), full_page=True)

            print("")
            print("=" * 60)
            print("SCORE DA AUTOMACAO: %s/100" % m["score"])
            print("Campos OK: %s/%s" % (m["campos_ok"], m["campos_total"]))
            print(
                "Submit executado: %s"
                % ("SIM" if submeter else "NAO (modo validacao)")
            )
            print("Relatorio: %s" % rel)
            print("Print do score: %s" % score_shot)
            print("=" * 60)
            if not submeter:
                print("")
                print("Para enviar de verdade:")
                print("  1) Edite config.yaml: submeter_formulario: false -> true")
                print("  2) Rode: python main.py")

        nav.close()

    logger.info("Execucao finalizada")


if __name__ == "__main__":
    main()
