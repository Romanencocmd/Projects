import random

class Survivor:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.health = 100
        self.hunger = 0
        self.thirst = 0
        self.morale = 75
        self.skills = {
            "combat": 1,
            "medical": 1,
            "farming": 1,
            "building": 1,
            "scouting": 1
        }
        self.current_job = None
        self.job_experience = {}

    def update_needs(self):
        self.hunger = min(100, self.hunger + 10)
        self.thirst = min(100, self.thirst + 15)
        if self.hunger >= 100 or self.thirst >= 100:
            self.health = 0

    def consume_resources(self, food=0, water=0):
        if food > 0:
            self.hunger = max(0, self.hunger - (food * 10))
        if water > 0:
            self.thirst = max(0, self.thirst - (water * 15))
        if self.hunger < 30 and self.thirst < 30:
            self.morale = min(100, self.morale + 5)

    def gain_experience(self, skill, amount):
        if skill in self.skills:
            self.skills[skill] += amount
            self.job_experience[skill] = self.job_experience.get(skill, 0) + amount
            if self.skills[skill] > 10:
                self.skills[skill] = 10

    def calculate_productivity(self):
        health_factor = self.health / 100
        morale_factor = self.morale / 100
        needs_factor = 1 - ((self.hunger + self.thirst) / 200)
        return (health_factor * 0.4 + morale_factor * 0.4 + needs_factor * 0.2)


class Job:
    def __init__(self, name, required_skill, danger_level):
        self.name = name
        self.required_skill = required_skill
        self.danger_level = danger_level
        self.assigned_survivors = []

    def assign_survivor(self, survivor):
        if survivor not in self.assigned_survivors:
            self.assigned_survivors.append(survivor)
            survivor.current_job = self.name

    def calculate_output(self):
        total_output = 0
        for survivor in self.assigned_survivors:
            skill_level = survivor.skills.get(self.required_skill, 1)
            productivity = survivor.calculate_productivity()
            total_output += skill_level * productivity
        return total_output

    def process_danger(self):
        for survivor in self.assigned_survivors:
            if random.random() < (self.danger_level / 100):
                damage = random.randint(1, self.danger_level)
                survivor.health = max(0, survivor.health - damage)
                if random.random() < 0.3:
                    survivor.gain_experience(self.required_skill, 0.5)


class PopulationManager:
    def __init__(self):
        self.survivors = []
        self.jobs = {
    "Guard": Job("Guard", "combat", 7),
    "Farmer": Job("Farmer", "farming", 2),
    "Medic": Job("Medic", "medical", 3),
    "Builder": Job("Builder", "building", 4),
    "Scout": Job("Scout", "scouting", 8)
}

    def add_survivor(self, survivor):
        self.survivors.append(survivor)

    def daily_update(self):
        dead_survivors = []
        for survivor in self.survivors:
            survivor.update_needs()
            if survivor.health <= 0:
                dead_survivors.append(survivor)
                if survivor.current_job and survivor in self.jobs[survivor.current_job].assigned_survivors:
                    self.jobs[survivor.current_job].assigned_survivors.remove(survivor)
        for dead in dead_survivors:
            self.survivors.remove(dead)
        for job in self.jobs.values():
            job.process_danger()

    def get_specialists(self, skill, min_level=3):
        return [s for s in self.survivors if s.skills.get(skill, 0) >= min_level]

    def calculate_total_consumption(self):
        total_food = 0
        total_water = 0
        for survivor in self.survivors:
            total_food += 2 + (survivor.hunger / 50)
            total_water += 1.5 + (survivor.thirst / 75)
        return {"food": total_food, "water": total_water}