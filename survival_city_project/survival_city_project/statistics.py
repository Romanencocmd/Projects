import statistics
import json
from collections import defaultdict

class GameStatistics:
    def __init__(self):
        self.daily_snapshots = []
        self.event_counter = defaultdict(int)
        self.resource_flow = {
            "production": defaultdict(list),
            "consumption": defaultdict(list)
        }
        self.combat_stats = {
            "battles": 0,
            "wins": 0,
            "losses": 0,
            "zombies_killed": 0,
            "survivors_lost": 0
        }

    def record_daily_snapshot(self, game_state):
        snapshot = {
            "day": game_state.get("day", len(self.daily_snapshots) + 1),
            "population": len(game_state.get("survivors", [])),
            "resources": game_state.get("resources", {}).copy(),
            "buildings": len(game_state.get("buildings", [])),
            "morale": sum(s.morale for s in game_state.get("survivors", [])) / max(1, len(game_state.get("survivors", []))),
            "health": sum(s.health for s in game_state.get("survivors", [])) / max(1, len(game_state.get("survivors", [])))
        }
        self.daily_snapshots.append(snapshot)
        return "Daily snapshot recorded"

    def track_resource_flow(self, resource_type, produced, consumed):
        self.resource_flow["production"][resource_type].append(produced)
        self.resource_flow["consumption"][resource_type].append(consumed)
        return f"Tracked {resource_type}: +{produced}, -{consumed}"

    def update_combat_stats(self, battle_result):
        self.combat_stats["battles"] += 1
        if battle_result["outcome"] == "win":
            self.combat_stats["wins"] += 1
        else:
            self.combat_stats["losses"] += 1
        self.combat_stats["zombies_killed"] += battle_result.get("zombies_killed", 0)
        self.combat_stats["survivors_lost"] += battle_result.get("survivors_lost", 0)
        return "Combat stats updated"

    def calculate_survival_rating(self):
        if not self.daily_snapshots:
            return 0
        
        resource_score = 0
        for resource in self.resource_flow["production"]:
            avg_production = statistics.mean(self.resource_flow["production"][resource]) if self.resource_flow["production"][resource] else 0
            avg_consumption = statistics.mean(self.resource_flow["consumption"][resource]) if self.resource_flow["consumption"][resource] else 0
            if avg_consumption > 0:
                resource_score += (avg_production / avg_consumption) * 20
        
        combat_score = 0
        if self.combat_stats["battles"] > 0:
            win_rate = self.combat_stats["wins"] / self.combat_stats["battles"]
            zombie_ratio = self.combat_stats["zombies_killed"] / max(1, self.combat_stats["survivors_lost"])
            combat_score = (win_rate * 40) + (zombie_ratio * 10)
        
        pop_score = 0
        if self.daily_snapshots:
            last_snapshot = self.daily_snapshots[-1]
            pop_score = (last_snapshot["population"] * 2) + last_snapshot["morale"] + last_snapshot["health"]
        return (resource_score + combat_score + pop_score) / 3

class StatisticsAnalyzer:
    def __init__(self):
        self.stats = None

    def load_statistics(self, stats_file):
        try:
            with open(stats_file, 'r') as f:
                data = json.load(f)
                self.stats = GameStatistics()
                self.stats.__dict__.update(data)
            return True, "Statistics loaded successfully"
        except Exception as e:
            return False, f"Error loading statistics: {str(e)}"

    def generate_report(self, report_type="full"):
        if not self.stats:
            return "No statistics data available"
        
        report = {}
        
        if report_type in ["full", "resource_efficiency"]:
            resource_data = {}
            for resource in self.stats.resource_flow["production"]:
                production = self.stats.resource_flow["production"][resource]
                consumption = self.stats.resource_flow["consumption"][resource]
                if production and consumption:
                    efficiency = sum(production) / sum(consumption) if sum(consumption) > 0 else float('inf')
                    resource_data[resource] = {
                        "total_produced": sum(production),
                        "total_consumed": sum(consumption),
                        "efficiency": efficiency,
                        "trend": "positive" if production[-1] > consumption[-1] else "negative"
                    }
            report["resource_efficiency"] = resource_data
        
        if report_type in ["full", "combat_performance"]:
            combat_data = {
                "win_rate": self.stats.combat_stats["wins"] / max(1, self.stats.combat_stats["battles"]),
                "zombie_kill_ratio": self.stats.combat_stats["zombies_killed"] / max(1, self.stats.combat_stats["survivors_lost"]),
                "battles_per_day": self.stats.combat_stats["battles"] / max(1, len(self.stats.daily_snapshots))
            }
            report["combat_performance"] = combat_data
        
        if report_type in ["full", "population_growth"]:
            if len(self.stats.daily_snapshots) >= 2:
                growth = (self.stats.daily_snapshots[-1]["population"] - self.stats.daily_snapshots[0]["population"]) / self.stats.daily_snapshots[0]["population"]
                morale_change = self.stats.daily_snapshots[-1]["morale"] - self.stats.daily_snapshots[0]["morale"]
                health_change = self.stats.daily_snapshots[-1]["health"] - self.stats.daily_snapshots[0]["health"]
            else:
                growth = morale_change = health_change = 0
            
            pop_data = {
                "initial_population": self.stats.daily_snapshots[0]["population"] if self.stats.daily_snapshots else 0,
                "current_population": self.stats.daily_snapshots[-1]["population"] if self.stats.daily_snapshots else 0,
                "growth_rate": growth,
                "morale_change": morale_change,
                "health_change": health_change
            }
            report["population_growth"] = pop_data
        
        if report_type in ["full", "survival_timeline"]:
            timeline = []
            for i, snapshot in enumerate(self.stats.daily_snapshots):
                entry = {
                    "day": snapshot["day"],
                    "population": snapshot["population"],
                    "key_events": []
                }
                timeline.append(entry)
            report["survival_timeline"] = timeline
        report["overall_survival_rating"] = self.stats.calculate_survival_rating()
        return report

    def find_critical_moments(self):
        critical_moments = []
        
        if len(self.stats.daily_snapshots) < 3:
            return "Not enough data to identify critical moments"
        
        pop_changes = []
        for i in range(1, len(self.stats.daily_snapshots)):
            change = self.stats.daily_snapshots[i]["population"] - self.stats.daily_snapshots[i-1]["population"]
            pop_changes.append((i, change))
        
        large_drops = sorted(pop_changes, key=lambda x: x[1])[:3]
        for day, drop in large_drops:
            if drop < 0:
                critical_moments.append({
                    "day": day,
                    "type": "population_drop",
                    "severity": abs(drop),
                    "description": f"Significant population loss of {abs(drop)} survivors"
                })
        
        large_gains = sorted(pop_changes, key=lambda x: -x[1])[:3]
        for day, gain in large_gains:
            if gain > 0:
                critical_moments.append({
                    "day": day,
                    "type": "population_gain",
                    "severity": gain,
                    "description": f"Significant population gain of {gain} survivors"
                })
        
        for i in range(1, len(self.stats.daily_snapshots)):
            prev = self.stats.daily_snapshots[i-1]["resources"]
            curr = self.stats.daily_snapshots[i]["resources"]
            for resource in ["food", "water"]:
                if curr.get(resource, 0) < 10 and prev.get(resource, 0) >= 10:
                    critical_moments.append({
                        "day": i,
                        "type": "resource_crisis",
                        "resource": resource,
                        "description": f"{resource.capitalize()} crisis on day {i}"
                    })
        
        return sorted(critical_moments, key=lambda x: x["day"])

    def export_charts_data(self):
        chart_data = {
            "population": {
                "labels": [str(s["day"]) for s in self.stats.daily_snapshots],
                "data": [s["population"] for s in self.stats.daily_snapshots]
            },
            "morale": {
                "labels": [str(s["day"]) for s in self.stats.daily_snapshots],
                "data": [s["morale"] for s in self.stats.daily_snapshots]
            },
            "resources": {
                "labels": [str(s["day"]) for s in self.stats.daily_snapshots],
                "datasets": {
                    "food": [s["resources"].get("food", 0) for s in self.stats.daily_snapshots],
                    "water": [s["resources"].get("water", 0) for s in self.stats.daily_snapshots]
                }
            }
        }
        return chart_data