from utilitarios import Utilits
from processar_etl import Process_file

class EtlFasta:

    REGEX_VALIDATIONS = {
        'specimenCode_id': {
            'regex': r'[A-Za-z]{3}[0-9]{7}',
            'descricao': 'Specimen number'
        }
    }
        
    # ------------------------------------------------------------------------- #
    # PROCESSAMENTO DO FASTA                                                    #
    # ------------------------------------------------------------------------- #
    def to_process(self, pasta, pasta_output, text_log, btn_exec, root, codespeciescompleted):
        Utilits.append_log(text_log, "Procurando arquivos fasta (.fa, .fasta)...")
        
        name_file = 'fasta' \
        ''
        df_fasta = Process_file._read_inputfiles_fasta(pasta, text_log, name_file)

        if df_fasta.empty:
            Utilits.append_log(text_log, "Nenhum arquivo fasta encontrado.")

            btn_exec.configure(state='normal')
            return None

        # ---- ETAPA 1: TRANSFORMAÇÃO E LIMPEZA DOS DADOS ---- #
        columns_fasta = ['id', 'seq']

        df_fasta.columns = columns_fasta

        # ---- ETAPA 2: VALIDAÇÃO DO TAMANHO DA SEQUÊNCIA ---- #
        self._validate_seq_length(df_fasta)

        df_fasta['specimenCode_id'] = df_fasta['id'].str.split('_').str[1]

        df_fasta = df_fasta.drop(columns=['id'])

        df_filtered = df_fasta[~df_fasta['specimenCode_id'].str.contains('neg', case=False)]

        # ---- ETAPA 3: VALIDAÇÃO DE REGEX ---- #
        self._validate_regex(df_filtered)

        # ---- ETAPA 4: VERIFICAÇÃO DE DUPLICATAS ---- #
        column_name = 'specimenCode_id'
        process_file = Process_file()
        process_file.verify_duplicates(
            df_fasta,
            text_log,
            btn_exec,
            root, 
            name_file,
            column_name
        )

        # ---- ETAPA 5: VERIFICAÇÃO DE CONSISTÊNCIA COM O DEMFILE ---- #
        codespeciescompleted_fasta = set(df_fasta
        ['specimenCode_id'])

        process_file = Process_file()
        process_file.verify_set(
            demfile=codespeciescompleted,
            other=codespeciescompleted_fasta,
            modo="demfile_blast-fasta",
            name_file=name_file, 
            text_log=text_log, 
            btn_exec=btn_exec, 
            root=root,   
        )

        return df_fasta
    
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
        
    def _validate_seq_length(self, df, max_len=658):
        if (df['seq'].str.len() > max_len).any():
            raise ValueError(f"Existe sequência com mais de {max_len} caracteres.")