from utilitarios import Utilits

class Intervals:
    # ------------------------------------------------------------------------- #
    # APLICAÇÃO DE INTERVALOS DE PLACA                                          #
    # ------------------------------------------------------------------------- #
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
