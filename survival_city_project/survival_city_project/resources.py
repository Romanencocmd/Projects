class ResourceProduction:
    def __init__(self):
        self.production_rates = {
            "farm": {"base": 10, "per_worker": 5, "skill_multiplier": 2},
            "water_collector": {"base": 15, "per_worker": 3, "skill_multiplier": 1.5},
            "scavenging": {"base": 0, "per_worker": 8, "skill_multiplier": 3}
        }
        self.consumption_rates = {
            "food": {"per_survivor": 2, "stress_multiplier": 1.5},
            "water": {"per_survivor": 1.5, "stress_multiplier": 1.2},
            "medicine": {"per_sick": 1, "prevention_use": 0.1}
        }

    def calculate_production(self, building_type, worker_count, avg_skill, building_level=1):
        if building_type not in self.production_rates:
            return 0
        rates = self.production_rates[building_type]
        base = rates["base"] * building_level
        worker_contribution = rates["per_worker"] * worker_count
        skill_bonus = rates["skill_multiplier"] * avg_skill
        return base + worker_contribution + skill_bonus

    def calculate_consumption(self, population, sick_count=0, stress_level=0):
        if not population:
            return {"food": 0, "water": 0, "medicine": 0}
            
        stress_factor = 1 + (stress_level / 100)
        food_consumption = self.consumption_rates["food"]["per_survivor"] * len(population) * stress_factor
        water_consumption = self.consumption_rates["water"]["per_survivor"] * len(population) * stress_factor
        medicine_consumption = (self.consumption_rates["medicine"]["per_sick"] * sick_count + 
                              self.consumption_rates["medicine"]["prevention_use"] * len(population))
        
        return {
            "food": food_consumption,
            "water": water_consumption,
            "medicine": medicine_consumption
        }

    def calculate_efficiency(self, worker_morale, building_damage, weather="normal"):
        morale_factor = worker_morale / 100
        damage_factor = 1 - (building_damage / 200)
        weather_modifiers = {
            "normal": 1.0,
            "rain": 0.9,
            "storm": 0.7,
            "drought": 0.8,
            "clear": 1.1
        }
        weather_factor = weather_modifiers.get(weather, 1.0)
        
        return morale_factor * damage_factor * weather_factor

    def predict_shortage(self, current_resources, production, consumption, days=7):
        shortage = {}
        for resource in current_resources:
            net_daily = production.get(resource, 0) - consumption.get(resource, 0)
            if net_daily >= 0:
                shortage[resource] = "No shortage predicted"
            else:
                days_until_empty = current_resources[resource] / abs(net_daily)
                shortage[resource] = f"Shortage in {days_until_empty:.1f} days"
        return shortage

class EconomyManager:
    def __init__(self):
        self.resources = {
            "food": 100, 
            "water": 100, 
            "medicine": 20, 
            "materials": 50,
            "wood": 50,
            "metal": 30
        }
        self.production_buildings = []
        self.daily_history = []
        self.production_system = ResourceProduction()

    def add_production_building(self, building_type, workers=[]):
        building_info = {
            "type": building_type,
            "workers": workers,
            "avg_skill": sum(w.skills.get("farming" if building_type == "farm" else "scouting", 1) 
                            for w in workers) / max(1, len(workers))
        }
        self.production_buildings.append(building_info)
        return f"Added {building_type} with {len(workers)} workers"

    def process_daily_economy(self, population, weather="normal"):
        if not population:
            return {
                "production": {r: 0 for r in ["food", "water", "materials"]},
                "consumption": {r: 0 for r in ["food", "water", "medicine"]},
                "current_resources": self.resources.copy()
            }

        daily_production = {
            "food": 0,
            "water": 0,
            "materials": 0
        }
        
        for building in self.production_buildings:
            workers = building["workers"]
            worker_count = len(workers)
            avg_morale = sum(w.morale for w in workers) / max(1, worker_count)
            efficiency = self.production_system.calculate_efficiency(
                avg_morale, 0, weather)
            if building["type"] == "farm":
                production = self.production_system.calculate_production(
                    "farm", worker_count, building["avg_skill"])
                daily_production["food"] += production * efficiency
            elif building["type"] == "water_collector":
                production = self.production_system.calculate_production(
                    "water_collector", worker_count, building["avg_skill"])
                daily_production["water"] += production * efficiency
            elif building["type"] == "scavenging":
                production = self.production_system.calculate_production(
                    "scavenging", worker_count, building["avg_skill"])
                daily_production["materials"] += production * efficiency
        
        sick_count = sum(1 for survivor in population if survivor.health < 70)
        stress_level = 100 - sum(survivor.morale for survivor in population) / len(population)
        daily_consumption = self.production_system.calculate_consumption(
            population, sick_count, stress_level)
        
        for resource in daily_production:
            self.resources[resource] = max(0, self.resources[resource] + daily_production[resource])
        for resource in daily_consumption:
            self.resources[resource] = max(0, self.resources[resource] - daily_consumption[resource])
        
        self.daily_history.append({
            "day": len(self.daily_history) + 1,
            "production": daily_production,
            "consumption": daily_consumption,
            "resources": self.resources.copy()
        })
        
        return {
            "production": daily_production,
            "consumption": daily_consumption,
            "current_resources": self.resources
        }

    def get_economy_report(self, days=7):
        if not self.daily_history:
            return "No economic data available"
        
        avg_production = {
            "food": sum(d["production"]["food"] for d in self.daily_history[-days:]) / days,
            "water": sum(d["production"]["water"] for d in self.daily_history[-days:]) / days
        }
        
        avg_consumption = {
            "food": sum(d["consumption"]["food"] for d in self.daily_history[-days:]) / days,
            "water": sum(d["consumption"]["water"] for d in self.daily_history[-days:]) / days
        }
        
        report = {
            "summary": {
                "total_food_produced": sum(d["production"]["food"] for d in self.daily_history[-days:]),
                "total_water_produced": sum(d["production"]["water"] for d in self.daily_history[-days:]),
                "average_food_consumption": avg_consumption["food"],
                "average_water_consumption": avg_consumption["water"],
                "resource_trends": {
                    "food": self.daily_history[-1]["resources"]["food"] - self.daily_history[-min(days+1, len(self.daily_history))]["resources"]["food"],
                    "water": self.daily_history[-1]["resources"]["water"] - self.daily_history[-min(days+1, len(self.daily_history))]["resources"]["water"]
                }
            },
            "shortage_prediction": self.production_system.predict_shortage(
                self.resources,
                avg_production,
                avg_consumption,
                days
            )
        }
        return report

    def optimize_worker_assignment(self, available_workers):
        recommendations = []
        food_priority = max(0, 100 - self.resources["food"]) / 100
        water_priority = max(0, 100 - self.resources["water"]) / 100
        materials_priority = max(0, 50 - self.resources["materials"]) / 50
        total_priority = food_priority + water_priority + materials_priority
        if total_priority == 0:
            total_priority = 1
        food_workers = int(len(available_workers) * (food_priority / total_priority))
        water_workers = int(len(available_workers) * (water_priority / total_priority))
        scavenge_workers = len(available_workers) - food_workers - water_workers
        recommendations.append(f"Assign {food_workers} to farms, {water_workers} to water collectors, {scavenge_workers} to scavenging")
        return recommendations