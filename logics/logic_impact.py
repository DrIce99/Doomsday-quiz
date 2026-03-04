import collections

def calculate_impacts(all_data, cond_data):
    # Raggruppa i tempi per etichetta di condizione
    stats_by_cond = collections.defaultdict(list)
    results_by_cond = collections.defaultdict(list)
    times_by_cond = collections.defaultdict(list)
    global_times = [d["time"] for d in all_data if d["correct"]]
    global_avg = sum(global_times) / len(global_times) if global_times else 0
    global_wr = (len(global_times) / len(all_data) * 100) if all_data else 0

    for d in all_data:
        # Prendi solo la data dal timestamp (YYYY-MM-DD)
        date_key = d["timestamp"].split(" ")[0]
        if date_key in cond_data:
            label = cond_data[date_key]["label"]
            results_by_cond[label].append(d["correct"])
            if d["correct"]:
                times_by_cond[label].append(d["time"])

    impact_results = []
    for label in results_by_cond:
        # Calcolo Tempo Medio
        times = times_by_cond[label]
        avg = sum(times) / len(times) if times else 0
        diff_time = avg - global_avg
        
        # Calcolo Winrate specifico della condizione
        attempts = results_by_cond[label]
        wr = (sum(1 for x in attempts if x) / len(attempts)) * 100
        diff_wr = wr - global_wr # Scostamento dal winrate abituale
        
        impact_results.append({
            "label": label,
            "avg": avg,
            "diff_time": diff_time,
            "wr": wr,
            "diff_wr": diff_wr,
            "count": len(attempts)
        })
    
    return impact_results, global_avg, global_wr

def calculate_trend_metrics(all_data):
    from datetime import datetime, date, timedelta

    today = date.today()

    # Solo risposte corrette
    correct_data = [
        d for d in all_data
        if d["correct"]
    ]

    if not correct_data:
        return 0, 0, 0, 0, "+"

    # --- MEDIA GLOBALE ---
    global_avg = sum(d["time"] for d in correct_data) / len(correct_data)

    # --- MEDIA ULTIMI 7 GIORNI ---
    last_7 = []
    for d in correct_data:
        dt = datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S").date()
        if (today - dt).days <= 7:
            last_7.append(d["time"])

    recent_avg = sum(last_7) / len(last_7) if last_7 else 0

    # --- MEDIA OGGI ---
    today_times = []
    for d in correct_data:
        dt = datetime.strptime(d["timestamp"], "%Y-%m-%d %H:%M:%S").date()
        if dt == today:
            today_times.append(d["time"])

    today_avg = sum(today_times) / len(today_times) if today_times else 0

    # --- PERCENTUALE MIGLIORAMENTO ---
    if global_avg > 0:
        perc = ((today_avg - global_avg) / global_avg) * 100
    else:
        perc = 0

    sign = "+" if perc > 0 else ""
    margine = abs(perc)

    return recent_avg, today_avg, perc, margine, sign