# Data Structurer

Aplicação desktop (Tkinter) para consolidar os arquivos gerados por uma corrida de sequenciamento MinION (Demfile, Mergedemfile, Fasta, clusters, BLAST) em planilhas CSV prontas para importação em banco de dados.

## Funcionalidades

- Seleção da pasta de saída de uma ou mais corridas MinION.
- Preenchimento de metadados da corrida (responsáveis, data do BLAST, ponto de amostragem, sucesso do sequenciamento).
- Edição de intervalos de placa (poços) associados a métodos de extração, fragmento, temperatura de pareamento do primer e ciclos de PCR.
- Execução de um pipeline de ETL que lê, valida e concatena os arquivos da corrida, exportando CSVs prontos para importação em banco de dados.

## Estrutura de dados esperada

Ao selecionar a pasta de uma corrida, o programa procura, dentro dela, arquivos de cinco tipos diferentes — todos os arquivos da pasta que casam com cada padrão são lidos e concatenados. Evite subpastas: elas não são varridas.

| Tipo | Como é identificado | Formato |
|---|---|---|
| Demfile | nome termina em `demfile.xlsx` | Excel (`.xlsx`) |
| Mergedemfile | nome termina em `mergeddemfile` | CSV separado por vírgula |
| Fasta | extensão `.fa` ou `.fasta` | FASTA |
| Cluster list | nome termina em `-ids` (sem extensão) | texto separado por tabulação |
| BLAST | extensão `.tsv` (output do ReadsIdentifier) | TSV |

### Colunas obrigatórias do Demfile

| Coluna | Formato esperado | Exemplo |
|---|---|---|
| `Researcher-name` | 1 a 5 letras | `AF` |
| `Specimen-code-prefix` | 3 letras | `BIN` |
| `Specimen-code-number` | 7 dígitos | `0001234` |
| `Plate-ID` | 3 letras + 3 dígitos | `BIN001` |
| `SampleID` | 5 letras + 4 dígitos | `BINPL0001` |
| `Locality` | `country-state-city-reserve-locality-samplingMethod` | — |

O programa concatena `Specimen-code-prefix` + `Specimen-code-number` para formar o `specimenCode` usado para casar as linhas entre os cinco tipos de arquivo. Linhas cujo prefixo contém `neg` (controles negativos) são tratadas à parte e não entram nas validações de duplicidade/consistência entre arquivos.

## Download

Para apenas usar o programa (sem mexer no código), baixe o instalador mais recente na aba [Releases](https://github.com/aline-pfelix/datastructurer/releases/latest) e rode o `.exe`. As seções abaixo são voltadas para desenvolvimento a partir do código-fonte.

## Estrutura do projeto

```
datastructurer/
├── data_structurer_etl.py    # ponto de entrada; monta a janela principal (GUI)
├── main_etl.py                # orquestra o pipeline de ETL (DemfileController)
├── etl_demfile.py              # ETL do Demfile
├── etl_clusters.py             # ETL da lista de clusters
├── etl_mergeddemfile.py        # ETL do Mergedemfile
├── etl_fasta.py                # ETL do Fasta
├── etl_blast.py                # ETL do output do BLAST
├── etl_infoextra.py            # ETL das colunas extra (intervalos de placa, coordenadas)
├── processar_etl.py            # leitura/escrita de arquivos (Excel, CSV, FASTA) e concatenação
├── validacao.py                 # regras de validação de arquivos e dados
├── intervalos.py                # lógica de mapeamento de intervalos de placa
├── placa_grid.py                # widget de grid de placa (96 poços) da GUI
├── utilitarios.py               # utilitários compartilhados (log, placeholders, abort)
├── Borboleta.ico                 # ícone do app
├── Data_Structurer_v3.0.1.spec   # build do executável com PyInstaller
├── requirements.txt
└── requirements-dev.txt
```

## Instalação

Requer Python 3.10+ e Windows (usa `tkinter.iconbitmap` com um `.ico`; as demais dependências são multiplataforma).

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
python data_structurer_etl.py
```

1. Selecione a pasta com os arquivos de uma corrida MinION (veja [Estrutura de dados esperada](#estrutura-de-dados-esperada)).
2. Preencha os metadados da corrida e o ponto de amostragem.
3. Preencha os intervalos de placa (extração, fragmento, temperatura, ciclos).
4. Clique em **Adicionar mais uma corrida** para processar várias corridas juntas, ou **Executar ETL** para rodar.
5. Os CSVs resultantes (`demfile_etl.csv`, `clustercode_etl.csv`, `mergeddemfile_etl.csv`, `filefasta_etl.csv`, `blast_etl.csv`, `infoextra_etl.csv`) são gerados em uma pasta `etl_results/` criada ao lado da pasta de entrada.

## Gerando o executável

```bash
pip install -r requirements-dev.txt
pyinstaller Data_Structurer_v3.0.1.spec
```

O executável e o `Borboleta.ico` são gerados em `dist/`. O instalador publicado nas Releases é gerado separadamente a partir desse executável e enviado manualmente.

## Observações

- O app é Windows-only (usa `tkinter.iconbitmap` com `.ico` e caminhos de instalação do Windows).
- A licença (MIT) e a autoria estão no arquivo `LICENSE`.
