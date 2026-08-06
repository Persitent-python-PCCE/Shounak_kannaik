team_games = [("Brazil", 3, 0, 0),
               ("Japan", 1, 2,0),
               ("Spain", 2, 0, 1),
               ("Ghana", 0, 1,2)]

qualified_teams = filter(lambda games: (3*games[1]) + (1*games[2]) + (0*games[3])>=6 and games[3]<=1, team_games)
print("going to knockouts:")
for team in qualified_teams:
    print(f'{team[0]} - {(3*team[1]) + (1*team[2]) + (0*team[3])}')