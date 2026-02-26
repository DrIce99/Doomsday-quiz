import calendar
import json
import os
from datetime import datetime, date
from customtkinter import *

class CalendarPicker(CTkToplevel):
    def __init__(self, master, current_selection, callback, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Seleziona Data")
        self.geometry("350x400")
        self.after(10, self.lift) # Porta la finestra in primo piano
        self.grab_set() # Blocca l'interazione con la finestra sotto

        self.callback = callback
        self.view_date = datetime.strptime(current_selection, "%Y-%m-%d").date() if "-" in current_selection else date.today()
        
        # Carica date con dati
        self.data_dates = self.load_played_dates()
        self.setup_ui()

    def load_played_dates(self):
        if not os.path.exists("doomsday_stats_v2.json"): return set()
        with open("doomsday_stats_v2.json", "r") as f:
            data = json.load(f)
            return {datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S").date() for d in data}

    def setup_ui(self):
        for w in self.winfo_children(): w.destroy()
        
        # Header: Mese e Anno
        hdr = CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=10)
        
        CTkButton(hdr, text="<", width=30, command=self.prev_month).pack(side="left", padx=10)
        self.lbl_month = CTkLabel(hdr, text=self.view_date.strftime("%B %Y").upper(), font=("Arial", 14, "bold"))
        self.lbl_month.pack(side="left", expand=True)
        CTkButton(hdr, text=">", width=30, command=self.next_month).pack(side="right", padx=10)

        # Griglia Giorni
        grid = CTkFrame(self, fg_color="transparent")
        grid.pack(expand=True, fill="both", padx=10, pady=5)

        days = ["Lu", "Ma", "Me", "Gi", "Ve", "Sa", "Do"]
        for i, d in enumerate(days):
            CTkLabel(grid, text=d, font=("Arial", 11, "bold"), text_color="gray").grid(row=0, column=i)

        # Recuperiamo il colore di sfondo del tema corrente per "nascondere" il bordo
        bg_color = ThemeManager.theme["CTkFrame"]["fg_color"]

        cal = calendar.monthcalendar(self.view_date.year, self.view_date.month)
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                if day == 0: continue
                
                cur_date = date(self.view_date.year, self.view_date.month, day)
                is_played = cur_date in self.data_dates
                
                # LOGICA COLORI CORRETTA
                # Se giocato: Verde. Se non giocato: Trasparente (usa il colore del frame)
                color = "#2ecc71" if is_played else "transparent"
                
                # Se non giocato, il bordo deve avere lo stesso colore dello sfondo
                # per evitare il crash di Tkinter
                b_color = "white" if is_played else bg_color
                border = 1 if is_played else 0
                
                btn = CTkButton(grid, text=str(day), width=35, height=35, 
                                fg_color=color, 
                                border_width=border,
                                border_color=b_color, # Niente più "transparent" qui
                                hover_color="#3b8ed0",
                                command=lambda d=cur_date: self.select_date(d))
                btn.grid(row=r+1, column=c, padx=2, pady=2)

    def prev_month(self):
        m, y = (self.view_date.month - 1, self.view_date.year) if self.view_date.month > 1 else (12, self.view_date.year - 1)
        self.view_date = date(y, m, 1)
        self.setup_ui()

    def next_month(self):
        m, y = (self.view_date.month + 1, self.view_date.year) if self.view_date.month < 12 else (1, self.view_date.year + 1)
        self.view_date = date(y, m, 1)
        self.setup_ui()

    def select_date(self, d):
        # Passiamo l'oggetto date direttamente al callback
        self.callback(d) 
        self.destroy()