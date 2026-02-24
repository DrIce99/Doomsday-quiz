import subprocess
from customtkinter import *

class DoomsdayLauncher(CTk):
    def __init__(self):
        super().__init__()
        self.title("Doomsday Training Suite")
        self.geometry("400x300")
        set_appearance_mode("dark")
        set_default_color_theme("blue")

        CTkLabel(self, text="🧠 Doomsday Trainer", font=("Arial", 24, "bold")).pack(pady=30)

        self.btn_play = CTkButton(self, text="GIOCA / ALLENATI", height=50, width=250,
                                  command=lambda: self.launch("quiz.py"))
        self.btn_play.pack(pady=10)

        self.btn_stats = CTkButton(self, text="STATISTICHE E ANALYTICS", height=50, width=250,
                                   fg_color="#2ecc71", hover_color="#27ae60",
                                   command=lambda: self.launch("stats.py"))
        self.btn_stats.pack(pady=10)

    def launch(self, file_name):
        # Lancia il processo separato senza chiudere il launcher
        subprocess.Popen(["python", file_name])

if __name__ == "__main__":
    app = DoomsdayLauncher()
    app.mainloop()
