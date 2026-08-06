name = input("Enter name: ")
signal = input("Enter signal: ")

houses = {
    'g': {"house": "Gryffindor", "count": 0},
    'h': {"house": "Hufflepuff", "count": 0},
    'r': {"house": "Ravenclaw", "count": 0},
    's': {"house": "Slytherin", "count": 0}
}

for c in signal.lower():
    if c in houses:
        houses[c]["count"] += 1

highest_count = -1
house = ""
prev_h = ""

for c, h in houses.items():
    count = h["count"]

    if count > highest_count:
        highest_count = count
        house = h["house"]
        prev_h = c

    elif count == highest_count:
        if c < prev_h:
            house = h["house"]
            prev_h = c

print(house)