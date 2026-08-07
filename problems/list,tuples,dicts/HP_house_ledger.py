house_points = {}
def award_points(house, points = 10, reason = "just because", ledger = None):
    global house_points
    if ledger is None:
        ledger = house_points
    ledger[house] = ledger.get(house, 0)+ points
    print(f'{house} +{points} ({reason}) --> toatal: {ledger[house]}')
    house_points = ledger
    return ledger

led = award_points("Gryffindor")
led = award_points("Gryffindor", 50,
"defeating a troll", led)
led = award_points("Slytherin", 30, ledger=led)
print(f'Final Ledger: {house_points}')