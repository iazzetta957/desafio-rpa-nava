from pathlib import Path
from openpyxl import Workbook

destino = Path(__file__).resolve().parent / "data" / "entrada.xlsx"
destino.parent.mkdir(parents=True, exist_ok=True)

colunas = [
    "Nome Completo", "Nome Social", "PCD", "Data de Nascimento", "CPF", "RG",
    "Cidade do RG", "Nome completo da mae", "Nome completo do pai",
    "Nacionalidade", "Naturalidade", "Endereco residencial completo",
    "CEP Residencial", "Telefone - Celular", "Telefone - Residencial",
    "E-mail pessoal", "Cidade de preferencia para exame medico",
    "Ja trabalhou na Nava", "Projeto cliente relacionado",
    "Afastamento previsto", "Referencia 1", "Referencia 2", "Referencia 3",
    "Veracidade",
]

dados = [
    "Matheus Iazzetta Rodrigues",
    "Matheus",
    "Nao",
    "07/10/1999",
    "507.766.028-02",
    "55.157.707-1",
    "Sao Paulo/SP",
    "Elaine Cristina Iazzetta Rodrigues",
    "Carlos Eduardo Rodrigues",
    "Brasileira",
    "Sao Paulo/SP",
    "Rua Antonio Paganini 59",
    "03732-140",
    "(11) 98514-9968",
    "(11) 98514-9968",
    "matheusiazzetta@gmail.com",
    "Sao Paulo/SP",
    "Nao",
    "Nao",
    "Nao",
    "Ramon Christian - Inmetrics - Engenheiro de Software Senior - (19) 99902-0154",
    "Aline Almeida - Inmetrics - Coordenadora de Projetos - (11) 96211-9480",
    "",
    "Sim",
]

wb = Workbook()
ws = wb.active
ws.title = "Dados"
ws.append(colunas)
ws.append(dados)
wb.save(destino)
print("Planilha criada em:", destino)
