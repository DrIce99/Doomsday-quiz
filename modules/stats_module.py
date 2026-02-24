import tkinter as tk
from customtkinter import *
import json, os, collections
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        f_bar = CTkFrame(self, fg_color="#2b2b2b")
        f_bar.pack(fill="x", padx=10, pady=10)
        
        self.seg_m = CTkSegmentedButton(f_bar, values=["Giorno Preciso", "Solo Doomsday"], command=self.update_f)
        self.seg_m.set(self.filter_mode); self.seg_m.pack(side="left", padx=15, pady=10)
        
        self.seg_d = CTkSegmentedButton(f_bar, values=["Facile", "Medio", "Difficile"], command=self.update_f)
        self.seg_d.set(self.filter_diff.capitalize()); self.seg_d.pack(side="left", padx=15)

        self.main_c = CTkFrame(self, fg_color="transparent")
        self.main_c.pack(fill="both", expand=True)
        
        self.side = CTkFrame(self.main_c, width=300)
        self.side.pack(side="left", fill="y", padx=10, pady=10)
        
        CTkLabel(self.side, text="Raggruppamento:", font=("Arial", 12)).pack(pady=(15,0))
        self.group_opt = CTkOptionMenu(self.side, values=["Nessuno", "Giorno", "Settimana"], command=lambda _: self.refresh_all())
        self.group_opt.set("Giorno"); self.group_opt.pack(pady=10)

        self.stats_box = CTkTextbox(self.side, width=270, height=350, font=("Consolas", 12))
        self.stats_box.pack(pady=10, padx=10)
        
        self.chart_c = CTkFrame(self.main_c, fg_color="#1e1e1e")
        self.chart_c.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def update_f(self, _=None):
        self.filter_mode = self.seg_m.get(); self.filter_diff = self.seg_d.get().lower()
        self.refresh_all()

    def refresh_all(self):
        if not os.path.exists("doomsday_stats_v2.json"): return
        with open("doomsday_stats_v2.json", "r") as f: all_data = json.load(f)
        data = [d for d in all_data if d["mode"] == self.filter_mode and d["difficulty"] == self.filter_diff]
        
        # --- SIDEBAR STATS ---
        # --- SIDEBAR STATS AGGIORNATA CON MEDIA ---
        self.stats_box.configure(state="normal"); self.stats_box.delete("0.0", "end")
        periods = [("Oggi", 1), ("Sett.", 7), ("Mese", 30), ("Sempre", 9999)]
        
        # Header con 4 colonne
        txt = f"{'PERIODO':<8} | {'REC':<5} | {'AVG':<5} | {'WR%'}\n" + "-"*35 + "\n"
        
        for label, days in periods:
            filt = [d for d in data if (datetime.now() - datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S")).days < days]
            cor = [d["time"] for d in filt if d["correct"]]
            
            wr = f"{(len(cor)/len(filt)*100):.0f}%" if filt else "--"
            best = f"{min(cor):.1f}s" if cor else "--"
            avg = f"{sum(cor)/len(cor):.1f}s" if cor else "--" # Calcolo della media
            
            txt += f"{label:<8} | {best:<5} | {avg:<5} | {wr}\n"
            
        self.stats_box.insert("end", txt); self.stats_box.configure(state="disabled")

        # --- GRAFICO ---
        for w in self.chart_c.winfo_children(): w.destroy()
        if not data: return
        
        plt.style.use('dark_background')
        fig, ax1 = plt.subplots(figsize=(5, 4), dpi=100); fig.patch.set_facecolor('#1e1e1e'); ax1.set_facecolor('#1e1e1e')
        
        g_t = collections.defaultdict(list); g_c = collections.defaultdict(list)
        mode = self.group_opt.get()
        for d in data:
            dt = datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S")
            if mode == "Giorno": key = dt.strftime("%d/%m")
            elif mode == "Settimana": key = f"Sett {dt.strftime('%W')}"
            else: key = d["timestamp"][-8:] # "Nessuno": Ora precisa
            
            if d["correct"]: g_t[key].append(d["time"])
            g_c[key].append(1 if d["correct"] else 0)
        
        # Prendiamo TUTTI i tasti (chiavi), ordinati cronologicamente
        keys = list(g_c.keys())
        y_t = [sum(g_t[k])/len(g_t[k]) if g_t[k] else None for k in keys]
        
        self.line_t, = ax1.plot(keys, y_t, color='#3b8ed0', marker='o', markersize=6, label="Tempo", pickradius=5)
        ax1.set_ylabel("Secondi", color='#3b8ed0', fontweight='bold')
        
        # Gestione asse X (se troppi punti, nascondi etichette intermedie)
        step = max(1, len(keys) // 10)
        ax1.set_xticks(keys[::step])
        ax1.tick_params(axis='x', rotation=30, labelsize=8)
        
        self.ax2 = None
        if mode != "Nessuno":
            self.ax2 = ax1.twinx()
            y_w = [(sum(g_c[k])/len(g_c[k])*100) for k in keys]
            self.line_w, = self.ax2.plot(keys, y_w, color='#2ecc71', linestyle='--', alpha=0.4, marker='s', markersize=4)
            self.ax2.set_ylabel("Winrate %", color='#2ecc71', fontweight='bold')
            self.ax2.set_ylim(-5, 105)

        # Annotazione Hover
        self.annot = ax1.annotate("", xy=(0,0), xytext=(15,15), textcoords="offset points",
                                  bbox=dict(boxstyle="round", fc="#2b2b2b", ec="white", alpha=0.9),
                                  arrowprops=dict(arrowstyle="->", color="white"))
        self.annot.set_visible(False)

        def update_annot(ind, line, is_wr=False):
            x, y = line.get_data()
            self.annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
            label_x = keys[ind["ind"][0]]
            val = y[ind["ind"][0]]
            unit = "%" if is_wr else "s"
            self.annot.set_text(f"{label_x}\n{val:.2f}{unit}")
            self.annot.get_bbox_patch().set_edgecolor(line.get_color())

        def hover(event):
            vis = self.annot.get_visible()
            if event.inaxes in [ax1, self.ax2]:
                cont_t, ind_t = self.line_t.contains(event)
                if cont_t:
                    update_annot(ind_t, self.line_t)
                    self.annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return
                if self.ax2:
                    cont_w, ind_w = self.line_w.contains(event)
                    if cont_w:
                        update_annot(ind_w, self.line_w, is_wr=True)
                        self.annot.set_visible(True)
                        fig.canvas.draw_idle()
                        return
            if vis:
                self.annot.set_visible(False)
                fig.canvas.draw_idle()

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_c)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.mpl_connect("motion_notify_event", hover)
        canvas.draw()
