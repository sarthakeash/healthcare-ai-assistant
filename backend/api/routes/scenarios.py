from typing import List
from fastapi import APIRouter, HTTPException
from backend.core.models import Scenario
from backend.services.scenario_service import ScenarioService

router = APIRouter()
scenario_service = ScenarioService()

@router.get("/", response_model=List[Scenario])
async def get_scenarios():
    """Get all available scenarios"""
    return scenario_service.get_all_scenarios()

@router.get("/{scenario_id}", response_model=Scenario)
async def get_scenario(scenario_id: str):
    """Get a specific scenario by ID"""
    scenario = scenario_service.get_scenario(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario