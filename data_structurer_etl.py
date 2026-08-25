from placa_grid import PlacaGrid
from utilitarios import Utilits
from validacao import Validate
from main_etl import DemfileController
import os
import threading
from tkcalendar import DateEntry
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
# ---------------------------------------------------------------------

# Lista global para armazenar as corridas
corridas_list = []

# ------------------------------------------------------------------------- #
# CONSTRUÇÃO DA JANELA PRINCIPAL                                            #
# ------------------------------------------------------------------------- #
def create_main_window():
    root = tk.Tk()
    root.iconbitmap("Borboleta.ico")
    root.title("ETL para o Banco de dados")
    root.geometry("1400x700")
    root.minsize(900,600)

    frm_top = ttk.Frame(root, padding=10)
    frm_top.pack(fill='x')

    def open_help_popup(widget_reference):
        popup = tk.Toplevel(root)
        popup.iconbitmap("Borboleta.ico")
        popup.title("Ajuda – Seleção da pasta")
        popup.resizable(False, False)
        popup.transient(root)
        popup.grab_set()  # modal

        # -------- POSICIONAR AO LADO DO BOTÃO --------
        widget_reference.update_idletasks()
        x = widget_reference.winfo_rootx() + widget_reference.winfo_width() + 10
        y = widget_reference.winfo_rooty()

        popup.geometry(f"420x300+{x}+{y}")

        # -------- CONTEÚDO --------
        ttk.Label(
            popup,
            text="Ajuda",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(10, 5))

        ttk.Label(
            popup,
            text=(
                "Selecione uma pasta contendo os outputs de uma corrida MinION.\n\n"
                "Essa pasta deve conter:\n"
                "• Arquivo(s) Demfile\n"
                "• Arquivo(s) Mergedemfile\n"
                "• Arquivo(s) Fasta\n "               
                "• Arquivo(s) .tsv (output do ReadsIdentifier)\n"
                "• Arquivo com a lista de clusters\n\n"

                "Obs1: Dados de clusterização podem incluir clusters das corridas anteriores.\n\n"
                "Obs2: Evite subpastas."
            ),
            wraplength=800,
            justify="left"
        ).pack(padx=10, pady=10)

        ttk.Button(
            popup,
            text="Fechar",
            command=popup.destroy
        ).pack(pady=(0, 10))

    def open_help_popup2(widget_reference):
        popup = tk.Toplevel(root)
        popup.iconbitmap("Borboleta.ico")
        popup.title("Ajuda – Seleção da amostragem")
        popup.resizable(False, False)
        popup.transient(root)
        popup.grab_set()  # modal

        # -------- POSICIONAR AO LADO DO BOTÃO --------
        widget_reference.update_idletasks()
        x = widget_reference.winfo_rootx() + widget_reference.winfo_width() + 10
        y = widget_reference.winfo_rooty() 

        popup.geometry(f"420x230+{x}+{y}")

        # -------- CONTEÚDO --------
        ttk.Label(
            popup,
            text="Ajuda2",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(10, 5))

        ttk.Label(
            popup,
            text=(
                "Coordenadas geográficas e altitude estão pré definidas.\n\n"

            ),
            wraplength=380,
            justify="left"
        ).pack(padx=15, pady=10)

        ttk.Button(
            popup,
            text="Fechar",
            command=popup.destroy
        ).pack(pady=(0, 10))

    lbl_folder = ttk.Label(frm_top, text="Arquivos de UMA corrida:")
    lbl_folder.grid(row=0, column=0, sticky='w')
    ent_folder = ttk.Entry(frm_top, width=90)
    ent_folder.grid(row=0, column=1, padx=5, sticky='w')
    def on_browse():
        sel = filedialog.askdirectory()
        if sel:
            ent_folder.delete(0, tk.END)
            ent_folder.insert(0, sel)
    
    btn_browse = ttk.Button(frm_top, text="Procurar", command=on_browse)
    btn_browse.grid(row=0, column=1, padx=(250, 2))

    btn_help = ttk.Button(frm_top, text="❓", width=3, command=lambda: open_help_popup(btn_browse))
    btn_help.grid(row=0, column=1, padx=(350, 0))

    lbl_sample = ttk.Label(frm_top, text="Ponto de amostragem:")
    lbl_sample.grid(row=6, column=0, sticky='w', pady=(8,0))

    btn_help2 = ttk.Button(frm_top, text="❓", width=3, command=lambda: open_help_popup2(lbl_sample))
    btn_help2.grid(row=6, column=0, sticky='w', padx=(130,0))

    ttk.Label(frm_top, text="Data de atualização do banco em que foi realizado o BLAST:").grid(row=1, column=0, sticky='w', pady=(8,0))
    
    ent_blast = DateEntry(
        frm_top,
        date_pattern="yyyy-mm-dd",
        width=20,
        state='readonly' 
    )
    ent_blast.grid(row=1, column=1, sticky="w", pady=(8,0))

    def update_coordinate_fields():
        if coord_var.get() == 4:  # valor do "Outro"
            ent_coord.configure(state="normal")
            ent_alt.configure(state="normal")
        else:
            ent_coord.configure(state="disabled")
            ent_alt.configure(state="disabled")

            # limpar valores
            ent_coord.delete(0, tk.END)
            ent_alt.delete(0, tk.END)

    ttk.Label(frm_top, text="Número da corrida MinION:").grid(row=2, column=0, sticky='w', pady=(8,0))
    ent_minion = ttk.Entry(frm_top, width=20); ent_minion.grid(row=2, column=1, sticky='w', pady=(8,0))
    Utilits.add_placeholder(ent_minion, "Ex: 001")

    ttk.Label(frm_top, text="Responsável pelo sequenciamento :").grid(row=3, column=0, sticky='w', pady=(8,0))
    ent_respseq = ttk.Entry(frm_top, width=20); ent_respseq.grid(row=3, column=1, sticky='w', pady=(8,0))
    Utilits.add_placeholder(ent_respseq, "Ex: Nome Sobrenome")

    ttk.Label(frm_top, text="Responsável pela coleta:").grid(row=4, column=0, sticky='w', pady=(8,0))
    ent_respcol = ttk.Entry(frm_top, width=20); ent_respcol.grid(row=4, column=1, sticky='w', pady=(8,0))
    Utilits.add_placeholder(ent_respcol, "Ex: Nome Sobrenome")

    ttk.Label(frm_top, text="Sucesso do sequenciamento (%):").grid(row=5, column=0, sticky='w', pady=(8,0))
    ent_sucess = ttk.Entry(frm_top, width=20); ent_sucess.grid(row=5, column=1, sticky='w', pady=(8,0))
    Utilits.add_placeholder(ent_sucess, "Ex: 88.3")

    coord_var = tk.IntVar(value=0)
    r1 = ttk.Radiobutton(frm_top, text="Iranduba", variable=coord_var, value=1,     command=update_coordinate_fields)
    r2 = ttk.Radiobutton(frm_top, text="ZF2", variable=coord_var, value=2,     command=update_coordinate_fields)
    r3 = ttk.Radiobutton(frm_top, text="Careiro-Castanho", variable=coord_var, value=3,     command=update_coordinate_fields)
    r4 = ttk.Radiobutton(frm_top, text="Outro", variable=coord_var, value=4,     command=update_coordinate_fields)
    r1.grid(row=6, column=1, sticky='w')
    r2.grid(row=6, column=1, padx=(120,0), sticky='w')
    r3.grid(row=6, column=1, padx=(240,0), sticky='w')
    r4.grid(row=6, column=1, padx=(400,0), sticky='w')

    ttk.Label(frm_top, text="Coordenada geográfica:").grid(row=6, column=1, sticky='w', padx=(500,0))
    ent_coord = ttk.Entry(frm_top, width=20, state="disabled"); ent_coord.grid(row=6, column=1, sticky='w', padx=(630,0))
    ttk.Label(frm_top, text="Altitude:").grid(row=6, column=1, sticky='w', padx=(780,0))
    ent_alt = ttk.Entry(frm_top, width=20, state="disabled"); ent_alt.grid(row=6, column=1, sticky='w', padx=(830,0))

    frm_intervals = ttk.Frame(root, padding=10)

    frm_amos = ttk.LabelFrame(root, text="Coordenada geográfica", padding=10)
    frm_amos2 = ttk.LabelFrame(root, text="Altitude", padding=10)
    frm_amos.pack(fill='x')
    frm_amos2.pack(fill='x')

    frm_intervals.pack(fill='x')

    placa_grid = PlacaGrid(frm_intervals)
    placa_grid.pack(fill="both", expand=True)

    frm_buttons = ttk.Frame(root, padding=10)
    frm_buttons.pack(fill='x')


    btn_add = ttk.Button(frm_buttons, text="Adicionar mais uma corrida", command=lambda: on_action(add_another=True))
    btn_add.pack(side='left', padx=(10,5))

    btn_exec = ttk.Button(frm_buttons, text="Executar ETL", command=lambda: on_action(add_another=False))
    btn_exec.pack(side='left', padx=(5,10))

    btn_reset = ttk.Button(frm_buttons, text="Reiniciar", command=lambda: reiniciar())
    btn_reset.pack(side='left', padx=(20, 5))

    # Área de log
    frm_log = ttk.Frame(root, padding=10)
    frm_log.pack(fill='both', expand=True)

    lbl_log = ttk.Label(frm_log, text="Log de execução:")
    lbl_log.pack(anchor='w')

    txt_log = tk.Text(frm_log, wrap='word', state='disabled', height=25)
    txt_log.pack(fill='both', expand=True)

    def reiniciar():
            if not messagebox.askyesno("Reiniciar", "Tem certeza? Todos os dados serão apagados."):
                return

            global corridas_list
            corridas_list.clear()

            ent_folder.delete(0, tk.END)
            ent_minion.delete(0, tk.END)
            ent_respseq.delete(0, tk.END)
            ent_respcol.delete(0, tk.END)
            ent_sucess.delete(0, tk.END)

            ent_blast.set_date(ent_blast._date.today())

            coord_var.set(0)
            ent_coord.configure(state='disabled')
            ent_alt.configure(state='disabled')
            ent_coord.delete(0, tk.END)
            ent_alt.delete(0, tk.END)

            placa_grid.reset()

            txt_log.configure(state='normal')
            txt_log.delete('1.0', tk.END)
            txt_log.configure(state='disabled')

            btn_exec.configure(state='normal')



    # ------------------------------------------------------------------------- #
    # COLETA E EXECUÇÃO DA CORRIDA                                              #
    # ------------------------------------------------------------------------- #
    def on_action(add_another: bool):
        global corridas_list

        # ---- ETAPA 1: COLETA E VALIDAÇÃO DOS DADOS BÁSICOS ---- #
        caminho = ent_folder.get().strip()
        if not caminho or not os.path.isdir(caminho):
            messagebox.showerror("Erro", "Selecione uma pasta válida da corrida.")
            return

        # Impede reutilizar a mesma pasta
        if any(c['caminho'] == caminho for c in corridas_list):
            messagebox.showerror(
                "Erro",
                "Esta pasta já foi adicionada em outra corrida."
            )
            return

        try:
            datablast_val = Validate.validate_required_date(ent_blast, "Data do BLAST")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        minionrun_val = ent_minion.get().strip()
        if not re.fullmatch(r"\d{3}", minionrun_val):
            messagebox.showerror(
                "Erro",
                "Número da corrida MinION deve ter 3 dígitos (ex: 001)."
            )
            return

        try:
            respseq_val = Validate.validate_entry_with_placeholder(
                ent_respseq, "Responsável pelo sequenciamento", max_len=50
            )
            respcol_val = Validate.validate_entry_with_placeholder(
                ent_respcol, "Responsável pela coleta", max_len=50
            )
            sucesso_val = Validate.validate_success_sequencing(ent_sucess.get())
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        try:
            coord_index_val, coord_outro, altitude_val = Validate.validate_sampling_point(
                coord_var, ent_coord, ent_alt
            )
            if coord_var.get() == 4:
                coord_outro = Validate.validate_coordinates(ent_coord.get())
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
            return

        # ---- ETAPA 2: INTERVALOS (RESPEITANDO 'TODAS') ---- #
        intervals_map = {}

        try:
            intervals_map = placa_grid.collect()
        except ValueError as e:
            messagebox.showerror("Erro de validação", str(e))
            return

        # limpar log
        txt_log.configure(state='normal')
        txt_log.delete('1.0', tk.END)
        txt_log.configure(state='disabled')


        # ---- ETAPA 3: ARMAZENAR CORRIDA ---- #
        corrida_atual = {
            'caminho': caminho,
            'parametros': {
                'datablast': datablast_val,
                'minionrun': minionrun_val,
                'respseq': respseq_val,
                'respcol': respcol_val,
                'sucesseq': sucesso_val,
                'coord_index': coord_index_val,
                'coord_geo': coord_outro,
                'altitude': altitude_val
            },
            'intervalos': intervals_map
        }

        corridas_list.append(corrida_atual)

        # ---- ETAPA 4: LIMPAR INTERFACE SE ADICIONAR ---- #
        if add_another:
            ent_folder.delete(0, tk.END)
            ent_minion.delete(0, tk.END)
            ent_respseq.delete(0, tk.END)
            ent_respcol.delete(0, tk.END)
            ent_sucess.delete(0, tk.END)

            coord_var.set(0)
            ent_coord.configure(state='disabled')
            ent_alt.configure(state='disabled')
            ent_coord.delete(0, tk.END)
            ent_alt.delete(0, tk.END)

            ent_blast.set_date(ent_blast._date.today())

            placa_grid.reset()

            txt_log.configure(state='normal')
            txt_log.insert(
                tk.END,
                f"Corrida adicionada ({len(corridas_list)} no total)\n"
            )
            txt_log.configure(state='disabled')
            return

        # ---- ETAPA 5: EXECUTAR ETL ---- #
        btn_exec.configure(state='disabled')

        txt_log.configure(state='normal')
        txt_log.insert(
            tk.END,
            f"Iniciando processamento de {len(corridas_list)} corrida(s)...\n"
        )
        txt_log.configure(state='disabled')

        threading.Thread(
            target=DemfileController.execute_etl_multiple,
            args=(corridas_list, txt_log, btn_exec, root),
            daemon=False
        ).start()

    return root

# ------------------------------------------------------------------------- #
# EXECUÇÃO                                                                  #
# ------------------------------------------------------------------------- #
if __name__ == "__main__":
    root = create_main_window()
    root.mainloop()