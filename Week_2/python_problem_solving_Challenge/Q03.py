goblin = ["Queens", "Manhattan",
"Brooklyn", "Bronx"]
octopus = ["Manhattan", "Brooklyn",
"Harlem"]
vulture = ["Manhattan", "Bronx",
"Harlem"]

# n_villains = int((input("no. of villains: ")))

# villains_territories = {}
# for i in range (n_villains):
#     name = str(input("enter villain name: "))
#     n_territories = int((input("no. of territories: ")))
#     for 
#     villains_territories[]

all_territories = goblin+octopus+vulture
most_common = set(goblin) & set(octopus) & set(vulture)
unique_territory= set(goblin)- set(octopus) - set(vulture)
distinct_territory = len(set(all_territories))

print(f"""Contested by all three: {most_common}
Controlled by exactly one: {unique_territory}
Distinct neighborhoods: {distinct_territory}

      """)