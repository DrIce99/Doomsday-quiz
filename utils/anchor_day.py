def get_anchor_day(month, year):
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    if month == 1: return 4 if is_leap else 3
    if month == 2: return 29 if is_leap else 28
    # Per gli altri mesi, estraiamo il primo numero dalla stringa (es: "11/7" -> 11 o "4/4" -> 4)
    # Basandoci sul tuo dizionario:
    anchors = {3:14, 4:4, 5:9, 6:6, 7:11, 8:8, 9:5, 10:10, 11:7, 12:12}
    return anchors.get(month)