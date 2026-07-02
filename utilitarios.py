import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class Utilits:
    def append_log(text_widget,message):
        def _append():
            text_widget.configure(state='normal')
            text_widget.insert(tk.END, message + '\n')
            text_widget.see(tk.END)
            text_widget.configure(state='disabled')
        text_widget.after(1, _append)

    def show_error(self,title, message, exc=None):
        if exc:
            message = f"{message}\n\nDetalhes:\n{exc}"
        messagebox.showerror(title, message)

    def add_placeholder(entry, text):
        entry._placeholder = text
        entry._has_placeholder = True

        entry.insert(0, text)
        entry.configure(foreground='gray')

        def on_focus_in(event):
            if entry.get() == text:
                entry.delete(0, tk.END)
                entry.configure(foreground='black')
                entry._has_placeholder = False        

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, text)
                entry.configure(foreground='gray')
                entry._has_placeholder = True

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        
    @staticmethod
    def abortar_execucao(mensagem, titulo="Execução interrompida", parent=None, log_widget=None, botao_exec=None):
        if log_widget:
            Utilits.append_log(log_widget, f"⛔ {mensagem}")

        messagebox.showwarning(titulo, mensagem, parent=parent)

        if botao_exec:
            botao_exec.configure(state="normal")

        raise AbortarExecucao(mensagem)
    

class AbortarExecucao(Exception):
    pass


