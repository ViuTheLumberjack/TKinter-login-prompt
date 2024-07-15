import tkinter as tk
import random
import string
import time
import configparser

# setting da file
config = configparser.ConfigParser(allow_no_value=True)
config.read_file(open(r'config.txt'))
LOGIN_PASSWORD = config.get('Password', 'password_accesso')
ACCESS_TIME = int(config.get('Tempistiche', 'attesa_login_corretto'))
COLUMN_COUNT = int(config.get('Sfondo', 'numero_colonne'))
COLUMN_UPDATE = int(config.get('Sfondo', 'frequenza_aggiornamento'))

class Fullscreen_Window:
    def __init__(self):
        self.tk = tk.Tk()
        self.tk.attributes('-zoomed', True)  # This just maximizes it so we can see the window. It's nothing to do with fullscreen.
        self.is_fullscreen = False
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def end_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def kill_window(self, event=None):
        self.tk.destroy()

class Login_Window(Fullscreen_Window): 
    def __init__(self):
        Fullscreen_Window.__init__(self)
        self.tk.configure(bg='black')  # colore di sfondo nero
        self.tk.title("Login")
        self.tk.bind("<Return>", self.login)
        self.tk.bind("<KP_Enter>", self.login)
        # Lista per memorizzare le colonne di testo
        self.colonne = []
        # Numero di colonne desiderato
        self.num_colonne = COLUMN_COUNT
        # Creazione delle colonne
        for _ in range(self.num_colonne):
            colonna = tk.Label(self.tk, font=("Courier", 18), fg="green", bg='black', justify=tk.LEFT)
            self.colonne.append(colonna)

        # Avvio dell'aggiornamento delle colonne
        self.update_columns()
        # Creazione della finestra di login
        self.grid = tk.Frame(self.tk, bg='black', )
        self.label = tk.Label(self.grid, text="Inserisci la password:", font=("Courier", 24), fg="green", bg='black')
        self.label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
        self.label.grid(row=0, column=0)
        self.entry = tk.Entry(self.grid, font=("Courier", 24), fg="green", bg='black')
        self.entry.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.entry.grid(row=1, column=0, sticky='s')
        self.entry.focus_set()
        self.grid.pack(expand=True, anchor=tk.CENTER)


    def login(self, event=None):
        password = self.entry.get()
        if password == LOGIN_PASSWORD:
            self.entry.destroy()
            self.label.destroy()
            self.correct_login()
            self.tk.after(ACCESS_TIME, self.tk.destroy)
        else:
            self.label.config(text="Password errata. Riprova.")
            self.entry.delete(0, tk.END)

    # Funzione per aggiornare il testo nelle colonne con caratteri casuali verticalmente
    def update_columns(self):
        caratteri = string.ascii_letters + string.digits
        altezza_colonna = self.tk.winfo_height()  # altezza della finestra
        larghezza_finestra = self.tk.winfo_width()   # larghezza della finestra
        # Calcola la larghezza della colonna
        larghezza_colonna = larghezza_finestra // self.num_colonne

        for colonna in range(self.num_colonne):
            testo = ''
            for _ in range(altezza_colonna // 20):  # numero di righe per colonna
                testo += random.choice(caratteri) + "\n"  # aggiunge un carattere seguito da un ritorno a capo
            self.colonne[colonna].config(text=testo)

            # calcola la posizione x della colonna per centrarla
            x_pos = colonna * larghezza_colonna + larghezza_colonna // 2
            self.colonne[colonna].place(x=x_pos, y=0, anchor=tk.N)

        self.tk.after(COLUMN_UPDATE, self.update_columns)  # aggiorna ogni 100 millisecondi

    # Funzione chiamata dopo 10 secondi per mostrare la password trovata
    def correct_login(self):
        self.label = tk.Label(self.grid, text=f"Password corretta", font=("Courier", 24), fg="green", bg='black')
        self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # posiziona al centro dello schermo

# Creazione della finestra principale
finestra = Login_Window()

# Loop principale della finestra
finestra.tk.mainloop()
