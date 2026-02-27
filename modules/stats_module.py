import json, os, collections
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from customtkinter import *
from datetime import date, datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils.calendar_util import CalendarPicker

def calculate_doomsday_odd11(y):
    anchor = {0: 2, 1: 0, 2: 5, 3: 3}[(y // 100) % 4]
    t = y % 100
    v = t
    steps = [f"Anno XX{t:02d}"]
    if v % 2 != 0: v += 11; steps.append(f"Dispari +11 = {v}")
    v //= 2; steps.append(f"Diviso 2 = {v}")
    if v % 2 != 0: v += 11; steps.append(f"Dispari +11 = {v}")
    rem = v % 7; diff = (7 - rem) % 7; final = (diff + anchor) % 7
    steps.append(f"7-({v}%7)={diff} | Doomsday={final}")
    return final, steps

class StatsFrame(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.filter_mode = "Giorno Preciso"
        self.filter_diff = "facile"
        self.setup_ui()
        self.refresh_all()

    def setup_ui(self):
        # 1. Header Filtri
        f_bar = CTkFrame(self, fg_color="#2b2b2b")
        f_bar.pack(fill="x", padx=10, pady=10)
        
        self.seg_m = CTkSegmentedButton(f_bar, values=["Giorno Preciso", "Solo Doomsday"], command=self.update_f)
        self.seg_m.set(self.filter_mode); self.seg_m.pack(side="left", padx=15, pady=10)
        
        self.seg_d = CTkSegmentedButton(f_bar, values=["Facile", "Medio", "Difficile"], command=self.update_f)
        self.seg_d.set(self.filter_diff.capitalize()); self.seg_d.pack(side="left", padx=15)

        # 2. Contenitore Principale
        self.main_c = CTkFrame(self, fg_color="transparent")
        self.main_c.pack(fill="both", expand=True)
        
        # 3. SIDEBAR (Creata PRIMA degli elementi che contiene)
        self.side = CTkFrame(self.main_c, width=320)
        self.side.pack(side="left", fill="y", padx=10, pady=10)
        
        # --- ORA PUOI AGGIUNGERE LO SWITCH A SELF.SIDE ---
        self.sw_continuity = CTkSwitch(self.side, text="Linea Continua", command=lambda: self.refresh_all())
        self.sw_continuity.select()
        self.sw_continuity.pack(pady=10)

        CTkLabel(self.side, text="Vista Temporale:", font=("Arial", 12)).pack(pady=(5,0))
        self.view_opt = CTkOptionMenu(self.side, values=["Sempre", "Giorno", "Settimana", "Mese"], command=lambda _: self.refresh_all())
        self.view_opt.set("Sempre"); self.view_opt.pack(pady=5)

        CTkLabel(self.side, text="Seleziona Periodo:", font=("Arial", 12)).pack(pady=(5,0))
        self.btn_calendar = CTkButton(self.side, text="📅 Scegli Data", command=self.open_calendar)
        self.btn_calendar.pack(pady=5)
        self.selected_date_str = date.today().strftime("%Y-%m-%d")

        CTkLabel(self.side, text="Raggruppamento:", font=("Arial", 12)).pack(pady=(5,0))
        self.group_opt = CTkOptionMenu(self.side, values=["Nessuno", "Giorno", "Settimana"], command=lambda _: self.refresh_all())
        self.group_opt.set("Giorno"); self.group_opt.pack(pady=5)

        self.stats_box = CTkTextbox(self.side, width=300, height=300, font=("Consolas", 12))
        self.stats_box.pack(pady=10, padx=10)
        
        # 4. Area Grafico
        self.chart_c = CTkFrame(self.main_c, fg_color="#1e1e1e")
        self.chart_c.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def update_f(self, _=None):
        self.filter_mode = self.seg_m.get()
        self.filter_diff = self.seg_d.get().lower()
        self.refresh_all()

    def update_nav_options(self, choice):
        # Logica per popolare il menu "Seleziona Periodo" in base alla vista
        if choice == "Sempre": self.nav_opt.configure(values=["Tutto lo storico"])
        elif choice == "Giorno": self.nav_opt.configure(values=["Oggi", "Ieri"])
        elif choice == "Settimana": self.nav_opt.configure(values=["Questa", "Scorsa"])
        else: self.nav_opt.configure(values=["Questo Mese", "Mese Scorso"])
        self.nav_opt.set(self.nav_opt.cget("values")[0])
        self.refresh_all()

    def refresh_all(self):
        plt.close('all') 
        for w in self.chart_c.winfo_children():
            w.destroy()
        if not os.path.exists("doomsday_stats_v2.json"): return
        with open("doomsday_stats_v2.json", "r") as f: all_data = json.load(f)
        
        # 1. FILTRO PER MODALITÀ E DIFFICOLTÀ
        data = [d for d in all_data if d["mode"] == self.filter_mode and d["difficulty"] == self.filter_diff]
        
        # 2. FILTRO TEMPORALE (Basato su View e Navigazione)
        view = self.view_opt.get()
        anchor = getattr(self, "anchor_date", date.today())
        now = datetime.now()
        
        filtered_data = []
        for d in data:
            dt = datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S").date()
            keep = False
            
            if view == "Sempre":
                keep = True
            elif view == "Giorno":
                # Se è "Sempre", il calendario agisce come selettore di giorno singolo
                if dt == anchor: keep = True
            elif view == "Settimana":
                # Range di 7 giorni che finisce alla data scelta
                start_range = anchor - timedelta(days=6)
                if start_range <= dt <= anchor: keep = True
            elif view == "Mese":
                # Tutti i dati del mese solare della data scelta
                if dt.month == anchor.month and dt.year == anchor.year: keep = True
            
            if keep: filtered_data.append(d)

        data = filtered_data # Sovrascriviamo con i dati filtrati per tempo
        
        if not data:
            for w in self.chart_c.winfo_children(): w.destroy()
            self.stats_box.configure(state="normal"); self.stats_box.delete("0.0", "end")
            self.stats_box.insert("0.0", "Nessun dato per questo periodo."); self.stats_box.configure(state="disabled")
            return

        # --- LOGICA SIDEBAR (Stats testo) ---
        self.stats_box.configure(state="normal"); self.stats_box.delete("0.0", "end")
        view = self.view_opt.get()
        if view == "Giorno":
            header_title = f"DATA: {self.selected_date_str}"
        else:
            header_title = f"VISTA: {view}"

        txt = f"{header_title}\n" + "-"*35 + "\n"
        
        cor = [d["time"] for d in data if d["correct"]]
        wr = f"{(len(cor)/len(data)*100):.0f}%" if data else "0%"
        best = f"{min(cor):.1f}s" if cor else "--"
        avg = f"{sum(cor)/len(cor):.1f}s" if cor else "--"
        txt += f"RECORD: {best}\nMEDIA:  {avg}\nWINRATE: {wr}\n"
        self.stats_box.insert("end", txt); self.stats_box.configure(state="disabled")

        # --- GRAFICO ---
        for w in self.chart_c.winfo_children(): w.destroy()
        plt.style.use('dark_background')
        fig, ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#1e1e1e'); ax1.set_facecolor('#1e1e1e')
        
        g_t = collections.defaultdict(list)
        mode = self.group_opt.get()
        plot_dates_dict = {}
        all_keys = []

        for d in data:
            dt = datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S")
            if mode == "Giorno": key = dt.strftime("%d/%m")
            elif mode == "Settimana": key = f"Sett {dt.strftime('%W')}"
            else: key = d["timestamp"][-8:]
            
            if key not in all_keys: all_keys.append(key)
            if d["correct"]: g_t[key].append(d["time"])
            if key not in plot_dates_dict: plot_dates_dict[key] = dt

        y_vals = [sum(g_t[k])/len(g_t[k]) if g_t[k] else None for k in all_keys]
        is_continuous = self.sw_continuity.get()
        
        if is_continuous:
            plot_keys = [all_keys[i] for i in range(len(all_keys)) if y_vals[i] is not None]
            plot_y = [v for v in y_vals if v is not None]
        else:
            plot_keys = all_keys
            plot_y = y_vals

        if plot_y:
            ax1.plot(plot_keys, plot_y, color='yellow', label="Tempo", linewidth=2)
            
            # Media Mobile (solo se ci sono almeno 2 punti)
            valid_y = [v for v in plot_y if v is not None]
            if len(valid_y) > 1:
                y_ma = [valid_y[0]] + [(valid_y[i] + valid_y[i-1])/2 for i in range(1, len(valid_y))]
                valid_keys = [plot_keys[i] for i in range(len(plot_y)) if plot_y[i] is not None]
                ax1.plot(valid_keys, y_ma, color='#3b8ed0', linestyle='--', alpha=0.7, label="Media (n, n-1)")

        # Separatori
        last_dt = None
        for i, k in enumerate(plot_keys):
            curr_dt = plot_dates_dict.get(k)
            if last_dt and curr_dt:
                if curr_dt.date() != last_dt.date():
                    ax1.axvline(i - 0.5, color='gray', alpha=0.2)
                if curr_dt.isocalendar()[1] != last_dt.isocalendar()[1]:
                    ax1.axvline(i - 0.5, color='#555555', alpha=0.6)
            last_dt = curr_dt

        ax1.tick_params(axis='x', rotation=35, labelsize=7)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_c)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def open_calendar(self):
        CalendarPicker(self, self.selected_date_str, self.on_date_selected)

    def on_date_selected(self, selected_date):
        # selected_date è un oggetto datetime.date
        self.anchor_date = selected_date
        view = self.view_opt.get()
        
        # Aggiorna il testo del pulsante per riflettere il periodo
        if view == "Settimana":
            start = self.anchor_date - timedelta(days=6)
            self.btn_calendar.configure(text=f"📅 {start.strftime('%d/%m')} - {self.anchor_date.strftime('%d/%m')}")
        elif view == "Mese":
            self.btn_calendar.configure(text=f"📅 Mese: {self.anchor_date.strftime('%b %Y')}")
        else:
            self.btn_calendar.configure(text=f"📅 Giorno: {self.anchor_date.strftime('%Y-%m-%d')}")
            
        self.refresh_all()