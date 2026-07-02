### --------------------------------------------------------------- ###
### Created by:  Aline Priscila Félix                               ###
### --------------------------------------------------------------- ###

import tkinter as tk
from tkinter import ttk, messagebox


# Chave interna → label exibido na grade
COLUNAS = {
    "extract": "Método de extração",
    "frag":    "Fragmento",
    "temp":    "Temperatura primer",
    "cycle":   "Ciclos da PCR",
}


class PlacaGrid(ttk.Frame):
    """
    Substitui os quatro IntervalEditor.

    Modos:
      • "todas"  → checkbox marcado (padrão): um campo de texto por coluna,
                   mesmo valor aplicado a todas as placas.
      • "grade"  → checkbox desmarcado: grade rolável com uma linha por placa;
                   primeira coluna é o Plate-ID (editável pelo usuário);
                   suporta colar (Ctrl+V) do Excel.

    collect(plate_ids_validos=None) devolve dict compatível com on_action:
        {
            "extract": {"modo": "todas",  "valor": "..."}  |
                       {"modo": "grade",  "linhas": [{"placa": "BIM001", "valor": "..."}, ...]},
            "frag":    ...,
            "temp":    ...,
            "cycle":   ...,
        }

    Se plate_ids_validos for uma lista/set, valida se cada Plate-ID
    digitado existe nela. Passe None para pular essa validação.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self._cells: list[dict] = []          # grade: _cells[row][col_key] = StringVar
        self._plate_vars: list[tk.StringVar] = []  # grade: var da coluna Plate-ID por linha
        self._todas_vars: dict[str, tk.StringVar] = {}

        # ── Linha superior: nº de placas + checkbox ─────────────────
        frm_top = ttk.Frame(self)
        frm_top.pack(anchor="w", pady=(0, 6))

        ttk.Label(frm_top, text="Número de placas:").pack(side="left")

        self._n_var = tk.StringVar()
        self._entry_n = ttk.Entry(frm_top, textvariable=self._n_var, width=6)
        self._entry_n.pack(side="left", padx=(4, 16))

        # checkbox PRÉ-SELECIONADO
        self._aplicar_todas = tk.BooleanVar(value=True)
        self._chk = ttk.Checkbutton(
            frm_top,
            text="Aplicar o mesmo valor para todas as placas",
            variable=self._aplicar_todas,
            command=self._toggle_modo
        )
        self._chk.pack(side="left")

        self._lbl_status = ttk.Label(frm_top, text="", foreground="gray")
        self._lbl_status.pack(side="left", padx=(16, 0))

        # ── Frame que alterna entre os dois modos ───────────────────
        self._frm_conteudo = ttk.Frame(self)
        self._frm_conteudo.pack(fill="both", expand=True, pady=(0, 6))

        # ── Modo TODAS: campos únicos ────────────────────────────────
        self._frm_todas = ttk.Frame(self._frm_conteudo)
        for key, label in COLUNAS.items():
            row = ttk.Frame(self._frm_todas)
            row.pack(anchor="w", pady=3)
            ttk.Label(row, text=f"{label}:", width=30, anchor="w").pack(side="left")
            var = tk.StringVar()
            ttk.Entry(row, textvariable=var, width=30).pack(side="left", padx=(4, 0))
            self._todas_vars[key] = var

        # ── Modo GRADE: área rolável ─────────────────────────────────
        self._frm_grade = ttk.Frame(self._frm_conteudo)

        outer = ttk.Frame(self._frm_grade)
        outer.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(outer, height=260, highlightthickness=0)
        self._canvas.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(outer, orient="vertical", command=self._canvas.yview)
        sb.pack(side="right", fill="y")
        self._canvas.configure(yscrollcommand=sb.set)

        self._container = ttk.Frame(self._canvas)
        self._win = self._canvas.create_window(
            (0, 0), window=self._container, anchor="nw"
        )
        self._container.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")
            )
        )
        self._canvas.bind(
            "<Configure>",
            lambda e: self._canvas.itemconfig(self._win, width=e.width)
        )
        self._canvas.bind_all(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1 * e.delta / 120), "units")
        )
        self._canvas.bind_all("<Button-4>",
            lambda e: self._canvas.yview_scroll(-1, "units"))
        self._canvas.bind_all("<Button-5>",
            lambda e: self._canvas.yview_scroll(1, "units"))

        # ── Botão limpar (sempre visível) ────────────────────────────
        ttk.Button(self, text="Limpar", command=self.clear).pack(anchor="w")

        # Estado inicial: checkbox marcado → modo todas
        self._toggle_modo()


    # ────────────────────────────────────────────────────────────────
    # ALTERNÂNCIA DE MODO
    # ────────────────────────────────────────────────────────────────

    def _toggle_modo(self):
        if self._aplicar_todas.get():
            # esconde grade, mostra campos únicos
            self._frm_grade.pack_forget()
            self._frm_todas.pack(fill="x", padx=4)
            self._lbl_status.configure(text="")
        else:
            # esconde campos únicos, monta grade automaticamente
            self._frm_todas.pack_forget()
            self._frm_grade.pack(fill="both", expand=True)
            self._criar_grade_automatica()


    # ────────────────────────────────────────────────────────────────
    # CRIAÇÃO DA GRADE
    # ────────────────────────────────────────────────────────────────

    def _criar_grade_automatica(self):
        """Lê o nº de placas e constrói a grade. Chamado automaticamente ao desmarcar."""
        n_str = self._n_var.get().strip()

        if not n_str.isdigit() or int(n_str) < 1:
            messagebox.showerror(
                "Número de placas não informado",
                "Informe o número de placas antes de desmarcar esta opção."
            )
            # reverte o checkbox
            self._aplicar_todas.set(True)
            self._toggle_modo()
            return

        self._build_grid(int(n_str))


    def _build_grid(self, n: int):
        for w in self._container.winfo_children():
            w.destroy()
        self._cells.clear()
        self._plate_vars.clear()

        col_keys   = list(COLUNAS.keys())
        col_labels = list(COLUNAS.values())

        # ── cabeçalho ──
        ttk.Label(
            self._container, text="Plate-ID", width=10,
            anchor="center", relief="groove", padding=(2, 2)
        ).grid(row=0, column=0, padx=1, pady=1, sticky="ew")

        for col_idx, label in enumerate(col_labels, start=1):
            ttk.Label(
                self._container, text=label,
                anchor="center", relief="groove", padding=(2, 2)
            ).grid(row=0, column=col_idx, padx=1, pady=1, sticky="ew")

        # ── linhas ──
        for row_idx in range(n):
            # coluna Plate-ID (editável)
            plate_var = tk.StringVar()
            plate_entry = ttk.Entry(
                self._container, textvariable=plate_var, width=10
            )
            plate_entry.grid(row=row_idx + 1, column=0, padx=1, pady=1, sticky="ew")
            plate_entry.bind("<Control-v>", self._on_paste)
            plate_entry.bind("<Control-V>", self._on_paste)
            self._plate_vars.append(plate_var)

            # colunas de dados
            row_vars: dict[str, tk.StringVar] = {}
            for col_idx, key in enumerate(col_keys, start=1):
                var = tk.StringVar()
                entry = ttk.Entry(self._container, textvariable=var, width=18)
                entry.grid(row=row_idx + 1, column=col_idx, padx=1, pady=1, sticky="ew")
                entry.bind("<Control-v>", self._on_paste)
                entry.bind("<Control-V>", self._on_paste)
                row_vars[key] = var

            self._cells.append(row_vars)

        # expande todas as colunas
        for col_idx in range(len(col_keys) + 1):
            self._container.columnconfigure(col_idx, weight=1)

        self._lbl_status.configure(text=f"{n} placa(s) — preencha os Plate-IDs")
        self.update_idletasks()
        self._canvas.yview_moveto(0)


    # ────────────────────────────────────────────────────────────────
    # COLAR DO EXCEL (Ctrl+V)
    # Suporta colar a partir da coluna Plate-ID ou de qualquer coluna de dados
    # ────────────────────────────────────────────────────────────────

    def _on_paste(self, event):
        try:
            raw = self.clipboard_get()
        except tk.TclError:
            return

        origin_row, origin_col = self._find_cell(event.widget)
        # origin_col: -1 = Plate-ID, 0..N = índice em COLUNAS
        if origin_row is None:
            return

        col_keys = list(COLUNAS.keys())
        for r_off, linha in enumerate(raw.strip("\n").split("\n")):
            valores  = linha.rstrip("\r").split("\t")
            row_idx  = origin_row + r_off
            if row_idx >= len(self._cells):
                break

            for c_off, valor in enumerate(valores):
                # coluna efetiva: origin_col + c_off
                # -1 = Plate-ID, 0+ = dados
                col_eff = origin_col + c_off

                if col_eff == -1:
                    self._plate_vars[row_idx].set(valor.strip())
                elif 0 <= col_eff < len(col_keys):
                    self._cells[row_idx][col_keys[col_eff]].set(valor.strip())

        return "break"


    def _find_cell(self, widget):
        """
        Devolve (row_idx, col_idx) onde col_idx == -1 para Plate-ID
        e 0..N-1 para as colunas de dados. Devolve (None, None) se não achar.
        """
        n_rows = len(self._cells)

        for r_idx in range(n_rows):
            # verifica coluna Plate-ID (col 0 no grid)
            slaves = self._container.grid_slaves(row=r_idx + 1, column=0)
            if slaves and slaves[0] == widget:
                return r_idx, -1

            # verifica colunas de dados
            for k_idx in range(len(COLUNAS)):
                slaves = self._container.grid_slaves(row=r_idx + 1, column=k_idx + 1)
                if slaves and slaves[0] == widget:
                    return r_idx, k_idx

        return None, None


    # ────────────────────────────────────────────────────────────────
    # INTERFACE PÚBLICA
    # ────────────────────────────────────────────────────────────────

    def collect(self, plate_ids_validos=None) -> dict:
        """
        Valida e devolve os dados.

        plate_ids_validos: lista ou set de Plate-IDs válidos lidos do demfile
                           (ex: {"BIM001", "BIM002", ...}).
                           Passe None para pular a validação de Plate-ID.

        Retorno modo todas:
            {"extract": {"modo":"todas","valor":"..."}, "frag": ..., ...}

        Retorno modo grade:
            {"extract": {"modo":"grade","linhas":[{"placa":"BIM001","valor":"..."}...]}, ...}

        Lança ValueError se algum campo obrigatório estiver vazio ou se
        um Plate-ID não existir na lista de válidos.
        """
        if self._aplicar_todas.get():
            result = {}
            for key, var in self._todas_vars.items():
                valor = var.get().strip()
                if not valor:
                    raise ValueError(
                        f"Campo '{COLUNAS[key]}' não foi informado."
                    )
                result[key] = {"modo": "todas", "valor": valor}
            return result

        # ── modo grade ──
        if not self._cells:
            raise ValueError(
                "A grade de placas ainda não foi criada. "
                "Informe o número de placas e desmarque a opção."
            )

        result = {key: {"modo": "grade", "linhas": []} for key in COLUNAS}

        for row_idx, row_vars in enumerate(self._cells):
            placa = self._plate_vars[row_idx].get().strip()

            if not placa:
                raise ValueError(
                    f"Linha {row_idx + 1} — Plate-ID não informado."
                )

            # validação contra lista do demfile
            if plate_ids_validos is not None and placa not in plate_ids_validos:
                raise ValueError(
                    f"Plate-ID '{placa}' não encontrado nos arquivos da corrida."
                )

            for key, var in row_vars.items():
                valor = var.get().strip()
                if not valor:
                    raise ValueError(
                        f"Plate-ID '{placa}' — campo '{COLUNAS[key]}' está vazio."
                    )
                result[key]["linhas"].append({"placa": placa, "valor": valor})

        return result


    def clear(self):
        """Limpa valores mantendo a estrutura."""
        for var in self._todas_vars.values():
            var.set("")
        for var in self._plate_vars:
            var.set("")
        for row_vars in self._cells:
            for var in row_vars.values():
                var.set("")
        self._lbl_status.configure(text="")


    def reset(self):
        """Volta ao estado inicial (checkbox marcado, grade destruída)."""
        for var in self._todas_vars.values():
            var.set("")
        for w in self._container.winfo_children():
            w.destroy()
        self._cells.clear()
        self._plate_vars.clear()
        self._n_var.set("")
        self._aplicar_todas.set(True)
        self._toggle_modo()
        self._lbl_status.configure(text="")
