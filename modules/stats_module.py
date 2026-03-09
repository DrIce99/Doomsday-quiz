import json, os, collections
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from customtkinter import *
from datetime import date, datetime, timedelta
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from managers.condition_manager import *
from logics.logic_impact import *
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
        
        CTkLabel(self.side, text="Condizione Giorno Selezionato:", font=("Arial", 12, "bold")).pack(pady=(20,0))
        self.cond_opt = CTkOptionMenu(self.side, 
                                    values=["Rimuovi"] + list(DEFAULT_CONDITIONS.keys()),
                                    command=self.update_day_condition)
        self.cond_opt.set("Seleziona...")
        self.cond_opt.pack(pady=5)
        
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

        self.stats_box = CTkTextbox(self.side, width=300, height=400, font=("Consolas", 12))
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
        if not os.path.exists("data/doomsday_stats_v2.json"): return
        with open("data/doomsday_stats_v2.json", "r") as f: all_data = json.load(f)
        
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

        all_conds = load_conditions()
        impacts, g_avg, w_sign = calculate_impacts(data, all_conds)

        recent_avg, today_avg, perc, margine, sign = calculate_trend_metrics(data)

        if impacts:
            txt += "\n" + "="*20 + "\nIMPATTO CONDIZIONI:\n"
            for imp in impacts:
                # Colore/Simbolo in base al peggioramento o miglioramento
                # Se diff > 0 significa che ci metti più tempo (peggio)
                t_icon = "⚠️" if imp["diff_time"] > 0 else "🚀"
                w_icon = "📈" if imp["diff_wr"] >= 0 else "📉"
                
                t_sign = "+" if imp["diff_time"] > 0 else ""
                w_sign = "+" if imp["diff_wr"] > 0 else ""
                txt += f"{t_icon} {imp['label']}: {imp['avg']:.1f}s ({t_sign}{imp['diff_time']:.1f}s)\n"
                txt += f"   (su {imp['count']} sessioni)\n"
                txt += f"{w_icon} (winrate: {imp['wr']:.0f}% ({w_sign}{imp['diff_wr']:.1f}%)\n\n"
        
        txt += f"\nTREND RECENTE (7gg): {recent_avg:.1f}s\n"
        txt += f"PERFORMANCE OGGI: {today_avg:.1f}s ({sign}{perc:.1f}%)\n"
        txt += f"MARGINE DI MIGLIORAMENTO: {margine:.1f}%\n"
        
        self.stats_box.configure(state="normal")
        self.stats_box.delete("0.0", "end")
        self.stats_box.insert("0.0", txt)
        self.stats_box.configure(state="disabled")

        # --- GRAFICO ---
        for w in self.chart_c.winfo_children(): w.destroy()
        plt.style.use('dark_background')
        fig, ax1 = plt.subplots(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor('#1e1e1e'); ax1.set_facecolor('#1e1e1e')
        
        g_t = collections.defaultdict(list)
        g_w = collections.defaultdict(list)
        mode = self.group_opt.get()
        plot_dates_dict = {}
        all_keys = []

        for d in data:
            dt = datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S")
            if mode == "Giorno": key = dt.strftime("%d/%m")
            elif mode == "Settimana": key = f"Sett {dt.strftime('%W')}"
            else: key = d["timestamp"][-8:]
            
            if key not in all_keys: all_keys.append(key)
            if key not in plot_dates_dict:
                plot_dates_dict[key] = dt
            if d["correct"]: g_t[key].append(d["time"])
            # if key not in plot_dates_dict: plot_dates_dict[key] = dt
            g_w[key].append(d["correct"])
            
        total_correct = 0
        total_attempts = 0

        plot_keys = []
        plot_y_temps = []
        plot_y_winrate = []
        total_correct = 0
        total_attempts = 0
        is_continuous = self.sw_continuity.get()

        for k in all_keys:
            # 1. BACKEND: Calcolo sempre (anche se non mostro il punto)
            correct_in_this_point = sum(1 for x in g_w[k] if x)
            attempts_in_this_point = len(g_w[k])
            
            total_correct += correct_in_this_point
            total_attempts += attempts_in_this_point
            
            # Calcolo winrate cumulativo (con protezione zero)
            current_wr = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
            
            # 2. FRONTEND: Decidiamo se mostrare il punto
            avg_t = sum(g_t[k])/len(g_t[k]) if g_t[k] else None
            
            # SE LA CONTINUITÀ È ATTIVA:
            # Se non c'è un tempo (risposta errata), saltiamo il punto del GRAFICO
            # ma il winrate è già stato aggiornato nel backend per il punto successivo!
            if self.sw_continuity.get() and avg_t is None:
                continue
            
            # Altrimenti (o se non c'è continuità), aggiungiamo il punto
            plot_keys.append(k)
            plot_y_temps.append(avg_t)
            plot_y_winrate.append(current_wr)

        # y_vals = [sum(g_t[k])/len(g_t[k]) if g_t[k] else None for k in all_keys]

        cond_data = load_conditions()
        
        for i, k in enumerate(plot_keys):
            dt = plot_dates_dict.get(k)
            if not dt:
                continue

            date_str = dt.strftime("%Y-%m-%d")

            if date_str in cond_data:
                c = cond_data[date_str]["color"]

                ax1.axvspan(i - 0.5, i + 0.5,
                            color=c,
                            alpha=0.15,
                            zorder=0)

                ax1.scatter(i, 1,
                            color=c,
                            marker='v',
                            s=40,
                            transform=ax1.get_xaxis_transform(),
                            zorder=10)

        # Separatori
        last_dt = None
        display_labels = []
        mode = self.group_opt.get()
        for i, k in enumerate(plot_keys):
            curr_dt = plot_dates_dict.get(k)
            if mode == "Nessuno" and curr_dt:
                # Mostra la data solo se è il primo punto del giorno
                if last_dt is None or curr_dt.date() != last_dt.date():
                    display_labels.append(curr_dt.strftime("%d/%m/%y"))
                else:
                    display_labels.append("") # Lascia vuoto per i test dello stesso giorno
            else:
                display_labels.append(k) # Usa l'etichetta standard per gli altri raggruppamenti

            if last_dt and curr_dt:
                if curr_dt.date() != last_dt.date():
                    ax1.axvline(i - 0.5, color='gray', alpha=0.2)
                if curr_dt.isocalendar()[1] != last_dt.isocalendar()[1]:
                    ax1.axvline(i - 0.5, color='#555555', alpha=0.6)
            last_dt = curr_dt

        ax1.set_xticks(range(len(plot_keys)))
        ax1.set_xticklabels(display_labels)

        ax1.tick_params(axis='x', rotation=35, labelsize=7)
        canvas = FigureCanvasTkAgg(fig, master=self.chart_c)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Asse Sinistro: Tempo (Linea Gialla)
        if plot_y_temps:
            tempo_line, = ax1.plot(plot_keys,
                    plot_y_temps,
                    color='yellow',
                    linewidth=2,
                    label="Tempo",
                    picker=5)

            # --- PALLINI SOLO SE NON CONTINUA ---
            if not self.sw_continuity.get():
                isolated_x = []
                isolated_y = []

                for i in range(len(plot_y_temps)):
                    prev_valid = i > 0 and plot_y_temps[i-1] is not None
                    next_valid = i < len(plot_y_temps)-1 and plot_y_temps[i+1] is not None

                    if not prev_valid and not next_valid:
                        isolated_x.append(plot_keys[i])
                        isolated_y.append(plot_y_temps[i])

                ax1.scatter(isolated_x,
                            isolated_y,
                            color='yellow',
                            s=10,
                            zorder=5)
    
        # --- MEDIA MOBILE (Trend di miglioramento) ---
        window = 5 # Calcola la media ogni 5 sessioni
        valid_temps = [t for t in plot_y_temps if t is not None]
        if len(plot_y_temps) > window:
            # Calcoliamo la media mobile semplice
            sma = [sum(valid_temps[i-window:i])/window for i in range(window, len(valid_temps)+1)]
            # La plottiamo sopra la linea gialla
            valid_keys = [plot_keys[i] for i in range(len(plot_y_temps)) if plot_y_temps[i] is not None]
            
            ax1.plot(valid_keys[window-1:], sma, color='#3498db', 
                linestyle=':', linewidth=2, label="Trend (SMA 5)")

        # Asse Destro: Winrate % (Linea Verde)
        ax2 = ax1.twinx()
        if plot_y_winrate:
            ax2.plot(plot_keys, plot_y_winrate, color='#2ecc71',
                    linestyle='--', alpha=0.8, label="Winrate %")
            ax2.set_ylabel("Winrate %", color='#2ecc71', fontsize=9)
            ax2.tick_params(axis='y', labelcolor='#2ecc71')
            ax2.set_ylim(0, 110)
        
        ax1.tick_params(axis='x', rotation=35, labelsize=7)
        
        # --- LEGENDA UNIFICATA ---
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, 
                   loc='upper center', bbox_to_anchor=(0.5, -0.15),
                   ncol=3, fontsize=8, frameon=False)
        
        # --- LOGICA HOVER (TOOLTIP) ---
        annot = ax1.annotate("", xy=(0,0), xytext=(10,10),
                            textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="#2b2b2b", ec="yellow", alpha=0.9),
                            arrowprops=dict(arrowstyle="->", color='white'),
                            color="white", fontsize=9)
        annot.set_visible(False)
        
        def update_annot(ind, line):
            x, y = line.get_data()
            idx = ind["ind"][0]
            annot.xy = (x[idx], y[idx])
            
            # Recuperiamo i dati corretti per quel punto
            data_label = plot_keys[idx]
            tempo_val = plot_y_temps[idx]
            wr_val = plot_y_winrate[idx]
            
            text = f"Data: {data_label}\n⏱️ Tempo: {tempo_val:.2f}s\n🎯 Winrate: {wr_val:.1f}%"
            annot.set_text(text)

        def hover(event):
            vis = annot.get_visible()
            if event.inaxes == ax1:
                # Controlliamo la linea del tempo (la gialla)
                cont, ind = tempo_line.contains(event)
                if cont:
                    update_annot(ind, tempo_line)
                    annot.set_visible(True)
                    canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        canvas.draw_idle()

        # Colleghiamo l'evento al canvas
        canvas.mpl_connect("motion_notify_event", hover)
        
        fig.subplots_adjust(bottom=0.25)

    def open_calendar(self):
        CalendarPicker(self, self.selected_date_str, self.on_date_selected)

    def on_date_selected(self, selected_date):
        # selected_date è un oggetto datetime.date
        self.selected_date_str = selected_date.strftime("%Y-%m-%d")
        self.anchor_date = selected_date
        
        conds = load_conditions()
        current_cond = conds.get(self.selected_date_str, {}).get("label", "Seleziona...")
        self.cond_opt.set(current_cond)
        
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
        
    def update_day_condition(self, choice):
        # Usiamo la data selezionata dal calendario (già salvata in self.selected_date_str)
        if hasattr(self, "selected_date_str"):
            save_condition(self.selected_date_str, choice)
            # Forziamo il refresh per mostrare il colore nel grafico e aggiornare il riassunto
            self.refresh_all()
    
    def get_trend_analysis(all_data, days=7):
        # 1. Prendi solo i dati degli ultimi 'days' giorni (esclusa oggi)
        today = date.today()
        start_trend = today - timedelta(days=days)
        
        recent_times = [
            d["time"] for d in all_data 
            if start_trend <= datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S").date() < today
            and d["correct"]
        ]
        
        # 2. Prendi i dati di OGGI
        today_times = [
            d["time"] for d in all_data 
            if datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S").date() == today
            and d["correct"]
        ]
        
        recent_avg = sum(recent_times) / len(recent_times) if recent_times else None
        today_avg = sum(today_times) / len(today_times) if today_times else None
        
        if recent_avg and today_avg:
            diff = today_avg - recent_avg
            perc = (diff / recent_avg) * 100
            return today_avg, recent_avg, diff, perc
        return None