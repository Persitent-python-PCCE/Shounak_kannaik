heroes = {}
def create_hero(name, *powers, **stats):
    global heroes
    heroes[name] = {"powers": powers, "stats": stats}
    stat_vals = []
    for k, v in stats.items():
        stat_vals.append(v)
    heroes[name]["overall_rating"] = round((sum(stat_vals)/len(stat_vals)), 1)     
    if heroes[name]["overall_rating"] >=90:
        heroes[name]["rank"] = "S"    
    

create_hero("Spider-Man", "wall-crawl","spider-sense",strength=85, agility=95,intelligence=92)

for hero, props in heroes.items():
    print(f"""
        Hero: {hero}
        Powers: {props["powers"]}
        Stats:{props["stats"]}
        Overall rating: {props["overall_rating"]} --> {props["rank"]}-Tier *
        """)