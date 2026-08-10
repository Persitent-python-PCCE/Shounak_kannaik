from abc import ABC, abstractmethod
import random

class Character(ABC):
    
    def __init__(self, name, health, attack_power, defence, speed):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack_power = attack_power
        self.defence = defence
        self.speed = speed
    
    def take_damage(self, damage):
        damage_taken = max(1, damage - self.defence)
        self.health = max(0, self.health - damage_taken)
        
        return damage_taken
    
    def is_alive(self):
        return self.health > 0
    
    @abstractmethod
    def attack(self, other):
        pass
    
    @staticmethod
    def attack_order(players):
        player_order = sorted(players, key=lambda x: x.speed, reverse=True)
        return player_order

class Warrior(Character):
    def __init__(self, name):
        super().__init__(name, health=130, attack_power=22, defence=12, speed=6)
        self.character_class = "Warrior"
        self.rage = 0
        self.is_berserk = False
    
    def attack(self, other):
        if not self.is_berserk and self.health < self.max_health * 0.30:
            print(f"{self.name} is in BERSERK MODE!")
            self.is_berserk = True
        raw_power = self.attack_power
        if self.is_berserk:
            raw_power *= 2
        if self.rage >= 50:
            raw_power += raw_power * 0.20
            self.rage = 0
        else:
            self.rage += 20
        damage_taken = other.take_damage(raw_power)
        print(f"{self.name} ({self.character_class}) attacks {other.name} for {damage_taken} damage.")

class Mage(Character):
    def __init__(self, name):
        super().__init__(name, health=90, attack_power=30, defence=5, speed=8)
        self.character_class = "Mage"
        self.mana = 100
        self.cast_fireball = True
    
    def attack(self, other):
        if self.cast_fireball and self.mana >= 20:
            raw_power = self.attack_power * 1.5
            self.mana -= 20
            self.health = max(0, self.health - 5)
            damage_taken = other.take_damage(raw_power)
            print(f"{self.name} casts FIREBALL at {other.name} for {damage_taken} damage and loses 5 health.")
        else:
            raw_power = self.attack_power
            damage_taken = other.take_damage(raw_power)
            print(f"{self.name} ({self.character_class}) attacks {other.name} for {damage_taken} damage.")
        
class Archer(Character):
    def __init__(self, name):
        super().__init__(name, health=100, attack_power=24, defence=7, speed=12)
        self.character_class = "Archer"
        self.critical_hit= 0.3
        
    def attack(self, other):
        raw_power = self.attack_power
        crit_chance = random.random()
        if crit_chance < self.critical_hit:
            raw_power = self.attack_power * 2
            print(f"{self.name} used PRECISION SHOT!")
            self.critical_hit = 0
        damage_taken = other.take_damage(raw_power)
        self.critical_hit += 0.1
        print (f"{self.name} ({self.character_class}) attacks {other.name} for {damage_taken} damage.")
        

        
print("Welcome to the Fantasy Battle Arena!")
players = []
n_players = int(input("Enter the number of players (2-3): "))
i = 0
while i < n_players:
    print("Choose your character class:")
    print("1. Warrior")
    print("2. Mage")
    print("3. Archer")
    choice = int(input("Enter your choice (1-3): "))
    name = input(f"Enter the name of your Hero: ")
    
    match choice:
        case 1:
            player = Warrior(name)
            players.append(player)
        case 2:
            player = Mage(name)
            players.append(player)
        case 3:
            player = Archer(name)
            players.append(player)
        case _:
            print("Invalid choice!")
            i -= 1
    i += 1
    
players = Character.attack_order(players)

while True:
    if len(players) == 1:
        print(f"{players[0].name} is the winner!")
        break
    for player in players:
        # print(f"turn: {player.name}")
        target = next(p for p in players if p is not player)
        if player.is_alive() and target.is_alive():
            player.attack(target)
            if not target.is_alive():
                print(f'{target.name} ({target.character_class}) has been defeated')
                players.pop(players.index(target))
            print(f"Health: {player.name}: {player.health}\t||\t{target.name}: {target.health} \n")
    
    
    