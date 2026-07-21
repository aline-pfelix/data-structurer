import pandas as pd
from utilitarios import Utilits
from intervalos import Intervals
from validacao import Validate

class EtlInfoExtra:
    # ------------------------------------------------------------------------- #
    # PROCESSAMENTO DO INFOEXTRA                                                #
    # ------------------------------------------------------------------------- #
    def to_process(self, dfs_demfile_concat, parametros, intervals_map, pasta_output, text_log, btn_exec, root):
        if dfs_demfile_concat is None:
            Utilits.abortar_execucao(
                mensagem='Erro: demfile não processado, não é possível gerar infoextra.',
                titulo="Erro de validação",
                parent=root,
                log_widget=text_log,
                botao_exec=btn_exec
            )
            return

        df_infoextra = dfs_demfile_concat[['specimenCode', 'plateRackCode', 'sampleCode']].copy()

        # ---- ETAPA 1: PREENCHER COLUNAS COM OS PARÂMETROS BÁSICOS ---- #
        df_infoextra['minionRun'] = parametros.get('minionrun')
        df_infoextra['sequenceResp'] = parametros.get('respseq')
        df_infoextra['collector'] = parametros.get('respcol')
        df_infoextra['sequenceSuccess'] = parametros.get('sucesseq')

        for c in ['extract', 'frag', 'temp', 'cycle']:
            if c not in df_infoextra.columns:
                df_infoextra[c] = pd.NA

        # ---- ETAPA 2: APLICAR INTERVALOS / GRADE ---- #
        if any(intervals_map.values()):
            Utilits.append_log(text_log, "Aplicando informações informadas pelo usuário nas colunas (extract/frag/temp/cycle)...")

            for col, data in intervals_map.items():
                modo = data.get("modo")

                if modo == "todas":
                    Intervals.apply_to_all_plates(df_infoextra, col, data["valor"], log_widget=text_log)

                elif modo == "grade":
                    # Valida se todos os Plate-IDs da grade existem no demfile
                    plate_ids_validos = set(df_infoextra['plateRackCode'].dropna().unique())
                    try:
                        Intervals.validate_plate_ids(data["linhas"], plate_ids_validos, col)
                    except ValueError as e:
                        Utilits.abortar_execucao(
                            mensagem=str(e),
                            titulo="Erro de validação",
                            parent=root,
                            log_widget=text_log,
                            botao_exec=btn_exec
                        )
                        return
                    df_infoextra = Intervals.apply_grade_to_df(df_infoextra, col, data["linhas"], log_widget=text_log)

                else:
                    Utilits.abortar_execucao(
                        mensagem=f"Modo inválido detectado na coluna '{col}': '{modo}'.",
                        titulo="Erro de validação",
                        parent=root,
                        log_widget=text_log,
                        botao_exec=btn_exec
                    )
                    return
        else:
            Utilits.abortar_execucao(
                mensagem="Nenhuma informação de placa foi informada. Preencha os campos ou selecione 'aplicar para todas as placas'.",
                titulo="Erro de validação",
                parent=root,
                log_widget=text_log,
                botao_exec=btn_exec
            )
            return
        
        # ---- ETAPA 3: COORDENADAS ---- #
        coord_index = parametros.get('coord_index')
        if coord_index == 1:
            df_infoextra['coordinates'] = "-2.924722, -60.861389"
            df_infoextra['altitude'] = "73"
        elif coord_index == 2:
            df_infoextra['coordinates'] = "-2.58833333, -60.11611111"
            df_infoextra['altitude'] = "124"
        elif coord_index == 3:
            df_infoextra['coordinates'] = "-3.58194444, -59.82888889"
            df_infoextra['altitude'] = "46"
        elif coord_index == 4:
            df_infoextra['coordinates']= parametros.get('coord_geo')
            df_infoextra['altitude']  = parametros.get('altitude')
        else:
            Utilits.abortar_execucao(
                mensagem="Opção de ponto de amostragem inválida. Nenhuma coordenada e ou altitude foi adicionada.",
                titulo="Erro de validação",
                parent=root,
                log_widget=text_log,
                botao_exec=btn_exec
            )
            return

        # ---- ETAPA 4: LIMPAR CONTROLES NEGATIVOS ---- #
        mask_neg = df_infoextra['specimenCode'].astype(str).str.contains('neg', case=False, na=False)
        columns_clean = ['sequenceSuccess', 'extract', 'frag', 'temp', 'cycle', 'coordinates', 'altitude']
        df_infoextra.loc[mask_neg, columns_clean] = pd.NA

        # ---- ETAPA 5: VALIDAÇÃO FINAL ---- #
        try:
            Validate.validate_df_not_nan_conditional(
                df_infoextra,
                col_not_nan=['minionRun', 'sequenceResp', 'collector', 'sequenceSuccess', 
                             'extract', 'frag', 'temp', 'cycle']
            )
        except ValueError as ve:
            Utilits.abortar_execucao(
                mensagem=f'Erro de validação", {str(ve)}',
                titulo="Erro de validação",
                parent=root,
                log_widget=text_log,
                botao_exec=btn_exec
            )
            return
        
        return df_infoextra
