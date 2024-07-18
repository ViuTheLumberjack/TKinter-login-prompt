import tkinter as tk
import random
import string
import configparser
import os
import markdown
from tkinterweb import HtmlFrame
from PIL import ImageTk, Image

# setting da file
config = configparser.ConfigParser(allow_no_value=True)
config.read_file(open(r'config.txt'))
LOGIN_PASSWORD = config.get('Password', 'password_accesso')
PASSWORD_ATTEMPTS = int(config.get('Password', 'numero_password'))
PASSWORDS = [config.get('Password', f'password{i}') for i in range(1,PASSWORD_ATTEMPTS)]
COLUMN_COUNT = int(config.get('Sfondo', 'numero_colonne'))
COLUMN_UPDATE = int(config.get('Sfondo', 'frequenza_aggiornamento'))
ACCESS_TIME = int(config.get('Tempistiche', 'attesa_login_corretto'))
START_TIME = int(config.get('Tempistiche', 'attesa_iniziale'))
RETRY_TIME= int(config.get('Tempistiche', 'attesa_riprova'))
CHARACTER_TIME = int(config.get('Tempistiche', 'attesa_carattere'))
ENTER_TIME = int(config.get('Tempistiche', 'attesa_invio')) 
FS = config.get('Filesystem', 'cartella_dati')

class Fullscreen_Window:
    def __init__(self):
        self.tk = tk.Tk()
        self.is_fullscreen = True
        self.tk.attributes("-fullscreen", self.is_fullscreen)
        self.tk.bind("<F1>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        self._job = None
        self.colonne = []
        # Numero di colonne desiderato
        self.num_colonne = COLUMN_COUNT
        # Creazione delle colonne
        for _ in range(self.num_colonne):
            colonna = tk.Label(self.tk, font=("Courier", 18), fg="green", bg='black', justify=tk.LEFT)
            self.colonne.append(colonna)

        # Avvio dell'aggiornamento delle colonne
        self.update_columns()

    def cancel(self):
        if self._job is not None:
            self.tk.after_cancel(self._job)
            self._job = None
    
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

        self._job = self.tk.after(COLUMN_UPDATE, self.update_columns)  # aggiorna ogni 100 millisecondi

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen  # Just toggling the boolean
        self.tk.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def end_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.tk.attributes("-fullscreen", False)
        return "break"

    def kill_window(self, event=None):
        self.cancel()
        self.tk.destroy()

class AutoLogin_FSM:
    def __init__(self):
        # Le password che voglio usare per fare le prove di login
        self.attempts = PASSWORDS + [LOGIN_PASSWORD] 
        self.password = ""
        self.num_attempts = 0

    def start(self):
        self.index = 0
        self.password = self.attempts[self.num_attempts]

    def typing(self):
        if self.index < len(self.password) and self.num_attempts < len(self.attempts):
            self.index += 1
            return self.password[:self.index]
        elif self.index >= len(self.password) and self.num_attempts < len(self.attempts):
            self.num_attempts += 1
            return "next"
        else:
            return "end"

    def end(self):
        return "end"

class Login_Window(Fullscreen_Window): 
    def __init__(self):
        Fullscreen_Window.__init__(self)
        self.tk.configure(bg='black')  # colore di sfondo nero
        self.tk.title("Login")
        
        self.login_fsm = AutoLogin_FSM()
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
        self.password_attempt = tk.StringVar()
        self.entry = tk.Entry(self.grid, font=("Courier", 24), fg="green", bg='black', textvariable=self.password_attempt)
        self.entry.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.entry.grid(row=1, column=0, sticky='s')
        self.entry.focus_set()
        self.grid.pack(expand=True, anchor=tk.CENTER)

        self.tk.after(START_TIME, self.login_attempt)

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
            self.tk.after(RETRY_TIME, self.login_attempt)

    def login_attempt(self):
        self.label.config(text="Inserisci la password:")
        self.login_fsm.start()
        self.write_password()

    def write_password(self):
        password = self.login_fsm.typing()
        if(password != "end" and password != "next"):
            self.password_attempt.set(password)
            #self.entry.update()
            self.tk.after(CHARACTER_TIME, self.write_password)
        elif(password == "next"):
            self.tk.after(ENTER_TIME, self.login)

    def correct_login(self):
        self.label = tk.Label(self.grid, text=f"Password corretta", font=("Courier", 24), fg="green", bg='black')
        self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # posiziona al centro dello schermo
         # apro il filesystem
        #self.tk.after(ACCESS_TIME, self.open_filesystem)

    def open_filesystem(self):
        self.grid.destroy()
        filesystem = FileSystem_Window()
        self.kill_window()
        filesystem.tk.mainloop()


class FileSystem_Window(Fullscreen_Window):
    def __init__(self):
        Fullscreen_Window.__init__(self)
        self.tk.configure(bg='black')
        self.tk.title("File System")
        self.tk.bind("<F11>", self.toggle_fullscreen)
        self.tk.bind("<Escape>", self.end_fullscreen)
        self.tk.bind("<Return>", self.change_path)
        self.tk.bind("<KP_Enter>", self.change_path)
        self.tk.bind("<BackSpace>", self.go_back)
        self.tk.bind("<Up>", self.change_focus)
        self.tk.bind("<Down>", self.change_focus)

        self.resize = False
        self.has_bio = False
        self.has_image = False
        self.has_overlay = False
        # elementi di struttura 
        self.grid = tk.Frame(self.tk, bg='black')
        self.grid.place(relx=0.5, rely=0.5, relwidth=.90, relheight=.90, anchor=tk.CENTER)
        # leggo la cartella da dove parte il programma e faccio vedere i 
        # contenuti della directory che contiene la struttura da far vedere
        self.base_path =  os.path.dirname(os.path.realpath(__file__)) + f'/{FS}'
        self.current_path = self.base_path
        self.entries = tk.StringVar(value=os.listdir(self.current_path))
        # inizializzo la struttura 
        self.init_listbox(80, 20, 0, 0)
        self.grid.pack(expand=True, anchor=tk.CENTER)

    def init_listbox(self, _width, _height, _row, _column):
        self.listbox = tk.Listbox(self.grid, bg='black', fg='green', font=("Courier", 20),
                                   selectmode=tk.SINGLE, listvariable=self.entries, 
                                   width=_width, height=_height, selectbackground='black', selectforeground='green')
        
        self.listbox.select_set(0) 
        self.listbox.focus_set()
        self.listbox.grid(row=_row, column=_column, columnspan=2) 

    def change_path(self, event=None):
        selection = self.listbox.get(self.listbox.curselection())
        selected_path = self.current_path + f'/{selection}'
        if os.path.isdir(selected_path):
            self.current_path = selected_path
            self.update_list()
        elif os.path.isfile(selected_path):
            self.open_popup(selected_path)

    def update_list(self):
        selected = self.listbox.curselection()
        if selected:
            self.listbox.select_clear(selected[0])

        directory_files = os.listdir(self.current_path)
        if 'bio.md' in directory_files:
            directory_files.remove('bio.md')
            self.has_bio = True
            self.resize = True
        else:  
            self.has_bio = False

        if 'image.jpg' in directory_files:
            directory_files.remove('image.jpg')
            self.has_image = True
            self.resize = True
        else:
            self.has_image = False
        
        if self.resize == True:
            self.grid.destroy()
            self.grid = tk.Frame(self.tk, bg='black')
            self.grid.place(relx=0.5, rely=0.5, relwidth=.90, relheight=.90, anchor=tk.CENTER)
            self.grid.pack(expand=True, anchor=tk.CENTER)
            if self.has_bio and self.has_image:
                self.show_bio()
                self.html_frame.grid(row=0, column=0)
                self.show_image()
                self.canvas.grid(row=0, column=1)
                self.init_listbox(80, 5, 1, 0)
                resize = False
            else:
                self.html_frame.destroy()
                self.canvas.destroy()
                self.init_listbox(80, 20, 0, 0)
                resize = False

        self.entries.set(directory_files)
        if(self.listbox.size() > 0):
            self.listbox.select_set(0)
            self.listbox.activate(0) 

        self.listbox.update()

    def show_bio(self):
        m_html = "<body>" + markdown.markdown(open(self.current_path + "/bio.md", "r").read()) + "</body>"
        self.html_frame = HtmlFrame(self.grid, vertical_scrollbar=False, messages_enabled = False)
        self.html_frame.load_html(m_html) 
        self.html_frame.add_css('''
            body {
                background-color: #000000;
                color: #007e00;
                font-family: Courier, sans-serif;
            }
        ''')

    def resize_image(self, image_path, base_width=None, base_height=None):
        img = Image.open(image_path)
        w, h = img.size

        if base_width and base_height:
            raise ValueError("Specify only one dimension (width or height)")
        elif base_width:
            w_percent = base_width / float(w)
            new_height = int(h * w_percent)
            new_size = (base_width, new_height)
        elif base_height:
            h_percent = base_height / float(h)
            new_width = int(w * h_percent)
            new_size = (new_width, base_height)
        else:
            raise ValueError("Specify either width or height")

        resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
        return resized_img

    def show_image(self):
        self.img = ImageTk.PhotoImage(self.resize_image(self.current_path + "/image.jpg", base_width=460))
        self.canvas = tk.Canvas(self.grid, borderwidth=0, width=460, height=520)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img)

    def go_back(self, event=None):
        if self.has_overlay == True:
            self.hide_overlay()
            return

        if self.current_path != self.base_path:
            self.current_path = os.path.dirname(self.current_path.rstrip('/'))
            self.update_list()

        directory_files = os.listdir(self.current_path)
        if 'bio.md' not in directory_files:
            self.resize = self.has_bio
            self.has_bio = False

        if 'image.jpg' not in directory_files:
            self.resize = self.has_image
            self.has_image = False

    def change_focus(self, event=None):
        if self.listbox.size() > 0:
            selected = self.listbox.curselection()[0]

            if event.keysym == 'Up':
                if selected == 0:
                    self.listbox.select_clear(selected)
                    self.listbox.select_set(self.listbox.size()-1)
                    self.listbox.activate(self.listbox.size()-1)
                else:
                    self.listbox.select_clear(selected)
                    self.listbox.select_set(selected-1 if selected > 0 else self.listbox.size()-1)
            elif event.keysym == 'Down':
                if selected == self.listbox.size()-1:
                    self.listbox.select_clear(self.listbox.size()-1)
                    self.listbox.select_set(0)
                    self.listbox.activate(0)
                else:
                    self.listbox.select_clear(selected)
                    self.listbox.select_set((selected+1) % (self.listbox.size()))

    def open_popup(self, file_path):
        self.overlay_frame = tk.Frame(self.tk, bg='black', bd=2, relief=tk.RAISED)
        m_html = "<body>" + markdown.markdown(open(file_path, "r").read()) + "</body>"
        self.overlay_text = HtmlFrame(self.overlay_frame, vertical_scrollbar=False, messages_enabled = False)
        self.overlay_text.load_html(m_html) 
        self.overlay_text.add_css('''
            body {
                background-color: #000000;
                color: #007e00;
                font-family: Courier, sans-serif;
                font-size: 40;
            }
        ''')
 
        self.overlay_text.pack(expand=True)
        self.show_overlay()

    def show_overlay(self):
        # Show overlay
        self.overlay_frame.place(relx=0.5, rely=0.5, relwidth=.90, relheight=.90, anchor=tk.CENTER)
        self.has_overlay = True

    def hide_overlay(self):
        # Hide overlay
        self.overlay_frame.place_forget()
        self.overlay_frame.destroy()
        self.has_overlay = False

# Creazione della finestra principale
finestra = Login_Window()

# Loop principale della finestra
finestra.tk.mainloop()
