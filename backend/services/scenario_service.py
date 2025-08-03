import json
import os
from typing import List, Optional
from backend.core.config import settings
from backend.core.models import Scenario

class ScenarioService:
    def __init__(self):
        self.scenarios_dir = settings.scenarios_dir
        self._ensure_scenarios_dir()
    
    def _ensure_scenarios_dir(self):
        os.makedirs(self.scenarios_dir, exist_ok=True)
    
    def get_all_scenarios(self) -> List[Scenario]:
        """Get all available scenarios"""
        scenarios = []
        if not os.path.exists(self.scenarios_dir):
            return scenarios
            
        for filename in os.listdir(self.scenarios_dir):
            if filename.endswith('.json'):
                try:
                    scenario = self.get_scenario_from_file(filename)
                    if scenario:
                        scenarios.append(scenario)
                except Exception as e:
                    print(f"Error loading scenario {filename}: {e}")
        
        return sorted(scenarios, key=lambda x: x.id)
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get a specific scenario by ID"""
        scenarios = self.get_all_scenarios()
        for scenario in scenarios:
            if scenario.id == scenario_id:
                return scenario
        return None
    
    def get_scenario_from_file(self, filename: str) -> Optional[Scenario]:
        """Load scenario from JSON file"""
        filepath = os.path.join(self.scenarios_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Scenario(**data)
        except Exception as e:
            print(f"Error loading scenario from {filename}: {e}")
            return None
    
    def save_scenario(self, scenario: Scenario) -> bool:
        """Save scenario to JSON file"""
        filename = f"{scenario.id}.json"
        filepath = os.path.join(self.scenarios_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scenario.dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving scenario {scenario.id}: {e}")
            return False