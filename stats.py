import json, os, collections
from customtkinter import *
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

STATS_FILE = "doomsday_stats_v2.json"

class StatsApp(CTk):
    def __init__(self):
        super().__init__()
        self.title("Doomsday Analytics - Filtri Avanzati")
        self.geometry("1100x850")
        
        self.filter_mode = "Giorno Preciso"
        self.filter_diff = "facile"
        self.data_points = []
        
        self.setup_ui()
        self.refresh_all()

    def setup_ui(self):
        # Barra Superiore Filtri
        filter_bar = CTkFrame(self)
        filter_bar.pack(fill="x", padx=10, pady=10)
        
        self.seg_mode = CTkSegmentedButton(filter_bar, values=["Giorno Preciso", "Solo Doomsday"], command=self.update_filters)
        self.seg_mode.set(self.filter_mode)
        self.seg_mode.pack(side="left", padx=20, pady=10)

        self.seg_diff = CTkSegmentedButton(filter_bar, values=["Facile", "Medio", "Difficile"], command=self.update_filters)
        self.seg_diff.set(self.filter_diff.capitalize())
        self.seg_diff.pack(side="left", padx=20)

        # Layout Main
        self.side = CTkFrame(self, width=320)
        self.side.pack(side="left", fill="y", padx=10, pady=10)
        
        self.stats_box = CTkTextbox(self.side, width=280, height=300, font=("Consolas", 12))
        self.stats_box.pack(padx=10, pady=10)

        self.group_opt = CTkOptionMenu(self.side, values=["Nessuno", "Giorno", "Settimana"], command=self.refresh_all)
        self.group_opt.set("Giorno")
        self.group_opt.pack(pady=20)

        self.chart_container = CTkFrame(self, fg_color="#1e1e1e")
        self.chart_container.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    def update_filters(self, _=None):
        self.filter_mode = self.seg_mode.get()
        self.filter_diff = self.seg_diff.get().lower()
        self.refresh_all()

    def refresh_all(self, _=None):
        if not os.path.exists(STATS_FILE): return
        with open(STATS_FILE, "r") as f:
            all_data = json.load(f)
        
        # FILTRO DATI
        data = [d for d in all_data if d["mode"] == self.filter_mode and d["difficulty"] == self.filter_diff]
        
        # Aggiorna Testo Sidebar
        self.stats_box.configure(state="normal")
        self.stats_box.delete("0.0", "end")
        now = datetime.now()
        txt = f"FILTRO: {self.filter_mode}\nLIVELLO: {self.filter_diff.upper()}\n" + "-"*28 + "\n"
        
        for label, days in [("Oggi", 1), ("Sett.", 7), ("Sempre", 9999)]:
            filt = [d for d in data if (now - datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S")).days < days]
            cor = [d["time"] for d in filt if d["correct"]]
            wr = f"{(len(cor)/len(filt)*100):.0f}%" if filt else "--"
            best = f"{min(cor):.1f}s" if cor else "--"
            txt += f"{label:<8} | REC: {best:<5} | WR: {wr}\n"
        
        self.stats_box.insert("0.0", txt)
        self.stats_box.configure(state="disabled")

        # Grafico interattivo
        for w in self.chart_container.winfo_children(): w.destroy()
        if not data: return

        plt.style.use('dark_background')
        fig, ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#1e1e1e')
        ax1.set_facecolor('#1e1e1e')
        
        g_t, g_c = collections.defaultdict(list), collections.defaultdict(list)
        mode = self.group_opt.get()
        for d in data:
            dt = datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S")
            key = dt.strftime("%d/%m") if mode=="Giorno" else dt.strftime("%W") if mode=="Settimana" else d["timestamp"][-8:]
            if d["correct"]: 
                g_t[key].append(d["time"])
            g_c[key].append(1 if d["correct"] else 0)
        
        keys = list(g_c.keys())[-12:]
        y_times = []
        for k in keys:
            if g_t[k]: # Se ci sono tempi corretti
                y_times.append(sum(g_t[k]) / len(g_t[k]))
            else:
                y_times.append(None) # Salta il punto invece di mettere 0

        # Plot Tempo (usando drawstyle per gestire eventuali buchi)
        # Usiamo marker='o' ma la linea si interromperà se c'è un None
        self.line_t, = ax1.plot(keys, y_times, color='#3b8ed0', marker='o', 
                                markersize=8, label="Tempo", linewidth=2)
        
        # Rendi il grafico più pulito: se il tempo è None, non mostrare nulla
        ax1.set_ylabel("Secondi", color='#3b8ed0', fontweight='bold')
        
        # Filtra i valori per l'asse Y per evitare che lo 0 (se presente) schiacci il grafico
        valid_times = [t for t in y_times if t is not None]
        if valid_times:
            ax1.set_ylim(min(valid_times)*0.8, max(valid_times)*1.2)

        # Plot Winrate
        self.ax2 = None
        if mode != "Nessuno":
            self.ax2 = ax1.twinx()
            y_wr = [(sum(g_c[k])/len(g_c[k])*100) for k in keys]
            self.line_w, = self.ax2.plot(keys, y_wr, color='#2ecc71', marker='s', linestyle='--', alpha=0.5, label="Winrate")
            self.ax2.set_ylabel("Winrate %", color='#2ecc71', fontweight='bold')
            self.ax2.set_ylim(0, 110)

        # Annotazione (nascosta di default)
        self.annot = ax1.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="#2b2b2b", ec="white", alpha=0.9),
                            arrowprops=dict(arrowstyle="->", color="white"))
        self.annot.set_visible(False)

        def update_annot(ind, line, is_wr=False):
            x, y = line.get_data()
            self.annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
            val = f"{y[ind['ind'][0]]:.2f}"
            unit = "%" if is_wr else "s"
            self.annot.set_text(f"{x[ind['ind'][0]]}\n{val}{unit}")
            self.annot.get_bbox_patch().set_edgecolor(line.get_color())

        def hover(event):
            vis = self.annot.get_visible()
            if event.inaxes == ax1:
                # Controlla linea tempo
                cont, ind = self.line_t.contains(event)
                if cont:
                    update_annot(ind, self.line_t)
                    self.annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return
                # Controlla linea winrate (se esiste)
                if self.ax2:
                    cont, ind = self.line_w.contains(event)
                    if cont:
                        update_annot(ind, self.line_w, is_wr=True)
                        self.annot.set_visible(True)
                        fig.canvas.draw_idle()
                        return
            
            if vis:
                self.annot.set_visible(False)
                fig.canvas.draw_idle()

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        canvas.mpl_connect("motion_notify_event", hover)
        canvas.draw()        

if __name__ == "__main__":
    StatsApp().mainloop()
