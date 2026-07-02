import pandas as pd
from utilitariosv2 import Utilits
from validacao_v2 import Validate
from processar_etlv2 import Process_file
from tkinter import messagebox



class EtlDemfile:
    
    REGEX_VALIDATIONS = {
        'Researcher-name': {
            'regex': r'[A-Za-z]{1,5}',
            'descricao': 'Researcher-name'
        },
        'Specimen-code-prefix': {
            'regex': r'[A-Za-z]{3}',
            'descricao': 'Specimen prefix'
        },
        'Specimen-code-number': {
            'regex': r'[0-9]{7}',
            'descricao': 'Specimen number'
        },
        'Plate-ID': {
            'regex': r'[A-Za-z]{3}[0-9]{3}',
            'descricao': 'Plate-ID'
        },
        'SampleID': {
            'regex': r'[A-Za-z]{5}[0-9]{4}',
            'descricao': 'SampleID'
        }
    }

    # REGEX_VALIDATIONS_LOCAL = {
    #     'Locality': {
    #         'regex': r'[A-Za-z]{1,20}-[A-Za-z]{1,30}-[A-Za-z]{1,50}-[A-Za-z0-9]{1,30}',
    #         'descricao': 'Locality'
    #     }
    # }

    def to_process(self, pasta, pasta_output, text_log, btn_exec, root):
        Utilits.append_log(text_log, "Procurando arquivos demfile.xlsx...")

        name_file = 'demfile.xlsx'

        dfs_demfile_concat = Process_file.read_inputfiles_excel(pasta=pasta, text_log=text_log, name_file=name_file)

        if dfs_demfile_concat.empty:
            Utilits.append_log(text_log, "Nenhum arquivo demfile.xlsx encontrado.")

            btn_exec.configure(state='normal')
            return None, None

        df_filtered = dfs_demfile_concat[~dfs_demfile_concat['Specimen-code-prefix'].str.contains('neg', case=False)]

        self._validate_regex(df_filtered)

        aviso_local = self.validar_local(df_filtered)

        if aviso_local:
            mensagem = (
                f"{aviso_local['mensagem']}\n\n"
                f"Registros afetados: {aviso_local['quantidade']}\n"
                f"Exemplos:\n- " + "\n- ".join(aviso_local['exemplos'])
            )

            continuar = messagebox.askyesno(
                title="Aviso de estrutura",
                message=mensagem,
                parent=root
            )

            if not continuar:
                Utilits.append_log(text_log, "⛔ Execução cancelada pelo usuário.")
                btn_exec.configure(state="normal")
                return None, None
            
            
        dfs_demfile_concat = self.transform_data(dfs_demfile_concat)

        dfs_demfile_concat = self._formatar_clean_datas(dfs_demfile_concat)

        #Lista para verificar duplicatas
        codespeciescompleted = dfs_demfile_concat['specimenCode'].tolist()
        #coluna para verficar duplicatas
        column_name = 'specimenCode'
        process_file = Process_file()
        process_file.verify_duplicates(
            df=dfs_demfile_concat,
            text_log=text_log,
            btn_exec=btn_exec,
            root=root, 
            name_file=name_file,
            column_name=column_name
        )

        # name_output = '/demfile_etl.csv'
        # Process_file.export_csv(self, dfs_demfile_concat, pasta_output, name_output)

        return dfs_demfile_concat, codespeciescompleted

    def _validate_regex(self, df):
        erros = []

        for coluna, regra in self.REGEX_VALIDATIONS.items():

            if coluna not in df.columns:
                erros.append(f"Coluna ausente: {coluna}")

                continue
            
            mask_valido = (
                df[coluna]
                .astype(str)
                .str.fullmatch(regra['regex'])
            )

            invalidos = df.loc[~mask_valido | df[coluna].isna(), [coluna]]

            if not invalidos.empty:
                erros.append(
                    f"{regra['descricao']} → {len(invalidos)} valores inválidos"
                )

        if erros:
            raise ValueError(
                "Erros de validação encontrados:\n" + "\n".join(erros)
            )

    # Valida a localização
    def validar_local(self, df):

        aviso = self._validate_local_parts(df)

        if aviso:
            return aviso  

        # self._validate_regex_local(df)

        return None
    
    def _validate_local_parts(self, df, coluna='Locality', max_hifens=5):

        mask_invalido = (
            df[coluna]
            .astype(str)
            .str.count('-') > max_hifens
        )

        if not mask_invalido.any():
            return None

        exemplos = (
            df.loc[mask_invalido, coluna]
            .dropna()
            .unique()[:5]
            .tolist()
        )

        return {
            'mensagem': (
                f"Atenção: conteúdo da coluna {coluna} nos arquivos demfile.xlsx possuem estrutura fora do esperado!\n"
                "Estrutura esperada:\n"
                "country-state-city-reserve-locality-samplingMethod\n\n"
                "A informação NÃO será perdida. Deseja continuar?"
            ),
            'quantidade': int(mask_invalido.sum()),
            'exemplos': exemplos
        }

    # def _validate_regex_local(self, df):
    #     erros = []

    #     for coluna, regra in self.REGEX_VALIDATIONS_LOCAL.items():

    #         if coluna not in df.columns:
    #             erros.append(f"Coluna ausente: {coluna}")

    #             continue

    #         mask_valido = (
    #             df[coluna]
    #             .astype(str)
    #             .str.fullmatch(regra['regex'])
    #         )

    #         invalidos = df.loc[~mask_valido | df[coluna].isna(), [coluna]]

    #         if not invalidos.empty:
    #             erros.append(
    #                 f"{regra['descricao']} → {len(invalidos)} valores inválidos"
    #                 f'{invalidos}'
    #             )

    #     if erros:
    #         raise ValueError(
    #             "Erros de validação encontrados:\n" + "\n".join(erros)
    #         )

    # Transformações e limpeza dos dados
    def transform_data(self, df):

        # Transformação para specimencode
        df['specimenCode'] = df.get('Specimen-code-prefix') + df.get('Specimen-code-number')

        # Transformação para sampleid
        sampleid = df['SampleID'].str[-4:]
        df['stratum'] = sampleid.str[:2]
        
        # Transformação para locality
        df['country']           = df['Locality'].str.split('-').str[0]
        df['state']             = df['Locality'].str.split('-').str[1]
        df['city']              = df['Locality'].str.split('-').str[2]
        df['reserve']           = df['Locality'].str.split('-').str[3]
        df['locality']          = df['Locality'].str.split('-').str[4:-1].str.join('-')
        df['samplingMethod']    = df['Locality'].str.split('-').str[-1]

        # Renomeação das colunas
        df.rename(columns={
            'Position':'position', 
            'SampleID': 'sampleCode', 
            'Collection Date': 'date',
            'Plate-ID': 'plateRackCode', 
            'F-primer-tag': 'tagF', 
            'R-primer-tag': 'tagR',
            'Researcher-name': 'responsible'
        }, inplace=True)

        # Tratamento de controles negativos
        mask_neg = df['specimenCode'].astype(str).str.contains('neg', case=False, na=False)
        df.loc[mask_neg, 'sampleCode'] = '#########'

        # Remover colunas desnecessárias
        cols_to_drop = ['Specimen-code-prefix', 
                        'Specimen-code-number', 
                        'Locality',
                        'F-primer-tag-ID', 
                        'R-primer-tag-ID', 
                        'R-primer-plate']
        cols_existing = [c for c in cols_to_drop if c in df.columns]
        if cols_existing:
            df = df.drop(columns=cols_existing)

        return df

    def _formatar_clean_datas(self, df, text_log=None, btn_exec=None, root=None):
        # Linhas NEG não são convertidas
        mask_neg = df['specimenCode'].str.contains(
            'neg',
            case=False,
            na=False
        )

        replacements = {
            'Fev': 'Feb',
            'Abr': 'Apr',
            'Mai': 'May',
            'Ago': 'Aug',
            'Set': 'Sep',
            'Out': 'Oct',
            'Dez': 'Dec'
        }

        # Garante string sem gerar "nan"
        df['date'] = df['date'].where(
            df['date'].notna(),
            ''
        ).astype(str).str.strip()

        # substituições sem case sensitive
        for pt, en in replacements.items():
            df.loc[~mask_neg, 'date'] = (
                df.loc[~mask_neg, 'date']
                .str.replace(
                    pt,
                    en,
                    case=False,   # <- remove case sensitivity
                    regex=False
                )
            )

        # valida conversão
        date_parsed = pd.to_datetime(
            df.loc[~mask_neg, 'date'],
            format='%d%b%Y',
            errors='coerce'
        )

        invalidos = df.loc[
            ~mask_neg &
            date_parsed.isna() &
            (df['date'].str.strip() != '')
        ]

        if not invalidos.empty:
            Utilits.abortar_execucao(
                mensagem=(
                    "Erro ao converter datas:\n\n"
                    + invalidos[
                        ['specimenCode','date']
                    ].to_string(index=False)
                ),
                parent=root,
                log_widget=text_log,
                botao_exec=btn_exec
            )
            return None

        # atualiza apenas se tudo válido
        df.loc[~mask_neg, 'date'] = (
            date_parsed.dt.strftime('%Y-%m-%d')
        )

        return df

    # def _formatar_clean_datas(self, df, text_log=None, btn_exec=None, root=None):
    #     # Linhas NEG não são convertidas
    #     mask_neg = df['specimenCode'].str.contains('neg', case=False, na=False)

    #     replacements = {
    #         'Fev': 'Feb', 'Abr': 'Apr', 'Mai': 'May',
    #         'Ago': 'Aug', 'Set': 'Sep', 'Out': 'Oct', 'Dez': 'Dec'
    #     }

    #     # Garante string sem gerar "nan"
    #     df['date'] = df['date'].where(df['date'].notna(), '')

    #     for pt, en in replacements.items():
    #         df.loc[~mask_neg, 'date'] = df.loc[~mask_neg, 'date'].str.replace(pt, en)

    #     # Converte apenas para validar
    #     date_parsed = pd.to_datetime(
    #         df.loc[~mask_neg, 'date'],
    #         format='%d%b%Y',
    #         errors='coerce'
    #     )

    #     invalidos = df.loc[
    #         ~mask_neg &
    #         date_parsed.isna() &
    #         (df['date'].str.strip() != '')
    #     ]

    #     if not invalidos.empty:
    #         Utilits.abortar_execucao(
    #             mensagem=(
    #                 "Erro ao converter datas:\n\n"
    #                 + invalidos[['specimenCode', 'date']].to_string(index=False)
    #             ),
    #             parent=root,
    #             log_widget=text_log,
    #             botao_exec=btn_exec
    #         )
    #         return None  # ⬅️ ENCERRA AQUI SEM TRAVAR

    #     # Atualiza date só se tudo estiver válido
    #     df.loc[~mask_neg, 'date'] = date_parsed.dt.strftime('%Y-%m-%d')

    #     return df
