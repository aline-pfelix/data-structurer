import pandas as pd
from utilitarios import Utilits
from validacao import Validate
from processar_etl import Process_file

class EtlMergedDemfile:

    REGEX_VALIDATIONS = {
        'specimenCodeMerged': {
            'regex': r'[A-Za-z]{3}[0-9]{7}',
            'descricao': 'Specimen number'
        }
    }

    def to_process(self, pasta, pasta_output, text_log, btn_exec, root, codespeciescompleted):
        Utilits.append_log(text_log, "Procurando arquivos 'mergeddemfile'...")
        
        name_file = 'mergeddemfile'
        sep = ','
        dfs_merged_concat = Process_file.read_inputfiles_csv(pasta, text_log, name_file, sep)

        if dfs_merged_concat.empty:
            Utilits.append_log(text_log, "Nenhum arquivo mergeddemfile encontrado.")

            btn_exec.configure(state='normal')
            return None
        
        # Transformação e limpza dos dados
        columns_merged = ['0', '1', '2', 'primerF', 'primerR']

        dfs_merged_concat.columns = columns_merged

        dfs_merged_concat['specimenCodeMerged'] = dfs_merged_concat['0'].str.split('_').str[1]

        dfs_merged_concat = dfs_merged_concat.drop(columns=[c for c in ['0','1','2'] if c in dfs_merged_concat.columns])

        df_filtered = dfs_merged_concat[~dfs_merged_concat['specimenCodeMerged'].str.contains('neg', case=False)]

        # Valida regex
        self._validate_regex(df_filtered)

        # Verifica duplicatas
        column_name = 'specimenCodeMerged'
        process_file = Process_file()
        process_file.verify_duplicates(
            dfs_merged_concat,
            text_log,
            btn_exec,
            root, 
            name_file,
            column_name
        )

        # Verifica se é igual ao demfile
        codespeciescompleted_merged = set(dfs_merged_concat
        ['specimenCodeMerged'])

        process_file = Process_file()
        process_file.verify_set(
            demfile=codespeciescompleted,
            other=codespeciescompleted_merged,
            modo="demfile_merge",
            name_file=name_file, 
            text_log=text_log, 
            btn_exec=btn_exec, 
            root=root,  
        )

        
        # # Exporta csv
        # name_output = '/mergeddemfile_etl.csv'
        # Process_file.export_csv(self, dfs_merged_concat, pasta_output, name_output)

        return dfs_merged_concat
    
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