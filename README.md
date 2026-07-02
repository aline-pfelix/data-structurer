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

## Instalador (uso direto, sem programar)

Se você só quer **usar** o programa no Windows — sem mexer no código, sem instalar
Python — use o instalador pronto, não o código-fonte:

```
D:\Workspace\Ferramentas_dev\Instaladores\Instalador_DataStructurer\Data Structurer installer 3.0.0.exe
```

É só rodar o `.exe`, seguir o assistente e o programa fica instalado com ícone na área
de trabalho (opcional). Use as instruções de "Instalação" e "Uso" mais abaixo apenas se
você for **desenvolver ou modificar** o código.

> **Sobre a versão atual do instalador (3.0.0):** ela foi gerada a partir do código-fonte
> de antes da reorganização deste repositório (renomeação de módulos, remoção de código
> morto, padronização de comentários — ver [Histórico de mudanças](#histórico-de-mudanças-recentes)
> abaixo). Nenhuma dessas mudanças alterou o comportamento do programa, então o
> instalador 3.0.0 continua funcionando normalmente. Ainda assim, o ideal é gerar uma
> nova versão do instalador a partir do código já reorganizado (veja
> [Gerando um novo instalador](#gerando-um-novo-instalador) abaixo) antes da próxima
> distribuição, porque o script `.iss` usado para gerar os instaladores antigos aponta
> para o caminho de pasta anterior do projeto (`ETL_Database_Biodossel_Bioinsecta`), que
> não existe mais — ele precisa ser atualizado para o caminho atual (`datastructurer`)
> antes de conseguir gerar um novo instalador.

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

## Gerando um novo instalador

Duas etapas: primeiro empacotar o `.exe` com PyInstaller, depois gerar o instalador com
Inno Setup.

1. **Empacotar o `.exe`:**

   ```bash
   pip install -r requirements-dev.txt
   pyinstaller Data_Structurer_v3.0.0.spec
   ```

   O executável e o `Borboleta.ico` são gerados em `dist/`.

2. **Gerar o instalador com Inno Setup:** abra
   `D:\Workspace\Ferramentas_dev\Instaladores\Instalador_DataStructurer\sript_data_structure_v106.iss`
   no Inno Setup e compile. **Atenção:** esse script ainda referencia o caminho antigo do
   projeto (`D:\Workspace\Ferramentas_dev\scripts\ETL_Database_Biodossel_Bioinsecta`), que
   não existe mais desde a reorganização do repositório. Antes de compilar, atualize as
   linhas `Source:` e `SetupIconFile` para apontar para este repositório
   (`D:\Workspace\Ferramentas_dev\scripts\datastructurer\dist\...`), e ajuste
   `MyAppVersion`/`OutputBaseFilename` para a nova versão.

## Histórico de mudanças recentes

Reorganização do projeto para publicação no GitHub (código-fonte apenas — sem mudança de
comportamento do programa):

- Adicionados `.gitignore`, `LICENSE` (MIT), `README.md`, `requirements.txt` e
  `requirements-dev.txt`; removidos os `.spec` de versões antigas do PyInstaller (mantido
  só o `v3.0.0`).
- Removido `guiv2.py` (código morto — versão antiga da UI de intervalos, substituída pelo
  `PlacaGrid`).
- Módulos renomeados para remover sufixos de versão do nome do arquivo (ex:
  `ETL_FASTA_v4.py` → `etl_fasta.py`, `main_etlv4.py` → `main_etl.py`,
  `utilitariosv2.py` → `utilitarios.py`); histórico de versão agora vive no `git`, não no
  nome do arquivo.
- Comentários de seção padronizados em blocos de "Título" (`# --- # / # TEXTO # / # --- #`)
  e "Subtítulo" (`# ---- ETAPA N: TEXTO ---- #`) nos métodos principais do pipeline de ETL.
- Removidos ~270 linhas de código morto: blocos comentados de implementações antigas,
  imports e variáveis locais não usados, um trecho inalcançável em `intervalos.py` e
  métodos nunca chamados (`Process_file.export_csv`, `Process_file._read_inputfiles_csv`,
  `Utilits.show_error`, `Validate.validate_regex`, `PlacaGrid.get_data`).

## Autoria

