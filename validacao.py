import re
import datetime
from pathlib import Path

class Validate:
    def validate_entry_with_placeholder(entry, nome, max_len=None):
        valor = entry.get().strip()

        # não aceita vazio
        if not valor:
            raise ValueError(f"O campo '{nome}' é obrigatório.")

        # não aceita placeholder
        if hasattr(entry, "_has_placeholder") and entry._has_placeholder:
            raise ValueError(f"O campo '{nome}' é obrigatório e não foi preenchido.")

        # tamanho máximo
        if max_len and len(valor) > max_len:
            raise ValueError(
                f"O campo '{nome}' deve ter no máximo {max_len} caracteres."
            )

        return valor

    def validate_df_not_nan_conditional(df, col_not_nan, col_condicional="specimenCode"):
        erros = []

        for col in col_not_nan:
            mask_vazio = (
                df[col].isna() |
                (df[col].astype(str).str.strip() == '')
            )

            mask_nao_neg = ~df[col_condicional].astype(str).str.contains("Neg", na=False)

            mask_erro = mask_vazio & mask_nao_neg

            if mask_erro.any():
                linhas = df.index[mask_erro].tolist()[:5]
                erros.append(
                    f"Coluna '{col}' contém valores em branco "
                    f"quando '{col_condicional}' não é 'Neg' "
                    f"(ex.: linhas {linhas})"
                )

        if erros:
            raise ValueError(
                "Erro de validação do infoextra:\n\n" +
                "\n".join(erros)
            )

    def validate_success_sequencing(valor):
        valor = valor.strip()

        if not valor:
            raise ValueError("O campo 'Sucesso do sequenciamento (%)' é obrigatório.")

        # aceita inteiro ou decimal com ponto
        if not re.fullmatch(r"\d+(\.\d+)?", valor):
            raise ValueError(
                "O campo 'Sucesso do sequenciamento (%)' deve ser um número "
                "(inteiro ou decimal, usando ponto)."
            )

        return float(valor)

    def validate_required_date(date_entry, nome_campo="Data"):
        valor = date_entry.get().strip()

        if not valor or valor == "Selecione a data":
            raise ValueError(f"{nome_campo} é obrigatória e não foi informada.")

        try:
            data_informada = datetime.datetime.strptime(valor, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(
                f"{nome_campo} inválida. Use o formato YYYY-MM-DD."
            )

        hoje = datetime.date.today()
        if data_informada == hoje:
            raise ValueError(
                f"{nome_campo} não pode ser a data de hoje."
            )

        return data_informada

    def validate_sampling_point(coord_var, ent_coord, ent_alt):
        coord_index = coord_var.get()

        if coord_index not in (1, 2, 3, 4):
            raise ValueError(
                "Selecione obrigatoriamente um ponto de amostragem."
            )

        # valores padrão
        coord = None
        altitude = None

        if coord_index == 4:
            try:
                entrada = ent_coord.get().strip()
                lat_str, lon_str = entrada.split(",")

                lat = float(lat_str.strip())
                lon = float(lon_str.strip())

                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    raise ValueError

                coord = (lat, lon)  # agora é tupla

                altitude = float(ent_alt.get().strip())

            except ValueError:
                raise ValueError(
                    "Coordenada deve estar no formato decimal e altitude deve ser numérica."
                )

        return coord_index, coord, altitude
        

    def validate_coordinates(coord_str: str, nome_campo="Coordenadas"):
        if not coord_str or not coord_str.strip():
            raise ValueError(f"{nome_campo} é obrigatório.")

        try:
            lat_str, lon_str = coord_str.split(',')
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
        except Exception:
            raise ValueError(
                f"{nome_campo} deve estar no formato 'latitude, longitude'. "
                "Exemplo: -2.924722, -60.861389"
            )

        if not (-90 <= lat <= 90):
            raise ValueError(f"Latitude fora do intervalo válido (-90 a 90): {lat}")

        if not (-180 <= lon <= 180):
            raise ValueError(f"Longitude fora do intervalo válido (-180 a 180): {lon}")

        return f"{lat:.6f}, {lon:.6f}"

    def valid_file(path: Path) -> bool:
        return (
            path.is_file()
            and not path.name.startswith('.')
            and not path.name.startswith('~$')
        )
    
