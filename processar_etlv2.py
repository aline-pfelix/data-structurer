import pandas as pd
from Bio import SeqIO
from utilitariosv2 import Utilits
from validacao_v2 import Validate
from tkinter import messagebox

class Process_file:    
    # Leitura dos arquivos excel
    @staticmethod
    def read_inputfiles_excel(pasta, text_log, name_file):
        dfs = []
        for inputfiles in pasta.iterdir():
            if not Validate.valid_file(inputfiles):
                continue

            if inputfiles.name.endswith(str(name_file)):
                Utilits.append_log(text_log, f'  - Lendo: {inputfiles.name}')
                dfs.append(pd.read_excel(inputfiles, dtype=str))
    
        if not dfs:
            return pd.DataFrame()

        return pd.concat(dfs, ignore_index=True)

    # Leitura dos arquivos csv
    @staticmethod
    def read_inputfiles_csv(pasta, text_log, name_file, sep, header=None):
        dfs = []
        for inputfiles in pasta.iterdir():
            if not Validate.valid_file(inputfiles):
                continue
            
            if inputfiles.name.endswith(str(name_file)):
                Utilits.append_log(text_log, f'  - Lendo: {inputfiles.name}')
                dfs.append(pd.read_csv(inputfiles, sep=sep, header=header, dtype=str, engine='python'))

        if not dfs:
            return pd.DataFrame()

        return pd.concat(dfs, ignore_index=True)

    # Leitura dos arquivos fasta
    @staticmethod
    def _read_inputfiles_fasta(pasta, text_log, name_file):
        seq_compl_all = []

        for fasta in pasta.iterdir():
                if not Validate.valid_file(fasta):
                    continue

                if fasta.name.endswith(('.fa', '.fasta')):
                    Utilits.append_log(text_log, f'  - Lendo: {fasta.name}')
                    file_fasta = SeqIO.parse(str(fasta), "fasta")
                    for s in file_fasta:
                        id_ = s.id
                        seq = str(s.seq)
                        seq_compl_all.append([id_, seq])
        
        dfs = pd.DataFrame(seq_compl_all)
        return dfs

    # Verificar duplicatas
    def verify_duplicates(self, df, text_log, btn_exec, root, name_file, column_name):
        df = df[df[column_name].notna()]

        dupli_df = df[df.duplicated(subset=[column_name], keep='first')]

        if dupli_df.empty:
            return

        exemplos = dupli_df[column_name].astype(str).unique()

        Utilits.abortar_execucao(
            mensagem=f"Foram encontrados códigos de espécime duplicados nos arquivos {name_file}.\n\n"
                    f"Exemplos: {', '.join(exemplos)}\n\n"
                    f"Os arquivos {name_file} precisam ser reavaliados. quanditade de duplicados {len(exemplos)}",
            titulo="Erro de validação",
            parent=root,
            log_widget=text_log,
            botao_exec=btn_exec
        )

        return 
    
    # Verifica os conjuntos de especimes
    def verify_set(
        self,
        demfile,
        other,
        modo,
        text_log,
        btn_exec,
        root,
        name_file,
        max_exemplos=5
    ):
        set_dem = set(demfile)
        set_other = set(other)

        miss_other = set_dem - set_other
        surpluses_no_other = set_other - set_dem

        # DEMFILE → CLUSTER
        if modo == "demfile_cluster":

            # excedentes do cluster NÃO quebram → só log
            if surpluses_no_other:
                Utilits.append_log(
                    text_log,
                    f"Cluster possui {len(surpluses_no_other)} códigos extras de espécimes "
                    f"que não estão no Demfile. Eles serão removidos."
                )
            return list(set_other & set_dem) 

        # DEMFILE ← BLAST / FASTA
        elif modo == "demfile_blast-fasta":

            if surpluses_no_other:
                exemplos = list(surpluses_no_other)[:max_exemplos]
                Utilits.abortar_execucao(
                    mensagem=(
                        f"Códigos de {name_file} ausentes no Demfile.\n\n"
                        f"({len(surpluses_no_other)} no total ). "
                        f"Exemplos: {', '.join(map(str, exemplos))}"
                    ),
                    titulo="Erro de validação",
                    parent=root,
                    log_widget=text_log,
                    botao_exec=btn_exec
                )

            return other  # nada a limpar


        # DEMFILE = MERGE
        elif modo == "demfile_merge":

            if miss_other or surpluses_no_other:
                exemplos_a = list(miss_other)[:max_exemplos]
                exemplos_b = list(surpluses_no_other)[:max_exemplos]

                Utilits.abortar_execucao(
                    mensagem=(
                        f"Inconsistência entre Demfile e {name_file}.\n\n"
                        f"Ausentes no Merge: {len(miss_other)}"
                        f"(ex: {', '.join(map(str, exemplos_a))})\n"
                        f"Excedentes no Merge: {len(surpluses_no_other)} "
                        f"(ex: {', '.join(map(str, exemplos_b))})"
                    ),
                    titulo="Erro de validação",
                    parent=root,
                    log_widget=text_log,
                    botao_exec=btn_exec
                )

            return other

        else:
            raise ValueError(f"Modo de validação desconhecido: {modo}")


    # Exportar .csv
    def export_csv (self, df, pasta_output, name_output):
        df.to_csv(str(pasta_output) + name_output, index=False)


    # Validar e exportar .csv concatenado 
    def export_csv_concat (df, pasta_output, name_output, text_log, btn_exec, root, column_name):
        
        dfs_all = pd.concat(df, ignore_index=True, sort=False)
        
        Process_file._verify_duplicates (dfs_all, text_log, btn_exec, root, name_output, column_name)       

        dfs_all.to_csv(str(pasta_output) + name_output, index=False)

    # Verificar duplicatas
    @staticmethod
    def _verify_duplicates(df, text_log, btn_exec, root, name_file, column_name):
        df = df[df[column_name].notna()]

        dupli_df = df[df.duplicated(subset=[column_name], keep='first')]

        if dupli_df.empty:
            return

        Utilits.abortar_execucao(
            mensagem=f"Foram encontrados códigos de espécime duplicados no arquivo {name_file} após concatenar mais de uma corrida.\n\n",
            titulo="Erro de validação",
            parent=root,
            log_widget=text_log,
            botao_exec=btn_exec
        )

        return 
    
    # Leitura dos arquivos csv
    @staticmethod
    def _read_inputfiles_csv(pasta, text_log, name_file, header=None):
        dfs = []
        for inputfiles in pasta.iterdir():
            if not Validate.valid_file(inputfiles):
                continue
            
            if inputfiles.name.endswith(str(name_file)):
                Utilits.append_log(text_log, f'  - Lendo: {inputfiles.name}')
                dfs.append(pd.read_csv(inputfiles, sep=',', header=header, dtype=str, engine='python'))

        if not dfs:
            return pd.DataFrame()

        return pd.concat(dfs, ignore_index=True)
