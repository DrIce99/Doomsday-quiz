import json, os

CONDITIONS_FILE = "data/conditions_v2.json"

# Mappa predefinita Colore -> Etichetta (puoi aggiungerne altre)
DEFAULT_CONDITIONS = {
    "Fretta": "#3b8ed0",    # Blu
    "Stanchezza": "#f39c12", # Arancione
    "Malattia": "#e74c3c",   # Rosso
    "Focus Alto": "#2ecc71", # Verde
    "Stress": "#9b59b6"      # Viola
}

def load_conditions():
    if not os.path.exists(CONDITIONS_FILE): return {}
    with open(CONDITIONS_FILE, "r") as f:
        try: return json.load(f)
        except: return {}

def save_condition(date_str, label):
    data = load_conditions()
    if label == "Rimuovi":
        if date_str in data: del data[date_str]
    else:
        data[date_str] = {"label": label, "color": DEFAULT_CONDITIONS.get(label, "#333333")}
    
    with open(CONDITIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)
