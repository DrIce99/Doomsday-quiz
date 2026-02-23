import tkinter as tk
from customtkinter import *
import random
import time
import json
import os
from datetime import date

# --- LOGICA DI CALCOLO (METODO ODD + 11) ---

def is_leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

def get_anchor(y):
    century = (y // 100) % 4
    return {0: 2, 1: 0, 2: 5, 3: 3}[century]

def calculate_doomsday_odd11(y):
    anchor = get_anchor(y)
    t = y % 100
    steps = []
    
    # Passaggio 1: Se dispari + 11
    val = t
    steps.append(f"Anno 20XX: {t}")
    if val % 2 != 0:
        val += 11
        steps.append(f"Dispari! +11 = {val}")
    else:
        steps.append(f"Pari: {val}")
        
    # Passaggio 2: Dividi per 2
    val //= 2
    steps.append(f"Dividi per 2 = {val}")
    
    # Passaggio 3: Se dispari + 11
    if val % 2 != 0:
        val += 11
        steps.append(f"Dispari! +11 = {val}")
    else:
        steps.append(f"Pari: {val}")
    
    # Passaggio 4: Modulo 7
    rem = val % 7
    steps.append(f"Modulo 7: {val} % 7 = {rem}")
    
    # Passaggio 5: Differenza da 7
    diff = (7 - rem) % 7
    steps.append(f"Sottrai da 7: 7 - {rem} = {diff}")
    
    # Passaggio 6: Aggiungi Anchor
    final_doomsday = (diff + anchor) % 7
    steps.append(f"Aggiungi Anchor ({anchor}): {diff} + {anchor} = {final_doomsday}")
    
    return final_doomsday, steps

# --- INTERFACCIA ---

class DoomsdayQuiz(CTk):
    def __init__(self):
        super().__init__()
        self.title("Doomsday Trainer - Odd+11 Method")
        self.geometry("600x880")
        
        self.mode = "day"
        self.difficulty = "facile"
        self.start_time = 0
        self.running = False
        self.days_names = ["Domenica", "Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato"]

        self.setup_ui()
        self.new_question()

    def setup_ui(self):
        CTkLabel(self, text="📅 Doomsday Trainer", font=("Arial", 24, "bold")).pack(pady=15)

        self.seg_mode = CTkSegmentedButton(self, values=["Giorno Preciso", "Solo Doomsday"], command=self.change_settings)
        self.seg_mode.set("Giorno Preciso")
        self.seg_mode.pack(pady=5)

        self.seg_diff = CTkSegmentedButton(self, values=["Facile", "Medio", "Difficile"], command=self.change_settings)
        self.seg_diff.set("Facile")
        self.seg_diff.pack(pady=5)

        self.lbl_stats = CTkLabel(self, text="Tempo: 0.0s | Record: --", font=("Consolas", 14))
        self.lbl_stats.pack(pady=10)

        self.lbl_question = CTkLabel(self, text="", font=("Arial", 32, "bold"), text_color="#3b8ed0")
        self.lbl_question.pack(pady=20)

        self.btn_frame = CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=10)
        
        for i, day in enumerate(["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab"]):
            btn = CTkButton(self.btn_frame, text=day, width=75, height=50, font=("Arial", 14, "bold"),
                            command=lambda x=i: self.check_answer(x))
            btn.grid(row=i//4, column=i%4, padx=5, pady=5)

        self.solution_frame = CTkFrame(self, fg_color="#2b2b2b", border_width=2, border_color="#e74c3c")
        self.lbl_math_title = CTkLabel(self.solution_frame, text="SPIEGAZIONE (METODO ODD+11)", font=("Arial", 14, "bold"), text_color="#e74c3c")
        self.lbl_math_title.pack(pady=(10, 5))
        
        self.lbl_sol_text = CTkLabel(self.solution_frame, text="", font=("Consolas", 12), justify="left")
        self.lbl_sol_text.pack(padx=20, pady=10)
        
        self.btn_retry = CTkButton(self.solution_frame, text="PROSSIMA PARTITA ➔", command=self.new_question, 
                                   fg_color="#2ecc71", hover_color="#27ae60", font=("Arial", 13, "bold"))
        self.btn_retry.pack(pady=15)

        self.lbl_result = CTkLabel(self, text="", font=("Arial", 18, "bold"))
        self.lbl_result.pack(pady=15)

    def change_settings(self, _=None):
        self.mode = "day" if self.seg_mode.get() == "Giorno Preciso" else "doomsday"
        self.difficulty = self.seg_diff.get().lower()
        self.new_question()

    def new_question(self):
        self.solution_frame.pack_forget()
        y = random.randint(2000, 2099) if self.difficulty == "facile" else \
            random.randint(1700, 2099) if self.difficulty == "medio" else random.randint(1, 2500)
        m = random.randint(1, 12)
        d = random.randint(1, 28 if m==2 and not is_leap(y) else 29 if m==2 else 30 if m in [4,6,9,11] else 31)
        self.current_date = (d, m, y)

        txt = f"{d:02d}/{m:02d}/{y}" if self.mode == "day" else f"Anno: {y}"
        self.lbl_question.configure(text=txt)
        self.lbl_result.configure(text="")
        
        self.start_time = time.perf_counter()
        self.running = True
        self.update_clock()

    def update_clock(self):
        if self.running:
            elapsed = time.perf_counter() - self.start_time
            self.lbl_stats.configure(text=f"Tempo: {elapsed:.1f}s")
            self.after(100, self.update_clock)

    def check_answer(self, guess):
        if not self.running: return
        self.running = False
        d, m, y = self.current_date
        
        doomsday, steps = calculate_doomsday_odd11(y)
        
        # Riferimenti mesi
        dm_ref = {1: 4 if is_leap(y) else 3, 2: 29 if is_leap(y) else 28,
                  3: 7, 4: 4, 5: 9, 6: 6, 7: 11, 8: 8, 9: 5, 10: 10, 11: 7, 12: 12}
        ref_day = dm_ref[m]
        final_wd = (doomsday + (d - ref_day)) % 7
        
        correct = final_wd if self.mode == "day" else doomsday

        if guess == correct:
            self.lbl_result.configure(text="CORRETTO!", text_color="#2ecc71")
            self.after(1500, self.new_question)
        else:
            self.lbl_result.configure(text="ERRORE!", text_color="#e74c3c")
            
            explanation = "\n".join(steps)
            if self.mode == "day":
                explanation += f"\n\nGIORNO:\n- Rif. Mese {m}: {ref_day}\n- Diff: {d} - {ref_day} = {d-ref_day}\n- Risultato: {self.days_names[final_wd]}"
            
            self.lbl_sol_text.configure(text=explanation)
            self.solution_frame.pack(pady=10, fill="x", padx=40)

if __name__ == "__main__":
    app = DoomsdayQuiz()
    app.mainloop()
