from customtkinter import *
import random, time, json, os
from datetime import date

def is_leap(y): return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

class QuizFrame(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.mode = "Giorno Preciso"
        self.difficulty = "facile"
        self.running = False
        self.start_time = 0
        self.days_names = ["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab"]
        self.setup_ui()
        self.new_question()

    def setup_ui(self):
        s_bar = CTkFrame(self, fg_color="transparent")
        s_bar.pack(fill="x", pady=10)
        self.seg_mode = CTkSegmentedButton(s_bar, values=["Giorno Preciso", "Solo Doomsday"], command=self.update_settings)
        self.seg_mode.set(self.mode); self.seg_mode.pack(side="left", padx=10)
        self.seg_diff = CTkSegmentedButton(s_bar, values=["Facile", "Medio", "Difficile"], command=self.update_settings)
        self.seg_diff.set(self.difficulty.capitalize()); self.seg_diff.pack(side="left", padx=10)

        # Timer Visibile
        self.lbl_timer = CTkLabel(self, text="0.0s", font=("Consolas", 24, "bold"), text_color="gray")
        self.lbl_timer.pack(pady=5)

        self.lbl_q = CTkLabel(self, text="", font=("Arial", 45, "bold"), text_color="#3b8ed0")
        self.lbl_q.pack(pady=20)

        grid = CTkFrame(self, fg_color="transparent")
        grid.pack(pady=10)
        for i, (val, name) in enumerate([(1,"Lun"),(2,"Mar"),(3,"Mer"),(4,"Gio"),(5,"Ven"),(6,"Sab")]):
            CTkButton(grid, text=name, width=110, height=60, font=("Arial", 14, "bold"), 
                      command=lambda v=val: self.check_answer(v)).grid(row=i//2, column=i%2, padx=8, pady=8)
        CTkButton(grid, text="Dom (0)", width=236, height=60, font=("Arial", 14, "bold"), 
                      command=lambda: self.check_answer(0)).grid(row=3, column=0, columnspan=2, pady=12)

        self.sol_frame = CTkFrame(self, border_width=2, border_color="#e74c3c")
        self.lbl_sol = CTkLabel(self.sol_frame, text="", font=("Consolas", 13), justify="left")
        self.lbl_sol.pack(padx=20, pady=15)
        CTkButton(self.sol_frame, text="PROSSIMA PARTITA ➔", command=self.new_question, font=("Arial", 12, "bold")).pack(pady=10)
        
        self.lbl_res = CTkLabel(self, text="", font=("Arial", 22, "bold"))
        self.lbl_res.pack(pady=10)

    def update_settings(self, _=None):
        self.mode = self.seg_mode.get()
        self.difficulty = self.seg_diff.get().lower()
        self.new_question()

    def update_clock(self):
        if self.running:
            elapsed = time.perf_counter() - self.start_time
            self.lbl_timer.configure(text=f"{elapsed:.1f}s")
            self.after(100, self.update_clock)

    def new_question(self):
        self.sol_frame.pack_forget(); self.lbl_res.configure(text="")
        y = random.randint(2000, 2099) if self.difficulty == "facile" else random.randint(1700, 2099) if self.difficulty == "medio" else random.randint(1, 2500)
        m = random.randint(1, 12)
        max_d = 31 if m in [1,3,5,7,8,10,12] else 30 if m != 2 else 29 if is_leap(y) else 28
        self.curr_date = (random.randint(1, max_d), m, y)
        d, m, y = self.curr_date
        self.lbl_q.configure(text=f"{d:02d}/{m:02d}/{y}" if self.mode == "Giorno Preciso" else f"Anno: {y}")
        self.start_time = time.perf_counter(); self.running = True
        self.update_clock()

    def check_answer(self, guess):
        if not self.running: return
        self.running = False
        elapsed = round(time.perf_counter() - self.start_time, 2)
        d, m, y = self.curr_date
        # Logica rapida per corretto
        from modules.stats_module import calculate_doomsday_odd11 # Riutilizzo logica
        dd, steps = calculate_doomsday_odd11(y)
        ans = (date(y, m, d).weekday() + 1) % 7 if self.mode == "Giorno Preciso" else dd
        
        is_c = (guess == ans)
        self.save_data(self.mode, self.difficulty, elapsed, is_c)

        if is_c:
            self.lbl_res.configure(text=f"CORRETTO! ({elapsed}s) ✅", text_color="#2ecc71")
            self.after(1000, self.new_question)
        else:
            self.lbl_res.configure(text="ERRORE ❌", text_color="#e74c3c")
            txt = "CALCOLO:\n" + "\n".join(steps)
            if self.mode == "Giorno Preciso": txt += f"\n\nRisultato: {self.days_names[ans]}"
            self.lbl_sol.configure(text=txt)
            self.sol_frame.pack(pady=10)

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
