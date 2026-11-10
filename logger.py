import logging
import csv
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def configurar_logger():
    log_path = BASE_DIR / "logs" / "etapas.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("rpa_nava")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def registrar_resultado_campo(linha_excel, campo, status, observacao,
                              csv_path=None):
    csv_path = csv_path or (BASE_DIR / "resultados" / "resultados.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    novo = not csv_path.exists()
    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        if novo:
            writer.writerow(
                ["linha_excel", "campo", "status", "observacao", "data_hora"]
            )
        writer.writerow(
            [
                linha_excel,
                campo,
                status,
                observacao,
                datetime.now().isoformat(sep=" ", timespec="seconds"),
            ]
        )
