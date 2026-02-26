import customtkinter as ctk
import tkinter as tk
import math
import random

class Node:
    def __init__(self, x, y, parent=None):
        self.base_rel_x = x - (parent.x if parent else x)
        self.base_rel_y = y - (parent.y if parent else y)
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.parent = parent
        self.children = []
        # Profondità del nodo per calcolare la resistenza al vento
        self.depth = parent.depth + 1 if parent else 0

class LSystemPhysicalTree(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("900x800")
        self.title("L-System Spring Tree")

        self.axiom = "X"
        self.rules = {"X": "F[+X][-X]FX", "F": "FF"}
        self.angle_cfg = 22
        
        self.canvas = tk.Canvas(self, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)

        self.slider = ctk.CTkSlider(self, from_=0, to=5, number_of_steps=5, command=self.update_tree)
        self.slider.set(0)
        self.slider.pack(pady=10)

        self.nodes = []
        self.wind_phase = 0
        self.stiffness = 0.95  # Aumentata rigidità
        self.damping = 0.40    # Aumentato smorzamento per meno oscillazioni "impazzite"
        
        self.update() 
        self.update_tree(0)
        self.animate()

    def generate_l_system(self, iterations):
        s = self.axiom
        for _ in range(iterations):
            s = "".join(self.rules.get(c, c) for c in s)
        return s

    def update_tree(self, value):
        iteration = int(value)
        instructions = self.generate_l_system(iteration)
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        stack, curr_x, curr_y, curr_angle = [], w / 2, h - 50, 90
        length = 110 / (pow(1.8, iteration)) if iteration > 0 else 60
        
        self.nodes = []
        root = Node(curr_x, curr_y)
        self.nodes.append(root)
        current_node = root

        for char in instructions:
            if char == "F":
                jitter = random.uniform(-2, 2) # Ridotto jitter per rami più puliti
                rad = math.radians(curr_angle + jitter)
                next_x = curr_x + length * math.cos(rad)
                next_y = curr_y - length * math.sin(rad)
                new_node = Node(next_x, next_y, parent=current_node)
                current_node.children.append(new_node)
                self.nodes.append(new_node)
                curr_x, curr_y, current_node = next_x, next_y, new_node
            elif char == "+": curr_angle += self.angle_cfg
            elif char == "-": curr_angle -= self.angle_cfg
            elif char == "[": stack.append((curr_x, curr_y, curr_angle, current_node))
            elif char == "]": curr_x, curr_y, curr_angle, current_node = stack.pop()

    def animate(self):
        self.wind_phase += 0.08
        # Vento più calmo
        base_wind = math.sin(self.wind_phase) * 0.2
        
        for node in self.nodes:
            if node.parent:
                # Il vento colpisce di più le parti alte (depth maggiore)
                wind_influence = (node.depth * 0.01) * base_wind
                
                target_x = node.parent.x + node.base_rel_x
                target_y = node.parent.y + node.base_rel_y
                
                ax = (target_x - node.x) * self.stiffness + wind_influence
                ay = (target_y - node.y) * self.stiffness
                
                node.vx = (node.vx + ax) * self.damping
                node.vy = (node.vy + ay) * self.damping
                node.x += node.vx
                node.y += node.vy

        self.draw_frame()
        self.after(30, self.animate)

    def draw_leaf(self, x, y, angle):
        """Disegna una foglia a forma di goccia/rombo orientata."""
        size = 6
        rad = math.radians(angle)
        # Coordinate relative per creare una forma a lancia
        p1 = (x + size*2 * math.cos(rad), y - size*2 * math.sin(rad))
        p2 = (x + size * math.cos(rad + 2), y - size * math.sin(rad + 2))
        p3 = (x + size * math.cos(rad - 2), y - size * math.sin(rad - 2))
        self.canvas.create_polygon(x, y, p2[0], p2[1], p1[0], p1[1], p3[0], p3[1], 
                                   fill="#388E3C", outline="#1B5E20")

    def draw_frame(self):
        self.canvas.delete("all")
        for node in self.nodes:
            if node.parent:
                # Spessore variabile: base più doppia, cime sottili
                w = max(1, 6 - (node.depth // 3))
                self.canvas.create_line(node.parent.x, node.parent.y, node.x, node.y, 
                                      fill="#4E342E", width=w, capstyle=tk.ROUND)
                
                if not node.children:
                    # Calcola l'angolo della foglia basandosi sulla direzione del ramo
                    angle = math.degrees(math.atan2(-(node.y - node.parent.y), node.x - node.parent.x))
                    self.draw_leaf(node.x, node.y, angle)

if __name__ == "__main__":
    app = LSystemPhysicalTree()
    app.mainloop()
