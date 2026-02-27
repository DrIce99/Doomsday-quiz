from customtkinter import *
import random, time, json, os
from datetime import date

def is_leap(y): return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

DOOMSDAY_MONTHS = {
        1: "3 (4 se bisestile)", 2: "28 (29 se bisestile)", 3: "14 (Pi Day)",
        4: "4/4", 5: "9/5 (9-5 at 7-11)", 6: "6/6",
        7: "11/7 (9-5 at 7-11)", 8: "8/8", 9: "5/9 (9-5 at 7-11)",
        10: "10/10", 11: "7/11 (9-5 at 7-11)", 12: "12/12"
    }

class QuizFrame(CTkFrame):
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.mode = "Giorno Preciso"
        self.difficulty = "facile"
        self.game_started = False
        self.running = False
        self.start_time = 0
        self.days_names = ["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab"]
        self.setup_ui()
        self.show_prepare_screen()

    def setup_ui(self):
        # --- HEADER (Modalità e Difficoltà) ---
        self.s_bar = CTkFrame(self, fg_color="transparent")
        self.s_bar.pack(fill="x", pady=10)
        self.seg_mode = CTkSegmentedButton(self.s_bar, values=["Giorno Preciso", "Solo Doomsday"], command=self.update_settings)
        self.seg_mode.set("Giorno Preciso"); self.seg_mode.pack(side="left", padx=10)
        
        # Timer e Domanda
        self.lbl_timer = CTkLabel(self, text="0.0s", font=("Consolas", 24, "bold"), text_color="gray")
        self.lbl_timer.pack()
        self.lbl_q = CTkLabel(self, text="---", font=("Arial", 45, "bold"), text_color="#3b8ed0")
        self.lbl_q.pack(pady=10)

        # --- CORPO CENTRALE (3 COLONNE) ---
        self.main_game_container = CTkFrame(self, fg_color="transparent")
        self.main_game_container.pack(fill="both", expand=True, pady=10)

        # 1. Colonna Sinistra (Ragionamento Doomsday)
        self.col_left = CTkFrame(self.main_game_container, width=250, fg_color="#2b2b2b", corner_radius=10)
        self.col_left.grid(row=0, column=0, padx=10, sticky="nsew")
        CTkLabel(self.col_left, text="CALCOLO DOOMSDAY", font=("Arial", 11, "bold"), text_color="gray").pack(pady=5)
        self.lbl_step_doomsday = CTkLabel(self.col_left, text="", font=("Consolas", 12), justify="left")
        self.lbl_step_doomsday.pack(padx=10, pady=10)

        # 2. Colonna Centrale (Pulsanti Giorni)
        self.col_mid = CTkFrame(self.main_game_container, fg_color="transparent")
        self.col_mid.grid(row=0, column=1, padx=10)
        
        self.grid_btns = CTkFrame(self.col_mid, fg_color="transparent")
        self.grid_btns.pack()
        
        for i, (val, name) in enumerate([(1,"Lun"),(2,"Mar"),(3,"Mer"),(4,"Gio"),(5,"Ven"),(6,"Sab")]):
            btn = CTkButton(self.grid_btns, text=name, width=100, height=50, font=("Arial", 13, "bold"), 
                            command=lambda v=val: self.check_answer(v))
            btn.grid(row=i//2, column=i%2, padx=5, pady=5)
        
        self.btn_dom = CTkButton(self.col_mid, text="Domenica (0)", width=210, height=50, 
                                 fg_color="#34495e", command=lambda: self.check_answer(0))
        self.btn_dom.pack(pady=10)

        # 3. Colonna Destra (Ragionamento Giorno)
        self.col_right = CTkFrame(self.main_game_container, width=250, fg_color="#2b2b2b", corner_radius=10)
        self.col_right.grid(row=0, column=2, padx=10, sticky="nsew")
        CTkLabel(self.col_right, text="CALCOLO GIORNO", font=("Arial", 11, "bold"), text_color="gray").pack(pady=5)
        self.lbl_step_day = CTkLabel(self.col_right, text="", font=("Consolas", 12), justify="left")
        self.lbl_step_day.pack(padx=10, pady=10)
        
        self.seg_diff = CTkSegmentedButton(self.s_bar, values=["Facile", "Medio", "Difficile"], command=self.update_settings)
        self.seg_diff.set("Facile")
        self.seg_diff.pack(side="left", padx=10)

        # --- FOOTER (Risposta Finale e Nuova Partita) ---
        self.footer = CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", pady=20)
        
        self.lbl_final_res = CTkLabel(self.footer, text="", font=("Arial", 18, "bold"))
        self.lbl_final_res.pack()
        
        self.btn_next = CTkButton(self.footer, text="PROSSIMA PARTITA ➔", width=250, height=45,
                                  fg_color="#2ecc71", hover_color="#27ae60",
                                  command=self.new_question)
        # Nascondiamo il footer all'inizio
        self.btn_next.pack_forget()

        # Configurazione pesi griglia per centratura
        self.main_game_container.columnconfigure((0,2), weight=1)

    def update_settings(self, _=None):
        self.mode = self.seg_mode.get()
        try:
            self.difficulty = self.seg_diff.get().lower()
        except AttributeError:
            self.difficulty = "facile"

        if not self.game_started:
            if self.mode == "Solo Doomsday":
                self.lbl_q.configure(text="PRONTO?\n(Solo Anno)")
            else:
                self.lbl_q.configure(text="PRONTO?\n(Giorno Preciso)")
            return 
        self.new_question()

    def update_clock(self):
        if self.running:
            elapsed = time.perf_counter() - self.start_time
            self.lbl_timer.configure(text=f"{elapsed:.1f}s")
            self.after(100, self.update_clock)

    def new_question(self):
        self.btn_next.pack_forget()
        self.lbl_final_res.configure(text="")
        self.lbl_step_doomsday.configure(text="")
        self.lbl_step_day.configure(text="")
        y = random.randint(2000, 2099) if self.difficulty == "facile" else random.randint(1700, 2099) if self.difficulty == "medio" else random.randint(1, 2500)
        m = random.randint(1, 12)
        max_d = 31 if m in [1,3,5,7,8,10,12] else 30 if m != 2 else 29 if is_leap(y) else 28
        self.curr_date = (random.randint(1, max_d), m, y)
        d, m, y = self.curr_date
        self.lbl_q.configure(text=f"{d:02d}/{m:02d}/{y}" if self.mode == "Giorno Preciso" else f"Anno: {y}")
        self.start_time = time.perf_counter(); self.running = True
        self.update_clock()

    def check_answer(self, guess):
        if not self.running or not self.game_started: return
        self.running = False
        
        # Logica di calcolo (riutilizzando quella esistente)
        from modules.stats_module import calculate_doomsday_odd11
        d, m, y = self.curr_date
        dd_val, dd_steps = calculate_doomsday_odd11(y)
        
        target_date = date(y, m, d)
        real_day = (target_date.weekday() + 1) % 7
        doomsday_day = dd_val

        if self.mode == "Solo Doomsday":
            ans = doomsday_day
        else:
            ans = real_day
        
        anchor_day = 3 if m == 1 and not is_leap(y) else 4 if m == 1 else \
                     28 if m == 2 and not is_leap(y) else 29 if m == 2 else \
                     int(DOOMSDAY_MONTHS[m].split('/')[0].split(' ')[0])
        
        distanza = d - anchor_day
        dist_mod = distanza % 7
        final_calc = (dd_val + dist_mod) % 7
        
        # DISPOSIZIONE TESTI RICHIESTA:
        # Sinistra: Ragionamento Doomsday
        self.lbl_step_doomsday.configure(text="\n".join(dd_steps))
        
        # Destra: Ragionamento Giorno (Esempio semplificato, puoi espanderlo)
        day_steps = [
            f"Mese: {target_date.strftime('%B')}",
            f"Ancora: il {anchor_day} è {self.days_names[dd_val]}",
            f"Target: il {d}",
            f"Distanza: {distanza} giorni",
            f"({distanza} % 7 = {dist_mod})",
            f"Calcolo: {dd_val} + {dist_mod} = {final_calc}",
            f"Risultato: {self.days_names[final_calc]}"
        ]
        if self.mode == "Giorno Preciso":
            self.lbl_step_day.configure(text="\n".join(day_steps))
        
        # Sotto: Risposta finale e tasto nuova partita
        is_c = (guess == ans)
        res_color = "#2ecc71" if is_c else "#e74c3c"
        if self.mode == "Solo Doomsday":
            # Mostra solo il giorno della settimana del Doomsday, senza data
            res_text = f"DOOMSDAY: {self.days_names[ans]} | {'CORRETTO ✅' if is_c else 'ERRORE ❌'}"
        else:
            # Mostra la data completa (Giorno Preciso)
            res_text = f"DATA: {d:02d}/{m:02d}/{y} è {self.days_names[ans]} | {'CORRETTO ✅' if is_c else 'ERRORE ❌'}"
        
        self.lbl_final_res.configure(text=res_text, text_color=res_color)
        self.btn_next.pack(pady=10)
        
        self.save_data(self.mode, self.difficulty, round(time.perf_counter() - self.start_time, 2), is_c)


    def save_data(self, m, d, t, c):
        data = []
        if os.path.exists("doomsday_stats_v2.json"):
            with open("doomsday_stats_v2.json", "r") as f: data = json.load(f)
        data.append({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "mode": m, "difficulty": d, "time": t, "correct": c})
        with open("doomsday_stats_v2.json", "w") as f: json.dump(data, f, indent=4)

    def update_clock(self):
        # Se l'app viene chiusa o cambiata pagina, winfo_exists() restituirà False
        if self.running and self.winfo_exists():
            try:
                elapsed = time.perf_counter() - self.start_time
                self.lbl_timer.configure(text=f"{elapsed:.1f}s")
                self.after(100, self.update_clock)
            except:
                pass # Evita errori se la distruzione avviene durante l'esecuzione

    def show_prepare_screen(self):
        """Mostra i pulsanti ma blocca l'interazione finché non si clicca START"""
        self.game_started = False
        self.lbl_q.configure(text="PRONTO?")
        self.lbl_step_doomsday.configure(text="")
        self.lbl_step_day.configure(text="")
        self.lbl_final_res.configure(text="")
        
        # Bottone di Start Gigante che copre la domanda
        self.btn_start = CTkButton(self, text="CLICCA PER INIZIARE", width=300, height=60,
                                   font=("Arial", 16, "bold"), command=self.start_game)
        self.btn_start.place(relx=0.5, rely=0.4, anchor="center")
        
    def start_game(self):
        self.btn_start.place_forget()
        self.game_started = True
        self.new_question()