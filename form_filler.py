import logging
import time

from playwright.sync_api import expect

logger = logging.getLogger("rpa_nava")


def preencher_campo(page, seletor, valor, nome_campo, tipo="text",
                    timeout=10000, tentativas=2):
    ultimo_erro = None
    for tentativa in range(1, tentativas + 1):
        try:
            if tipo == "radio":
                alvo = page.locator(
                    "%s[value^='%s']" % (seletor, str(valor))
                ).first
                alvo.wait_for(state="attached", timeout=timeout)
                alvo.scroll_into_view_if_needed()
                alvo.check(force=True)
                logger.info(
                    "Radio '%s' marcado (valor '%s', tentativa %s).",
                    nome_campo, valor, tentativa,
                )
                return True, "Radio marcado com sucesso."

            campo = page.locator(seletor).first
            campo.wait_for(state="visible", timeout=timeout)
            campo.scroll_into_view_if_needed()

            if tipo == "date":
                campo.fill(str(valor))
                campo.press("Tab")
                logger.info("Data '%s' preenchida com '%s'.", nome_campo, valor)
                return True, "Data preenchida com sucesso."

            campo.fill(str(valor))
            expect(campo).to_have_value(str(valor), timeout=2000)
            logger.info(
                "Campo '%s' preenchido (tentativa %s).", nome_campo, tentativa
            )
            return True, "Preenchido com sucesso."
        except Exception as e:
            ultimo_erro = str(e)
            logger.warning(
                "Tentativa %s falhou no campo '%s': %s",
                tentativa, nome_campo, ultimo_erro,
            )
            time.sleep(1)
    return False, "Falha: %s" % ultimo_erro


def clicar_botao(page, seletor, nome_botao, timeout=15000):
    try:
        botao = page.locator(seletor).first
        botao.wait_for(state="visible", timeout=timeout)
        botao.scroll_into_view_if_needed()
        botao.click()
        logger.info("Botao '%s' clicado.", nome_botao)
        return True, "Botao clicado com sucesso."
    except Exception as e:
        logger.error("Falha ao clicar '%s': %s", nome_botao, e)
        return False, "Falha ao clicar: %s" % e


def preencher_formulario(page, dados, config):
    resultados = []

    for item in config["campos"]:
        coluna = item["coluna"]
        seletor = item["seletor"]
        nome = item.get("label", coluna)
        tipo = item.get("tipo", "text")
        obrigatorio = item.get("obrigatorio", True)

        if coluna not in dados or dados[coluna] in (None, ""):
            if obrigatorio:
                logger.error("Campo obrigatorio '%s' sem valor no Excel.", nome)
                resultados.append({
                    "campo": nome,
                    "status": "NOK",
                    "observacao": "Valor ausente no Excel (campo obrigatorio)",
                })
            else:
                logger.info("Campo opcional '%s' vazio, pulando.", nome)
                resultados.append({
                    "campo": nome,
                    "status": "OK",
                    "observacao": "Campo opcional nao preenchido no Excel",
                })
            continue

        ok, msg = preencher_campo(
            page, seletor, dados[coluna], nome, tipo=tipo,
            timeout=config.get("timeout_campo_ms", 10000),
        )
        resultados.append({
            "campo": nome,
            "status": "OK" if ok else "NOK",
            "observacao": msg,
        })

    todos_ok = all(r["status"] == "OK" for r in resultados)
    return todos_ok, resultados
