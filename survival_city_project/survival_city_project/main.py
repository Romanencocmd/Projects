import random
from buildings import BuildingManager
from survivors import Survivor, PopulationManager
from resources import EconomyManager
from zombies import ZombieHorde
from events import EventProbabilityEngine, EventChainSystem
from combat import CombatSystem
from statistics import GameStatistics
from save import SaveGameManager

class SurvivalGame:
    def __init__(self):
        self.day = 1
        self.weather = "clear"
        self.building_manager = BuildingManager()
        self.population_manager = PopulationManager()
        self.economy_manager = EconomyManager()
        self.zombie_horde = ZombieHorde()
        self.event_engine = EventProbabilityEngine()
        self.event_system = EventChainSystem(self.event_engine)
        self.combat_system = CombatSystem()
        self.statistics = GameStatistics()
        self.save_manager = SaveGameManager()
        
      
        for i in range(5):
            self.add_random_survivor()
    
    def add_random_survivor(self):
        names = ["Alex", "Jamie", "Taylor", "Casey", "Riley", "Morgan"]
        survivor = Survivor(random.choice(names), random.randint(18, 60))
        for skill in survivor.skills:
            survivor.skills[skill] += random.uniform(-0.5, 0.5)
            survivor.skills[skill] = max(1, min(10, survivor.skills[skill]))
        self.population_manager.add_survivor(survivor)
        return survivor
    
    def process_day(self):
        if not self.population_manager.survivors:
            return {
                "game_over": True,
                "reason": "All survivors have died",
                "day": self.day
            }

        self.population_manager.daily_update()
        if not self.population_manager.survivors:
            return {
                "game_over": True,
                "reason": "All survivors have died",
                "day": self.day
            }

        economy_report = self.economy_manager.process_daily_economy(
            self.population_manager.survivors, self.weather)
        
        self.building_manager.daily_update()
        
        game_state = {
            "day_number": self.day,
            "population": len(self.population_manager.survivors),
            "resource_shortage": sum(1 for r in economy_report["current_resources"].values() if r < 20),
            "weather": self.weather
        }
        
        triggered_events = self.event_engine.check_event_triggers(game_state)
        for event in triggered_events:
            self.handle_event(event)
        human_positions = [[random.randint(0, 100), random.randint(0, 100)] 
                          for _ in self.population_manager.survivors]
        self.zombie_horde.update_all(human_positions)
        

        survivors_in_combat = [{
            "name": s.name,
            "combat_skill": s.skills["combat"],
            "weapon": random.choice(["fists", "knife", "melee_weapon"]),
            "position": [random.randint(0, 100), random.randint(0, 100)]
        } for s in self.population_manager.survivors if s.skills["combat"] > 3]
        
        combat_results = self.combat_system.group_combat(survivors_in_combat, self.zombie_horde.zombies)
        
        self.statistics.record_daily_snapshot({
            "day": self.day,
            "survivors": self.population_manager.survivors,
            "resources": economy_report["current_resources"],
            "buildings": self.building_manager.buildings
        })
        
        self.day += 1
        self.weather = random.choice(["clear", "rain", "storm"])
        
        return {
            "day": self.day - 1,
            "events": triggered_events,
            "combat_results": combat_results,
            "economy": economy_report
        }
    
    def handle_event(self, event):
        if event["type"] == "zombie_attack":
            for _ in range(event["severity"]):
                self.zombie_horde.spawn_zombie(random.choice(["shambler", "runner"]))
        elif event["type"] == "survivor_joins":
            for _ in range(event["severity"]):
                self.add_random_survivor()
        elif event["type"] == "resource_discovery":
            resources = ["food", "water", "wood", "metal"]
            for _ in range(event["severity"]):
                resource = random.choice(resources)
                self.economy_manager.resources[resource] += random.randint(10, 30)
        elif event["type"] == "disease_outbreak":
            for survivor in random.sample(self.population_manager.survivors, 
                                       min(event["severity"], len(self.population_manager.survivors))):
                survivor.health -= random.randint(10, 30)
    
    def save_game(self, save_name=None):
        game_state = {
            "day": self.day,
            "weather": self.weather,
            "buildings": [{
                "name": b.name,
                "position": b.position,
                "level": b.level,
                "current_hp": b.current_hp,
                "is_built": b.is_built
            } for b in self.building_manager.buildings],
            "survivors": [{
                "name": s.name,
                "age": s.age,
                "health": s.health,
                "skills": s.skills
            } for s in self.population_manager.survivors],
            "resources": self.economy_manager.resources
        }
        return self.save_manager.save_game(game_state, save_name)
    
    def load_game(self, save_file):
        success, result = self.save_manager.load_game(save_file)
        if not success:
            return False, result
        
        self.day = 1
        self.weather = "clear"
        self.building_manager = BuildingManager()
        self.population_manager = PopulationManager()
        self.economy_manager = EconomyManager()
        self.zombie_horde = ZombieHorde()
        
        self.day = result.get("day", 1)
        self.weather = result.get("weather", "clear")
        self.economy_manager.resources = result.get("resources", {
            "food": 100, "water": 100, "medicine": 20, 
            "materials": 50, "wood": 50, "metal": 30
        })
        
        for building_data in result.get("buildings", []):
            try:
                pos_tuple = tuple(building_data["position"]) if isinstance(building_data["position"], list) else building_data["position"]
                success, _ = self.building_manager.place_building(building_data["name"].lower(), pos_tuple)
                if success:
                    building = self.building_manager.buildings[-1]
                    building.level = building_data.get("level", 1)
                    building.current_hp = building_data.get("current_hp", building.max_hp)
                    building.is_built = building_data.get("is_built", True)
            except Exception as e:
                print(f"Error loading building: {str(e)}")
                continue
        
        for survivor_data in result.get("survivors", []):
            try:
                survivor = Survivor(
                    survivor_data["name"],
                    survivor_data["age"]
                )
                survivor.health = survivor_data.get("health", 100)
                survivor.skills = survivor_data.get("skills", {
                    "combat": 1, "medical": 1, "farming": 1, 
                    "building": 1, "scouting": 1
                })
                self.population_manager.add_survivor(survivor)
            except Exception as e:
                print(f"Error loading survivor: {str(e)}")
                continue
        
        return True, "Game loaded successfully"

def main():
    print("Welcome to Zombie Survival Simulator!")
    print("1. New Game")
    print("2. Load Game")
    choice = input("Select an option: ")
    
    game = SurvivalGame()
    
    if choice == "2":
        saves = game.save_manager.list_saves()
        if not saves:
            print("No save games found")
        else:
            print("Available saves:")
            for i, save in enumerate(saves, 1):
                print(f"{i}. {save}")
            save_choice = int(input("Select save to load: ")) - 1
            success, message = game.load_game(saves[save_choice])
            print(message)
            if not success:
                return
    
    while True:
        print(f"\nDay {game.day} - Weather: {game.weather}")
        print(f"Survivors: {len(game.population_manager.survivors)}")
        print("Resources:", game.economy_manager.resources)
        print("\nActions:")
        print("1. Build (shelter/farm/watchtower/workshop)")
        print("2. Assign jobs")
        print("3. View statistics")
        print("4. Next day")
        print("5. Quit")
        
        action = input("Choose action: ")
        
        if action == "1":
            building_type = input("Building type (shelter/farm/watchtower/workshop): ")
            x = int(input("X position (0-100): "))
            y = int(input("Y position (0-100): "))
            success, message = game.building_manager.place_building(building_type, (x, y))
            print(message)
        
        elif action == "2":
            for i, survivor in enumerate(game.population_manager.survivors, 1):
                print(f"{i}. {survivor.name} - Combat: {survivor.skills['combat']} Farming: {survivor.skills['farming']}")
            survivor_idx = int(input("Select survivor: ")) - 1
            job = input("Job (guard/farmer/medic/builder/scout): ")
            if job in game.population_manager.jobs:
                game.population_manager.jobs[job].assign_survivor(
                    game.population_manager.survivors[survivor_idx])
                print(f"Assigned {game.population_manager.survivors[survivor_idx].name} to {job}")
        
        elif action == "3":
            stats = game.statistics.calculate_survival_rating()
            print(f"Survival Rating: {stats:.1f}/100")
        
        
        elif action == "4":
            day_report = game.process_day()
            if day_report.get("game_over"):
                print(f"\nGAME OVER! {day_report['reason']}")
                print(f"Survived until day {day_report['day']}")
                break
            print(f"Day {day_report['day']} completed")
            for event in day_report["events"]:
                print(f"Event: {event['type']} (severity: {event['severity']})")
            for result in day_report["combat_results"]:
                print(result)
        
        elif action == "5":
            save = input("Save before quitting? (y/n): ")
            if save.lower() == "y":
                game.save_game()
            break

if __name__ == "__main__":
    main()