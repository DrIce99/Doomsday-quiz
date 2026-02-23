probopass = True
while probopass:
    day = 0
    month = 0
    while day < 1 or day > 31:
        day = int(input("Immetti giorno (1-31): "))
    while month < 1 or month > 12:
        month = int(input("Immetti mese (1-12): "))
    year = int(input("Immetti anno (es. 2023): "))
    
    if month == 2 and (day == 29 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) or day > 29):
        print("Quel febbraio non è bisestile/ha meno giorni di quelli immessi. Immetti una data corretta.")
    elif month == 4 and day > 30:
        print("Aprile ha solo 30 giorni. Immetti una data corretta.")
    elif month == 6 and day > 30:
        print("Giugno ha solo 30 giorni. Immetti una data corretta.")
    elif month == 9 and day > 30:
        print("Settembre ha solo 30 giorni. Immetti una data corretta.")
    elif month == 11 and day > 30:
        print("Novembre ha solo 30 giorni. Immetti una data corretta.")
    else:
        probopass = False

anchor = 0
doomsday = 0

weekday_ref = {
    0: "Domenica",
    1: "Lunedì",
    2: "Martedì",
    3: "Mercoledì",
    4: "Giovedì",
    5: "Venerdì",
    6: "Sabato"
}

day_of_month_ref = {
    1: 4 if year%4 == 0 and (year % 100 != 0 or year % 400 == 0) else 3,
    2: 29 if year%4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
    3: 7,
    4: 4,
    5: 9,
    6: 6,
    7: 11,
    8: 8,
    9: 5,
    10: 10,
    11: 7,
    12: 12
}

# anchor_ref = {
#     1800: 5,
#     1900: 3,
#     2000: 2,
#     2100: 0
# }

def calculate_anchor_day():
    temp_year = (year - (year % 100)) / 100
    if temp_year % 4 == 0:
        return 2
    elif temp_year % 4 == 1:
        return 0
    elif temp_year % 4 == 2:
        return 5
    elif temp_year % 4 == 3:
        return 3
    
def calculate_doomsday():
    anchor = calculate_anchor_day()
    last_two_digits = year % 1000
    if last_two_digits % 2 == 1:
        last_two_digits += 11
    else:
        last_two_digits /= 2
    if last_two_digits % 2 == 1:
        last_two_digits += 11
    return 7 - (last_two_digits % 7) + anchor
    

def calculate_weekday():
    doomsday = calculate_doomsday()
    day_of_month = day_of_month_ref[month]
    difference = day - day_of_month
    weekday = (doomsday + difference) % 7
    print(f"anchor: {anchor}")
    print(f"doomsday calculated: {doomsday}")
    print(f"Il giorno della settimana del {day}/{month}/{year} è {weekday_ref[weekday]}")

calculate_weekday()