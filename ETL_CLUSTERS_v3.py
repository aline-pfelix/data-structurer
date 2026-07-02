from utilitariosv2 import Utilits
from validacao_v2 import Validate
from tkinter import messagebox
from processar_etlv2 import Process_file

class EtlClusters:

    REGEX_VALIDATIONS = {
        'specimenCodeCluster': {
            'regex': r'[A-Za-z]{3}[0-9]{7}',
            'descricao': 'Specimen number'
        },
        'clusterCode': {
        'regex': r'[A-Za-z]{3}[0-9]{7}',
        'descricao': 'Cluster number'
        }
    }

    def to_process(self, pasta, pasta_output, text_log, btn_exec, root, codespeciescompleted):
        Utilits.append_log(text_log, "Procurando arquivos com sufixo '-ids' (lista de clusters)...")
        
        name_file = '-ids'

        sep = '\t'
        dfs_cluster = Process_file.read_inputfiles_csv(pasta, text_log, name_file, sep)

        if dfs_cluster.empty:
            Utilits.append_log(text_log, "Nenhum arquivo '-ids' encontrado.")

            btn_exec.configure(state='normal')
            return None
        
        # Trasnformação e limpeza dos dados
        columns_cluster = ['clusterCode', 'especime']

        dfs_cluster.columns = columns_cluster

        dfs_cluster['specimenCodeCluster'] = dfs_cluster['especime'].str.split('_').str[1]
        
        if 'especime' in dfs_cluster.columns:
            dfs_cluster = dfs_cluster.drop(columns=['especime'])

        df_filtered = dfs_cluster[~dfs_cluster['specimenCodeCluster'].str.contains('neg', case=False)]

        # Valida regex
        self._validate_regex(df_filtered)

        # Verifica duplicatas
        column_name = 'specimenCodeCluster'
        process_file = Process_file()
        process_file.verify_duplicates(
            dfs_cluster,
            text_log,
            btn_exec,
            root, 
            name_file,
            column_name
        )

        # Verifica se demfile está em cluters 
        codespeciescompleted_cluster = set(dfs_cluster
        ['specimenCodeCluster'])

        process_file = Process_file()
        list_clean = process_file.verify_set(
            demfile=codespeciescompleted,
            other=codespeciescompleted_cluster,
            modo="demfile_cluster",
            name_file=name_file, 
            text_log=text_log, 
            btn_exec=btn_exec, 
            root=root, 
            
        )

        # Limpa excedente
        dfs_cluster = dfs_cluster[dfs_cluster['specimenCodeCluster'].isin(list_clean)]


        # # Exporta csv
        # name_output = '/clustercode_etl.csv'
        # Process_file.export_csv(self, dfs_cluster, pasta_output, name_output)

        return dfs_cluster


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
                    f'\n'
                    f'Números de indivíduos inválidos na lista de cluster\n'
                    f"{regra['descricao']} → {len(invalidos)} valores inválidos {invalidos}"
                )

        if erros:
            raise ValueError(
                "Erros de validação encontrados:\n" + "\n".join(erros)
            )