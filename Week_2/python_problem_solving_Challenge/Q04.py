coordiantes = [("Falcon", 34.05, -118.24), ("Ghost",99.9, 12.0), ("Condor", 40.71, -74.00)]

for coordinate in coordiantes:
    if coordinate[1] > 90 or coordinate[1] < -90 or coordinate[2] > 180 or coordinate[2] < -180:
        print(f"""INVALID: {coordinate[0]} ({coordinate[1]}, {coordinate[2]})""")
        coordiantes.pop(coordiantes.index(coordinate))
    
print("Briefing (N-->S):")
for coordinate in coordiantes:
        print(f"\t{coordinate[0]} --> lat: {coordinate[1]}, lon: {coordinate[2]}")
