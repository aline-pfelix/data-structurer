from pathlib import Path
import pandas as pd
import os
import traceback
from tkinter import messagebox
from utilitarios import Utilits


# Importando as novas classes
from etl_demfile import EtlDemfile
from etl_clusters import EtlClusters
from etl_mergeddemfile import EtlMergedDemfile
from etl_fasta import EtlFasta
from etl_blast import EtlBlast
from etl_infoextra import EtlInfoExtra
from utilitarios import AbortarExecucao
from processar_etl import Process_file

dfs_demfile_concat_all = []
dfs_cluster_all = []
dfs_merged_concat_all = []
df_fasta_all = []
dfs_blasted_concat_all = []
dfs_infoextra_all = []
class DemfileController:
    global dfs_demfile_concat_all
    global dfs_cluster_concat_all
    global dfs_mergedemfile_concat_all
    global dfs_fasta_concat_all
    global dfs_blasted_concat_all
    global dfs_infoextra_concat_all

    # ------------------------------------------------------------------------- #
    # EXECUÇÃO DO PIPELINE                                                      #
    # ------------------------------------------------------------------------- #
    @staticmethod
    def execute_etl_multiple(corridas_list, text_log, btn_exec, root):
        try:
            total = len(corridas_list)
            for i, corrida in enumerate(corridas_list, 1):
                caminho_pasta = corrida['caminho']
                parametros = corrida['parametros']
                intervals_map = corrida['intervalos']

                Utilits.append_log(text_log, "------------------------------------------------------------------------------")
                Utilits.append_log(text_log, f"Iniciando corrida {i}/{total}: {caminho_pasta}")

                pasta = Path(caminho_pasta)
                pasta_output = Path(pasta).parent / "etl_results"

                if not os.path.exists(pasta_output):
                    os.mkdir(pasta_output)
                    Utilits.append_log(text_log, f"Pasta etl_results criada: {pasta_output}")
                # else:
                #     # Utilits.append_log(text_log, f"Pasta etl_results já existe, resultados serão sobrescritos.")
                #     Utilits.append_log(text_log, 'Pasta "etl_results" já existe no destino. Abortando.')
                #     Utilits.abortar_execucao(mensagem= 'A pasta "etl_results" já existe no destino.')
                #     btn_exec.configure(state='normal')

                # ---- ETAPA 1: PROCESSAR DEMFILE ---- #
                etl_demfile = EtlDemfile()
                dfs_demfile_concat, codespeciescompleted = etl_demfile.to_process(
                    pasta, pasta_output, text_log, btn_exec, root,
                )
                dfs_demfile_concat_all.append(dfs_demfile_concat)

                if dfs_demfile_concat is None:
                    Utilits.append_log(text_log, f"Erro: DEMFILE não processado para a corrida {i}. Abortando.")
                    Utilits.abortar_execucao(mensagem= 'Abortando')

                # ---- ETAPA 2: PROCESSAR CLUSTERS ---- #
                etl_clusters = EtlClusters()
                dfs_cluster = etl_clusters.to_process(
                    pasta, pasta_output, text_log, btn_exec, root, codespeciescompleted,
                )
                dfs_cluster_all.append(dfs_cluster)

                if dfs_cluster is None:
                    Utilits.append_log(text_log, f"Erro: CLUSTERS não processado para a corrida {i}. Continuando.")
                    Utilits.abortar_execucao(mensagem= 'Abortando')

                # ---- ETAPA 3: PROCESSAR MERGEDDEMFILE ---- #
                etl_merged = EtlMergedDemfile()
                dfs_merged_concat = etl_merged.to_process(
                    pasta, pasta_output, text_log, btn_exec, root, codespeciescompleted, 
                )
                dfs_merged_concat_all.append(dfs_merged_concat)

                if dfs_merged_concat is None:
                    Utilits.append_log(text_log, f"Erro: MERGEDDEMFILE não processado para a corrida {i}. Continuando.")
                    Utilits.abortar_execucao(mensagem= 'Abortando')

                # ---- ETAPA 4: PROCESSAR FASTA ---- #
                etl_fasta = EtlFasta()
                df_fasta = etl_fasta.to_process(
                    pasta, pasta_output, text_log, btn_exec, root, codespeciescompleted,
                )
                df_fasta_all.append(df_fasta)

                if df_fasta is None:
                    Utilits.append_log(text_log, f"Erro: FASTA não processado para a corrida {i}. Continuando.")
                    Utilits.abortar_execucao(mensagem= 'Abortando')

                # ---- ETAPA 5: PROCESSAR BLAST ---- #
                etl_blast = EtlBlast()
                dfs_blasted_concat = etl_blast.to_process(
                    pasta, pasta_output, text_log, btn_exec, root,
                    parametros.get('datablast'), codespeciescompleted, 
                )
                dfs_blasted_concat_all.append(dfs_blasted_concat)

                if dfs_blasted_concat is None:
                    Utilits.append_log(text_log, f"Erro: BLAST não processado para a corrida {i}. Continuando.")
                    Utilits.abortar_execucao(mensagem= 'Abortando')

                # ---- ETAPA 6: PROCESSAR INFOEXTRA ---- #
                etl_info = EtlInfoExtra()
                dfs_infoextra = etl_info.to_process(
                    dfs_demfile_concat, parametros, intervals_map,
                    pasta_output, text_log, btn_exec, root, 
                )

                dfs_infoextra_all.append(dfs_infoextra)

                Utilits.append_log(text_log, f"Corrida {i}/{total} concluída.\n")
                
            if i > 1:
                Utilits.append_log(text_log, f"Dados estão sendo concatenados.\n")

            Process_file.export_csv_concat(dfs_demfile_concat_all, pasta_output, name_output='/demfile_etl.csv', column_name= 'specimenCode', text_log=text_log, btn_exec=btn_exec, root=root)
            Process_file.export_csv_concat(dfs_cluster_all, pasta_output, name_output='/clustercode_etl.csv', column_name= 'specimenCodeCluster', text_log=text_log, btn_exec=btn_exec, root=root)
            Process_file.export_csv_concat(dfs_merged_concat_all, pasta_output, name_output='/mergeddemfile_etl.csv', column_name= 'specimenCodeMerged', text_log=text_log, btn_exec=btn_exec, root=root)
            Process_file.export_csv_concat(df_fasta_all, pasta_output, name_output='/filefasta_etl.csv', column_name= 'specimenCode_id', text_log=text_log, btn_exec=btn_exec, root=root)
            Process_file.export_csv_concat(dfs_blasted_concat_all, pasta_output, name_output='/blast_etl.csv', column_name= 'specimenCodeBlast', text_log=text_log, btn_exec=btn_exec, root=root)
            Process_file.export_csv_concat(dfs_infoextra_all, pasta_output, name_output='/infoextra_etl.csv', column_name= 'specimenCode', text_log=text_log, btn_exec=btn_exec, root=root)

            # Finalização
            Utilits.append_log(text_log, "------------------------------------------------------------------------------")
            Utilits.append_log(text_log, f"Processamento finalizado para {total} corrida(s).")
            messagebox.showinfo("Concluído", f"Processamento finalizado para {total} corrida(s).")

        except Exception as e:
            Utilits.append_log(text_log, "Erro inesperado durante a execução:")
            Utilits.append_log(text_log, str(e))
            Utilits.append_log(text_log, traceback.format_exc())
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado:\n{str(e)}")
        finally:
            btn_exec.configure(state='normal')

