import customtkinter as ctk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.patches as mpatches
import random

class FuocoComposto(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("Sistema di Fiamme Vettoriali")
        self.configure(fg_color="#1a1a1a")

        # Configurazione Figura
        self.fig, self.ax = plt.subplots(figsize=(5, 8), facecolor="#1a1a1a")
        self.ax.set_facecolor("#1a1a1a")
        self.ax.set_xlim(-0.8, 0.8)
        self.ax.set_ylim(0, 2.5)
        self.ax.axis('off')

        # Parametri del sistema
        self.num_fiamme = 4
        self.fiamme_patches = []
        # Ogni fiamma ha: [offset_fase, velocità, scala_altezza, colore]
        self.fiamme_data = [
            [random.uniform(0, 3), random.uniform(18, 22), 1.6, "#FF5733"],
            [random.uniform(0, 3), random.uniform(20, 24), 1.2, "#FF8D33"],
            [random.uniform(0, 3), random.uniform(17, 20), 1.4, "#C70039"],
            [random.uniform(0, 3), random.uniform(22, 26), 0.9, "#FFC300"]
        ]
        
        # Particelle (fiammelle che salgono)
        self.particles = [] # Ogni particella: [patch, y_pos, x_offset, speed]

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.ani = FuncAnimation(self.fig, self.update, frames=np.linspace(0, 100, 1000),
                                 interval=20, blit=False)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update(self, frame):
        # 1. Pulizia frame precedente
        for p in self.fiamme_patches: p.remove()
        self.fiamme_patches = []

        # 2. Aggiornamento Fiamme Principali
        for data in self.fiamme_data:
            fase_init, vel, h_max, col = data
            t = frame * (vel / 50) + fase_init # Tempo accelerato
            
            y = np.linspace(0, h_max, 30)
            # Ampiezza ridotta (0.05) e velocità aumentata
            oscillation = 0.05 * np.sin(6 * y - t) * (y / h_max)
            width = 0.18 * np.sin(np.pi * (y / h_max)**0.6)
            
            verts = np.column_stack([
                np.concatenate([oscillation - width, (oscillation + width)[::-1]]),
                np.concatenate([y, y[::-1]])
            ])
            
            patch = mpatches.Polygon(verts, facecolor=col, alpha=0.25, edgecolor="#FF5733")
            self.ax.add_patch(patch)
            self.fiamme_patches.append(patch)

        # 3. Gestione Piccole Fiamme (Scintille/Particelle)
        if random.random() > 0.95: # Probabilità di nascita
            p_patch = mpatches.Circle((random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1)), 0.01, color="#FFC300", alpha=0.4)
            self.ax.add_patch(p_patch)
            self.particles.append({'patch': p_patch, 'y': 0.5, 'x': random.uniform(-0.05, 0.05), 'speed': random.uniform(0.03, 0.06)})

        for p in self.particles[:]:
            p['y'] += p['speed']
            # Movimento erratico laterale
            p['x'] += 0.01 * np.sin(frame + p['y']*10)
            p['patch'].center = (p['x'], p['y'])
            p['patch'].set_alpha(max(0, 0.4 - (p['y']-0.5)/1.5)) # Svanisce salendo
            
            if p['y'] > 2.2: # Rimuovi se troppo in alto
                p['patch'].remove()
                self.particles.remove(p)

        return self.fiamme_patches

    def on_closing(self):
        self.ani.event_source.stop()
        plt.close(self.fig)
        self.quit()
        self.destroy()

if __name__ == "__main__":
    app = FuocoComposto()
    app.mainloop()
