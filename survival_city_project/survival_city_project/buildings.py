class BaseBuilding:
    def __init__(self, name, build_cost, build_time, max_hp):
        self.name = name
        self.build_cost = build_cost  
        self.build_time = build_time  
        self.current_hp = max_hp
        self.max_hp = max_hp
        self.level = 1
        self.position = None
        self.is_built = False
        self.construction_progress = 0

    def start_construction(self, position):
        self.position = position
        self.is_built = False
        self.construction_progress = 0
        return f"Construction of {self.name} started at {position}"

    def advance_construction(self, workers=1):
        if not self.is_built:
            self.construction_progress += workers / self.build_time
            if self.construction_progress >= 1:
                self.is_built = True
                return f"{self.name} construction completed!"
            return f"{self.name} construction progress: {self.construction_progress*100:.1f}%"
        return f"{self.name} is already built"

    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp <= 0:
            return f"{self.name} has been destroyed!"
        return f"{self.name} took {amount} damage ({self.current_hp}/{self.max_hp} HP remaining)"

    def repair(self, materials):
        repair_amount = min(materials.get("wood", 0), materials.get("metal", 0)) * 10
        self.current_hp = min(self.max_hp, self.current_hp + repair_amount)
        return f"{self.name} repaired to {self.current_hp}/{self.max_hp} HP"

    def upgrade(self):
        if self.level >= 3:
            return f"{self.name} is already at maximum level"
        self.level += 1
        self.max_hp *= 1.5
        self.current_hp = self.max_hp
        return f"{self.name} upgraded to level {self.level}"

class Shelter(BaseBuilding):
    def __init__(self):
        super().__init__("Shelter", {"wood": 20, "metal": 5}, 2, 200)
        self.capacity = 5 
        self.current_occupants = 0

    def add_occupant(self):
        if self.current_occupants < self.capacity:
            self.current_occupants += 1
            return True
        else:
            return False

    def remove_occupant(self):
        if self.current_occupants > 0:
            self.current_occupants -= 1
            return True
        else:
            return False

class Farm(BaseBuilding):
    def __init__(self):
        super().__init__("Farm", {"wood": 15, "metal": 2}, 3, 150)
        self.production_rate = 10  
        self.assigned_workers = 0

    def produce_food(self, skill_level=1):
        return self.production_rate * self.assigned_workers * skill_level

class Watchtower(BaseBuilding):
    def __init__(self):
        super().__init__("Watchtower", {"wood": 10, "metal": 8}, 4, 120)
        self.vision_range = 50  
        self.detection_chance = 0.7

    def get_vision_range(self, weather="clear"):
        modifiers = {"clear": 1.0, "rain": 0.8, "fog": 0.5, "storm": 0.3}
        return self.vision_range * modifiers.get(weather, 1.0)

class Workshop(BaseBuilding):
    def __init__(self):
        super().__init__("Workshop", {"wood": 25, "metal": 15}, 5, 180)
        self.crafting_speed = 1.0

    def craft_item(self, item_type, materials):
        recipes = {
            "tool": {"wood": 2, "metal": 1},
            "weapon": {"wood": 1, "metal": 3},
            "barricade": {"wood": 5, "metal": 2}
        }
        if item_type in recipes:
            required = recipes[item_type]
            if all(materials.get(k, 0) >= v for k, v in required.items()):
                for k, v in required.items():
                    materials[k] -= v
                return True, f"Successfully crafted {item_type}"
            return False, "Not enough materials"
        return False, "Invalid item type"

class BuildingManager:
    def __init__(self):
        self.buildings = []
        self.building_grid = {}  

    def can_build_at(self, position, building_type):
        if position in self.building_grid:
            return False, "Position already occupied"
        if not (0 <= position[0] < 100 and 0 <= position[1] < 100):
            return False, "Position out of bounds"
        return True, "Position available"

    def place_building(self, building_type, position):
        can_build, message = self.can_build_at(position, building_type)
        if not can_build:
            return False, message
        
        building_classes = {
            "shelter": Shelter,
            "farm": Farm,
            "watchtower": Watchtower,
            "workshop": Workshop
        }
        
        if building_type not in building_classes:
            return False, "Invalid building type"
        
        new_building = building_classes[building_type]()
        new_building.start_construction(position)
        self.buildings.append(new_building)
        self.building_grid[position] = new_building
        return True, f"Started construction of {building_type} at {position}"

    def get_total_capacity(self, building_type=None):
        if building_type == "shelter":
            return sum(b.capacity for b in self.buildings if isinstance(b, Shelter))
        elif building_type == "farm":
            return sum(b.production_rate for b in self.buildings if isinstance(b, Farm))
        return len(self.buildings)

    def daily_update(self):
        for building in self.buildings:
            if not building.is_built:
                building.advance_construction()