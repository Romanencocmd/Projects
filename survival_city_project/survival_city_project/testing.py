import unittest
import random
from survivor_system import Survivor, PopulationManager

class GameBalanceTester:
    def __init__(self):
        self.test_scenarios = []
        self.balance_metrics = {
            "survival_rate": 0,
            "resource_balance": 0,
            "combat_balance": 0
        }

    def create_test_scenario(self, name, initial_conditions):
        scenario = {
            "name": name,
            "initial_conditions": initial_conditions,
            "results": None
        }
        self.test_scenarios.append(scenario)
        return scenario

    def run_survival_test(self, days=30, iterations=10):
        success_count = 0
        for _ in range(iterations):
            population = PopulationManager()
            for i in range(5):
                survivor = Survivor(f"Test{i}", random.randint(20, 50))
                population.add_survivor(survivor)
            survived = True
            for day in range(days):
                population.daily_update()
                if not population.survivors:
                    survived = False
                    break
            if survived:
                success_count += 1
        survival_rate = success_count / iterations
        self.balance_metrics["survival_rate"] = survival_rate
        return survival_rate

    def test_resource_balance(self, population_sizes=[10, 20, 50]):
        results = {}
        for size in population_sizes:
            population = PopulationManager()
            resources = {"food": 100, "water": 100}
            for i in range(size):
                survivor = Survivor(f"Test{i}", random.randint(20, 50))
                population.add_survivor(survivor)
            farmers = random.sample(population.survivors, min(5, size))
            for farmer in farmers:
                population.jobs["farmer"].assign_survivor(farmer)
            starvation_days = 0
            for day in range(7):
                consumption = population.calculate_total_consumption()
                food_production = len(farmers) * 5
                water_production = len(farmers) * 3
                resources["food"] += food_production - consumption["food"]
                resources["water"] += water_production - consumption["water"]
                if resources["food"] < 0 or resources["water"] < 0:
                    starvation_days += 1
            results[size] = {
                "starvation_days": starvation_days,
                "final_food": resources["food"],
                "final_water": resources["water"]
            }
        balance_score = sum(result["starvation_days"] for result in results.values()) / len(results)
        self.balance_metrics["resource_balance"] = 1 - (balance_score / 7)
        return results

    def test_combat_balance(self):
        results = {"win_rate": 0, "survivor_loss_rate": 0, "zombie_kill_rate": 0}
        test_runs = 20
        for _ in range(test_runs):
            survivors = [Survivor(f"Fighter{i}", 30) for i in range(5)]
            for s in survivors:
                s.skills["combat"] = random.randint(2, 5)
            zombies = [
                {"type": "shambler", "health": 100, "damage": 10},
                {"type": "shambler", "health": 100, "damage": 10},
                {"type": "runner", "health": 70, "damage": 15}
            ]
            survivor_losses = 0
            zombie_kills = 0
            while survivors and zombies:
                for survivor in survivors:
                    target = random.choice(zombies)
                    damage = survivor.skills["combat"] * 10
                    target["health"] -= damage
                    if target["health"] <= 0:
                        zombies.remove(target)
                        zombie_kills += 1
                for zombie in zombies:
                    target = random.choice(survivors)
                    target.health -= zombie["damage"]
                    if target.health <= 0:
                        survivors.remove(target)
                        survivor_losses += 1
            if zombies:
                results["win_rate"] += 0
            else:
                results["win_rate"] += 1
            results["survivor_loss_rate"] += survivor_losses / 5
            results["zombie_kill_rate"] += zombie_kills / 3
        results["win_rate"] /= test_runs
        results["survivor_loss_rate"] /= test_runs
        results["zombie_kill_rate"] /= test_runs
        combat_score = abs(results["win_rate"] - 0.5) + \
                      abs(results["survivor_loss_rate"] - 0.3) + \
                      abs(results["zombie_kill_rate"] - 0.8)
        self.balance_metrics["combat_balance"] = 1 - (combat_score / 1.6)
        return results


class GameValidator:
    def __init__(self):
        self.validation_rules = {
            "health_range": lambda s: 0 <= s.health <= 100,
            "hunger_range": lambda s: 0 <= s.hunger <= 100,
            "thirst_range": lambda s: 0 <= s.thirst <= 100,
            "morale_range": lambda s: 0 <= s.morale <= 100,
            "skill_range": lambda s: all(1 <= v <= 10 for v in s.skills.values())
        }
        self.errors = []
        self.warnings = []

    def add_validation_rule(self, rule_name, validation_func):
        self.validation_rules[rule_name] = validation_func

    def validate_game_config(self, config):
        required_keys = ["starting_resources", "starting_survivors", "difficulty"]
        for key in required_keys:
            if key not in config:
                self.errors.append(f"Missing required config key: {key}")
        if "difficulty" in config and config["difficulty"] not in ["easy", "medium", "hard"]:
            self.errors.append("Invalid difficulty setting")

    def validate_game_state(self, game_state):
        for survivor in game_state.get("survivors", []):
            for rule_name, rule_func in self.validation_rules.items():
                if not rule_func(survivor):
                    self.errors.append(f"Survivor {survivor.name} failed validation: {rule_name}")
        resources = game_state.get("resources", {})
        for resource, amount in resources.items():
            if amount < 0:
                self.warnings.append(f"Negative resource amount: {resource} = {amount}")
        buildings = game_state.get("buildings", [])
        if len(buildings) > 20:
            self.warnings.append("Large number of buildings may impact performance")

    def generate_validation_report(self):
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "is_valid": not bool(self.errors)
        }


class AutomatedTester(unittest.TestCase):
    def __init__(self):
        super().__init__()
        self.test_suite = unittest.TestSuite()
        self.test_results = []

    def generate_unit_tests(self, module_name):
        def test_survivor_creation():
            survivor = Survivor("Test", 30)
            self.assertEqual(survivor.name, "Test")
            self.assertEqual(survivor.age, 30)
            self.assertEqual(survivor.health, 100)
        self.test_suite.addTest(unittest.FunctionTestCase(test_survivor_creation))
        
        def test_needs_update():
            survivor = Survivor("Test", 30)
            survivor.update_needs()
            self.assertGreater(survivor.hunger, 0)
            self.assertGreater(survivor.thirst, 0)
        self.test_suite.addTest(unittest.FunctionTestCase(test_needs_update))
        
        def test_job_assignment():
            survivor = Survivor("Test", 30)
            job = Job("TestJob", "combat", 5)
            job.assign_survivor(survivor)
            self.assertEqual(survivor.current_job, "TestJob")
            self.assertIn(survivor, job.assigned_survivors)
        self.test_suite.addTest(unittest.FunctionTestCase(test_job_assignment))

    def run_stress_test(self, game_instance, actions=1000):
        valid_actions = ["add_survivor", "daily_update", "assign_job", "consume_resources"]
        for _ in range(actions):
            action = random.choice(valid_actions)
            try:
                if action == "add_survivor":
                    game_instance.population_manager.add_survivor(
                        Survivor(f"StressTest{random.randint(1, 100)}", random.randint(18, 60)))
                elif action == "daily_update":
                    game_instance.population_manager.daily_update()
                elif action == "assign_job":
                    if game_instance.population_manager.survivors:
                        survivor = random.choice(game_instance.population_manager.survivors)
                        job = random.choice(list(game_instance.population_manager.jobs.values()))
                        job.assign_survivor(survivor)
                elif action == "consume_resources":
                    if game_instance.population_manager.survivors:
                        survivor = random.choice(game_instance.population_manager.survivors)
                        survivor.consume_resources(random.randint(1, 3), random.randint(1, 2))
            except Exception as e:
                self.test_results.append({
                    "action": action,
                    "error": str(e),
                    "game_state": {
                        "survivors": len(game_instance.population_manager.survivors),
                        "resources": getattr(game_instance, 'resources', {})
                    }
                })

    def test_edge_cases(self):
        pm = PopulationManager()
        pm.daily_update()
        survivor = Survivor("Test", 30)
        survivor.consume_resources(1000, 1000)
        self.assertEqual(survivor.hunger, 0)
        self.assertEqual(survivor.thirst, 0)
        survivor.gain_experience("combat", 100)
        self.assertEqual(survivor.skills["combat"], 10)

    def generate_test_report(self):
        return {
            "unit_tests": self.test_suite.countTestCases(),
            "stress_test_errors": len([r for r in self.test_results if "error" in r]),
            "edge_cases_tested": 3,
            "success_rate": 1 - (len(self.test_results) / 1000) if self.test_results else 1
        }