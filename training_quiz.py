import tkinter as tk
from customtkinter import *
import random
import time
import json
import os
from datetime import datetime, date

# --- LOGICA DI CALCOLO (ODD + 11) ---

def is_leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

def get_anchor(y):
    century = (y // 100) % 4
    return {0: 2, 1: 0, 2: 5, 3: 3}[century]

def calculate_doomsday_odd11(y):
    anchor = get_anchor(y)
    t = y % 100
    val = t
    steps = [f"Anno XX{t:02d}"]
    if val % 2 != 0: val += 11; steps.append(f"Dispari +11 = {val}")
    val //= 2; steps.append(f"Diviso 2 = {val}")
    if val % 2 != 0: val += 11; steps.append(f"Dispari +11 = {val}")
    rem = val % 7
    diff = (7 - rem) % 7
    steps.append(f"7 - ({val}%7) = {diff}")
    final = (diff + anchor) % 7
    steps.append(f"Doomsday: {final} (+Anchor {anchor})")
    return final, steps

# --- GESTIONE STATISTICHE ---
STATS_FILE = "doomsday_stats_v2.json"

def save_attempt(mode, diff, elapsed_time, is_correct):
    data = []
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f: data = json.load(f)
        except: data = []
    
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode, 
        "difficulty": diff, 
        "time": round(elapsed_time, 2) if is_correct else None,
        "correct": is_correct
    }
    data.append(entry)
    with open(STATS_FILE, "w") as f: json.dump(data, f, indent=4)

def get_advanced_stats(mode, diff):
    if not os.path.exists(STATS_FILE): return 0.0, 0, 0
    try:
        with open(STATS_FILE, "r") as f: data = json.load(f)
    except: return 0.0, 0, 0
    
    filtered = [d for d in data if d["mode"] == mode and d["difficulty"] == diff]
    if not filtered: return 0.0, 0, 0
    
    total = len(filtered)
    correct_ones = [d["time"] for d in filtered if d["correct"] is True]
    success_count = len(correct_ones)
    
    avg_time = sum(correct_ones) / success_count if success_count > 0 else 0.0
    winrate = (success_count / total) * 100
    
    return avg_time, success_count, round(winrate, 1)

# --- INTERFACCIA ---
class DoomsdayQuiz(CTk):
    def __init__(self):
        super().__init__()
        self.title("Doomsday Trainer Pro 2026")
        self.geometry("620x960")
        
        self.current_theme = "Dark"
        self.current_accent = "blue"
        self.mode = "Giorno Preciso"
        self.difficulty = "Facile"
        self.running = False
        self.current_date = (1, 1, 2024)
        self.days_names = ["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab"]

        self.setup_ui()
        self.new_question()

    def setup_ui(self):
        for widget in self.winfo_children(): widget.destroy()
        set_appearance_mode(self.current_theme)
        set_default_color_theme(self.current_accent)

        self.main_container = CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=25, pady=20)

        # Barra Superiore
        top_bar = CTkFrame(self.main_container, fg_color="transparent")
        top_bar.pack(fill="x", pady=(0, 10))
        
        self.theme_opt = CTkOptionMenu(top_bar, values=["Dark", "Light"], command=self.update_theme, width=80)
        self.theme_opt.set(self.current_theme)
        self.theme_opt.pack(side="left", padx=2)
        
        self.color_opt = CTkOptionMenu(top_bar, values=["blue", "green", "dark-blue"], command=self.update_accent, width=90)
        self.color_opt.set(self.current_accent)
        self.color_opt.pack(side="left", padx=2)

        CTkButton(top_bar, text="Reset", fg_color="#c0392b", width=60, command=self.reset_stats).pack(side="right", padx=2)

        # Pannello Statistiche Avanzate
        avg, count, wr = get_advanced_stats(self.mode, self.difficulty.lower())
        stats_txt = f"Media: {avg:.2f}s  |  Successi: {count}  |  Winrate: {wr}%"
        self.stats_label = CTkLabel(self.main_container, text=stats_txt, font=("Arial", 13, "bold"), text_color="gray")
        self.stats_label.pack(pady=5)

        # Selettori
        self.seg_mode = CTkSegmentedButton(self.main_container, values=["Giorno Preciso", "Solo Doomsday"], command=self.change_mode)
        self.seg_mode.set(self.mode)
        self.seg_mode.pack(fill="x", pady=5)
        self.seg_diff = CTkSegmentedButton(self.main_container, values=["Facile", "Medio", "Difficile"], command=self.change_diff)
        self.seg_diff.set(self.difficulty)
        self.seg_diff.pack(fill="x", pady=5)

        # Quiz Area
        self.lbl_clock = CTkLabel(self.main_container, text="0.0s", font=("Consolas", 20, "bold"))
        self.lbl_clock.pack(pady=10)
        self.lbl_q = CTkLabel(self.main_container, text="", font=("Arial", 46, "bold"))
        self.lbl_q.pack(pady=20)

         # --- NUOVA GRIGLIA PULSANTI
        # --- GRIGLIA PULSANTI (COPPIE + DOMENICA SOTTO) ---
        parent = getattr(self, "main_container", self)
        
        grid = CTkFrame(parent, fg_color="transparent")
        grid.pack(pady=20)

        # 1. GIORNI DA LUNEDÌ A SABATO (A coppie, righe 0-2)
        giorni_feriali = [
            (1, "Lun"), (2, "Mar"), 
            (3, "Mer"), (4, "Gio"), 
            (5, "Ven"), (6, "Sab")
        ]

        for i, (valore, nome) in enumerate(giorni_feriali):
            row_idx = i // 2
            col_idx = i % 2
            
            btn = CTkButton(grid, text=nome, width=105, height=60, 
                            font=("Arial", 16, "bold"),
                            command=lambda v=valore: self.check_answer(v))
            btn.grid(row=row_idx, column=col_idx, padx=7, pady=7)

        # 2. DOMENICA (Riga finale, centrata su 2 colonne)
        # La mettiamo alla riga 3 (dopo le 3 righe precedenti 0,1,2)
        btn_dom = CTkButton(grid, text="Dom (0)", width=220, height=60, 
                            font=("Arial", 16, "bold"),
                            fg_color="#c0392b", hover_color="#962d22",
                            command=lambda: self.check_answer(0))
        btn_dom.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Soluzione
        self.sol_frame = CTkFrame(self.main_container, border_width=2, border_color="#e74c3c")
        self.lbl_sol_math = CTkLabel(self.sol_frame, text="", font=("Consolas", 13), justify="left")
        self.lbl_sol_math.pack(padx=20, pady=20)
        CTkButton(self.sol_frame, text="PROSSIMA PARTITA ➔", command=self.new_question).pack(pady=(0, 15))

        self.lbl_res = CTkLabel(self.main_container, text="", font=("Arial", 22, "bold"))
        self.lbl_res.pack(pady=20)

    # --- LOGICA ---
    def update_theme(self, v): self.current_theme = v; set_appearance_mode(v)
    def update_accent(self, v): self.current_accent = v; self.setup_ui(); self.refresh_view()
    def change_mode(self, v): self.mode = v; self.new_question()
    def change_diff(self, v): self.difficulty = v; self.new_question()
    def reset_stats(self):
        if os.path.exists(STATS_FILE): os.remove(STATS_FILE)
        self.refresh_view()

    def new_question(self):
        y = random.randint(2000, 2099) if self.difficulty == "Facile" else \
            random.randint(1700, 2099) if self.difficulty == "Medio" else random.randint(1, 2500)
        m = random.randint(1, 12)
        if m in [1,3,5,7,8,10,12]: max_d = 31
        elif m in [4,6,9,11]: max_d = 30
        else: max_d = 29 if is_leap(y) else 28
        
        self.current_date = (random.randint(1, max_d), m, y)
        self.sol_frame.pack_forget()
        self.refresh_view()
        self.start_time = time.perf_counter()
        self.running = True
        self.update_clock()

    def refresh_view(self):
        d, m, y = self.current_date
        txt = f"{d:02d}/{m:02d}/{y}" if self.mode == "Giorno Preciso" else f"Anno: {y}"
        self.lbl_q.configure(text=txt)
        self.lbl_res.configure(text="")
        avg, count, wr = get_advanced_stats(self.mode, self.difficulty.lower())
        self.stats_label.configure(text=f"Media: {avg:.2f}s  |  Successi: {count}  |  Winrate: {wr}%")

    def update_clock(self):
        if self.running:
            self.lbl_clock.configure(text=f"{time.perf_counter() - self.start_time:.1f}s")
            self.after(100, self.update_clock)

    def check_answer(self, guess):
        if not self.running: return
        self.running = False
        elapsed = time.perf_counter() - self.start_time
        d, m, y = self.current_date
        
        doomsday, steps = calculate_doomsday_odd11(y)
        correct_wd = (date(y, m, d).weekday() + 1) % 7
        ans = correct_wd if self.mode == "Giorno Preciso" else doomsday

        is_correct = (guess == ans)
        save_attempt(self.mode, self.difficulty.lower(), elapsed, is_correct)

        if is_correct:
            self.lbl_res.configure(text="CORRETTO! ✅", text_color="#2ecc71")
            self.after(1000, self.new_question)
        else:
            self.lbl_res.configure(text="ERRORE ❌", text_color="#e74c3c")
            full_txt = "CALCOLO ODD+11:\n" + "\n".join(steps)
            if self.mode == "Giorno Preciso":
                full_txt += f"\n\nRisultato: {self.days_names[correct_wd]}"
            self.lbl_sol_math.configure(text=full_txt)
            self.sol_frame.pack(pady=10, fill="x")

if __name__ == "__main__":
    app = DoomsdayQuiz()
    app.mainloop()
