import json, os, collections
from customtkinter import *
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

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
        self.view_opt = CTkOptionMenu(self.side, values=["Sempre", "Ultimo Giorno", "Ultima Settimana", "Ultimo Mese"], command=self.update_nav_options)
        self.view_opt.set("Sempre"); self.view_opt.pack(pady=5)

        CTkLabel(self.side, text="Seleziona Periodo:", font=("Arial", 12)).pack(pady=(5,0))
        self.nav_opt = CTkOptionMenu(self.side, values=["Tutto lo storico"], command=lambda _: self.refresh_all())
        self.nav_opt.set("Tutto lo storico"); self.nav_opt.pack(pady=5)

        CTkLabel(self.side, text="Raggruppamento:", font=("Arial", 12)).pack(pady=(5,0))
        self.group_opt = CTkOptionMenu(self.side, values=["Nessuno", "Giorno", "Settimana"], command=lambda _: self.refresh_all())
        self.group_opt.set("Giorno"); self.group_opt.pack(pady=5)

        self.stats_box = CTkTextbox(self.side, width=300, height=300, font=("Consolas", 12))
        self.stats_box.pack(pady=10, padx=10)
        
        # 4. Area Grafico
        self.chart_c = CTkFrame(self.main_c, fg_color="#1e1e1e")
        self.chart_c.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def update_f(self, _=None):
        self.filter_mode = self.seg_m.get(); self.filter_diff = self.seg_d.get().lower()
        self.refresh_all()

    def update_nav_options(self, choice):
        # Logica per popolare il menu "Seleziona Periodo" in base alla vista
        if choice == "Sempre": self.nav_opt.configure(values=["Tutto lo storico"])
        elif choice == "Ultimo Giorno": self.nav_opt.configure(values=["Oggi", "Ieri"])
        elif choice == "Ultima Settimana": self.nav_opt.configure(values=["Questa", "Scorsa"])
        else: self.nav_opt.configure(values=["Questo Mese", "Mese Scorso"])
        self.nav_opt.set(self.nav_opt.cget("values")[0])
        self.refresh_all()

    def refresh_all(self):
        plt.close('all')
        if not self.winfo_exists():
            return
        if not os.path.exists("doomsday_stats_v2.json"): return
        with open("doomsday_stats_v2.json", "r") as f: all_data = json.load(f)
        
        data = [d for d in all_data if d["mode"] == self.filter_mode and d["difficulty"] == self.filter_diff]
        if not data: 
            for w in self.chart_c.winfo_children(): w.destroy()
            return

        # --- LOGICA SIDEBAR (Stats testo) ---
        self.stats_box.configure(state="normal"); self.stats_box.delete("0.0", "end")
        txt = f"{'PERIODO':<8} | {'REC':<5} | {'AVG':<5} | {'WR%'}\n" + "-"*35 + "\n"
        now = datetime.now()
        for label, days in [("Oggi", 1), ("Sett.", 7), ("Mese", 30), ("Sempre", 9999)]:
            filt = [d for d in data if (now - datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S")).days < days]
            cor = [d["time"] for d in filt if d["correct"]]
            wr = f"{(len(cor)/len(filt)*100):.0f}%" if filt else "--"
            best = f"{min(cor):.1f}s" if cor else "--"
            avg = f"{sum(cor)/len(cor):.1f}s" if cor else "--"
            txt += f"{label:<8} | {best:<5} | {avg:<5} | {wr}\n"
        self.stats_box.insert("end", txt); self.stats_box.configure(state="disabled")

        # --- GRAFICO AVANZATO ---
        for w in self.chart_c.winfo_children(): w.destroy()
        plt.style.use('dark_background')
        fig, ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#1e1e1e'); ax1.set_facecolor('#1e1e1e')
        
        g_t = collections.defaultdict(list)
        mode = self.group_opt.get()
        plot_dates_dict = {}
        
        # 1. Raggruppiamo TUTTE le chiavi temporali presenti nei dati
        all_keys = []
        for d in data:
            dt = datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S")
            if mode == "Giorno": key = dt.strftime("%d/%m")
            elif mode == "Settimana": key = f"Sett {dt.strftime('%W')}"
            else: key = d["timestamp"][-8:]
            
            if key not in all_keys: all_keys.append(key)
            if d["correct"]: 
                g_t[key].append(d["time"])
            if key not in plot_dates_dict: 
                plot_dates_dict[key] = dt

        # 2. Prepariamo y_vals: conterrà il tempo medio o None se non ci sono corretti
        y_vals = []
        for k in all_keys:
            if g_t[k]:
                y_vals.append(sum(g_t[k])/len(g_t[k]))
            else:
                y_vals.append(None) # Qui creiamo il "buco"
        
        is_continuous = self.sw_continuity.get()
        
        if is_continuous:
            # Rimuoviamo i None per unire i punti
            plot_keys = [all_keys[i] for i in range(len(all_keys)) if y_vals[i] is not None]
            plot_y = [v for v in y_vals if v is not None]
        else:
            # Teniamo i None: Matplotlib interromperà la linea gialla
            plot_keys = all_keys
            plot_y = y_vals

        if not plot_y or all(v is None for v in plot_y): return

        # 3. Disegno Linea Gialla
        ax1.plot(plot_keys, plot_y, color='yellow', marker='o', label="Tempo", linewidth=2)
        
        # 4. Media Mobile (solo su punti validi)
        valid_y = [v for v in plot_y if v is not None]
        if len(valid_y) > 1:
            y_ma = [valid_y[0]]
            for i in range(1, len(valid_y)):
                y_ma.append((valid_y[i] + valid_y[i-1]) / 2)
            # Se non è continuo, la media mobile potrebbe non allinearsi bene, 
            # quindi la disegniamo solo sui punti esistenti
            plot_keys_valid = [plot_keys[i] for i in range(len(plot_y)) if plot_y[i] is not None]
            ax1.plot(plot_keys_valid, y_ma, color='#3b8ed0', linestyle='--', alpha=0.7, label="Media (n, n-1)")

        # 5. Separatori Temporali
        last_dt = None
        for i, k in enumerate(plot_keys):
            curr_dt = plot_dates_dict.get(k)
            if last_dt and curr_dt:
                if curr_dt.date() != last_dt.date():
                    ax1.axvline(i - 0.5, color='gray', alpha=0.2)
                if curr_dt.isocalendar()[1] != last_dt.isocalendar()[1]:
                    ax1.axvline(i - 0.5, color='#555555', alpha=0.6, linewidth=1.5)
                if curr_dt.month != last_dt.month:
                    ax1.axvline(i - 0.5, color='white', alpha=0.4, linestyle='--')
            last_dt = curr_dt

        ax1.set_ylabel("Secondi", color='yellow', fontweight='bold')
        ax1.tick_params(axis='x', rotation=35, labelsize=7)
        ax1.legend(loc='upper right', fontsize='x-small', framealpha=0.3)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_c)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.draw()

