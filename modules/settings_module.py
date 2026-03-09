from customtkinter import *
import json
import os
from managers.theme_manager import ThemeManagerFrame

CONFIG_FILE = "config.json"

class SettingsFrame(CTkFrame):
    def __init__(self, master, home_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.home_callback = home_callback
        self.config = self.load_config()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDEBAR
        self.sidebar = CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        CTkLabel(self.sidebar, text="⚙️ MENU", font=("Arial", 18, "bold")).pack(pady=20)
        
        # Categorie
        CTkButton(self.sidebar, text="Generali", fg_color="transparent", anchor="w",
                  command=lambda: self.show_category("Generali")).pack(fill="x", padx=10, pady=5)

        CTkButton(self.sidebar, text="Input & Tastiera", fg_color="transparent", anchor="w",
                  command=lambda: self.show_category("Input")).pack(fill="x", padx=10, pady=5)

        # --- RIPRISTINO TEMI ---
        CTkButton(self.sidebar, text="🎨 Temi Avanzati", fg_color="transparent", anchor="w",
                  command=lambda: self.show_category("Temi")).pack(fill="x", padx=10, pady=5)

        self.btn_back = CTkButton(self.sidebar, text="💾 SALVA E ESCI", fg_color="#2ecc71", 
                                  command=self.exit_settings)
        self.btn_back.pack(side="bottom", pady=20, padx=10)

        # 2. PANNELLO CONTENUTO
        self.content_frame = CTkScrollableFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        self.show_category("Generali")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                try:
                    cfg = json.load(f)
                except:
                    cfg = {}
        else:
            cfg = {}

        cfg.setdefault("last_theme", "blue")
        cfg.setdefault("confirm_required", False)

        return cfg

    def show_category(self, name):
        for child in self.content_frame.winfo_children():
            child.destroy()

        if name == "Generali":
            self.draw_general_settings()
        elif name == "Input":
            self.draw_input_settings()
        elif name == "Temi":
            # Richiama la vecchia interfaccia ThemeManagerFrame nel pannello di destra
            ThemeManagerFrame(self.content_frame, lambda: print("Tema aggiornato")).pack(fill="both", expand=True)

    def draw_general_settings(self):
        CTkLabel(self.content_frame, text="Impostazioni Generali", font=("Arial", 20, "bold")).pack(anchor="w", pady=20)
        
        # CTkLabel(self.content_frame, text="Luminosità (Esempio):").pack(anchor="w")
        # CTkSlider(self.content_frame, from_=0, to=100).pack(fill="x", pady=10)

    def draw_input_settings(self):
        CTkLabel(self.content_frame, text="Input & Tastiera", font=("Arial", 20, "bold")).pack(anchor="w", pady=20)
        
        f = CTkFrame(self.content_frame, fg_color="transparent")
        f.pack(fill="x", pady=10)
        CTkLabel(f, text="Richiedi INVIO per confermare:").pack(side="left")
        
        sw = CTkSwitch(f, text="", command=lambda: self.update_config("confirm_required", sw.get()))
        if self.config.get("confirm_required", False): sw.select()
        sw.pack(side="right")

        # lbl = CTkLabel(self.content_frame, text="Nome Profilo (Esempio Testo):")
        # lbl.pack(anchor="w", pady=(20, 0)) # <--- Qui la tupla funziona!
        
        CTkEntry(self.content_frame, placeholder_text="Inserisci nome...").pack(fill="x", pady=5)

    def update_config(self, key, value):
        self.config[key] = value

    def exit_settings(self):
        self.config["last_theme"] = ThemeManagerFrame.current_theme
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)
        self.home_callback()
