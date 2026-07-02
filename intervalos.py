import pandas as pd
import re
from utilitarios import Utilits
from validacao import Validate

class Intervals:
    def generate_continuous_intervals(valores):
        if not valores:
            return []

        valores = sorted(set(valores))
        intervalos = []

        inicio = valores[0]
        prev = valores[0]

        for v in valores[1:]:
            if v == prev + 1:
                prev = v
            else:
                intervalos.append((inicio, prev))
                inicio = v
                prev = v

        intervalos.append((inicio, prev))
        return intervalos

    def format_intervals(intervalos):
        return ", ".join(
            f"{start:03d}–{end:03d}" if start != end else f"{start:03d}"
            for start, end in intervalos
        )

    # ------------------------------------------------------------------------- #
    # APLICAÇÃO DE INTERVALOS DE PLACA                                          #
    # ------------------------------------------------------------------------- #
    def apply_intervals_to_df(df_infoextra, intervals_map, log_widget=None):
        if 'plateRackCode' not in df_infoextra.columns:
            raise ValueError("DataFrame infoextra não contém a coluna 'plateRackCode'.")

        def extract_last3(x):
            if pd.isna(x):
                return pd.NA

            s = str(x)
            m = re.search(r'(\d{3})$', s)
            if not m:
                return pd.NA

            val = int(m.group(1))
            return val if val != 0 else pd.NA

        df_infoextra['_rack_num'] = df_infoextra['plateRackCode'].apply(extract_last3)

        racks_existentes = df_infoextra['_rack_num'].dropna().unique()

        if len(racks_existentes) == 0:
            raise ValueError("Nenhuma placa válida foi encontrada no demfile.")

        def validate_non_overlapping_intervals(intervals, col_name=None):
            # ordenar por início
            intervals_sorted = sorted(intervals, key=lambda x: x[0])

            for i in range(len(intervals_sorted) - 1):
                start1, end1, _ = intervals_sorted[i]
                start2, end2, _ = intervals_sorted[i + 1]

                if start1 > end1:
                    raise ValueError(
                        f"Intervalo inválido{f' na coluna {col_name}' if col_name else ''}: "
                        f"início {start1} > fim {end1}"
                    )

                # Não permite sobreposição real (encostar é permitido)
                if start2 <= end1:
                    raise ValueError(
                        f"Intervalos sobrepostos{f' na coluna {col_name}' if col_name else ''}: "
                        f"[{start1}, {end1}] e [{start2}, {end2}]"
                    )
        
        def validate_existing_intervals(intervals, racks_reais, col_name):
            if not racks_reais:
                raise ValueError("Não há racks válidos no arquivo base.")

            min_real = min(racks_reais)
            max_real = max(racks_reais)

            for start, end, _ in intervals:

                # 1️⃣ valida range
                if start < min_real or end > max_real:
                    raise ValueError(
                        f"Intervalo inválido em '{col_name}': "
                        f"{start:03d}–{end:03d} está fora do range real "
                        f"({min_real:03d}–{max_real:03d})."
                    )

                # 2️⃣ valida existência real
                valores_intervalo = set(range(start, end + 1))
                inexistentes = valores_intervalo - racks_reais

                if inexistentes:
                    intervalos_reais = Intervals.generate_continuous_intervals(racks_reais)
                    esperado = Intervals.format_intervals(intervalos_reais)

                    raise ValueError(
                        f"Intervalo inválido em '{col_name}'.\n\n"
                        f"Intervalos mínimos esperados com base no demfile:\n"
                        f"{esperado}"
                    )

        def validate_full_coverage(intervals, racks_reais, col_name):
            racks_reais = set(racks_reais)

            coberto = set()
            for start, end, _ in intervals:
                coberto.update(range(start, end + 1))

            faltantes = racks_reais - coberto

            if faltantes:
                intervalos_reais = Intervals.generate_continuous_intervals(racks_reais)
                esperado = Intervals.format_intervals(intervalos_reais)

                intervalos_faltantes = Intervals.generate_continuous_intervals(faltantes)
                faltante_fmt = Intervals.format_intervals(intervalos_faltantes)

                raise ValueError(
                    f"Intervalos incompletos em '{col_name}'.\n\n"
                    f"O intervalo informado não contempla todo o range mínimo esperado.\n\n"
                    f"Range esperado (demfile):\n{esperado}\n\n"
                    f"Placas sem informação:\n{faltante_fmt}"
                )

        # ---- ETAPA 1: APLICAR INTERVALOS ---- #
        for col, intervals in intervals_map.items():

            racks_reais = set(df_infoextra['_rack_num'].dropna())

            validate_non_overlapping_intervals(intervals, col_name=col)
            validate_existing_intervals(intervals, racks_reais, col_name=col)
            validate_full_coverage(intervals, racks_reais, col_name=col)

            if log_widget:
                Utilits.append_log(
                    log_widget,
                    f"Aplicando {len(intervals)} intervalo(s) para '{col}'..."
                )

            for start, end, val in intervals:
                mask = (
                    df_infoextra['_rack_num'].notna()
                    & (df_infoextra['_rack_num'] >= start)
                    & (df_infoextra['_rack_num'] <= end)
                )

                df_infoextra.loc[mask, col] = val

                if log_widget:
                    Utilits.append_log(
                        log_widget,
                        f"{col}: {Validate.format_three(start)}–{Validate.format_three(end)}"
                        f"→ '{val}' aplicado em {mask.sum()} linha(s)"
                    )

        # remover coluna auxiliar
        df_infoextra.drop(columns=['_rack_num'], inplace=True)
        return df_infoextra

    def apply_to_all_plates(df, col, valor, log_widget=None):
        mask = df['plateRackCode'].notna()
        df.loc[mask, col] = valor

        if log_widget:
            Utilits.append_log(
                log_widget,
                f"{col}: valor '{valor}' aplicado a todas as placas ({mask.sum()} linhas)"
            )

    def validate_plate_ids(linhas, plate_ids_validos, col_name):
        """
        Verifica se todos os Plate-IDs informados na grade existem no demfile.
        Lança ValueError listando os inválidos.

        linhas: lista de {"placa": "BIM001", "valor": "..."}
        plate_ids_validos: set com os Plate-IDs presentes no demfile (plateRackCode)
        col_name: nome da coluna (para mensagem de erro)
        """
        invalidos = [
            l["placa"] for l in linhas
            if l["placa"] not in plate_ids_validos
        ]

        if invalidos:
            raise ValueError(
                f"Coluna '{col_name}': os seguintes Plate-IDs informados na grade "
                f"não foram encontrados no demfile:\n"
                + "\n".join(f"  - {p}" for p in invalidos)
            )

    def apply_grade_to_df(df_infoextra, col, linhas, log_widget=None):
        """
        Aplica os valores da grade (modo "grade") ao df_infoextra,
        cruzando pelo Plate-ID (plateRackCode).

        linhas: lista de {"placa": "BIM001", "valor": "..."}
        """
        aplicados = 0
        for linha in linhas:
            placa = linha["placa"]
            valor = linha["valor"]
            mask  = df_infoextra['plateRackCode'] == placa
            df_infoextra.loc[mask, col] = valor
            aplicados += mask.sum()

        if log_widget:
            Utilits.append_log(
                log_widget,
                f"{col}: valores da grade aplicados em {aplicados} linha(s)"
            )

        return df_infoextra