import json, os
import customtkinter
import colorsys
from customtkinter import *

class ThemeManagerFrame(CTkFrame):
    def __init__(self, master, home_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.home_callback = home_callback
        self.user_themes_dir = "themes/user/"
        if not os.path.exists(self.user_themes_dir): os.makedirs(self.user_themes_dir)
        self.setup_main_view()

    def setup_main_view(self):
        for w in self.winfo_children(): w.destroy()
        CTkLabel(self, text="🎨 Gestione Temi", font=("Arial", 24, "bold")).pack(pady=20)
        
        container = CTkScrollableFrame(self, width=550, height=450)
        container.pack(pady=10, padx=20, fill="both", expand=True)

        # Temi Predefiniti
        CTkLabel(container, text="SISTEMA", font=("Arial", 14, "bold"), text_color="gray").pack(pady=10)
        for t in ["blue", "green", "dark-blue"]:
            CTkButton(container, text=t.capitalize(), fg_color="transparent", border_width=1,
                      command=lambda x=t: self.apply_theme(x)).pack(pady=2, fill="x", padx=40)

        # Temi Utente
        CTkLabel(container, text="I TUOI TEMI", font=("Arial", 14, "bold"), text_color="gray").pack(pady=20)
        user_files = [f for f in os.listdir(self.user_themes_dir) if f.endswith(".json")]
        for f in user_files:
            name = f.replace(".json", "")
            CTkButton(container, text=name, command=lambda x=f: self.apply_theme(os.path.join(self.user_themes_dir, x))).pack(pady=2, fill="x", padx=40)

        btn_bar = CTkFrame(self, fg_color="transparent")
        btn_bar.pack(side="bottom", pady=20, fill="x")
        CTkButton(btn_bar, text="➕ Crea Nuovo Tema", fg_color="#2ecc71", command=self.setup_editor_view).pack(side="left", padx=20, expand=True)
        CTkButton(btn_bar, text="🏠 Home", command=self.home_callback).pack(side="left", padx=20, expand=True)

    def setup_editor_view(self):
        for w in self.winfo_children(): w.destroy()
        
        CTkLabel(self, text="🛠️ Advanced Theme Editor", font=("Arial", 22, "bold")).pack(pady=15)
        edit_area = CTkScrollableFrame(self, width=500, height=450)
        edit_area.pack(fill="both", expand=True, padx=30, pady=10)

        # --- SEZIONE ACCENTO (Pulsanti) ---
        CTkLabel(edit_area, text="COLORE ACCENTO (RGB)", font=("Arial", 13, "bold")).pack(pady=5)
        self.sl_r, self.lbl_r = self.create_labeled_slider(edit_area, "Rosso", 59)
        self.sl_g, self.lbl_g = self.create_labeled_slider(edit_area, "Verde", 142)
        self.sl_b, self.lbl_b = self.create_labeled_slider(edit_area, "Blu", 208)

        # --- SEZIONE SFONDO (HSV con Limite Saturazione) ---
        CTkLabel(edit_area, text="COLORE SFONDO (Tonalità & Luminosità)", font=("Arial", 13, "bold")).pack(pady=(20, 5))
        # Tonalità (0-360 gradi)
        self.sl_h, self.lbl_h = self.create_labeled_slider(edit_area, "Tonalità (H)", 210, max_val=360)
        # Luminosità (0-100%)
        self.sl_v, self.lbl_v = self.create_labeled_slider(edit_area, "Luminosità (V)", 15, max_val=100)
        
        CTkLabel(edit_area, text="*Saturazione bloccata al 12% per eleganza", font=("Arial", 10, "italic"), text_color="gray").pack()

        self.sw_holographic = CTkSwitch(edit_area, text="Effetto Olografico (Solo Bordo)", 
                                        command=self.update_preview)
        self.sw_holographic.pack(pady=15)

        # --- PREVIEW ---
        self.preview_box = CTkFrame(self, border_width=2)
        self.preview_box.pack(fill="x", padx=50, pady=20)
        self.preview_lbl = CTkLabel(self.preview_box, text="ANTEPRIMA TESTO", font=("Arial", 12, "bold"))
        self.preview_lbl.pack(pady=5)
        self.preview_btn = CTkButton(self.preview_box, text="Pulsante Esempio")
        self.preview_btn.pack(pady=10)

        # Salvataggio (Resto uguale...)
        save_f = CTkFrame(self, fg_color="transparent")
        save_f.pack(fill="x", pady=15)
        self.entry_name = CTkEntry(save_f, placeholder_text="Nome del tema...")
        self.entry_name.pack(side="left", padx=20, expand=True, fill="x")
        CTkButton(save_f, text="💾 Salva", command=self.save_theme).pack(side="left", padx=10)
        CTkButton(save_f, text="❌ Esci", fg_color="gray", command=self.setup_main_view).pack(side="left", padx=20)
        
        self.update_preview()

    def create_labeled_slider(self, master, text, start_val, max_val=255):
        f = CTkFrame(master, fg_color="transparent")
        f.pack(fill="x", padx=20)
        lbl = CTkLabel(f, text=f"{text}: {start_val}", width=130, anchor="w")
        lbl.pack(side="left")
        sl = CTkSlider(f, from_=0, to=max_val, number_of_steps=max_val, command=lambda _: self.update_preview())
        sl.set(start_val)
        sl.pack(side="right", fill="x", expand=True, padx=10)
        return sl, lbl

    def update_preview(self, _=None):
        import colorsys
        
        # 1. Recupero valori dagli slider Accento (RGB)
        r, g, b = int(self.sl_r.get()), int(self.sl_g.get()), int(self.sl_b.get())
        accent_hex = "#{:02x}{:02x}{:02x}".format(r, g, b)
        
        # 2. Recupero valori dagli slider Sfondo (HSV con saturazione bloccata)
        h = self.sl_h.get() / 360.0
        s = 0.12  # Saturazione bassa per eleganza
        v = self.sl_v.get() / 100.0
        
        rgb_bg = colorsys.hsv_to_rgb(h, s, v)
        bg_hex = "#{:02x}{:02x}{:02x}".format(int(rgb_bg[0]*255), int(rgb_bg[1]*255), int(rgb_bg[2]*255))
        
        # 3. Logica Olografica vs Piena
        is_holo = self.sw_holographic.get()
        
        if is_holo:
            # Effetto Olografico: Interno trasparente, bordo colorato, testo colorato
            btn_fg = "transparent"
            btn_border_w = 2
            btn_text_color = accent_hex
            btn_hover = accent_hex # Al passaggio diventa pieno
            btn_hover_text = self.get_contrast_color(r, g, b) # Testo cambia per contrasto su hover
        else:
            # Effetto Standard: Interno colorato, niente bordo, testo contrastato
            btn_fg = accent_hex
            btn_border_w = 0
            btn_text_color = self.get_contrast_color(r, g, b)
            btn_hover = accent_hex # Resta uguale o potresti scurirlo leggermente
            btn_hover_text = btn_text_color

        # 4. Aggiornamento Etichette Testuali
        self.lbl_r.configure(text=f"Rosso (R): {r}")
        self.lbl_g.configure(text=f"Verde (G): {g}")
        self.lbl_b.configure(text=f"Blu (B): {b}")
        self.lbl_h.configure(text=f"Tonalità H: {int(self.sl_h.get())}°")
        self.lbl_v.configure(text=f"Luminosità V: {int(self.sl_v.get())}%")

        # 5. Applicazione all'Anteprima (Preview)
        self.preview_box.configure(fg_color=bg_hex, border_color=accent_hex)
        self.preview_lbl.configure(text_color=accent_hex)
        
        self.preview_btn.configure(
            fg_color=btn_fg,
            border_color=accent_hex,
            border_width=btn_border_w,
            text_color=btn_text_color,
            hover_color=btn_hover
        )


    def get_contrast_color(self, r, g, b):
        """Calcola se il testo deve essere bianco o nero (Luminanza YIQ)"""
        luminance = (r * 299 + g * 587 + b * 114) / 1000
        return "#000000" if luminance > 128 else "#FFFFFF"

    def save_theme(self):
        import colorsys, json, os, customtkinter
        name = self.entry_name.get().strip() or "CustomTheme"
        
        # 1. Colore Accento (RGB)
        r, g, b = int(self.sl_r.get()), int(self.sl_g.get()), int(self.sl_b.get())
        accent_hex = "#{:02x}{:02x}{:02x}".format(r, g, b)
        # Colore di contrasto (Nero o Bianco) per quando il pulsante è PIENO
        txt_on_accent = self.get_contrast_color(r, g, b)

        # 2. Colore Sfondo (HSV -> RGB)
        h, v = self.sl_h.get() / 360.0, self.sl_v.get() / 100.0
        rgb_tuple = colorsys.hsv_to_rgb(h, 0.12, v)
        bg_r, bg_g, bg_b = [int(x * 255) for x in rgb_tuple]
        bg_hex = "#{:02x}{:02x}{:02x}".format(bg_r, bg_g, bg_b)

        # 3. Caricamento Template
        path_ctk = os.path.dirname(customtkinter.__file__)
        with open(os.path.join(path_ctk, "assets", "themes", "blue.json"), "r") as f:
            theme_data = json.load(f)

        is_holo = self.sw_holographic.get()
        
        # --- LOGICA COLORI ---
        # Se olografico: sfondo=bg, testo=accento. Se pieno: sfondo=accento, testo=contrasto.
        btn_fg = [bg_hex, bg_hex] if is_holo else [accent_hex, accent_hex]
        btn_text = [accent_hex, accent_hex] if is_holo else [txt_on_accent, txt_on_accent]
        btn_border = 2 if is_holo else 0
        
        # 4. AGGIORNAMENTO GLOBALE
        theme_data["CTk"]["fg_color"] = [bg_hex, bg_hex]
        
        # Frame e Pannelli
        for frame_type in ["CTkFrame", "CTkScrollableFrame", "CTkTabview"]:
            if frame_type in theme_data:
                theme_data[frame_type]["fg_color"] = [bg_hex, bg_hex]
                theme_data[frame_type]["top_fg_color"] = [bg_hex, bg_hex]
                theme_data[frame_type]["border_color"] = [accent_hex, accent_hex]

        # Pulsanti Standard
        theme_data["CTkButton"].update({
            "fg_color": btn_fg,
            "text_color": btn_text,
            "border_color": [accent_hex, accent_hex],
            "border_width": btn_border,
            "hover_color": [accent_hex, accent_hex],
            # IMPORTANTE: Su hover il pulsante diventa pieno, quindi il testo deve cambiare colore!
            "text_color_disabled": [txt_on_accent, txt_on_accent] 
        })

        # Segmented Buttons (Modalità/Difficoltà)
        theme_data["CTkSegmentedButton"].update({
            "fg_color": [bg_hex, bg_hex],
            "selected_color": [accent_hex, accent_hex],
            "selected_hover_color": [accent_hex, accent_hex],
            "unselected_color": [bg_hex, bg_hex],
            "unselected_hover_color": [accent_hex, accent_hex],
            "text_color": [txt_on_accent, txt_on_accent],
            "text_color_disabled": [txt_on_accent, txt_on_accent]
        })

        # Altri componenti (Switch, Menu, ecc.)
        theme_data["CTkLabel"]["text_color"] = [accent_hex, accent_hex]
        theme_data["CTkSwitch"]["progress_color"] = [accent_hex, accent_hex]
        theme_data["CTkOptionMenu"].update({
            "fg_color": [accent_hex, accent_hex],
            "button_color": [accent_hex, accent_hex],
            "text_color": [txt_on_accent, txt_on_accent]
        })

        # 5. Salvataggio
        file_path = os.path.join(self.user_themes_dir, f"{name}.json")
        with open(file_path, "w") as f:
            json.dump(theme_data, f, indent=4)
        
        self.setup_main_view()

    def apply_theme(self, theme_path):
        from game import save_last_theme # Import locale per evitare circolarità
        set_default_color_theme(theme_path)
        save_last_theme(theme_path) # Salva nel config.json
        self.home_callback()