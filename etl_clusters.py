from utilitarios import Utilits
from processar_etl import Process_file

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

    # ------------------------------------------------------------------------- #
    # PROCESSAMENTO DOS CLUSTERS                                                #
    # ------------------------------------------------------------------------- #
    def to_process(self, pasta, pasta_output, text_log, btn_exec, root, codespeciescompleted):
        Utilits.append_log(text_log, "Procurando arquivos com sufixo '-ids' (lista de clusters)...")
        
        name_file = '-ids'

        sep = '\t'
        dfs_cluster = Process_file.read_inputfiles_csv(pasta, text_log, name_file, sep)

        if dfs_cluster.empty:
            Utilits.append_log(text_log, "Nenhum arquivo '-ids' encontrado.")

            btn_exec.configure(state='normal')
            return None
        
        # ---- ETAPA 1: TRANSFORMAÇÃO E LIMPEZA DOS DADOS ---- #
        columns_cluster = ['clusterCode', 'especime']

        dfs_cluster.columns = columns_cluster

        dfs_cluster['specimenCodeCluster'] = dfs_cluster['especime'].str.split('_').str[1]
        
        if 'especime' in dfs_cluster.columns:
            dfs_cluster = dfs_cluster.drop(columns=['especime'])

        df_filtered = dfs_cluster[~dfs_cluster['specimenCodeCluster'].str.contains('neg', case=False)]

        # ---- ETAPA 2: VALIDAÇÃO DE REGEX ---- #
        self._validate_regex(df_filtered)

        # ---- ETAPA 3: VERIFICAÇÃO DE DUPLICATAS ---- #
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

        # ---- ETAPA 4: VERIFICAÇÃO DE CONSISTÊNCIA COM O DEMFILE ---- #
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

        # ---- ETAPA 5: LIMPEZA DE EXCEDENTES ---- #
        dfs_cluster = dfs_cluster[dfs_cluster['specimenCodeCluster'].isin(list_clean)]

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