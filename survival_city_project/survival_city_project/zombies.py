import math
import random

class BaseZombie:
    def __init__(self, zombie_type, health, speed, damage):
        self.zombie_type = zombie_type
        self.health = health
        self.max_health = health
        self.speed = speed
        self.damage = damage
        self.position = [random.randint(0, 100), random.randint(0, 100)]
        self.state = "wandering"

    def move_towards(self, target_position):
        direction = [target_position[0] - self.position[0], target_position[1] - self.position[1]]
        distance = math.sqrt(direction[0]**2 + direction[1]**2)
        if distance > 0:
            self.position[0] += (direction[0] / distance) * self.speed
            self.position[1] += (direction[1] / distance) * self.speed

    def take_damage(self, amount):
        self.health -= amount
        return f"{self.zombie_type} {'died' if self.health <= 0 else f'has {self.health} health left'}."

    def can_detect_human(self, human_position, max_range):
        distance = math.sqrt((human_position[0] - self.position[0])**2 + 
                           (human_position[1] - self.position[1])**2)
        return distance <= max_range

class Shambler(BaseZombie):
    def __init__(self):
        super().__init__("shambler", health=100, speed=1, damage=10)

class Runner(BaseZombie):
    def __init__(self):
        super().__init__("runner", health=70, speed=4, damage=15)

    def lunge_attack(self, target_position):
        self.move_towards(target_position)
        self.speed += 2

class Screamer(BaseZombie):
    def __init__(self):
        super().__init__("screamer", health=50, speed=2, damage=5)

    def alert_nearby(self, horde):
        for zombie in horde.zombies:
            if zombie != self and self.can_detect_human(zombie.position, 15):
                zombie.state = "chasing"

class ZombieHorde:
    def __init__(self):
        self.zombies = []

    def spawn_zombie(self, zombie_type):
        zombie_classes = {"shambler": Shambler, "runner": Runner, "screamer": Screamer}
        self.zombies.append(zombie_classes[zombie_type]())

    def update_all(self, human_positions):
        for zombie in self.zombies:
            for human_pos in human_positions:
                if zombie.can_detect_human(human_pos, 30):
                    zombie.state = "chasing"
                    zombie.move_towards(human_pos)