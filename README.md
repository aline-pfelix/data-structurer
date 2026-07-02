# Data Structurer

Aplicação desktop (Tkinter) para consolidar os arquivos gerados por uma corrida de
sequenciamento MinION (Demfile, Mergedemfile, Fasta, clusters, BLAST) em planilhas CSV
prontas para importação em banco de dados.

## Funcionalidades

- Seleção da pasta de saída de uma ou mais corridas MinION.
- Preenchimento de metadados da corrida (responsáveis, data do BLAST, ponto de amostragem,
  sucesso do sequenciamento).
- Edição de intervalos de placa (poços) associados a métodos de extração, fragmento,
  temperatura de pareamento do primer e ciclos de PCR.
- Execução de um pipeline de ETL que lê, valida e concatena os arquivos da corrida,
  exportando os seguintes CSVs em `etl_results/`:
  - `demfile_etl.csv`
  - `clustercode_etl.csv`
  - `mergeddemfile_etl.csv`
  - `filefasta_etl.csv`
  - `blast_etl.csv`
  - `infoextra_etl.csv`

## Estrutura do código

| Arquivo | Responsabilidade |
|---|---|
| `data_structurer_etl.py` | Ponto de entrada; monta a janela principal (GUI). |
| `main_etl.py` | Orquestra o pipeline de ETL (`DemfileController`). |
| `etl_demfile.py`, `etl_clusters.py`, `etl_mergeddemfile.py`, `etl_fasta.py`, `etl_blast.py`, `etl_infoextra.py` | Um ETL por tipo de arquivo de entrada. |
| `processar_etl.py` | Leitura/escrita de arquivos (Excel, CSV, FASTA) e concatenação. |
| `validacao.py` | Regras de validação de arquivos e dados. |
| `intervalos.py` | Lógica de mapeamento de intervalos de placa. |
| `placa_grid.py` | Widget de grid de placa (96 poços) da GUI. |
| `utilitarios.py` | Utilitários compartilhados (log, placeholders, abort). |

## Requisitos

- Python 3.10+ (testado com o ambiente empacotado em `venv_etl`, Python 3.11)
- Windows (usa `tkinter.iconbitmap` com um `.ico`; as demais dependências são multiplataforma)

## Instalação

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
python data_structurer_etl.py
```

## Gerando o executável (Windows)

```bash
pip install -r requirements-dev.txt
pyinstaller Data_Structurer_v3.0.0.spec
```

O executável é gerado em `dist/`.

## Autoria

