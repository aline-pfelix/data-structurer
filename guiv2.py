# import tkinter as tk
# from tkinter import ttk

# class IntervalEditor(ttk.Frame):

#     def __init__(self, parent, title):
#         super().__init__(parent)

#         self.title = title
#         self.intervals = []

#         self.aplicar_todas = tk.BooleanVar(value=True)

#         ttk.Label(self, text=title).pack(anchor="w")

#         frm_val = ttk.Frame(self)
#         frm_val.pack(anchor="w", pady=(2,4))

#         ttk.Label(frm_val).pack(side="left")

#         self.entry_valor = ttk.Entry(frm_val, width=25)
#         self.entry_valor.configure(state="normal")

#         self.entry_valor.pack(side="left", padx=5)

#         chk = ttk.Checkbutton(
#             frm_val,
#             text="Aplicar a todas as placas",
#             variable=self.aplicar_todas,
#             command=self._toggle_modo
#         )
#         chk.pack(side="left", padx=(10,0))

#         # self.container = ttk.Frame(self)
#         # self.container.pack(fill="x", pady=(4,6))

#         # -------------------------
#         # área rolável dos intervalos
#         # -------------------------
#         scroll_frame = ttk.Frame(self)
#         scroll_frame.pack(fill="both", expand=True, pady=(4,6))

#         self.canvas = tk.Canvas(
#             scroll_frame,
#             height=180   # altura visível
#         )
#         self.canvas.pack(side="left", fill="both", expand=True)

#         scrollbar = ttk.Scrollbar(
#             scroll_frame,
#             orient="vertical",
#             command=self.canvas.yview
#         )
#         scrollbar.pack(side="right", fill="y")

#         self.canvas.configure(
#             yscrollcommand=scrollbar.set
#         )

#         self.container = ttk.Frame(self.canvas)

#         self.canvas_window = self.canvas.create_window(
#             (0,0),
#             window=self.container,
#             anchor="nw"
#         )

#         # atualizar região rolável
#         def on_configure(event):
#             self.canvas.configure(
#                 scrollregion=self.canvas.bbox("all")
#             )

#         self.container.bind(
#             "<Configure>",
#             on_configure
#         )

#         # ajustar largura do frame interno
#         def resize_frame(event):
#             self.canvas.itemconfig(
#                 self.canvas_window,
#                 width=event.width
#             )

#         self.canvas.bind(
#             "<Configure>",
#             resize_frame
#         )

#         self.btn_add = ttk.Button(
#             self,
#             text="Adicionar intervalo de placas",
#             command=self.add_interval_row
#         )
#         self.btn_add.pack(anchor="w")
#         self.btn_add.configure(state="disabled")

#     def _toggle_modo(self):
#         if self.aplicar_todas.get():
#             self.entry_valor.configure(state="normal")

#             for _, _, _, row in self.intervals:
#                 row.destroy()
#             self.intervals.clear()

#             self.btn_add.configure(state="disabled")

#         else:
#             self.entry_valor.configure(state="disabled")
#             self.btn_add.configure(state="normal")

#     def _mousewheel(event):
#         self.canvas.yview_scroll(
#             int(-1*(event.delta/120)),
#             "units"
#         )

#         self.canvas.bind_all(
#             "<MouseWheel>",
#             _mousewheel
#         )

#     def add_interval_row(self, start='', end='', value=''):
#             # força modo intervalos
#             if self.aplicar_todas.get():
#                 self.aplicar_todas.set(False)
#                 self._toggle_modo()

#             row = ttk.Frame(self.container)
#             row.pack(fill='x', pady=2)

#             e_start = ttk.Entry(row, width=6)
#             e_start.insert(0, start)
#             e_start.pack(side='left', padx=(0,6))

#             ttk.Label(row, text="até").pack(side='left')

#             e_end = ttk.Entry(row, width=6)
#             e_end.insert(0, end)
#             e_end.pack(side='left', padx=(6,6))

#             e_val = ttk.Entry(row, width=15)
#             e_val.insert(0, value)
#             e_val.pack(side='left', padx=(6,6))

#             def remove():
#                 row.destroy()
#                 self.intervals = [t for t in self.intervals if t[3] != row]

#             btn_rm = ttk.Button(row, text="Remover", command=remove)
#             btn_rm.pack(side='left', padx=(6,0))

#             self.intervals.append((e_start, e_end, e_val, row))

#             self.update_idletasks()
#             self.canvas.yview_moveto(1.0)

#     def get_intervals(self):
#         out = []

#         for e_start, e_end, e_val, _ in self.intervals:
#             s = e_start.get().strip()
#             e = e_end.get().strip()
#             v = e_val.get().strip()

#             if not s and not e and not v:
#                 continue

#             if not s or not e:
#                 raise ValueError(
#                     f"No intervalo em '{self.title}' falta início ou fim."
#                 )

#             if int(s) > int(e):
#                 raise ValueError(
#                     f"Início maior que fim em '{self.title}': {s} > {e}"
#                 )

#             out.append((int(s), int(e), v))

#         return out

#     def collect(self):

#         # ---------------------------
#         # MODO: TODAS AS PLACAS
#         # ---------------------------
#         if self.aplicar_todas.get():
#             valor = self.entry_valor.get().strip()

#             if not valor:
#                 raise ValueError(
#                     f"O campo '{self.title}' não foi informado."
#                 )

#             return {
#                 "modo": "todas",
#                 "valor": valor
#             }

#         # ---------------------------
#         # MODO: INTERVALOS
#         # ---------------------------
#         intervalos = self.get_intervals()

#         if not intervalos:
#             raise ValueError(
#                 f"Em '{self.title}', informe ao menos um intervalo ou selecione 'todas as placas'."
#             )

#         return {
#             "modo": "intervalos",
#             "intervalos": intervalos
#         }

#     def get_valor_unico(self):
#         for _, _, e_val, _ in self.intervals:
#             v = e_val.get().strip()
#             if v:
#                 return v
#         return ''
    
#     def clear(self):
#         # 1. Limpa campo "aplicar a todas"
#         self.entry_valor.delete(0, tk.END)

#         # 2. Remove todos os intervalos visuais
#         for _, _, _, row in self.intervals:
#             row.destroy()
#         self.intervals.clear()

#         # 3. Volta para o modo "Aplicar a todas"
#         self.aplicar_todas.set(True)
#         self.entry_valor.configure(state="normal")
#         self.btn_add.configure(state="disabled")


#     def get_data(self):
#         if self.aplicar_todas.get():
#             return {
#                 "modo": "todas",
#                 "valor": self.entry_valor.get().strip()
#             }

#         return {
#             "modo": "intervalos",
#             "intervalos": self.get_intervals()
#         }

#     def reset(self):
#         # limpa campo valor único
#         self.entry_valor.delete(0, tk.END)

#         # remove intervalos
#         for _, _, _, row in self.intervals:
#             row.destroy()
#         self.intervals.clear()

#         # restaura estado inicial
#         self.aplicar_todas.set(True)
#         self.entry_valor.configure(state="normal")
#         self.btn_add.configure(state="disabled")


import tkinter as tk
from tkinter import ttk


class IntervalEditor(ttk.Frame):

    def __init__(self, parent, title):
        super().__init__(parent)

        self.title = title
        self.intervals = []

        self.aplicar_todas = tk.BooleanVar(value=True)

        ttk.Label(self, text=title).pack(anchor="w")

        frm_val = ttk.Frame(self)
        frm_val.pack(anchor="w", pady=(2,4))

        ttk.Label(frm_val).pack(side="left")

        self.entry_valor = ttk.Entry(frm_val, width=25)
        self.entry_valor.configure(state="normal")
        self.entry_valor.pack(side="left", padx=5)

        chk = ttk.Checkbutton(
            frm_val,
            text="Aplicar a todas as placas",
            variable=self.aplicar_todas,
            command=self._toggle_modo
        )
        chk.pack(side="left", padx=(10,0))


        # ==========================================
        # ÁREA ROLÁVEL DOS INTERVALOS
        # ==========================================
        scroll_frame = ttk.Frame(self)
        scroll_frame.pack(fill="both", expand=True, pady=(4,6))

        self.canvas = tk.Canvas(
            scroll_frame,
            height=240,
            highlightthickness=0
        )
        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = ttk.Scrollbar(
            scroll_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.configure(
            yscrollcommand=scrollbar.set
        )

        self.container = ttk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window(
            (0,0),
            window=self.container,
            anchor="nw"
        )

        # Atualiza área rolável
        def on_configure(event):
            self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )

        self.container.bind(
            "<Configure>",
            on_configure
        )

        # Ajusta largura do frame interno
        def resize_frame(event):
            self.canvas.itemconfig(
                self.canvas_window,
                width=event.width
            )

        self.canvas.bind(
            "<Configure>",
            resize_frame
        )

        # Mouse wheel Windows/Mac
        self.canvas.bind_all(
            "<MouseWheel>",
            self._mousewheel
        )

        # Mouse wheel Linux
        self.canvas.bind_all(
            "<Button-4>",
            self._mousewheel_linux
        )
        self.canvas.bind_all(
            "<Button-5>",
            self._mousewheel_linux
        )
        # ==========================================


        self.btn_add = ttk.Button(
            self,
            text="Adicionar intervalo de placas",
            command=self.add_interval_row
        )
        self.btn_add.pack(anchor="w")
        self.btn_add.configure(state="disabled")


    # ----------------------------------------
    # ROLAGEM MOUSE
    # ----------------------------------------
    def _mousewheel(self, event):
        self.canvas.yview_scroll(
            int(-1*(event.delta/120)),
            "units"
        )


    def _mousewheel_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(
                -1,
                "units"
            )
        elif event.num == 5:
            self.canvas.yview_scroll(
                1,
                "units"
            )
    # ----------------------------------------


    def _toggle_modo(self):
        if self.aplicar_todas.get():
            self.entry_valor.configure(state="normal")

            for _, _, _, row in self.intervals:
                row.destroy()

            self.intervals.clear()

            self.btn_add.configure(
                state="disabled"
            )

        else:
            self.entry_valor.configure(
                state="disabled"
            )

            self.btn_add.configure(
                state="normal"
            )


    def add_interval_row(
        self,
        start='',
        end='',
        value=''
    ):

        if self.aplicar_todas.get():
            self.aplicar_todas.set(False)
            self._toggle_modo()

        row = ttk.Frame(self.container)
        row.pack(fill='x', pady=2)

        e_start = ttk.Entry(
            row,
            width=6
        )
        e_start.insert(0, start)
        e_start.pack(
            side='left',
            padx=(0,6)
        )

        ttk.Label(
            row,
            text="até"
        ).pack(side='left')

        e_end = ttk.Entry(
            row,
            width=6
        )
        e_end.insert(0, end)
        e_end.pack(
            side='left',
            padx=(6,6)
        )

        e_val = ttk.Entry(
            row,
            width=15
        )
        e_val.insert(0, value)
        e_val.pack(
            side='left',
            padx=(6,6)
        )

        def remove():
            row.destroy()

            self.intervals = [
                t for t in self.intervals
                if t[3] != row
            ]

        btn_rm = ttk.Button(
            row,
            text="Remover",
            command=remove
        )
        btn_rm.pack(
            side='left',
            padx=(6,0)
        )

        self.intervals.append(
            (e_start,e_end,e_val,row)
        )

        # autoscroll para último
        self.update_idletasks()
        self.canvas.yview_moveto(1.0)


    def get_intervals(self):
        out=[]

        for e_start,e_end,e_val,_ in self.intervals:

            s=e_start.get().strip()
            e=e_end.get().strip()
            v=e_val.get().strip()

            if not s and not e and not v:
                continue

            if not s or not e:
                raise ValueError(
                    f"No intervalo em '{self.title}' falta início ou fim."
                )

            if int(s)>int(e):
                raise ValueError(
                    f"Início maior que fim em '{self.title}': {s}>{e}"
                )

            out.append(
                (int(s),int(e),v)
            )

        return out


    def collect(self):

        if self.aplicar_todas.get():

            valor=self.entry_valor.get().strip()

            if not valor:
                raise ValueError(
                    f"O campo '{self.title}' não foi informado."
                )

            return {
                "modo":"todas",
                "valor":valor
            }

        intervalos=self.get_intervals()

        if not intervalos:
            raise ValueError(
                f"Em '{self.title}', informe ao menos um intervalo ou selecione 'todas as placas'."
            )

        return {
            "modo":"intervalos",
            "intervalos":intervalos
        }


    def get_valor_unico(self):
        for _,_,e_val,_ in self.intervals:
            v=e_val.get().strip()

            if v:
                return v

        return ''


    def clear(self):

        self.entry_valor.delete(
            0,
            tk.END
        )

        for _,_,_,row in self.intervals:
            row.destroy()

        self.intervals.clear()

        self.aplicar_todas.set(True)

        self.entry_valor.configure(
            state="normal"
        )

        self.btn_add.configure(
            state="disabled"
        )


    def get_data(self):

        if self.aplicar_todas.get():

            return {
                "modo":"todas",
                "valor":self.entry_valor.get().strip()
            }

        return {
            "modo":"intervalos",
            "intervalos":self.get_intervals()
        }


    def reset(self):

        self.entry_valor.delete(
            0,
            tk.END
        )

        for _,_,_,row in self.intervals:
            row.destroy()

        self.intervals.clear()

        self.aplicar_todas.set(True)

        self.entry_valor.configure(
            state="normal"
        )

        self.btn_add.configure(
            state="disabled"
        )