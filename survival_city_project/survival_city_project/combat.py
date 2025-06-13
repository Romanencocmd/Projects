import math
import random

class CombatSystem:
    def __init__(self):
        self.weapon_stats = {
            "fists": {"damage": 5, "range": 1, "accuracy": 0.8},
            "knife": {"damage": 15, "range": 1, "accuracy": 0.85},
            "pistol": {"damage": 30, "range": 5, "accuracy": 0.7},
            "rifle": {"damage": 50, "range": 10, "accuracy": 0.75},
            "melee_weapon": {"damage": 25, "range": 2, "accuracy": 0.8}
        }

    def calculate_hit_chance(self, attacker_skill, weapon_accuracy, distance, is_night=False):
        base_chance = weapon_accuracy * (1 + attacker_skill * 0.05)
        distance_penalty = max(0.1, 1 - (distance / 20))
        night_penalty = 0.7 if is_night else 1.0
        return min(0.95, base_chance * distance_penalty * night_penalty)

    def calculate_damage(self, base_damage, attacker_skill, critical_hit=False):
        variance = random.uniform(0.8, 1.2)
        skill_bonus = 1 + (attacker_skill * 0.1)
        crit_multiplier = 1.5 if critical_hit else 1.0
        return int(base_damage * variance * skill_bonus * crit_multiplier)

    def resolve_attack(self, attacker, target, weapon, distance):
        weapon_stats = self.weapon_stats.get(weapon, {})
        if not weapon_stats:
            return {"hit": False, "damage": 0, "critical": False}
        
        hit_chance = self.calculate_hit_chance(
            attacker.get("combat_skill", 1),
            weapon_stats["accuracy"],
            distance
        )
        
        hit = random.random() <= hit_chance
        critical = hit and random.random() <= 0.1
        damage = self.calculate_damage(
            weapon_stats["damage"],
            attacker.get("combat_skill", 1),
            critical
        ) if hit else 0
        
        if hit:
            target.health -= damage
        
        return {
            "hit": hit,
            "damage": damage,
            "critical": critical,
            "distance": distance
        }

    def group_combat(self, survivors, zombies):
        results = []
        for survivor in survivors:
            if not zombies:
                break
            nearest_zombie = min(zombies, key=lambda z: math.dist(
                survivor["position"], z.position))
            distance = math.dist(survivor["position"], nearest_zombie.position)
            
            if distance <= self.weapon_stats.get(survivor["weapon"], {}).get("range", 1):
                attack_result = self.resolve_attack(
                    survivor, nearest_zombie, survivor["weapon"], distance)
                results.append(
                    f"{survivor['name']} attacked {nearest_zombie.zombie_type} - "
                    f"Hit: {attack_result['hit']}, "
                    f"Damage: {attack_result['damage']}, "
                    f"Critical: {attack_result['critical']}"
                )
                if nearest_zombie.health <= 0:
                    zombies.remove(nearest_zombie)
                    results.append(f"{nearest_zombie.zombie_type} died!")
        
        return results