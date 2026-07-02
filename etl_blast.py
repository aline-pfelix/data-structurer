from utilitarios import Utilits
from processar_etl import Process_file

class EtlBlast:

    REGEX_VALIDATIONS = {
        'specimenCodeBlast': {
            'regex': r'[A-Za-z]{3}[0-9]{7}',
            'descricao': 'Specimen number'
        }
    }

    # ------------------------------------------------------------------------- #
    # PROCESSAMENTO DO BLAST                                                    #
    # ------------------------------------------------------------------------- #
    def to_process(self, pasta, pasta_output, text_log, btn_exec, root, datablast, codespeciescompleted):
        Utilits.append_log(text_log, "Procurando arquivos .tsv (output do ReadsIdentifier)...")
        
        name_file = '.tsv'
        sep = '\t'
        dfs_blasted_concat = Process_file.read_inputfiles_csv(pasta, text_log, name_file, sep)

        if dfs_blasted_concat.empty:
            Utilits.append_log(text_log, "Nenhum arquivo .tsv encontrado.")

            btn_exec.configure(state='normal')
            return None

        # ---- ETAPA 1: TRANSFORMAÇÃO E LIMPEZA DOS DADOS ---- #
        columns_blasted = ['id_blasted', 'blastSimilarity', 'blastSpecies', 'blastGenus','blastFamily', 'blastOrder', 'class', 'phylum', 'kingdom', '0']
        
        dfs_blasted_concat.columns = columns_blasted

        dfs_blasted_concat['specimenCodeBlast'] = dfs_blasted_concat['id_blasted'].str.split('_').str[1]
        
        if 'id_blasted' in dfs_blasted_concat.columns:
            dfs_blasted_concat = dfs_blasted_concat.drop(columns=['id_blasted', '0'], errors='ignore')
        
        df_filtered = dfs_blasted_concat[~dfs_blasted_concat['specimenCodeBlast'].str.contains('neg', case=False)]

        # ---- ETAPA 2: VALIDAÇÃO DE REGEX ---- #
        self._validate_regex(df_filtered)

        # ---- ETAPA 3: RECEBER PARÂMETRO DA INTERFACE (DATA DO BLAST) ---- #
        dfs_blasted_concat['blastIdDate'] = datablast

        # ---- ETAPA 4: VERIFICAÇÃO DE DUPLICATAS ---- #
        column_name = 'specimenCodeBlast'
        process_file = Process_file()
        process_file.verify_duplicates(
            dfs_blasted_concat,
            text_log,
            btn_exec,
            root, 
            name_file,
            column_name
        )

        # ---- ETAPA 5: VERIFICAÇÃO DE CONSISTÊNCIA COM O DEMFILE ---- #
        codespeciescompleted_blasted = set(dfs_blasted_concat
        ['specimenCodeBlast'])

        process_file = Process_file()
        process_file.verify_set(
            demfile=codespeciescompleted,
            other=codespeciescompleted_blasted,
            modo="demfile_blast-fasta",
            name_file=name_file, 
            text_log=text_log, 
            btn_exec=btn_exec, 
            root=root, 
            
        )

        return dfs_blasted_concat
    
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