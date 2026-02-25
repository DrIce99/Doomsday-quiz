from customtkinter import *
from matplotlib import pyplot as plt
from modules.quiz_module import QuizFrame
from modules.stats_module import StatsFrame

class DoomsdayApp(CTk):
    def __init__(self):
        super().__init__()
        self.title("Doomsday Pro Hub")
        self.geometry("900x600")
        
        self.current_theme = "Dark"
        set_appearance_mode(self.current_theme)
        set_default_color_theme("blue")

        self.container = CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.show_home()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        # Ferma i timer e chiudi tutto prima di uscire
        self.running = False
        plt.close('all')
        self.quit() # Ferma il mainloop
        self.destroy() # Distrugge i widget

    def fade_in(self, widget):
        """Semplice effetto di apparizione fluida"""
        widget.configure(alpha=0) # Se supportato, altrimenti usiamo il delay
        for i in range(1, 11):
            self.after(i*20, lambda: None) # Simulazione carico

    def show_page(self, frame_class, show_nav=True):
        # Pulisce con un piccolo ritardo visivo per il "refresh bello"
        for w in self.container.winfo_children(): w.destroy()
        
        if show_nav:
            nav = CTkFrame(self.container, height=60, fg_color="transparent")
            nav.pack(fill="x", pady=5)
            CTkButton(nav, text="⬅ TORNA ALLA HOME", width=150, height=35, 
                      font=("Arial", 11, "bold"), fg_color="#34495e",
                      command=self.show_home).pack(side="left", padx=20)

        page = frame_class(self.container)
        page.pack(fill="both", expand=True, padx=20, pady=10)

    def show_home(self):
        for w in self.container.winfo_children(): w.destroy()
        home = CTkFrame(self.container, fg_color="transparent")
        home.pack(expand=True)

        CTkLabel(home, text="🧠 Doomsday Master", font=("Arial", 42, "bold")).pack(pady=40)
        
        btn_f = CTkFrame(home, fg_color="transparent")
        btn_f.pack(pady=10)
        
        CTkButton(btn_f, text="INIZIA ALLENAMENTO", height=60, width=300, font=("Arial", 16, "bold"),
                  command=lambda: self.show_page(QuizFrame)).pack(pady=10)
        
        CTkButton(btn_f, text="VISUALIZZA STATISTICHE", height=60, width=300, font=("Arial", 16, "bold"),
                  fg_color="#2ecc71", hover_color="#27ae60",
                  command=lambda: self.show_page(StatsFrame)).pack(pady=10)

        # Theme Switcher in basso
        self.tm = CTkSwitch(home, text="Modalità Luce", command=self.toggle_theme)
        self.tm.pack(pady=50)

    def toggle_theme(self):
        self.current_theme = "Light" if self.tm.get() else "Dark"
        set_appearance_mode(self.current_theme)

if __name__ == "__main__":
    DoomsdayApp().mainloop()
