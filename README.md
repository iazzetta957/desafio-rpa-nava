# Automação de Formulário - Nava

Este projeto realiza a leitura de uma base em Excel, o preenchimento automatizado de um formulário web dinâmico (Microsoft Forms) e a geração de logs de execução e relatórios de score.

## Estrutura do Projeto

```text
nava_rpa/
├── main.py              # Orquestrador da execução
├── form_filler.py       # Módulo de interação com o formulário web
├── logger.py            # Configuração de logs de etapas e resultados
├── score.py             # Gerador de relatório e cálculo de métricas
├── gerar_planilha.py    # Script para gerar a planilha base de entrada
├── config.yaml          # Arquivo de configuração (URL, seletores, timeouts)
├── requirements.txt     # Dependências do projeto
├── data/                # Diretório da planilha de entrada (Excel)
├── evidencias/          # Prints da tela e relatórios HTML
├── logs/                # Arquivo de log de execução
└── resultados/          # Planilha de resultados (OK/NOK por campo)
```

## Pré-requisitos e Instalação

1. Python 3.10+
2. Google Chrome instalado na máquina

Crie o ambiente virtual e instale as dependências:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Como Executar

1. Gere a planilha base com os dados a serem preenchidos:
```bash
python gerar_planilha.py
```

2. (Opcional) Abra o `config.yaml` e verifique as configurações. O parâmetro `submeter_formulario` define se o robô deve clicar no botão de envio (`true`) ou apenas preencher e validar (`false`).

3. Execute o robô:
```bash
python main.py
```

## Artefatos Gerados

Após a execução, os seguintes artefatos estarão disponíveis:

- **Logs de execução:** `logs/etapas.log` (rastreabilidade passo a passo).
- **Log de resultados:** `resultados/resultados.csv` (status OK/NOK por campo com timestamp).
- **Evidências:** `evidencias/` contendo o print da tela do formulário preenchido (ou da confirmação de envio) e o relatório de score (`relatorio.html` e `score_final.png`).

## Observações

- O código converte automaticamente datas no formato `DD/MM/AAAA` para o padrão aceito pelo formulário (`M/D/YYYY`).
- O score final é calculado com base na taxa de sucesso do preenchimento de todos os campos (campos OK / total de campos).
- O robô utiliza a instância local do Google Chrome para execução, garantindo compatibilidade com o sistema operacional.
