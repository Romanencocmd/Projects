import random

class EventProbabilityEngine:
    def __init__(self):
        self.base_events = {
            "zombie_attack": {"base_prob": 0.3, "severity_range": (1, 5)},
            "survivor_joins": {"base_prob": 0.1, "severity_range": (1, 3)},
            "resource_discovery": {"base_prob": 0.15, "severity_range": (1, 4)},
            "equipment_failure": {"base_prob": 0.2, "severity_range": (1, 3)},
            "disease_outbreak": {"base_prob": 0.1, "severity_range": (2, 5)},
            "weather_event": {"base_prob": 0.25, "severity_range": (1, 4)}
        }
        self.condition_modifiers = {
            "day_number": lambda x: 1 + (x / 100),
            "population": lambda x: 1 + (x / 50),
            "resource_shortage": lambda x: 1 + (x / 20),
            "weather": {"clear": 0.8, "rain": 1.2, "storm": 1.5}
        }

    def calculate_event_probability(self, event_type, conditions):
        if event_type not in self.base_events:
            return 0
        base_prob = self.base_events[event_type]["base_prob"]
        modified_prob = base_prob
        modified_prob *= self.condition_modifiers["day_number"](conditions.get("day_number", 1))
        modified_prob *= self.condition_modifiers["population"](conditions.get("population", 1))
        if event_type in ["zombie_attack", "equipment_failure", "disease_outbreak"]:
            modified_prob *= self.condition_modifiers["resource_shortage"](
                conditions.get("resource_shortage", 0))
        current_weather = conditions.get("weather", "clear")
        weather_mod = self.condition_modifiers["weather"].get(current_weather, 1)
        modified_prob *= weather_mod
        return max(0, min(1, modified_prob))

    def generate_severity(self, event_type, conditions):
        if event_type not in self.base_events:
            return 0
        min_sev, max_sev = self.base_events[event_type]["severity_range"]
        base_severity = random.randint(min_sev, max_sev)
        day_mod = 1 + (conditions.get("day_number", 1) / 50)
        final_severity = min(max_sev * 2, base_severity * day_mod)
        return round(final_severity)

    def check_event_triggers(self, game_state):
        triggered_events = []
        for event_type in self.base_events:
            prob = self.calculate_event_probability(event_type, game_state)
            if random.random() < prob:
                severity = self.generate_severity(event_type, game_state)
                triggered_events.append({
                    "type": event_type,
                    "severity": severity,
                    "day": game_state.get("day_number", 1)
                })
        return triggered_events

    def calculate_cascade_probability(self, initial_event, game_state):
        cascade_map = {
            "equipment_failure": [("zombie_attack", 0.4), ("survivor_joins", 0.1)],
            "disease_outbreak": [("resource_discovery", 0.2), ("survivor_joins", -0.3)],
            "weather_event": [("resource_discovery", 0.1), ("equipment_failure", 0.3)]
        }
        cascades = []
        if initial_event["type"] in cascade_map:
            for followup_type, prob_mod in cascade_map[initial_event["type"]]:
                base_prob = self.base_events[followup_type]["base_prob"]
                new_prob = max(0, min(1, base_prob + prob_mod))
                if random.random() < new_prob:
                    severity = self.generate_severity(followup_type, game_state)
                    cascades.append({
                        "type": followup_type,
                        "severity": severity,
                        "day": game_state.get("day_number", 1)
                    })
        return cascades


class EventChainSystem:
    def __init__(self, probability_engine):
        self.probability_engine = probability_engine
        self.active_event_chains = []
        self.event_history = []

    def create_event_chain(self, initial_event, max_length=3):
        chain = [initial_event]
        current_event = initial_event
        for _ in range(max_length - 1):
            cascades = self.probability_engine.calculate_cascade_probability(current_event, {
                "day_number": current_event["day"],
                "population": 10
            })
            if not cascades:
                break
            next_event = random.choice(cascades)
            chain.append(next_event)
            current_event = next_event
        return chain

    def calculate_combined_impact(self, events):
        impact = 0
        multipliers = {
            "zombie_attack": 1.5,
            "survivor_joins": -1,
            "resource_discovery": -0.8,
            "equipment_failure": 1.2,
            "disease_outbreak": 2,
            "weather_event": 1
        }
        for event in events:
            impact += event["severity"] * multipliers.get(event["type"], 1)
        return impact

    def get_event_forecast(self, game_state, days=3):
        forecast = []
        for day in range(game_state["day_number"], game_state["day_number"] + days):
            daily_forecast = {}
            for event_type in self.probability_engine.base_events:
                prob = self.probability_engine.calculate_event_probability(
                    event_type, {**game_state, "day_number": day})
                daily_forecast[event_type] = prob
            forecast.append({"day": day, "probabilities": daily_forecast})
        return forecast

    def analyze_event_patterns(self):
        if not self.event_history:
            return {}
        event_counts = {}
        for event in self.event_history:
            event_counts[event["type"]] = event_counts.get(event["type"], 0) + 1
        sequences = []
        for i in range(len(self.event_history) - 1):
            seq = (self.event_history[i]["type"], self.event_history[i+1]["type"])
            sequences.append(seq)
        seq_counts = {}
        for seq in sequences:
            seq_counts[seq] = seq_counts.get(seq, 0) + 1
        days_between = []
        event_days = [e["day"] for e in self.event_history]
        for i in range(len(event_days) - 1):
            days_between.append(event_days[i+1] - event_days[i])
        avg_days_between = sum(days_between) / len(days_between) if days_between else 0
        return {
            "event_counts": event_counts,
            "common_sequences": sorted(seq_counts.items(), key=lambda x: -x[1])[:5],
            "average_days_between_events": avg_days_between
        }